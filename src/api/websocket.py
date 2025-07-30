"""WebSocket server for real-time communication."""

import asyncio
import json
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.websockets import WebSocketState
import jwt

from ..config.settings import get_settings
from ..utils.logging import get_logger
from ..agents.base.registry import agent_registry

logger = get_logger(__name__)
settings = get_settings()

class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: str):
        """Accept a WebSocket connection."""
        await websocket.accept()
        
        self.active_connections[connection_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "last_ping": datetime.utcnow()
        }
        
        logger.info(f"WebSocket connection established", 
                   connection_id=connection_id, user_id=user_id)
        
        # Send initial connection confirmation
        await self.send_personal_message({
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection."""
        if connection_id in self.active_connections:
            metadata = self.connection_metadata.get(connection_id, {})
            user_id = metadata.get("user_id")
            
            # Remove from active connections
            del self.active_connections[connection_id]
            del self.connection_metadata[connection_id]
            
            # Remove from user connections
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            logger.info(f"WebSocket connection closed", 
                       connection_id=connection_id, user_id=user_id)
    
    async def send_personal_message(self, message: Dict[str, Any], connection_id: str):
        """Send a message to a specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                self.disconnect(connection_id)
    
    async def send_user_message(self, message: Dict[str, Any], user_id: str):
        """Send a message to all connections for a specific user."""
        if user_id in self.user_connections:
            connection_ids = list(self.user_connections[user_id])
            for connection_id in connection_ids:
                await self.send_personal_message(message, connection_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all active connections."""
        if not self.active_connections:
            return
        
        disconnected_connections = []
        
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to {connection_id}: {e}")
                disconnected_connections.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected_connections:
            self.disconnect(connection_id)
    
    async def broadcast_agent_status(self):
        """Broadcast current agent status to all connections."""
        try:
            agents_status = []
            for agent in agent_registry.get_all_agents():
                agents_status.append({
                    "id": agent.agent_id,
                    "name": agent.name,
                    "type": agent.agent_type.value,
                    "status": agent.status.value,
                    "health": agent.health.value,
                    "last_activity": agent.last_activity.isoformat() if agent.last_activity else None,
                    "tasks_completed": agent.tasks_completed,
                    "tasks_pending": agent.task_queue.qsize() if hasattr(agent.task_queue, 'qsize') else 0,
                    "performance_metrics": agent.performance_metrics
                })
            
            await self.broadcast({
                "type": "agent_status_update",
                "data": agents_status,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to broadcast agent status: {e}")
    
    async def broadcast_system_health(self):
        """Broadcast system health information."""
        try:
            # Get system health from various components
            health_data = {
                "agents": {
                    "total": len(agent_registry.get_all_agents()),
                    "healthy": len([a for a in agent_registry.get_all_agents() 
                                  if a.health.value == "healthy"]),
                    "active": len([a for a in agent_registry.get_all_agents() 
                                 if a.status.value == "active"])
                },
                "websocket": {
                    "active_connections": len(self.active_connections),
                    "connected_users": len(self.user_connections)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.broadcast({
                "type": "system_health_update",
                "data": health_data,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to broadcast system health: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection manager statistics."""
        return {
            "active_connections": len(self.active_connections),
            "connected_users": len(self.user_connections),
            "connections_by_user": {
                user_id: len(connections) 
                for user_id, connections in self.user_connections.items()
            }
        }

# Global connection manager
connection_manager = ConnectionManager()

async def get_current_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """Extract user information from JWT token."""
    try:
        payload = jwt.decode(
            token, 
            settings.security.secret_key, 
            algorithms=[settings.security.algorithm]
        )
        
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role", "user"),
            "permissions": payload.get("permissions", [])
        }
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None

async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time communication."""
    connection_id = None
    
    try:
        # Get token from query parameters
        token = websocket.query_params.get("token")
        if not token:
            logger.warning("WebSocket connection attempted without token")
            await websocket.close(code=4001, reason="Missing authentication token")
            return
        
        # Validate token and get user info
        user_info = await get_current_user_from_token(token)
        if not user_info:
            logger.warning("WebSocket connection attempted with invalid token")
            await websocket.close(code=4001, reason="Invalid authentication token")
            return
        
        # Generate unique connection ID
        connection_id = f"{user_info['user_id']}_{datetime.utcnow().timestamp()}"
        
        # Accept connection
        await connection_manager.connect(websocket, connection_id, user_info["user_id"])
        
        # Send initial agent status
        await connection_manager.broadcast_agent_status()
        await connection_manager.broadcast_system_health()
        
        # Listen for messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()
                await handle_websocket_message(connection_id, user_info, data)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket client disconnected: {connection_id}")
                break
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from {connection_id}")
                await connection_manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, connection_id)
            except Exception as e:
                logger.error(f"Error handling WebSocket message from {connection_id}: {e}")
                await connection_manager.send_personal_message({
                    "type": "error", 
                    "message": "Internal server error"
                }, connection_id)
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected during handshake")
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        if connection_id:
            connection_manager.disconnect(connection_id)

async def handle_websocket_message(
    connection_id: str, 
    user_info: Dict[str, Any], 
    message: Dict[str, Any]
):
    """Handle incoming WebSocket messages from clients."""
    message_type = message.get("type")
    
    try:
        if message_type == "ping":
            # Handle ping messages
            await connection_manager.send_personal_message({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            }, connection_id)
            
            # Update last ping time
            if connection_id in connection_manager.connection_metadata:
                connection_manager.connection_metadata[connection_id]["last_ping"] = datetime.utcnow()
        
        elif message_type == "subscribe_agent_updates":
            # Client wants to subscribe to agent updates for specific agents
            agent_ids = message.get("agent_ids", [])
            
            # Store subscription preferences (in a real implementation, 
            # you'd want to store this more persistently)
            await connection_manager.send_personal_message({
                "type": "subscription_confirmed",
                "agent_ids": agent_ids,
                "timestamp": datetime.utcnow().isoformat()
            }, connection_id)
        
        elif message_type == "request_agent_status":
            # Client requesting current agent status
            await connection_manager.broadcast_agent_status()
        
        elif message_type == "request_system_health":
            # Client requesting system health
            await connection_manager.broadcast_system_health()
        
        else:
            logger.warning(f"Unknown message type: {message_type}")
            await connection_manager.send_personal_message({
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }, connection_id)
            
    except Exception as e:
        logger.error(f"Error handling message type {message_type}: {e}")
        await connection_manager.send_personal_message({
            "type": "error",
            "message": "Error processing message"
        }, connection_id)

async def broadcast_agent_update(agent_id: str, update_data: Dict[str, Any]):
    """Broadcast an agent status update to all connected clients."""
    try:
        await connection_manager.broadcast({
            "type": "agent_status_update",
            "agent_id": agent_id,
            "data": update_data,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to broadcast agent update: {e}")

async def broadcast_task_update(task_id: str, agent_id: str, status: str, data: Dict[str, Any] = None):
    """Broadcast a task status update to all connected clients."""
    try:
        await connection_manager.broadcast({
            "type": "task_update",
            "task_id": task_id,
            "agent_id": agent_id,
            "status": status,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to broadcast task update: {e}")

async def broadcast_system_notification(
    notification_type: str, 
    message: str, 
    level: str = "info",
    data: Dict[str, Any] = None
):
    """Broadcast a system notification to all connected clients."""
    try:
        await connection_manager.broadcast({
            "type": "system_notification",
            "notification_type": notification_type,
            "message": message,
            "level": level,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to broadcast system notification: {e}")

# Background task for periodic updates
async def periodic_status_broadcaster():
    """Periodically broadcast status updates to all connected clients."""
    while True:
        try:
            if connection_manager.active_connections:
                await connection_manager.broadcast_agent_status()
                await connection_manager.broadcast_system_health()
            
            await asyncio.sleep(30)  # Broadcast every 30 seconds
            
        except Exception as e:
            logger.error(f"Error in periodic status broadcaster: {e}")
            await asyncio.sleep(30)

# Global task reference for broadcaster
_broadcaster_task = None

# Start the periodic broadcaster
def start_periodic_broadcaster():
    """Start the background task for periodic status updates."""
    global _broadcaster_task
    _broadcaster_task = asyncio.create_task(periodic_status_broadcaster())


def stop_periodic_broadcaster():
    """Stop the periodic broadcaster task."""
    global _broadcaster_task
    if _broadcaster_task and not _broadcaster_task.done():
        _broadcaster_task.cancel()

async def authenticate_websocket(token: str) -> Optional[Dict[str, Any]]:
    """Authenticate WebSocket connection using JWT token."""
    return await get_current_user_from_token(token)


# Export for use in main app
__all__ = [
    'websocket_endpoint',
    'connection_manager',
    'broadcast_agent_update',
    'broadcast_task_update', 
    'broadcast_system_notification',
    'start_periodic_broadcaster',
    'stop_periodic_broadcaster',
    'authenticate_websocket'
]