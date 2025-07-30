"""Database connection utilities and dependency injection."""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from ..config.database import get_database_session, init_database


# Re-export for backward compatibility
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for FastAPI dependency injection.
    
    Yields:
        AsyncSession: Database session.
    """
    async for session in get_database_session():
        yield session


# Only initialize database if not in test environment
if not os.getenv("PYTEST_CURRENT_TEST"):
    try:
        init_database()
    except Exception:
        # Silently fail during tests or when dependencies are missing
        pass