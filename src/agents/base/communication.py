"""Agent communication system for inter-agent messaging and coordination."""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from ...utils.logging import get_logger
from .agent import AgentTask, AgentResponse, AgentType, TaskPriority
from .registry import agent_registry

logger = get_logger(__name__)


class Message:
    """Base message class for inter-agent communication."""
    
    def __init__(
        self,
        sender_id: str,
        recipient_id: Optional[str] = None,
        recipient_type: Optional[AgentType] = None,
        message_type: str = "generic",
        payload: Dict[str, Any] = None,
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        ttl_seconds: int = 300,
    ):
        """
        Initialize a message.
        
        Args:
            sender_id: ID of the sending agent.
            recipient_id: ID of the target agent (optional if recipient_type is specified).
            recipient_type: Type of target agent (for load balancing).
            message_type: Type of message.
            payload: Message payload.
            correlation_id: Correlation ID for request tracking.
            reply_to: Message ID this is a reply to.
            ttl_seconds: Time to live in seconds.
        """
        self.id = str(uuid4())
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.recipient_type = recipient_type
        self.message_type = message_type
        self.payload = payload or {}
        self.correlation_id = correlation_id or str(uuid4())
        self.reply_to = reply_to
        self.ttl_seconds = ttl_seconds
        self.created_at = datetime.utcnow()
        self.attempts = 0
        self.max_attempts = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "recipient_type": self.recipient_type.value if self.recipient_type else None,
            "message_type": self.message_type,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "reply_to": self.reply_to,
            "ttl_seconds": self.ttl_seconds,
            "created_at": self.created_at.isoformat(),
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        message = cls(
            sender_id=data["sender_id"],
            recipient_id=data.get("recipient_id"),
            recipient_type=AgentType(data["recipient_type"]) if data.get("recipient_type") else None,
            message_type=data["message_type"],
            payload=data.get("payload", {}),
            correlation_id=data.get("correlation_id"),
            reply_to=data.get("reply_to"),
            ttl_seconds=data.get("ttl_seconds", 300),
        )
        message.id = data["id"]
        message.created_at = datetime.fromisoformat(data["created_at"])
        message.attempts = data.get("attempts", 0)
        message.max_attempts = data.get("max_attempts", 3)
        return message
    
    def is_expired(self) -> bool:
        """Check if the message has expired."""
        elapsed = (datetime.utcnow() - self.created_at).total_seconds()
        return elapsed > self.ttl_seconds
    
    def can_retry(self) -> bool:
        """Check if the message can be retried."""
        return self.attempts < self.max_attempts and not self.is_expired()


