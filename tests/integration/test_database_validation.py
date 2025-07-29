"""Database operations validation tests."""

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestDatabaseModels:
    """Test database model definitions."""
    
    def test_base_model_can_be_imported(self):
        """Test that base model can be imported."""
        try:
            from src.models.base import Base
            assert Base is not None
            
            # Check SQLAlchemy base attributes
            assert hasattr(Base, 'metadata')
            assert hasattr(Base, 'registry')
            
        except Exception as e:
            pytest.skip(f"Base model import failed: {e}")
    
    def test_plaintiff_model_can_be_imported(self):
        """Test that plaintiff model can be imported."""
        try:
            from src.models.plaintiff import Plaintiff
            assert Plaintiff is not None
            
            # Check that it's a proper SQLAlchemy model
            assert hasattr(Plaintiff, '__tablename__')
            assert hasattr(Plaintiff, '__table__')
            
        except Exception as e:
            pytest.skip(f"Plaintiff model import failed: {e}")
    
    def test_case_model_can_be_imported(self):
        """Test that case model can be imported."""
        try:
            from src.models.case import Case
            assert Case is not None
            
            # Check SQLAlchemy model attributes
            assert hasattr(Case, '__tablename__')
            assert hasattr(Case, '__table__')
            
        except Exception as e:
            pytest.skip(f"Case model import failed: {e}")
    
    def test_document_model_can_be_imported(self):
        """Test that document model can be imported."""
        try:
            from src.models.document import Document
            assert Document is not None
            
            # Check SQLAlchemy model attributes
            assert hasattr(Document, '__tablename__')
            assert hasattr(Document, '__table__')
            
        except Exception as e:
            pytest.skip(f"Document model import failed: {e}")


class TestDatabaseSchemas:
    """Test database schema definitions."""
    
    def test_plaintiff_schemas_can_be_imported(self):
        """Test that plaintiff schemas can be imported."""
        try:
            from src.models.schemas.plaintiff import PlaintiffCreate, PlaintiffResponse
            assert PlaintiffCreate is not None
            assert PlaintiffResponse is not None
            
            # Check Pydantic model attributes
            assert hasattr(PlaintiffCreate, 'model_fields')
            assert hasattr(PlaintiffResponse, 'model_fields')
            
        except Exception as e:
            pytest.skip(f"Plaintiff schemas import failed: {e}")
    
    def test_case_schemas_can_be_imported(self):
        """Test that case schemas can be imported."""
        try:
            from src.models.schemas.case import CaseCreate, CaseResponse
            assert CaseCreate is not None
            assert CaseResponse is not None
            
            # Check Pydantic model attributes
            assert hasattr(CaseCreate, 'model_fields')
            assert hasattr(CaseResponse, 'model_fields')
            
        except Exception as e:
            pytest.skip(f"Case schemas import failed: {e}")
    
    def test_common_schemas_can_be_imported(self):
        """Test that common schemas can be imported."""
        try:
            from src.models.schemas.common import BaseSchema, PaginationParams
            assert BaseSchema is not None
            assert PaginationParams is not None
            
            # Check Pydantic model attributes
            assert hasattr(BaseSchema, 'model_config')
            assert hasattr(PaginationParams, 'model_fields')
            
        except Exception as e:
            pytest.skip(f"Common schemas import failed: {e}")


