"""Audit log model for the AI CRM system."""

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
import enum

from .base import BaseModel


class ActionType(enum.Enum):
    """Enumeration of audit action types."""
    
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    SYNC = "sync"
    APPROVE = "approve"
    REJECT = "reject"
    FUND = "fund"
    CANCEL = "cancel"
    ARCHIVE = "archive"
    RESTORE = "restore"
    ASSIGN = "assign"
    UNASSIGN = "unassign"
    SEND = "send"
    RECEIVE = "receive"
    SIGN = "sign"
    EXECUTE = "execute"
    TERMINATE = "terminate"
    OTHER = "other"


class EntityType(enum.Enum):
    """Enumeration of entity types for audit logging."""
    
    PLAINTIFF = "plaintiff"
    LAW_FIRM = "law_firm"
    LAWYER = "lawyer"
    CASE = "case"
    DOCUMENT = "document"
    COMMUNICATION = "communication"
    CONTRACT = "contract"
    USER = "user"
    SYSTEM = "system"
    AGENT = "agent"
    TASK = "task"
    REPORT = "report"
    SETTING = "setting"
    OTHER = "other"


class LogLevel(enum.Enum):
    """Enumeration of log levels."""
    
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLog(BaseModel):
    """
    Audit log model for comprehensive compliance and security tracking.
    
    Records all significant actions, data access, and system events
    for compliance, security monitoring, and forensic analysis.
    """
    
    __tablename__ = "audit_logs"
    
    # Action Information
    action_type = Column(
        SQLEnum(ActionType),
        nullable=False,
        index=True,
        comment="Type of action performed",
    )
    
    action_description = Column(
        String(255),
        nullable=False,
        comment="Brief description of the action",
    )
    
    log_level = Column(
        SQLEnum(LogLevel),
        nullable=False,
        default=LogLevel.INFO,
        index=True,
        comment="Severity level of the log entry",
    )
    
    # Actor Information
    user_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID of the user who performed the action",
    )
    
    user_email = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Email of the user who performed the action",
    )
    
    user_role = Column(
        String(50),
        nullable=True,
        comment="Role of the user who performed the action",
    )
    
    agent_id = Column(
        String(100),
        nullable=True,
        index=True,
        comment="ID of the agent that performed the action",
    )
    
    agent_type = Column(
        String(100),
        nullable=True,
        comment="Type of agent that performed the action",
    )
    
    # Target Information
    entity_type = Column(
        SQLEnum(EntityType),
        nullable=False,
        index=True,
        comment="Type of entity that was acted upon",
    )
    
    entity_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID of the entity that was acted upon",
    )
    
    entity_name = Column(
        String(255),
        nullable=True,
        comment="Name or identifier of the entity",
    )
    
    # Context Information
    session_id = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Session ID for grouping related actions",
    )
    
    request_id = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Request ID for tracing across systems",
    )
    
    correlation_id = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Correlation ID for related actions",
    )
    
    # Technical Details
    ip_address = Column(
        String(45),  # IPv6 compatible
        nullable=True,
        index=True,
        comment="IP address of the request origin",
    )
    
    user_agent = Column(
        Text,
        nullable=True,
        comment="User agent string from the request",
    )
    
    endpoint = Column(
        String(255),
        nullable=True,
        comment="API endpoint or URL accessed",
    )
    
    http_method = Column(
        String(10),
        nullable=True,
        comment="HTTP method used (GET, POST, etc.)",
    )
    
    http_status_code = Column(
        Integer,
        nullable=True,
        comment="HTTP status code returned",
    )
    
    # Data Changes
    old_values = Column(
        JSON,
        nullable=True,
        comment="JSON object containing previous values",
    )
    
    new_values = Column(
        JSON,
        nullable=True,
        comment="JSON object containing new values",
    )
    
    changed_fields = Column(
        JSON,
        nullable=True,
        comment="JSON array of fields that were changed",
    )
    
    # Request/Response Details
    request_payload = Column(
        JSON,
        nullable=True,
        comment="JSON object containing request payload (sanitized)",
    )
    
    response_payload = Column(
        JSON,
        nullable=True,
        comment="JSON object containing response payload (sanitized)",
    )
    
    # Performance Metrics
    execution_time_ms = Column(
        Integer,
        nullable=True,
        comment="Execution time in milliseconds",
    )
    
    database_queries = Column(
        Integer,
        nullable=True,
        comment="Number of database queries executed",
    )
    
    memory_usage_mb = Column(
        Integer,
        nullable=True,
        comment="Memory usage in megabytes",
    )
    
    # Error Information
    error_code = Column(
        String(50),
        nullable=True,
        comment="Error code if action failed",
    )
    
    error_message = Column(
        Text,
        nullable=True,
        comment="Error message if action failed",
    )
    
    stack_trace = Column(
        Text,
        nullable=True,
        comment="Stack trace if error occurred",
    )
    
    # Business Context
    case_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Associated case ID for business context",
    )
    
    plaintiff_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Associated plaintiff ID for business context",
    )
    
    law_firm_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Associated law firm ID for business context",
    )
    
    # Compliance and Security
    is_sensitive_data = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether action involved sensitive data",
    )
    
    compliance_tags = Column(
        JSON,
        nullable=True,
        comment="JSON array of compliance-related tags",
    )
    
    data_classification = Column(
        String(50),
        nullable=True,
        comment="Classification level of data accessed",
    )
    
    retention_date = Column(
        "retention_date",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Date when log entry should be deleted",
    )
    
    # System Information
    application_version = Column(
        String(20),
        nullable=True,
        comment="Version of the application",
    )
    
    environment = Column(
        String(20),
        nullable=True,
        comment="Environment where action occurred",
    )
    
    server_instance = Column(
        String(100),
        nullable=True,
        comment="Server instance identifier",
    )
    
    # Additional Metadata
    tags = Column(
        JSON,
        nullable=True,
        comment="JSON array of tags for categorization",
    )
    
    custom_fields = Column(
        JSON,
        nullable=True,
        comment="JSON object for custom field values",
    )
    
    notes = Column(
        Text,
        nullable=True,
        comment="Additional notes about the action",
    )
    
    def __repr__(self) -> str:
        """Return string representation of the audit log."""
        return (
            f"<AuditLog(id={self.id}, "
            f"action='{self.action_type.value}', "
            f"entity='{self.entity_type.value}', "
            f"user_email='{self.user_email}')>"
        )
    
    def is_error_log(self) -> bool:
        """Check if this is an error log entry."""
        return self.log_level in [LogLevel.ERROR, LogLevel.CRITICAL]
    
    def is_security_relevant(self) -> bool:
        """Check if this log entry is security-relevant."""
        security_actions = [
            ActionType.LOGIN,
            ActionType.LOGOUT,
            ActionType.DELETE,
            ActionType.EXPORT,
            ActionType.READ,
        ]
        return (
            self.action_type in security_actions or
            self.is_sensitive_data or
            self.error_code is not None
        )
    
    def is_data_access(self) -> bool:
        """Check if this represents data access."""
        return self.action_type in [
            ActionType.READ,
            ActionType.EXPORT,
            ActionType.UPDATE,
            ActionType.CREATE,
        ]
    
    def involves_pii(self) -> bool:
        """Check if this action involved personally identifiable information."""
        pii_entities = [
            EntityType.PLAINTIFF,
            EntityType.COMMUNICATION,
            EntityType.DOCUMENT,
        ]
        return (
            self.entity_type in pii_entities or
            self.is_sensitive_data or
            (self.data_classification and "confidential" in self.data_classification.lower())
        )
    
    def get_duration_seconds(self) -> float:
        """Get execution duration in seconds."""
        if self.execution_time_ms is None:
            return 0.0
        return self.execution_time_ms / 1000.0
    
    def was_successful(self) -> bool:
        """Check if the action was successful."""
        if self.http_status_code:
            return 200 <= self.http_status_code < 400
        return self.error_code is None
    
    def get_risk_score(self) -> float:
        """
        Calculate a risk score for this action.
        
        Returns:
            float: Risk score from 0.0 (low) to 1.0 (high).
        """
        score = 0.0
        
        # Base score for different action types
        high_risk_actions = [ActionType.DELETE, ActionType.EXPORT]
        medium_risk_actions = [ActionType.UPDATE, ActionType.SIGN, ActionType.EXECUTE]
        
        if self.action_type in high_risk_actions:
            score += 0.4
        elif self.action_type in medium_risk_actions:
            score += 0.2
        
        # Increase score for sensitive data
        if self.is_sensitive_data:
            score += 0.2
        
        # Increase score for errors
        if self.is_error_log():
            score += 0.3
        
        # Increase score for unusual access patterns
        if self.ip_address and self.user_id:
            # This would need to be calculated based on historical patterns
            pass
        
        # Increase score for high-privilege actions
        if self.user_role in ["admin", "system"]:
            score += 0.1
        
        return min(score, 1.0)
    
    @classmethod
    def create_user_action(
        cls,
        user_id: str,
        user_email: str,
        user_role: str,
        action_type: ActionType,
        entity_type: EntityType,
        entity_id: str = None,
        description: str = None,
        **kwargs
    ) -> "AuditLog":
        """
        Create an audit log entry for a user action.
        
        Args:
            user_id: ID of the user performing the action.
            user_email: Email of the user.
            user_role: Role of the user.
            action_type: Type of action being performed.
            entity_type: Type of entity being acted upon.
            entity_id: ID of the entity (optional).
            description: Description of the action (optional).
            **kwargs: Additional fields.
            
        Returns:
            AuditLog: The created audit log entry.
        """
        return cls(
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            action_description=description or f"{action_type.value} {entity_type.value}",
            **kwargs
        )
    
    @classmethod
    def create_system_action(
        cls,
        agent_id: str,
        agent_type: str,
        action_type: ActionType,
        entity_type: EntityType,
        entity_id: str = None,
        description: str = None,
        **kwargs
    ) -> "AuditLog":
        """
        Create an audit log entry for a system/agent action.
        
        Args:
            agent_id: ID of the agent performing the action.
            agent_type: Type of agent.
            action_type: Type of action being performed.
            entity_type: Type of entity being acted upon.
            entity_id: ID of the entity (optional).
            description: Description of the action (optional).
            **kwargs: Additional fields.
            
        Returns:
            AuditLog: The created audit log entry.
        """
        return cls(
            agent_id=agent_id,
            agent_type=agent_type,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            action_description=description or f"{agent_type} {action_type.value} {entity_type.value}",
            **kwargs
        )