"""Tests for database connection module."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import (
    DatabaseConnection,
    get_db,
    get_database_connection,
    create_database_connection
)


class TestDatabaseConnection:
    """Test database connection functionality."""
    
    @pytest.fixture
    def mock_engine(self):
        """Create mock database engine."""
        engine = AsyncMock()
        engine.dispose = AsyncMock()
        return engine
    
    @pytest.fixture
    def db_connection(self, mock_engine):
        """Create database connection for testing."""
        with patch('src.database.connection.create_async_engine', return_value=mock_engine):
            return DatabaseConnection("sqlite+aiosqlite:///test.db")
    
    @pytest.mark.asyncio
    async def test_get_session(self, db_connection, mock_engine):
        """Test getting database session."""
        mock_session = AsyncMock(spec=AsyncSession)
        
        with patch('src.database.connection.async_sessionmaker') as mock_sessionmaker:
            mock_sessionmaker.return_value = Mock(return_value=mock_session)
            
            async with db_connection.get_session() as session:
                assert session == mock_session
    
    @pytest.mark.asyncio
    async def test_execute_query_success(self, db_connection):
        """Test successful query execution."""
        mock_result = Mock()
        mock_result.fetchall.return_value = [{"id": 1, "name": "test"}]
        
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        
        with patch.object(db_connection, 'get_session') as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            result = await db_connection.execute_query("SELECT * FROM users")
            
            assert result == [{"id": 1, "name": "test"}]
            mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_query_with_params(self, db_connection):
        """Test query execution with parameters."""
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        
        with patch.object(db_connection, 'get_session') as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            await db_connection.execute_query(
                "SELECT * FROM users WHERE id = :id",
                {"id": 1}
            )
            
            mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_query_error_handling(self, db_connection):
        """Test query execution error handling."""
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("Database error")
        
        with patch.object(db_connection, 'get_session') as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            with pytest.raises(Exception, match="Database error"):
                await db_connection.execute_query("SELECT * FROM users")
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, db_connection):
        """Test successful database health check."""
        mock_result = Mock()
        mock_result.scalar.return_value = 1
        
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        
        with patch.object(db_connection, 'get_session') as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            is_healthy = await db_connection.health_check()
            
            assert is_healthy is True
            mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, db_connection):
        """Test database health check failure."""
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("Connection failed")
        
        with patch.object(db_connection, 'get_session') as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            is_healthy = await db_connection.health_check()
            
            assert is_healthy is False
    
    @pytest.mark.asyncio
    async def test_close_connection(self, db_connection, mock_engine):
        """Test closing database connection."""
        await db_connection.close()
        mock_engine.dispose.assert_called_once()
    
    def test_connection_string_property(self, db_connection):
        """Test connection string property."""
        assert db_connection.connection_string == "sqlite+aiosqlite:///test.db"
    
    def test_is_connected_property(self, db_connection, mock_engine):
        """Test is_connected property."""
        # Engine exists, so should be connected
        assert db_connection.is_connected is True
        
        # Set engine to None
        db_connection.engine = None
        assert db_connection.is_connected is False


class TestDatabaseDependency:
    """Test database dependency injection."""
    
    @pytest.mark.asyncio
    async def test_get_db_dependency(self):
        """Test get_db dependency function."""
        mock_session = AsyncMock()
        mock_connection = Mock()
        mock_connection.get_session.return_value.__aenter__.return_value = mock_session
        
        with patch('src.database.connection.get_database_connection', return_value=mock_connection):
            async for session in get_db():
                assert session == mock_session
                break
    
    def test_get_database_connection_singleton(self):
        """Test database connection singleton behavior."""
        with patch('src.database.connection.create_database_connection') as mock_create:
            mock_connection = Mock()
            mock_create.return_value = mock_connection
            
            # First call should create connection
            conn1 = get_database_connection()
            mock_create.assert_called_once()
            
            # Second call should return same connection
            conn2 = get_database_connection()
            assert conn1 == conn2
            assert mock_create.call_count == 1
    
    def test_create_database_connection(self):
        """Test database connection creation."""
        with patch('src.database.connection.DatabaseConnection') as mock_db_class:
            with patch('src.database.connection.get_settings') as mock_settings:
                mock_settings.return_value.DATABASE_URL = "postgresql://test"
                mock_connection = Mock()
                mock_db_class.return_value = mock_connection
                
                conn = create_database_connection()
                
                mock_db_class.assert_called_once_with("postgresql://test")
                assert conn == mock_connection


class TestDatabaseTransactions:
    """Test database transaction handling."""
    
    @pytest.mark.asyncio
    async def test_transaction_commit(self, mock_engine):
        """Test successful transaction commit."""
        with patch('src.database.connection.create_async_engine', return_value=mock_engine):
            db_connection = DatabaseConnection("sqlite+aiosqlite:///test.db")
            
            mock_session = AsyncMock()
            mock_session.commit = AsyncMock()
            mock_session.rollback = AsyncMock()
            
            with patch.object(db_connection, 'get_session') as mock_get_session:
                mock_get_session.return_value.__aenter__.return_value = mock_session
                
                async with db_connection.get_session() as session:
                    # Simulate successful operation
                    await session.commit()
                
                mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self, mock_engine):
        """Test transaction rollback on error."""
        with patch('src.database.connection.create_async_engine', return_value=mock_engine):
            db_connection = DatabaseConnection("sqlite+aiosqlite:///test.db")
            
            mock_session = AsyncMock()
            mock_session.commit = AsyncMock()
            mock_session.rollback = AsyncMock()
            
            with patch.object(db_connection, 'get_session') as mock_get_session:
                mock_get_session.return_value.__aenter__.return_value = mock_session
                mock_get_session.return_value.__aexit__ = AsyncMock(return_value=False)
                
                try:
                    async with db_connection.get_session() as session:
                        raise Exception("Test error")
                except Exception:
                    pass
                
                # Rollback should be called by context manager
                mock_session.rollback.assert_called_once()