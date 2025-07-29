"""Tests for WebSocket functionality."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi import WebSocket, WebSocketDisconnect

from src.api.websocket import (
    ConnectionManager,
    websocket_endpoint,
    authenticate_websocket,
    start_periodic_broadcaster,
    stop_periodic_broadcaster
)


class TestConnectionManager:
    """Test WebSocket connection manager."""
    
    @pytest.fixture
    def manager(self):
        """Create connection manager for testing."""
        return ConnectionManager()
    
    @pytest.mark.asyncio
    async def test_connect_user(self, manager):
        """Test connecting a user."""
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        
        await manager.connect(mock_websocket, "user123")
        
        mock_websocket.accept.assert_called_once()
        assert "user123" in manager.active_connections
        assert manager.active_connections["user123"] == mock_websocket
    
    def test_disconnect_user(self, manager):
        """Test disconnecting a user."""
        mock_websocket = AsyncMock()
        manager.active_connections["user123"] = mock_websocket
        
        manager.disconnect("user123")
        
        assert "user123" not in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_send_personal_message(self, manager):
        """Test sending personal message to user."""
        mock_websocket = AsyncMock()
        manager.active_connections["user123"] = mock_websocket
        
        await manager.send_personal_message("Hello", "user123")
        
        mock_websocket.send_text.assert_called_once_with("Hello")
    
    @pytest.mark.asyncio
    async def test_send_personal_message_user_not_connected(self, manager):
        """Test sending message to disconnected user."""
        # Should not raise exception
        await manager.send_personal_message("Hello", "user123")
    
    @pytest.mark.asyncio
    async def test_broadcast_success(self, manager):
        """Test broadcasting message to all users."""
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        manager.active_connections["user1"] = mock_websocket1
        manager.active_connections["user2"] = mock_websocket2
        
        await manager.broadcast("Hello everyone")
        
        mock_websocket1.send_text.assert_called_once_with("Hello everyone")
        mock_websocket2.send_text.assert_called_once_with("Hello everyone")
    
    @pytest.mark.asyncio
    async def test_broadcast_with_failed_connection(self, manager):
        """Test broadcasting with one failed connection."""
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        mock_websocket2.send_text.side_effect = Exception("Connection failed")
        
        manager.active_connections["user1"] = mock_websocket1
        manager.active_connections["user2"] = mock_websocket2
        
        await manager.broadcast("Hello everyone")
        
        # user1 should receive message
        mock_websocket1.send_text.assert_called_once_with("Hello everyone")
        # user2 should be disconnected due to error
        assert "user2" not in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_send_agent_status(self, manager):
        """Test sending agent status update."""
        mock_websocket = AsyncMock()
        manager.active_connections["user123"] = mock_websocket
        
        status_data = {
            "agent_id": "lead_intake",
            "status": "running",
            "last_activity": "2024-01-15T10:00:00Z"
        }
        
        await manager.send_agent_status("user123", status_data)
        
        expected_message = {
            "type": "agent_status",
            "data": status_data
        }
        mock_websocket.send_json.assert_called_once_with(expected_message)
    
    @pytest.mark.asyncio
    async def test_send_system_alert(self, manager):
        """Test sending system alert."""
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        manager.active_connections["user1"] = mock_websocket1
        manager.active_connections["user2"] = mock_websocket2
        
        alert_data = {
            "level": "warning",
            "message": "System maintenance in 10 minutes",
            "timestamp": "2024-01-15T10:00:00Z"
        }
        
        await manager.send_system_alert(alert_data)
        
        expected_message = {
            "type": "system_alert",
            "data": alert_data
        }
        
        mock_websocket1.send_json.assert_called_once_with(expected_message)
        mock_websocket2.send_json.assert_called_once_with(expected_message)


class TestWebSocketEndpoint:
    """Test WebSocket endpoint functionality."""
    
    @pytest.mark.asyncio
    async def test_websocket_endpoint_successful_connection(self):
        """Test successful WebSocket connection."""
        mock_websocket = AsyncMock()
        mock_websocket.headers = {"authorization": "Bearer valid-token"}
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(side_effect=WebSocketDisconnect())
        
        with patch('src.api.websocket.authenticate_websocket', return_value="user123"):
            with patch('src.api.websocket.manager') as mock_manager:
                mock_manager.connect = AsyncMock()
                mock_manager.disconnect = Mock()
                
                await websocket_endpoint(mock_websocket)
                
                mock_manager.connect.assert_called_once_with(mock_websocket, "user123")
                mock_manager.disconnect.assert_called_once_with("user123")
    
    @pytest.mark.asyncio
    async def test_websocket_endpoint_authentication_failure(self):
        """Test WebSocket connection with authentication failure."""
        mock_websocket = AsyncMock()
        mock_websocket.headers = {"authorization": "Bearer invalid-token"}
        mock_websocket.close = AsyncMock()
        
        with patch('src.api.websocket.authenticate_websocket', return_value=None):
            await websocket_endpoint(mock_websocket)
            
            mock_websocket.close.assert_called_once_with(code=4001, reason="Authentication failed")
    
    @pytest.mark.asyncio
    async def test_websocket_endpoint_handles_messages(self):
        """Test WebSocket endpoint handling incoming messages."""
        mock_websocket = AsyncMock()
        mock_websocket.headers = {"authorization": "Bearer valid-token"}
        mock_websocket.accept = AsyncMock()
        
        # Simulate receiving messages then disconnect
        messages = ["ping", "status_request"]
        mock_websocket.receive_text = AsyncMock(side_effect=messages + [WebSocketDisconnect()])
        
        with patch('src.api.websocket.authenticate_websocket', return_value="user123"):
            with patch('src.api.websocket.manager') as mock_manager:
                mock_manager.connect = AsyncMock()
                mock_manager.disconnect = Mock()
                mock_manager.send_personal_message = AsyncMock()
                
                await websocket_endpoint(mock_websocket)
                
                # Should handle ping message
                mock_manager.send_personal_message.assert_any_call("pong", "user123")


class TestWebSocketAuthentication:
    """Test WebSocket authentication."""
    
    def test_authenticate_websocket_valid_token(self):
        """Test authentication with valid token."""
        mock_websocket = Mock()
        mock_websocket.headers = {"authorization": "Bearer valid-token"}
        
        with patch('src.api.websocket.decode_jwt_token', return_value={"sub": "user123"}):
            user_id = authenticate_websocket(mock_websocket)
            assert user_id == "user123"
    
    def test_authenticate_websocket_no_authorization_header(self):
        """Test authentication without authorization header."""
        mock_websocket = Mock()
        mock_websocket.headers = {}
        
        user_id = authenticate_websocket(mock_websocket)
        assert user_id is None
    
    def test_authenticate_websocket_invalid_token_format(self):
        """Test authentication with invalid token format."""
        mock_websocket = Mock()
        mock_websocket.headers = {"authorization": "invalid-format"}
        
        user_id = authenticate_websocket(mock_websocket)
        assert user_id is None
    
    def test_authenticate_websocket_invalid_token(self):
        """Test authentication with invalid token."""
        mock_websocket = Mock()
        mock_websocket.headers = {"authorization": "Bearer invalid-token"}
        
        with patch('src.api.websocket.decode_jwt_token', side_effect=Exception("Invalid token")):
            user_id = authenticate_websocket(mock_websocket)
            assert user_id is None


class TestPeriodicBroadcaster:
    """Test periodic broadcaster functionality."""
    
    @pytest.mark.asyncio
    async def test_start_periodic_broadcaster(self):
        """Test starting periodic broadcaster."""
        with patch('asyncio.create_task') as mock_create_task:
            start_periodic_broadcaster()
            mock_create_task.assert_called_once()
    
    def test_stop_periodic_broadcaster(self):
        """Test stopping periodic broadcaster."""
        # Create mock task
        mock_task = Mock()
        mock_task.cancel = Mock()
        
        with patch('src.api.websocket._broadcaster_task', mock_task):
            stop_periodic_broadcaster()
            mock_task.cancel.assert_called_once()
    
    def test_stop_periodic_broadcaster_no_task(self):
        """Test stopping broadcaster when no task exists."""
        with patch('src.api.websocket._broadcaster_task', None):
            # Should not raise exception
            stop_periodic_broadcaster()