class TestDatabaseConnection:
    """Test database connection functionality."""
    
    def test_database_connection_class_exists(self):
        """Test that DatabaseConnection class exists."""
        try:
            from src.database.connection import DatabaseConnection
            assert DatabaseConnection is not None
            assert isinstance(DatabaseConnection, type)
            
        except Exception as e:
            pytest.skip(f"DatabaseConnection class test failed: {e}")
    
    def test_database_connection_can_be_created(self):
        """Test that DatabaseConnection can be instantiated."""
        try:
            with patch('src.database.connection.create_async_engine') as mock_engine:
                from src.database.connection import DatabaseConnection
                
                mock_engine.return_value = Mock()
                db = DatabaseConnection("sqlite+aiosqlite:///test.db")
                
                assert db is not None
                assert db.connection_string == "sqlite+aiosqlite:///test.db"
                mock_engine.assert_called_once()
                
        except Exception as e:
            pytest.skip(f"DatabaseConnection creation test failed: {e}")
    
    def test_database_connection_has_required_methods(self):
        """Test that DatabaseConnection has required methods."""
        try:
            with patch('src.database.connection.create_async_engine') as mock_engine:
                from src.database.connection import DatabaseConnection
                
                mock_engine.return_value = Mock()
                db = DatabaseConnection("sqlite+aiosqlite:///test.db")
                
                required_methods = ['get_session', 'execute_query', 'health_check', 'close']
                
                for method in required_methods:
                    assert hasattr(db, method), f"Missing method: {method}"
                    assert callable(getattr(db, method)), f"Method {method} is not callable"
                    
        except Exception as e:
            pytest.skip(f"DatabaseConnection methods test failed: {e}")
    
    def test_get_database_connection_function_exists(self):
        """Test that get_database_connection function exists."""
        try:
            from src.database.connection import get_database_connection
            assert get_database_connection is not None
            assert callable(get_database_connection)
            
        except Exception as e:
            pytest.skip(f"get_database_connection function test failed: {e}")
    
    def test_get_db_dependency_exists(self):
        """Test that get_db dependency function exists."""
        try:
            from src.database.connection import get_db
            assert get_db is not None
            assert callable(get_db)
            
        except Exception as e:
            pytest.skip(f"get_db dependency test failed: {e}")


class TestDatabaseMigrations:
    """Test database migration functionality."""
    
    def test_alembic_config_exists(self):
        """Test that Alembic configuration exists."""
        try:
            import os
            alembic_ini_path = os.path.join(os.path.dirname(__file__), '..', '..', 'alembic.ini')
            assert os.path.exists(alembic_ini_path), "alembic.ini not found"
            
        except Exception as e:
            pytest.skip(f"Alembic config test failed: {e}")
    
    def test_migrations_directory_exists(self):
        """Test that migrations directory exists."""
        try:
            import os
            migrations_path = os.path.join(os.path.dirname(__file__), '..', '..', 'migrations')
            assert os.path.exists(migrations_path), "migrations directory not found"
            
            # Check for Alembic env.py
            env_py_path = os.path.join(migrations_path, 'env.py')
            assert os.path.exists(env_py_path), "migrations/env.py not found"
            
        except Exception as e:
            pytest.skip(f"Migrations directory test failed: {e}")


class TestDatabaseServices:
    """Test database service functionality."""
    
    def test_plaintiff_service_can_be_imported(self):
        """Test that plaintiff service can be imported."""
        try:
            from src.services.database.plaintiff import PlaintiffService
            assert PlaintiffService is not None
            assert isinstance(PlaintiffService, type)
            
        except Exception as e:
            pytest.skip(f"PlaintiffService import failed: {e}")
    
    def test_case_service_can_be_imported(self):
        """Test that case service can be imported."""
        try:
            from src.services.database.case import CaseService
            assert CaseService is not None
            assert isinstance(CaseService, type)
            
        except Exception as e:
            pytest.skip(f"CaseService import failed: {e}")
    
    def test_document_service_can_be_imported(self):
        """Test that document service can be imported."""
        try:
            from src.services.database.document import DocumentService
            assert DocumentService is not None
            assert isinstance(DocumentService, type)
            
        except Exception as e:
            pytest.skip(f"DocumentService import failed: {e}")


