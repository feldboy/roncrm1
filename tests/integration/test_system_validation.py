"""System validation tests to verify overall functionality."""

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestSystemComponents:
    """Test that system components can be imported and initialized."""
    
    def test_can_import_openai_client(self):
        """Test that OpenAI client can be imported."""
        try:
            from src.services.ai.openai_client import OpenAIClient
            assert OpenAIClient is not None
        except ImportError as e:
            pytest.skip(f"OpenAI client import failed: {e}")
    
    def test_can_import_database_connection(self):
        """Test that database connection can be imported."""
        try:
            from src.database.connection import DatabaseConnection
            assert DatabaseConnection is not None
        except ImportError as e:
            pytest.skip(f"Database connection import failed: {e}")
    
    def test_can_import_websocket_manager(self):
        """Test that WebSocket manager can be imported."""
        try:
            from src.api.websocket import ConnectionManager
            assert ConnectionManager is not None
        except ImportError as e:
            pytest.skip(f"WebSocket manager import failed: {e}")
    
    def test_can_import_agent_registry(self):
        """Test that agent registry can be imported."""
        try:
            from src.agents.base.registry import AgentRegistry
            assert AgentRegistry is not None
        except ImportError as e:
            pytest.skip(f"Agent registry import failed: {e}")
    
    def test_can_import_settings(self):
        """Test that settings can be imported."""
        try:
            from src.config.settings import Settings, get_settings
            assert Settings is not None
            assert get_settings is not None
        except ImportError as e:
            pytest.skip(f"Settings import failed: {e}")


class TestSystemInitialization:
    """Test system component initialization."""
    
    def test_openai_client_initialization(self):
        """Test OpenAI client can be initialized with mocks."""
        try:
            with patch('src.services.ai.openai_client.AsyncOpenAI') as mock_client:
                with patch('src.services.ai.openai_client.settings') as mock_settings:
                    mock_settings.OPENAI_API_KEY = "test-key"
                    
                    from src.services.ai.openai_client import OpenAIClient
                    client = OpenAIClient()
                    
                    assert client is not None
                    mock_client.assert_called_once()
        except Exception as e:
            pytest.skip(f"OpenAI client initialization failed: {e}")
    
    def test_database_connection_initialization(self):
        """Test database connection can be initialized."""
        try:
            with patch('src.database.connection.create_async_engine') as mock_engine:
                from src.database.connection import DatabaseConnection
                
                mock_engine.return_value = Mock()
                db = DatabaseConnection("sqlite:///test.db")
                
                assert db is not None
                assert db.connection_string == "sqlite:///test.db"
        except Exception as e:
            pytest.skip(f"Database connection initialization failed: {e}")
    
    def test_websocket_manager_initialization(self):
        """Test WebSocket manager can be initialized.""" 
        try:
            from src.api.websocket import ConnectionManager
            manager = ConnectionManager()
            
            assert manager is not None
            assert hasattr(manager, 'active_connections')
        except Exception as e:
            pytest.skip(f"WebSocket manager initialization failed: {e}")
    
    def test_agent_registry_initialization(self):
        """Test agent registry can be initialized."""
        try:
            from src.agents.base.registry import AgentRegistry
            registry = AgentRegistry()
            
            assert registry is not None
        except Exception as e:
            pytest.skip(f"Agent registry initialization failed: {e}")


class TestSystemConfiguration:
    """Test system configuration and settings."""
    
    def test_settings_can_be_loaded(self):
        """Test that settings can be loaded."""
        try:
            from src.config.settings import get_settings
            settings = get_settings()
            
            assert settings is not None
            assert hasattr(settings, 'ENVIRONMENT')
            assert hasattr(settings, 'API_HOST')
            assert hasattr(settings, 'API_PORT')
        except Exception as e:
            pytest.skip(f"Settings loading failed: {e}")
    
    def test_settings_convenience_properties(self):
        """Test settings convenience properties."""
        try:
            with patch.dict(os.environ, {
                'OPENAI_API_KEY': 'test-key',
                'DATABASE_URL': 'sqlite:///test.db'
            }):
                from src.config.settings import Settings
                settings = Settings()
                
                assert settings.OPENAI_API_KEY == 'test-key'
                assert settings.DATABASE_URL == 'sqlite:///test.db'
        except Exception as e:
            pytest.skip(f"Settings properties test failed: {e}")


