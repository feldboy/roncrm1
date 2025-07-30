"""SQLAlchemy ORM models for the AI CRM system."""

from .base import Base, TimestampMixin, UUIDMixin, BaseModel, AuditMixin
from .plaintiff import Plaintiff, CaseType, CaseStatus, ContactMethod
from .law_firm import LawFirm, FirmSize, FirmType
from .lawyer import Lawyer, LawyerRole, LawyerStatus
from .case import Case, CasePriority, FundingStatus
from .document import Document, DocumentType, DocumentStatus, DocumentSecurity
from .communication import Communication, CommunicationType, CommunicationDirection, CommunicationStatus, Priority
from .contract import Contract, ContractType, ContractStatus, SignatureStatus
from .audit_log import AuditLog, ActionType, EntityType, LogLevel
from .settings import Setting, SettingsCategory, UserSetting, AgentSetting, SettingAuditLog, SettingsProfile

__all__ = [
    # Base classes
    "Base",
    "BaseModel",
    "TimestampMixin",
    "UUIDMixin",
    "AuditMixin",
    
    # Main entities
    "Plaintiff",
    "LawFirm", 
    "Lawyer",
    "Case",
    "Document",
    "Communication",
    "Contract",
    "AuditLog",
    "Setting",
    "SettingsCategory", 
    "UserSetting",
    "AgentSetting",
    "SettingAuditLog",
    "SettingsProfile",
    
    # Enums
    "CaseType",
    "CaseStatus",
    "ContactMethod",
    "FirmSize",
    "FirmType",
    "LawyerRole",
    "LawyerStatus",
    "CasePriority",
    "FundingStatus",
    "DocumentType",
    "DocumentStatus",
    "DocumentSecurity",
    "CommunicationType",
    "CommunicationDirection",
    "CommunicationStatus",
    "Priority",
    "ContractType",
    "ContractStatus",
    "SignatureStatus",
    "ActionType",
    "EntityType",
    "LogLevel",
]