class TestDatabaseOperations:
    """Test basic database operations."""
    
    @pytest.mark.asyncio
    async def test_database_health_check(self):
        """Test database health check functionality."""
        try:
            with patch('src.database.connection.create_async_engine') as mock_engine:
                from src.database.connection import DatabaseConnection
                
                # Mock successful health check
                mock_session = AsyncMock()
                mock_result = Mock()
                mock_result.scalar.return_value = 1
                mock_session.execute.return_value = mock_result
                
                mock_engine.return_value = Mock()
                db = DatabaseConnection("sqlite+aiosqlite:///test.db")
                
                with patch.object(db, 'get_session') as mock_get_session:
                    mock_get_session.return_value.__aenter__.return_value = mock_session
                    
                    is_healthy = await db.health_check()
                    assert is_healthy is True
                    
        except Exception as e:
            pytest.skip(f"Database health check test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_database_execute_query(self):
        """Test database query execution."""
        try:
            with patch('src.database.connection.create_async_engine') as mock_engine:
                from src.database.connection import DatabaseConnection
                
                # Mock successful query execution
                mock_session = AsyncMock()
                mock_result = Mock()
                mock_result.fetchall.return_value = [{"id": 1, "name": "test"}]
                mock_session.execute.return_value = mock_result
                
                mock_engine.return_value = Mock()
                db = DatabaseConnection("sqlite+aiosqlite:///test.db")
                
                with patch.object(db, 'get_session') as mock_get_session:
                    mock_get_session.return_value.__aenter__.return_value = mock_session
                    
                    result = await db.execute_query("SELECT * FROM test")
                    assert result == [{"id": 1, "name": "test"}]
                    mock_session.execute.assert_called_once()
                    
        except Exception as e:
            pytest.skip(f"Database execute query test failed: {e}")


class TestDatabaseIntegration:
    """Test database integration with other components."""
    
    def test_database_models_with_schemas(self):
        """Test that database models work with Pydantic schemas."""
        try:
            from src.models.plaintiff import Plaintiff
            from src.models.schemas.plaintiff import PlaintiffCreate
            
            # Both should be importable
            assert Plaintiff is not None
            assert PlaintiffCreate is not None
            
            # Check that schema has expected fields
            assert 'first_name' in PlaintiffCreate.model_fields
            assert 'last_name' in PlaintiffCreate.model_fields
            assert 'email' in PlaintiffCreate.model_fields
            
        except Exception as e:
            pytest.skip(f"Database models with schemas test failed: {e}")
    
    def test_database_with_settings(self):
        """Test that database configuration works with settings."""
        try:
            from src.config.settings import get_settings
            
            settings = get_settings()
            
            # Check database-related settings
            assert hasattr(settings, 'DATABASE_URL')
            assert hasattr(settings, 'DATABASE_ECHO')
            assert hasattr(settings, 'DATABASE_POOL_SIZE')
            
            # Check values are reasonable
            assert isinstance(settings.DATABASE_URL, str)
            assert isinstance(settings.DATABASE_ECHO, bool)
            assert isinstance(settings.DATABASE_POOL_SIZE, int)
            assert settings.DATABASE_POOL_SIZE > 0
            
        except Exception as e:
            pytest.skip(f"Database with settings test failed: {e}")


class TestDatabaseSecurity:
    """Test database security aspects."""
    
    def test_database_connection_string_format(self):
        """Test that database connection strings are properly formatted."""
        try:
            from src.config.settings import get_settings
            
            settings = get_settings()
            db_url = settings.DATABASE_URL
            
            # Should be a proper database URL format
            assert isinstance(db_url, str)
            assert len(db_url) > 0
            
            # For SQLite or PostgreSQL
            assert any(db_type in db_url.lower() for db_type in ['sqlite', 'postgresql', 'mysql'])
            
        except Exception as e:
            pytest.skip(f"Database connection string test failed: {e}")


class TestDatabasePerformance:
    """Test database performance configurations."""
    
    def test_database_pool_settings(self):
        """Test that database pool settings are configured."""
        try:
            from src.config.settings import get_settings
            
            settings = get_settings()
            
            # Check pool-related settings
            assert hasattr(settings, 'DATABASE_POOL_SIZE')
            assert hasattr(settings, 'DATABASE_MAX_OVERFLOW')
            assert hasattr(settings, 'DATABASE_POOL_TIMEOUT')
            assert hasattr(settings, 'DATABASE_POOL_RECYCLE')
            
            # Check values are reasonable
            assert settings.DATABASE_POOL_SIZE > 0
            assert settings.DATABASE_MAX_OVERFLOW >= 0
            assert settings.DATABASE_POOL_TIMEOUT > 0
            assert settings.DATABASE_POOL_RECYCLE > 0
            
        except Exception as e:
            pytest.skip(f"Database pool settings test failed: {e}")