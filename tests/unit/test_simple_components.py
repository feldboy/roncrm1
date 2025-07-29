"""Simple tests for core components without complex dependencies."""

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestOpenAIClientSimple:
    """Simple tests for OpenAI client."""
    
    def test_openai_client_initialization(self):
        """Test OpenAI client can be initialized."""
        with patch('src.services.ai.openai_client.AsyncOpenAI') as mock_client:
            with patch('src.services.ai.openai_client.settings') as mock_settings:
                mock_settings.OPENAI_API_KEY = "test-key"
                
                from src.services.ai.openai_client import OpenAIClient
                
                client = OpenAIClient()
                assert client is not None
                mock_client.assert_called_once()
    
    def test_openai_error_class(self):
        """Test OpenAI error class exists."""
        from src.services.ai.openai_client import OpenAIError
        
        error = OpenAIError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)


class TestDatabaseConnectionSimple:
    """Simple tests for database connection."""
    
    def test_database_connection_initialization(self):
        """Test database connection can be initialized."""
        with patch('src.database.connection.create_async_engine') as mock_engine:
            from src.database.connection import DatabaseConnection
            
            mock_engine.return_value = Mock()
            
            db = DatabaseConnection("sqlite:///test.db")
            assert db.connection_string == "sqlite:///test.db"
            mock_engine.assert_called_once()
    
    def test_database_connection_properties(self):
        """Test database connection properties."""
        with patch('src.database.connection.create_async_engine') as mock_engine:
            from src.database.connection import DatabaseConnection
            
            mock_engine_instance = Mock()
            mock_engine.return_value = mock_engine_instance
            
            db = DatabaseConnection("sqlite:///test.db")
            
            # Test connection string
            assert db.connection_string == "sqlite:///test.db"
            
            # Test is_connected when engine exists
            assert db.is_connected is True
            
            # Test is_connected when engine is None
            db.engine = None
            assert db.is_connected is False


class TestWebSocketConnectionManager:
    """Simple tests for WebSocket connection manager."""
    
    def test_connection_manager_initialization(self):
        """Test connection manager initialization."""
        from src.api.websocket import ConnectionManager
        
        manager = ConnectionManager()
        assert manager.active_connections == {}
    
    def test_connection_manager_disconnect(self):
        """Test disconnecting user."""
        from src.api.websocket import ConnectionManager
        
        manager = ConnectionManager()
        mock_websocket = Mock()
        
        # Add connection
        manager.active_connections["user123"] = mock_websocket
        
        # Disconnect
        manager.disconnect("user123")
        
        # Should be removed
        assert "user123" not in manager.active_connections


class TestSettings:
    """Simple tests for settings configuration."""
    
    def test_settings_convenience_properties(self):
        """Test settings convenience properties."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-openai-key',
            'DATABASE_URL': 'sqlite:///test.db',
            'SECRET_KEY': 'test-secret'
        }):
            from src.config.settings import Settings
            
            settings = Settings()
            
            # Test OpenAI properties
            assert settings.OPENAI_API_KEY == 'test-openai-key'
            
            # Test database properties
            assert settings.DATABASE_URL == 'sqlite:///test.db'
            
            # Test server properties
            assert isinstance(settings.API_HOST, str)
            assert isinstance(settings.API_PORT, int)
    
    def test_settings_validation(self):
        """Test settings validation."""
        from src.config.settings import Settings
        
        # Test with valid environment
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'test',
            'LOG_LEVEL': 'INFO'
        }):
            settings = Settings()
            assert settings.environment == 'test'
            assert settings.log_level == 'INFO'


class TestAgentRegistry:
    """Simple tests for agent registry."""
    
    def test_agent_registry_initialization(self):
        """Test agent registry initialization."""
        from src.agents.base.registry import AgentRegistry
        
        registry = AgentRegistry()
        assert registry.agents == {}
    
    def test_agent_registry_register_agent(self):
        """Test registering an agent."""
        from src.agents.base.registry import AgentRegistry
        from src.agents.base.agent import BaseAgent
        
        class MockAgent(BaseAgent):
            def __init__(self):
                super().__init__("test_agent", "Test Agent", "A test agent")
            
            async def start(self):
                pass
            
            async def stop(self):
                pass
            
            async def process_message(self, message_type, data):
                return {"processed": True}
        
        registry = AgentRegistry()
        agent = MockAgent()
        
        registry.register_agent(agent)
        
        assert "test_agent" in registry.agents
        assert registry.agents["test_agent"] == agent
    
    def test_agent_registry_get_all_agents(self):
        """Test getting all agents."""
        from src.agents.base.registry import AgentRegistry
        
        registry = AgentRegistry()
        agents = registry.get_all_agents()
        
        assert isinstance(agents, list)
        assert len(agents) == 0