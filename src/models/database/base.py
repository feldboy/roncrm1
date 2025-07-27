"""Base model classes and mixins for SQLAlchemy ORM."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# Create the base class for all ORM models
Base = declarative_base()


class UUIDMixin:
    """Mixin to add UUID primary key to models."""
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True,
    )


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models."""
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
    )


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """
    Abstract base model with UUID primary key and timestamps.
    
    All business entity models should inherit from this class.
    """
    
    __abstract__ = True
    
    def __repr__(self) -> str:
        """Return string representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert model to dictionary.
        
        Returns:
            dict: Dictionary representation of the model.
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    @classmethod
    def get_table_name(cls) -> str:
        """
        Get the table name for this model.
        
        Returns:
            str: The table name.
        """
        return cls.__tablename__


class AuditMixin:
    """Mixin to add audit fields to models."""
    
    created_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID of the user who created this record",
    )
    
    updated_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID of the user who last updated this record",
    )
    
    version = Column(
        "version",
        String(50),
        nullable=True,
        comment="Version number for optimistic locking",
    )