class AgentCommunication:
    """
    Communication system for inter-agent messaging and coordination.
    
    Provides publish/subscribe messaging, request/response patterns,
    and coordination primitives for the multi-agent system.
    """
    
    def __init__(self):
        """Initialize the communication system."""
        self._message_queue: asyncio.Queue[Message] = asyncio.Queue()
        self._subscribers: Dict[str, List[callable]] = {}
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._running = False
        self._message_processor_task: Optional[asyncio.Task] = None
        
        logger.info("Agent communication system initialized")
    
    async def start(self) -> None:
        """Start the communication system."""
        if self._running:
            logger.warning("Communication system is already running")
            return
        
        self._running = True
        self._message_processor_task = asyncio.create_task(self._process_messages())
        
        logger.info("Agent communication system started")
    
    async def stop(self) -> None:
        """Stop the communication system."""
        if not self._running:
            logger.warning("Communication system is not running")
            return
        
        self._running = False
        
        if self._message_processor_task:
            self._message_processor_task.cancel()
            try:
                await self._message_processor_task
            except asyncio.CancelledError:
                pass
            self._message_processor_task = None
        
        # Cancel pending requests
        for future in self._pending_requests.values():
            if not future.done():
                future.cancel()
        self._pending_requests.clear()
        
        logger.info("Agent communication system stopped")
    
    async def send_message(self, message: Message) -> bool:
        """
        Send a message to an agent.
        
        Args:
            message: The message to send.
            
        Returns:
            bool: True if message was queued successfully.
        """
        if not self._running:
            logger.error("Communication system is not running")
            return False
        
        try:
            await self._message_queue.put(message)
            
            logger.debug(
                "Message queued",
                message_id=message.id,
                sender=message.sender_id,
                recipient=message.recipient_id or message.recipient_type.value if message.recipient_type else "unknown",
                type=message.message_type,
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to queue message: {e}")
            return False
    
    async def send_task(
        self,
        sender_id: str,
        agent_type: AgentType,
        operation: str,
        payload: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout_seconds: int = 300,
    ) -> AgentResponse:
        """
        Send a task to an agent and wait for response.
        
        Args:
            sender_id: ID of the sending agent.
            agent_type: Type of target agent.
            operation: Operation to perform.
            payload: Task payload.
            priority: Task priority.
            timeout_seconds: Timeout for the task.
            
        Returns:
            AgentResponse: The response from the agent.
            
        Raises:
            TimeoutError: If the task times out.
            RuntimeError: If no agent is available.
        """
        # Find an available agent
        agent = agent_registry.get_least_loaded_agent(agent_type)
        if not agent:
            raise RuntimeError(f"No healthy agent available for type {agent_type.value}")
        
        # Create task
        task = AgentTask(
            agent_type=agent_type,
            operation=operation,
            payload=payload or {},
            priority=priority,
            timeout_seconds=timeout_seconds,
        )
        
        # Submit task to agent
        await agent.submit_task(task)
        
        # Wait for response (this is simplified - in a real implementation,
        # you'd need a more sophisticated response tracking mechanism)
        # For now, we'll use a simple timeout
        start_time = asyncio.get_event_loop().time()
        
        while True:
            if task.status.value in ["completed", "failed", "cancelled"]:
                break
            
            if asyncio.get_event_loop().time() - start_time > timeout_seconds:
                raise TimeoutError(f"Task {task.id} timed out")
            
            await asyncio.sleep(0.1)
        
        # Create response based on task status
        if task.status.value == "completed":
            return AgentResponse(
                task_id=task.id,
                agent_id=agent.agent_id,
                agent_type=agent_type,
                success=True,
                data={"status": "completed"},
            )
        else:
            return AgentResponse(
                task_id=task.id,
                agent_id=agent.agent_id,
                agent_type=agent_type,
                success=False,
                errors=[task.error_message or "Task failed"],
            )
    
    async def request_response(
        self,
        sender_id: str,
        recipient_type: AgentType,
        message_type: str,
        payload: Dict[str, Any] = None,
        timeout_seconds: int = 30,
    ) -> Optional[Message]:
        """
        Send a request message and wait for a response.
        
        Args:
            sender_id: ID of the sending agent.
            recipient_type: Type of target agent.
            message_type: Type of message.
            payload: Message payload.
            timeout_seconds: Timeout for the response.
            
        Returns:
            Message: The response message or None if timeout.
        """
        # Create request message
        request = Message(
            sender_id=sender_id,
            recipient_type=recipient_type,
            message_type=message_type,
            payload=payload or {},
        )
        
        # Create future for response
        response_future = asyncio.Future()
        self._pending_requests[request.correlation_id] = response_future
        
        try:
            # Send request
            await self.send_message(request)
            
            # Wait for response
            response = await asyncio.wait_for(response_future, timeout=timeout_seconds)
            return response
            
        except asyncio.TimeoutError:
            logger.warning(
                f"Request timeout",
                correlation_id=request.correlation_id,
                message_type=message_type,
            )
            return None
            
        finally:
            # Clean up
            self._pending_requests.pop(request.correlation_id, None)
    
    async def publish(
        self,
        sender_id: str,
        event_type: str,
        payload: Dict[str, Any] = None,
    ) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            sender_id: ID of the publishing agent.
            event_type: Type of event.
            payload: Event payload.
        """
        message = Message(
            sender_id=sender_id,
            message_type=f"event.{event_type}",
            payload=payload or {},
        )
        
        # Notify all subscribers
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        asyncio.create_task(callback(message))
                    else:
                        callback(message)
                except Exception as e:
                    logger.error(f"Error in event subscriber: {e}")
        
        logger.debug(
            "Event published",
            sender=sender_id,
            event_type=event_type,
            subscribers=len(self._subscribers.get(event_type, [])),
        )
    
    def subscribe(self, event_type: str, callback: callable) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to.
            callback: Callback function to invoke when event is published.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
        
        logger.debug(
            "Subscribed to event",
            event_type=event_type,
            callback=callback.__name__,
        )
    
    def unsubscribe(self, event_type: str, callback: callable) -> None:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from.
            callback: Callback function to remove.
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
                if not self._subscribers[event_type]:
                    del self._subscribers[event_type]
                
                logger.debug(
                    "Unsubscribed from event",
                    event_type=event_type,
                    callback=callback.__name__,
                )
            except ValueError:
                logger.warning(
                    "Callback not found for unsubscribe",
                    event_type=event_type,
                    callback=callback.__name__,
                )
    
    async def _process_messages(self) -> None:
        """Background message processor."""
        while self._running:
            try:
                # Get message from queue with timeout
                try:
                    message = await asyncio.wait_for(self._message_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Process message
                await self._deliver_message(message)
                
            except Exception as e:
                logger.error(f"Error in message processor: {e}")
                await asyncio.sleep(1)
    
    async def _deliver_message(self, message: Message) -> None:
        """
        Deliver a message to the target agent.
        
        Args:
            message: The message to deliver.
        """
        message.attempts += 1
        
        # Check if message has expired
        if message.is_expired():
            logger.warning(
                f"Message expired",
                message_id=message.id,
                age_seconds=(datetime.utcnow() - message.created_at).total_seconds(),
            )
            return
        
        try:
            # Find target agent
            target_agent = None
            
            if message.recipient_id:
                target_agent = agent_registry.get_agent(message.recipient_id)
            elif message.recipient_type:
                target_agent = agent_registry.get_least_loaded_agent(message.recipient_type)
            
            if not target_agent:
                logger.warning(
                    f"No target agent found",
                    message_id=message.id,
                    recipient_id=message.recipient_id,
                    recipient_type=message.recipient_type.value if message.recipient_type else None,
                )
                
                # Retry if possible
                if message.can_retry():
                    await asyncio.sleep(1)  # Brief delay
                    await self._message_queue.put(message)
                
                return
            
            # Deliver message based on type
            await self._handle_message(target_agent, message)
            
        except Exception as e:
            logger.error(
                f"Failed to deliver message: {e}",
                message_id=message.id,
                attempts=message.attempts,
            )
            
            # Retry if possible
            if message.can_retry():
                await asyncio.sleep(2 ** message.attempts)  # Exponential backoff
                await self._message_queue.put(message)
    
    async def _handle_message(self, target_agent, message: Message) -> None:
        """
        Handle message delivery to target agent.
        
        Args:
            target_agent: The target agent.
            message: The message to handle.
        """
        # Handle different message types
        if message.message_type.startswith("event."):
            # Event messages - just log and notify
            event_type = message.message_type[6:]  # Remove "event." prefix
            
            logger.debug(
                f"Event delivered",
                event_type=event_type,
                target_agent=target_agent.agent_id,
                sender=message.sender_id,
            )
            
        elif message.message_type == "task":
            # Task messages - convert to AgentTask and submit
            task_data = message.payload
            task = AgentTask(
                agent_type=target_agent.agent_type,
                operation=task_data.get("operation", "unknown"),
                payload=task_data.get("payload", {}),
                correlation_id=message.correlation_id,
            )
            
            await target_agent.submit_task(task)
            
        elif message.message_type == "response":
            # Response messages - resolve pending requests
            if message.correlation_id in self._pending_requests:
                future = self._pending_requests[message.correlation_id]
                if not future.done():
                    future.set_result(message)
            
        else:
            # Generic messages - log
            logger.debug(
                f"Message delivered",
                message_type=message.message_type,
                target_agent=target_agent.agent_id,
                sender=message.sender_id,
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get communication system statistics.
        
        Returns:
            dict: Communication statistics.
        """
        return {
            "running": self._running,
            "queue_size": self._message_queue.qsize(),
            "pending_requests": len(self._pending_requests),
            "subscribers": {
                event_type: len(callbacks)
                for event_type, callbacks in self._subscribers.items()
            },
        }


# Global communication instance
agent_communication = AgentCommunication()