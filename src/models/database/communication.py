"""Communication model for the AI CRM system."""

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel, AuditMixin


class CommunicationType(enum.Enum):
    """Enumeration of communication types."""
    
    EMAIL = "email"
    SMS = "sms"
    PHONE_CALL = "phone_call"
    VIDEO_CALL = "video_call"
    IN_PERSON_MEETING = "in_person_meeting"
    LETTER = "letter"
    FAX = "fax"
    CHAT = "chat"
    NOTIFICATION = "notification"
    SYSTEM_MESSAGE = "system_message"


class CommunicationDirection(enum.Enum):
    """Enumeration of communication directions."""
    
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    INTERNAL = "internal"


class CommunicationStatus(enum.Enum):
    """Enumeration of communication statuses."""
    
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    REPLIED = "replied"
    FAILED = "failed"
    BOUNCED = "bounced"
    CANCELLED = "cancelled"


class Priority(enum.Enum):
    """Enumeration of communication priorities."""
    
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Communication(BaseModel, AuditMixin):
    """
    Communication model representing all interactions and messages.
    
    Manages multi-channel communication including email, SMS, calls,
    and other interactions with comprehensive tracking and audit capabilities.
    """
    
    __tablename__ = "communications"
    
    # Communication Identification
    subject = Column(
        String(255),
        nullable=True,
        comment="Subject line for emails or call summary",
    )
    
    communication_type = Column(
        SQLEnum(CommunicationType),
        nullable=False,
        index=True,
        comment="Type of communication",
    )
    
    direction = Column(
        SQLEnum(CommunicationDirection),
        nullable=False,
        index=True,
        comment="Direction of communication",
    )
    
    status = Column(
        SQLEnum(CommunicationStatus),
        nullable=False,
        default=CommunicationStatus.DRAFT,
        index=True,
        comment="Current status of the communication",
    )
    
    priority = Column(
        SQLEnum(Priority),
        nullable=False,
        default=Priority.NORMAL,
        index=True,
        comment="Priority level of the communication",
    )
    
    # Relationships
    plaintiff_id = Column(
        UUID(as_uuid=True),
        ForeignKey("plaintiffs.id"),
        nullable=True,
        index=True,
        comment="Associated plaintiff",
    )
    
    case_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cases.id"),
        nullable=True,
        index=True,
        comment="Associated case",
    )
    
    law_firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("law_firms.id"),
        nullable=True,
        index=True,
        comment="Associated law firm",
    )
    
    lawyer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lawyers.id"),
        nullable=True,
        index=True,
        comment="Associated lawyer",
    )
    
    # Sender and Recipient Information
    sender_name = Column(
        String(200),
        nullable=True,
        comment="Name of the sender",
    )
    
    sender_email = Column(
        String(255),
        nullable=True,
        comment="Email address of the sender",
    )
    
    sender_phone = Column(
        String(20),
        nullable=True,
        comment="Phone number of the sender",
    )
    
    recipient_name = Column(
        String(200),
        nullable=True,
        comment="Name of the recipient",
    )
    
    recipient_email = Column(
        String(255),
        nullable=True,
        comment="Email address of the recipient",
    )
    
    recipient_phone = Column(
        String(20),
        nullable=True,
        comment="Phone number of the recipient",
    )
    
    cc_recipients = Column(
        JSON,
        nullable=True,
        comment="JSON array of CC recipients",
    )
    
    bcc_recipients = Column(
        JSON,
        nullable=True,
        comment="JSON array of BCC recipients",
    )
    
    # Content
    content = Column(
        Text,
        nullable=True,
        comment="Main content of the communication",
    )
    
    html_content = Column(
        Text,
        nullable=True,
        comment="HTML version of the content (for emails)",
    )
    
    template_id = Column(
        String(100),
        nullable=True,
        comment="ID of the template used",
    )
    
    template_variables = Column(
        JSON,
        nullable=True,
        comment="JSON object containing template variables",
    )
    
    # Attachments and References
    attachments = Column(
        JSON,
        nullable=True,
        comment="JSON array of attachment information",
    )
    
    external_references = Column(
        JSON,
        nullable=True,
        comment="JSON object containing external system references",
    )
    
    # Timing Information
    scheduled_at = Column(
        "scheduled_at",
        String(19),  # YYYY-MM-DD HH:MM:SS format
        nullable=True,
        comment="When the communication is scheduled to be sent",
    )
    
    sent_at = Column(
        "sent_at",
        String(19),  # YYYY-MM-DD HH:MM:SS format
        nullable=True,
        comment="When the communication was sent",
    )
    
    delivered_at = Column(
        "delivered_at",
        String(19),  # YYYY-MM-DD HH:MM:SS format
        nullable=True,
        comment="When the communication was delivered",
    )
    
    read_at = Column(
        "read_at",
        String(19),  # YYYY-MM-DD HH:MM:SS format
        nullable=True,
        comment="When the communication was read",
    )
    
    replied_at = Column(
        "replied_at",
        String(19),  # YYYY-MM-DD HH:MM:SS format
        nullable=True,
        comment="When a reply was received",
    )
    
    # Call-Specific Information
    call_duration_seconds = Column(
        Integer,
        nullable=True,
        comment="Duration of phone/video call in seconds",
    )
    
    call_recording_url = Column(
        String(500),
        nullable=True,
        comment="URL to call recording",
    )
    
    call_transcript = Column(
        Text,
        nullable=True,
        comment="Transcript of the call",
    )
    
    call_quality_score = Column(
        "call_quality_score",
        String(5),  # Score as string (e.g., "4.5")
        nullable=True,
        comment="Quality score for the call",
    )
    
    # SMS-Specific Information
    sms_segments = Column(
        Integer,
        nullable=True,
        comment="Number of SMS segments",
    )
    
    sms_cost = Column(
        Integer,
        nullable=True,
        comment="Cost of SMS in cents",
    )
    
    # Email-Specific Information
    email_message_id = Column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
        comment="Unique email message ID",
    )
    
    email_thread_id = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Email thread ID for grouping",
    )
    
    email_bounce_reason = Column(
        String(255),
        nullable=True,
        comment="Reason if email bounced",
    )
    
    email_open_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of times email was opened",
    )
    
    email_click_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of times links were clicked",
    )
    
    # AI and Automation
    is_automated = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this communication was automated",
    )
    
    automation_trigger = Column(
        String(100),
        nullable=True,
        comment="What triggered the automated communication",
    )
    
    ai_generated = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether content was AI-generated",
    )
    
    ai_confidence_score = Column(
        "ai_confidence_score",
        String(5),  # Confidence as string (e.g., "0.95")
        nullable=True,
        comment="AI confidence score for generated content",
    )
    
    sentiment_score = Column(
        "sentiment_score",
        String(6),  # Sentiment as string (e.g., "0.75" or "-0.25")
        nullable=True,
        comment="AI-analyzed sentiment score (-1.0 to 1.0)",
    )
    
    # Error Handling
    error_message = Column(
        Text,
        nullable=True,
        comment="Error message if communication failed",
    )
    
    retry_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of retry attempts",
    )
    
    max_retries = Column(
        Integer,
        nullable=False,
        default=3,
        comment="Maximum number of retry attempts",
    )
    
    # Follow-up and Response Management
    requires_response = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this communication requires a response",
    )
    
    response_deadline = Column(
        "response_deadline",
        String(19),  # YYYY-MM-DD HH:MM:SS format
        nullable=True,
        comment="Deadline for response",
    )
    
    parent_communication_id = Column(
        UUID(as_uuid=True),
        ForeignKey("communications.id"),
        nullable=True,
        index=True,
        comment="Parent communication for replies/follow-ups",
    )
    
    follow_up_required = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether a follow-up is required",
    )
    
    follow_up_date = Column(
        "follow_up_date",
        String(19),  # YYYY-MM-DD HH:MM:SS format
        nullable=True,
        comment="When to follow up",
    )
    
    # Compliance and Archival
    archived = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether the communication is archived",
    )
    
    compliance_reviewed = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether communication has been compliance reviewed",
    )
    
    retention_date = Column(
        "retention_date",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Date when communication should be deleted",
    )
    
    # Metadata
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
        comment="Internal notes about the communication",
    )
    
    # Relationships
    plaintiff = relationship(
        "Plaintiff",
        back_populates="communications",
        lazy="select",
    )
    
    case = relationship(
        "Case",
        back_populates="communications",
        lazy="select",
    )
    
    law_firm = relationship(
        "LawFirm",
        back_populates="communications",
        lazy="select",
    )
    
    lawyer = relationship(
        "Lawyer",
        back_populates="communications",
        lazy="select",
    )
    
    parent_communication = relationship(
        "Communication",
        remote_side="Communication.id",
        lazy="select",
    )
    
    replies = relationship(
        "Communication",
        lazy="select",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        """Return string representation of the communication."""
        return (
            f"<Communication(id={self.id}, "
            f"type='{self.communication_type.value}', "
            f"direction='{self.direction.value}', "
            f"status='{self.status.value}')>"
        )
    
    def is_sent(self) -> bool:
        """Check if the communication has been sent."""
        return self.status in [
            CommunicationStatus.SENT,
            CommunicationStatus.DELIVERED,
            CommunicationStatus.READ,
            CommunicationStatus.REPLIED,
        ]
    
    def is_delivered(self) -> bool:
        """Check if the communication has been delivered."""
        return self.status in [
            CommunicationStatus.DELIVERED,
            CommunicationStatus.READ,
            CommunicationStatus.REPLIED,
        ]
    
    def needs_follow_up(self) -> bool:
        """Check if communication needs follow-up."""
        if not self.follow_up_required or not self.follow_up_date:
            return False
        
        from datetime import datetime
        follow_up = datetime.strptime(self.follow_up_date, "%Y-%m-%d %H:%M:%S")
        return datetime.now() >= follow_up
    
    def is_overdue_response(self) -> bool:
        """Check if response is overdue."""
        if not self.requires_response or not self.response_deadline:
            return False
        
        if self.status == CommunicationStatus.REPLIED:
            return False
        
        from datetime import datetime
        deadline = datetime.strptime(self.response_deadline, "%Y-%m-%d %H:%M:%S")
        return datetime.now() > deadline
    
    def can_retry(self) -> bool:
        """Check if communication can be retried."""
        return (
            self.status == CommunicationStatus.FAILED and
            self.retry_count < self.max_retries
        )
    
    def get_engagement_score(self) -> float:
        """
        Calculate engagement score for email communications.
        
        Returns:
            float: Engagement score (0.0 to 1.0).
        """
        if self.communication_type != CommunicationType.EMAIL:
            return 0.0
        
        score = 0.0
        
        # Base score for delivery
        if self.is_delivered():
            score += 0.3
        
        # Score for opens
        if self.email_open_count > 0:
            score += 0.4
        
        # Score for clicks
        if self.email_click_count > 0:
            score += 0.3
        
        return min(score, 1.0)
    
    def get_response_time_hours(self) -> float:
        """
        Calculate response time in hours.
        
        Returns:
            float: Response time in hours, 0 if no response.
        """
        if not self.sent_at or not self.replied_at:
            return 0.0
        
        from datetime import datetime
        sent = datetime.strptime(self.sent_at, "%Y-%m-%d %H:%M:%S")
        replied = datetime.strptime(self.replied_at, "%Y-%m-%d %H:%M:%S")
        return (replied - sent).total_seconds() / 3600
    
    def has_positive_sentiment(self) -> bool:
        """Check if communication has positive sentiment."""
        if not self.sentiment_score:
            return False
        return float(self.sentiment_score) > 0.1