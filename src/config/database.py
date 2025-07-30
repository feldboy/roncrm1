"""Database configuration and connection management."""

from typing import AsyncGenerator, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool

from .settings import get_settings

# Create the base class for ORM models
Base = declarative_base()

# Global database session factory
async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_database_url() -> str:
    """
    Get the database URL from settings.
    
    Returns:
        str: The database URL.
    """
    settings = get_settings()
    return settings.database.url


def create_database_engine(url: Optional[str] = None):
    """
    Create the SQLAlchemy async engine.
    
    Args:
        url: Database URL, uses settings if not provided.
        
    Returns:
        AsyncEngine: The SQLAlchemy async engine.
    """
    settings = get_settings()
    database_url = url or settings.database.url
    
    # Configure engine based on environment
    engine_kwargs = {
        "echo": settings.database.echo,
        "pool_size": settings.database.pool_size,
        "max_overflow": settings.database.max_overflow,
        "pool_pre_ping": True,  # Validate connections before use
        "pool_recycle": 3600,   # Recycle connections every hour
    }
    
    # Handle SQLite for testing
    if database_url.startswith("sqlite"):
        engine_kwargs.update({
            "poolclass": StaticPool,
            "connect_args": {
                "check_same_thread": False,
            },
        })
        # Remove PostgreSQL-specific settings for SQLite
        del engine_kwargs["pool_size"]
        del engine_kwargs["max_overflow"]
        del engine_kwargs["pool_recycle"]
    
    return create_async_engine(database_url, **engine_kwargs)


def init_database(engine=None) -> None:
    """
    Initialize the database session factory.
    
    Args:
        engine: Database engine, creates new one if not provided.
    """
    global async_session_factory
    
    if engine is None:
        engine = create_database_engine()
    
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True,
        autocommit=False,
    )


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session for dependency injection.
    
    Yields:
        AsyncSession: The database session.
        
    Raises:
        RuntimeError: If database is not initialized.
    """
    if async_session_factory is None:
        raise RuntimeError(
            "Database not initialized. Call init_database() first."
        )
    
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_all_tables(engine=None) -> None:
    """
    Create all database tables.
    
    Args:
        engine: Database engine, creates new one if not provided.
    """
    if engine is None:
        engine = create_database_engine()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables(engine=None) -> None:
    """
    Drop all database tables.
    
    Args:
        engine: Database engine, creates new one if not provided.
    """
    if engine is None:
        engine = create_database_engine()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class DatabaseHealthCheck:
    """Database health check utilities."""
    
    def __init__(self, engine=None):
        """
        Initialize health check.
        
        Args:
            engine: Database engine, creates new one if not provided.
        """
        self.engine = engine or create_database_engine()
    
    async def check_connection(self) -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            bool: True if connection is healthy, False otherwise.
        """
        try:
            async with self.engine.connect() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    async def get_connection_info(self) -> dict:
        """
        Get database connection information.
        
        Returns:
            dict: Connection information.
        """
        try:
            async with self.engine.connect() as conn:
                result = await conn.execute("SELECT version()")
                version = result.scalar()
                
                return {
                    "healthy": True,
                    "version": version,
                    "pool_size": self.engine.pool.size(),
                    "checked_out": self.engine.pool.checkedout(),
                    "overflow": self.engine.pool.overflow(),
                }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
            }