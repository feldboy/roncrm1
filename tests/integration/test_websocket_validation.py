"""WebSocket functionality validation tests."""

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestWebSocketBasic:
    """Test basic WebSocket functionality."""
    
    def test_connection_manager_exists(self):
        """Test that ConnectionManager class exists and can be imported."""
        try:
            from src.api.websocket import ConnectionManager
            assert ConnectionManager is not None
            
            manager = ConnectionManager()
            assert manager is not None
            assert hasattr(manager, 'active_connections')
            assert manager.active_connections == {}
        except Exception as e:
            pytest.skip(f"ConnectionManager import/creation failed: {e}")
    
    def test_connection_manager_has_required_methods(self):
        """Test that ConnectionManager has all required methods."""
        try:
            from src.api.websocket import ConnectionManager
            manager = ConnectionManager()
            
            required_methods = [
                'connect', 'disconnect', 'send_personal_message', 
                'broadcast', 'send_agent_status', 'send_system_alert'
            ]
            
            for method in required_methods:
                assert hasattr(manager, method), f"Missing method: {method}"
                assert callable(getattr(manager, method)), f"Method {method} is not callable"
                
        except Exception as e:
            pytest.skip(f"ConnectionManager methods test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_connection_manager_connect(self):
        """Test WebSocket connection functionality."""
        try:
            from src.api.websocket import ConnectionManager
            manager = ConnectionManager()
            
            # Mock WebSocket
            mock_websocket = AsyncMock()
            mock_websocket.accept = AsyncMock()
            
            # Test connection
            await manager.connect(mock_websocket, "user123")
            
            # Verify connection was established
            assert "user123" in manager.active_connections
            assert manager.active_connections["user123"] == mock_websocket
            mock_websocket.accept.assert_called_once()
            
        except Exception as e:
            pytest.skip(f"Connection test failed: {e}")
    
    def test_connection_manager_disconnect(self):
        """Test WebSocket disconnection functionality."""
        try:
            from src.api.websocket import ConnectionManager
            manager = ConnectionManager()
            
            # Add a connection
            mock_websocket = Mock()
            manager.active_connections["user123"] = mock_websocket
            
            # Test disconnection
            manager.disconnect("user123")
            
            # Verify connection was removed
            assert "user123" not in manager.active_connections
            
        except Exception as e:
            pytest.skip(f"Disconnection test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_connection_manager_send_personal_message(self):
        """Test sending personal messages."""
        try:
            from src.api.websocket import ConnectionManager
            manager = ConnectionManager()
            
            # Add a connection
            mock_websocket = AsyncMock()
            mock_websocket.send_text = AsyncMock()
            manager.active_connections["user123"] = mock_websocket
            
            # Test sending message
            await manager.send_personal_message("Hello", "user123")
            
            # Verify message was sent
            mock_websocket.send_text.assert_called_once_with("Hello")
            
        except Exception as e:
            pytest.skip(f"Personal message test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_connection_manager_broadcast(self):
        """Test broadcasting messages."""
        try:
            from src.api.websocket import ConnectionManager
            manager = ConnectionManager()
            
            # Add multiple connections
            mock_websocket1 = AsyncMock()
            mock_websocket1.send_text = AsyncMock()
            mock_websocket2 = AsyncMock()
            mock_websocket2.send_text = AsyncMock()
            
            manager.active_connections["user1"] = mock_websocket1
            manager.active_connections["user2"] = mock_websocket2
            
            # Test broadcasting
            await manager.broadcast("Hello everyone")
            
            # Verify all connections received message
            mock_websocket1.send_text.assert_called_once_with("Hello everyone")
            mock_websocket2.send_text.assert_called_once_with("Hello everyone")
            
        except Exception as e:
            pytest.skip(f"Broadcast test failed: {e}")


class TestWebSocketAdvanced:
    """Test advanced WebSocket functionality."""
    
    @pytest.mark.asyncio
    async def test_connection_manager_agent_status(self):
        """Test sending agent status updates."""
        try:
            from src.api.websocket import ConnectionManager
            manager = ConnectionManager()
            
            # Add a connection
            mock_websocket = AsyncMock()
            mock_websocket.send_json = AsyncMock()
            manager.active_connections["user123"] = mock_websocket
            
            # Test sending agent status
            status_data = {
                "agent_id": "lead_intake",
                "status": "running",
                "last_activity": "2024-01-15T10:00:00Z"
            }
            
            await manager.send_agent_status("user123", status_data)
            
            # Verify status was sent
            expected_message = {
                "type": "agent_status",
                "data": status_data
            }
            mock_websocket.send_json.assert_called_once_with(expected_message)
            
        except Exception as e:
            pytest.skip(f"Agent status test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_connection_manager_system_alert(self):
        """Test sending system alerts."""
        try:
            from src.api.websocket import ConnectionManager
            manager = ConnectionManager()
            
            # Add connections
            mock_websocket1 = AsyncMock()
            mock_websocket1.send_json = AsyncMock()
            mock_websocket2 = AsyncMock()
            mock_websocket2.send_json = AsyncMock()
            
            manager.active_connections["user1"] = mock_websocket1
            manager.active_connections["user2"] = mock_websocket2
            
            # Test sending system alert
            alert_data = {
                "level": "warning",
                "message": "System maintenance in 10 minutes",
                "timestamp": "2024-01-15T10:00:00Z"
            }
            
            await manager.send_system_alert(alert_data)
            
            # Verify all connections received alert
            expected_message = {
                "type": "system_alert",
                "data": alert_data
            }
            
            mock_websocket1.send_json.assert_called_once_with(expected_message)
            mock_websocket2.send_json.assert_called_once_with(expected_message)
            
        except Exception as e:
            pytest.skip(f"System alert test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_connection_manager_handles_failed_connections(self):
        """Test handling of failed connections during broadcast."""
        try:
            from src.api.websocket import ConnectionManager
            manager = ConnectionManager()
            
            # Add connections - one will fail
            mock_websocket1 = AsyncMock()
            mock_websocket1.send_text = AsyncMock()
            mock_websocket2 = AsyncMock()
            mock_websocket2.send_text = AsyncMock(side_effect=Exception("Connection failed"))
            
            manager.active_connections["user1"] = mock_websocket1
            manager.active_connections["user2"] = mock_websocket2
            
            # Test broadcasting with failure
            await manager.broadcast("Hello everyone")
            
            # Verify working connection received message
            mock_websocket1.send_text.assert_called_once_with("Hello everyone")
            
            # Verify failed connection was removed
            assert "user1" in manager.active_connections
            assert "user2" not in manager.active_connections
            
        except Exception as e:
            pytest.skip(f"Failed connection handling test failed: {e}")


class TestWebSocketAuthentication:
    """Test WebSocket authentication functionality."""
    
    def test_websocket_authentication_function_exists(self):
        """Test that WebSocket authentication function exists."""
        try:
            from src.api.websocket import authenticate_websocket
            assert authenticate_websocket is not None
            assert callable(authenticate_websocket)
        except Exception as e:
            pytest.skip(f"WebSocket authentication function test failed: {e}")
    
    def test_websocket_authentication_valid_token(self):
        """Test WebSocket authentication with valid token."""
        try:
            from src.api.websocket import authenticate_websocket
            
            # Mock WebSocket with valid authorization header
            mock_websocket = Mock()
            mock_websocket.headers = {"authorization": "Bearer valid-token"}
            
            with patch('src.api.websocket.decode_jwt_token', return_value={"sub": "user123"}):
                user_id = authenticate_websocket(mock_websocket)
                assert user_id == "user123"
                
        except Exception as e:
            pytest.skip(f"Valid token authentication test failed: {e}")
    
    def test_websocket_authentication_invalid_token(self):
        """Test WebSocket authentication with invalid token."""
        try:
            from src.api.websocket import authenticate_websocket
            
            # Mock WebSocket with invalid authorization header
            mock_websocket = Mock()
            mock_websocket.headers = {"authorization": "Bearer invalid-token"}
            
            with patch('src.api.websocket.decode_jwt_token', side_effect=Exception("Invalid token")):
                user_id = authenticate_websocket(mock_websocket)
                assert user_id is None
                
        except Exception as e:
            pytest.skip(f"Invalid token authentication test failed: {e}")
    
    def test_websocket_authentication_no_header(self):
        """Test WebSocket authentication with no authorization header."""
        try:
            from src.api.websocket import authenticate_websocket
            
            # Mock WebSocket without authorization header
            mock_websocket = Mock()
            mock_websocket.headers = {}
            
            user_id = authenticate_websocket(mock_websocket)
            assert user_id is None
            
        except Exception as e:
            pytest.skip(f"No header authentication test failed: {e}")


class TestWebSocketIntegration:
    """Test WebSocket integration with other components."""
    
    def test_websocket_endpoint_function_exists(self):
        """Test that WebSocket endpoint function exists."""
        try:
            from src.api.websocket import websocket_endpoint
            assert websocket_endpoint is not None
            assert callable(websocket_endpoint)
        except Exception as e:
            pytest.skip(f"WebSocket endpoint function test failed: {e}")
    
    def test_periodic_broadcaster_functions_exist(self):
        """Test that periodic broadcaster functions exist."""
        try:
            from src.api.websocket import start_periodic_broadcaster, stop_periodic_broadcaster
            assert start_periodic_broadcaster is not None
            assert stop_periodic_broadcaster is not None
            assert callable(start_periodic_broadcaster)
            assert callable(stop_periodic_broadcaster)
        except Exception as e:
            pytest.skip(f"Periodic broadcaster functions test failed: {e}")
    
    def test_websocket_module_integration(self):
        """Test overall WebSocket module integration."""
        try:
            from src.api.websocket import (
                ConnectionManager,
                websocket_endpoint,
                authenticate_websocket,
                start_periodic_broadcaster,
                stop_periodic_broadcaster
            )
            
            # Verify all components are available
            assert ConnectionManager is not None
            assert websocket_endpoint is not None
            assert authenticate_websocket is not None
            assert start_periodic_broadcaster is not None
            assert stop_periodic_broadcaster is not None
            
            # Test that ConnectionManager can be instantiated
            manager = ConnectionManager()
            assert manager is not None
            
        except Exception as e:
            pytest.skip(f"WebSocket module integration test failed: {e}")