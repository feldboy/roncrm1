"""SQLAlchemy ORM models for the AI CRM system."""

from .base import Base, TimestampMixin, UUIDMixin
from .plaintiff import Plaintiff
from .law_firm import LawFirm
from .lawyer import Lawyer
from .case import Case
from .document import Document
from .communication import Communication
from .contract import Contract
from .audit_log import AuditLog

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    "Plaintiff",
    "LawFirm",
    "Lawyer",
    "Case",
    "Document",
    "Communication",
    "Contract",
    "AuditLog",
]