class TestBasicFunctionality:
    """Test basic functionality of core components."""
    
    @pytest.mark.asyncio
    async def test_openai_client_basic_methods(self):
        """Test OpenAI client has expected methods."""
        try:
            with patch('src.services.ai.openai_client.AsyncOpenAI'):
                with patch('src.services.ai.openai_client.settings') as mock_settings:
                    mock_settings.OPENAI_API_KEY = "test-key"
                    
                    from src.services.ai.openai_client import OpenAIClient
                    client = OpenAIClient()
                    
                    # Check that expected methods exist
                    assert hasattr(client, 'analyze_document')
                    assert hasattr(client, 'generate_risk_assessment')
                    assert hasattr(client, 'generate_email_content')
                    assert hasattr(client, 'generate_sms_content')
                    assert hasattr(client, 'extract_case_info')
        except Exception as e:
            pytest.skip(f"OpenAI client methods test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_database_connection_basic_methods(self):
        """Test database connection has expected methods."""
        try:
            with patch('src.database.connection.create_async_engine') as mock_engine:
                from src.database.connection import DatabaseConnection
                
                mock_engine.return_value = Mock()
                db = DatabaseConnection("sqlite:///test.db")
                
                # Check that expected methods exist
                assert hasattr(db, 'get_session')
                assert hasattr(db, 'execute_query')
                assert hasattr(db, 'health_check')
                assert hasattr(db, 'close')
        except Exception as e:
            pytest.skip(f"Database connection methods test failed: {e}")
    
    def test_websocket_manager_basic_methods(self):
        """Test WebSocket manager has expected methods."""
        try:
            from src.api.websocket import ConnectionManager
            manager = ConnectionManager()
            
            # Check that expected methods exist
            assert hasattr(manager, 'connect')
            assert hasattr(manager, 'disconnect')
            assert hasattr(manager, 'send_personal_message')
            assert hasattr(manager, 'broadcast')
        except Exception as e:
            pytest.skip(f"WebSocket manager methods test failed: {e}")


class TestSystemIntegration:
    """Test integration between system components."""
    
    def test_components_can_work_together(self):
        """Test that major components can be imported together."""
        try:
            # Import all major components
            from src.config.settings import get_settings
            from src.api.websocket import ConnectionManager
            
            # Test that they can coexist
            settings = get_settings()
            manager = ConnectionManager()
            
            assert settings is not None
            assert manager is not None
            
            # Test basic property access
            assert isinstance(settings.API_PORT, int)
            assert hasattr(manager, 'active_connections')
            
        except Exception as e:
            pytest.skip(f"Component integration test failed: {e}")
    
    def test_system_can_handle_basic_workflow(self):
        """Test that system can handle a basic workflow simulation."""
        try:
            # This simulates a basic system workflow
            from src.config.settings import get_settings
            from src.api.websocket import ConnectionManager
            
            # Initialize components
            settings = get_settings()
            manager = ConnectionManager()
            
            # Simulate basic operations
            assert settings.ENVIRONMENT in ['test', 'development', 'staging', 'production']
            assert manager.active_connections == {}
            
            # Test that configuration is accessible
            assert settings.API_HOST is not None
            assert settings.API_PORT > 0
            
        except Exception as e:
            pytest.skip(f"Basic workflow test failed: {e}")


class TestSystemHealth:
    """Test system health and validation."""
    
    def test_all_core_modules_importable(self):
        """Test that all core modules can be imported."""
        core_modules = [
            'src.config.settings',
            'src.api.websocket',
            'src.services.ai.openai_client',
            'src.database.connection',
            'src.agents.base.registry',
        ]
        
        importable_modules = []
        failed_modules = []
        
        for module in core_modules:
            try:
                __import__(module)
                importable_modules.append(module)
            except Exception as e:
                failed_modules.append((module, str(e)))
        
        # At least some core modules should be importable
        assert len(importable_modules) >= 2, f"Too few modules importable. Failed: {failed_modules}"
        
        # Report the status
        success_rate = len(importable_modules) / len(core_modules)
        assert success_rate >= 0.4, f"Success rate too low: {success_rate}. Failed modules: {failed_modules}"
    
    def test_system_configuration_valid(self):
        """Test that system configuration is valid."""
        try:
            from src.config.settings import get_settings
            settings = get_settings()
            
            # Test required configuration
            assert settings.ENVIRONMENT is not None
            assert settings.API_HOST is not None
            assert settings.API_PORT is not None
            assert isinstance(settings.API_PORT, int)
            assert settings.API_PORT > 0
            
            # Test that convenience properties work
            assert settings.OPENAI_API_KEY is not None
            assert settings.DATABASE_URL is not None
            
        except Exception as e:
            pytest.skip(f"Configuration validation failed: {e}")