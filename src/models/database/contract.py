"""Contract model for the AI CRM system."""

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    Boolean,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel, AuditMixin


class ContractType(enum.Enum):
    """Enumeration of contract types."""
    
    FUNDING_AGREEMENT = "funding_agreement"
    PURCHASE_AGREEMENT = "purchase_agreement"
    ASSIGNMENT_AGREEMENT = "assignment_agreement"
    SETTLEMENT_AGREEMENT = "settlement_agreement"
    RETAINER_AGREEMENT = "retainer_agreement"
    NON_DISCLOSURE_AGREEMENT = "non_disclosure_agreement"
    SERVICE_AGREEMENT = "service_agreement"
    AMENDMENT = "amendment"
    ADDENDUM = "addendum"
    OTHER = "other"


class ContractStatus(enum.Enum):
    """Enumeration of contract statuses."""
    
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    PENDING_SIGNATURE = "pending_signature"
    PARTIALLY_SIGNED = "partially_signed"
    FULLY_EXECUTED = "fully_executed"
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    BREACHED = "breached"


class SignatureStatus(enum.Enum):
    """Enumeration of signature statuses."""
    
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    SIGNED = "signed"
    DECLINED = "declined"
    EXPIRED = "expired"


class Contract(BaseModel, AuditMixin):
    """
    Contract model representing legal agreements and funding contracts.
    
    Manages all types of contracts with comprehensive tracking of
    signatures, terms, payments, and lifecycle management.
    """
    
    __tablename__ = "contracts"
    
    # Contract Identification
    contract_number = Column(
        String(50),
        nullable=True,
        unique=True,
        index=True,
        comment="Unique contract number",
    )
    
    title = Column(
        String(255),
        nullable=False,
        comment="Contract title",
    )
    
    contract_type = Column(
        SQLEnum(ContractType),
        nullable=False,
        index=True,
        comment="Type of contract",
    )
    
    status = Column(
        SQLEnum(ContractStatus),
        nullable=False,
        default=ContractStatus.DRAFT,
        index=True,
        comment="Current status of the contract",
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
    
    parent_contract_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contracts.id"),
        nullable=True,
        index=True,
        comment="Parent contract for amendments/addendums",
    )
    
    # Contract Content
    content = Column(
        Text,
        nullable=True,
        comment="Full contract text content",
    )
    
    template_id = Column(
        String(100),
        nullable=True,
        comment="ID of the template used to generate this contract",
    )
    
    template_variables = Column(
        JSON,
        nullable=True,
        comment="JSON object containing template variables used",
    )
    
    key_terms = Column(
        JSON,
        nullable=True,
        comment="JSON object containing key contract terms",
    )
    
    # Financial Terms
    principal_amount = Column(
        Integer,
        nullable=True,
        comment="Principal amount in cents",
    )
    
    interest_rate = Column(
        Float,
        nullable=True,
        comment="Interest rate as decimal (e.g., 0.15 for 15%)",
    )
    
    fee_rate = Column(
        Float,
        nullable=True,
        comment="Fee rate as decimal (e.g., 0.05 for 5%)",
    )
    
    total_repayment_amount = Column(
        Integer,
        nullable=True,
        comment="Total repayment amount in cents",
    )
    
    payment_terms = Column(
        JSON,
        nullable=True,
        comment="JSON object containing payment terms",
    )
    
    # Important Dates
    effective_date = Column(
        "effective_date",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Date when contract becomes effective",
    )
    
    expiration_date = Column(
        "expiration_date",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Date when contract expires",
    )
    
    settlement_date = Column(
        "settlement_date",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Expected settlement date",
    )
    
    termination_date = Column(
        "termination_date",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Date when contract was terminated",
    )
    
    # Signature Management
    requires_signatures = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether contract requires signatures",
    )
    
    signature_deadline = Column(
        "signature_deadline",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Deadline for all signatures",
    )
    
    signatories = Column(
        JSON,
        nullable=True,
        comment="JSON array of required signatories",
    )
    
    signatures = Column(
        JSON,
        nullable=True,
        comment="JSON array of collected signatures",
    )
    
    electronic_signatures_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether electronic signatures are enabled",
    )
    
    signature_provider = Column(
        String(50),
        nullable=True,
        comment="Electronic signature provider (DocuSign, Adobe, etc.)",
    )
    
    signature_envelope_id = Column(
        String(100),
        nullable=True,
        comment="External signature provider envelope ID",
    )
    
    # Document Management
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=True,
        index=True,
        comment="Associated document file",
    )
    
    version = Column(
        String(20),
        nullable=False,
        default="1.0",
        comment="Contract version",
    )
    
    is_latest_version = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether this is the latest version",
    )
    
    pdf_url = Column(
        String(500),
        nullable=True,
        comment="URL to the PDF version of the contract",
    )
    
    # Review and Approval Workflow
    review_required = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether contract requires review before execution",
    )
    
    reviewed_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="ID of user who reviewed the contract",
    )
    
    reviewed_at = Column(
        "reviewed_at",
        String(19),  # YYYY-MM-DD HH:MM:SS format
        nullable=True,
        comment="When the contract was reviewed",
    )
    
    approved_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="ID of user who approved the contract",
    )
    
    approved_at = Column(
        "approved_at",
        String(19),  # YYYY-MM-DD HH:MM:SS format
        nullable=True,
        comment="When the contract was approved",
    )
    
    review_notes = Column(
        Text,
        nullable=True,
        comment="Notes from contract review",
    )
    
    # Performance and Compliance
    performance_milestones = Column(
        JSON,
        nullable=True,
        comment="JSON array of performance milestones",
    )
    
    compliance_requirements = Column(
        JSON,
        nullable=True,
        comment="JSON array of compliance requirements",
    )
    
    breach_notifications = Column(
        JSON,
        nullable=True,
        comment="JSON array of breach notifications",
    )
    
    amendments = Column(
        JSON,
        nullable=True,
        comment="JSON array of amendments made to the contract",
    )
    
    # Automation and AI
    auto_generated = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether contract was auto-generated",
    )
    
    ai_risk_score = Column(
        Float,
        nullable=True,
        comment="AI-calculated risk score for the contract",
    )
    
    ai_recommendations = Column(
        JSON,
        nullable=True,
        comment="JSON array of AI recommendations",
    )
    
    # Notifications and Reminders
    notification_settings = Column(
        JSON,
        nullable=True,
        comment="JSON object containing notification preferences",
    )
    
    reminder_dates = Column(
        JSON,
        nullable=True,
        comment="JSON array of important reminder dates",
    )
    
    # Legal and Compliance
    governing_law = Column(
        String(100),
        nullable=True,
        comment="Governing law jurisdiction",
    )
    
    dispute_resolution = Column(
        String(100),
        nullable=True,
        comment="Dispute resolution mechanism",
    )
    
    confidentiality_clause = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether contract contains confidentiality clause",
    )
    
    non_compete_clause = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether contract contains non-compete clause",
    )
    
    # Archival and Retention
    archived = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether the contract is archived",
    )
    
    retention_date = Column(
        "retention_date",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Date when contract should be deleted",
    )
    
    legal_hold = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether contract is under legal hold",
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
        comment="Internal notes about the contract",
    )
    
    # Relationships
    plaintiff = relationship(
        "Plaintiff",
        back_populates="contracts",
        lazy="select",
    )
    
    case = relationship(
        "Case",
        back_populates="contracts",
        lazy="select",
    )
    
    law_firm = relationship(
        "LawFirm",
        lazy="select",
    )
    
    document = relationship(
        "Document",
        lazy="select",
    )
    
    parent_contract = relationship(
        "Contract",
        remote_side="Contract.id",
        lazy="select",
    )
    
    child_contracts = relationship(
        "Contract",
        lazy="select",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        """Return string representation of the contract."""
        return (
            f"<Contract(id={self.id}, "
            f"contract_number='{self.contract_number}', "
            f"type='{self.contract_type.value}', "
            f"status='{self.status.value}')>"
        )
    
    def is_active(self) -> bool:
        """Check if the contract is currently active."""
        return self.status == ContractStatus.ACTIVE
    
    def is_fully_executed(self) -> bool:
        """Check if the contract is fully executed."""
        return self.status == ContractStatus.FULLY_EXECUTED
    
    def is_expired(self) -> bool:
        """Check if the contract has expired."""
        if not self.expiration_date:
            return False
        
        from datetime import datetime
        expiration = datetime.strptime(self.expiration_date, "%Y-%m-%d")
        return datetime.now().date() > expiration.date()
    
    def needs_signatures(self) -> bool:
        """Check if contract still needs signatures."""
        return (
            self.requires_signatures and
            self.status in [
                ContractStatus.PENDING_SIGNATURE,
                ContractStatus.PARTIALLY_SIGNED,
            ]
        )
    
    def is_signature_deadline_approaching(self, days: int = 7) -> bool:
        """
        Check if signature deadline is approaching.
        
        Args:
            days: Number of days to consider as "approaching".
            
        Returns:
            bool: True if deadline is within the specified days.
        """
        if not self.signature_deadline:
            return False
        
        from datetime import datetime, timedelta
        deadline = datetime.strptime(self.signature_deadline, "%Y-%m-%d")
        threshold = datetime.now() + timedelta(days=days)
        return deadline.date() <= threshold.date()
    
    def calculate_total_cost(self) -> int:
        """
        Calculate total cost including principal, interest, and fees.
        
        Returns:
            int: Total cost in cents.
        """
        if not self.principal_amount:
            return 0
        
        total = self.principal_amount
        
        if self.interest_rate:
            total += int(self.principal_amount * self.interest_rate)
        
        if self.fee_rate:
            total += int(self.principal_amount * self.fee_rate)
        
        return total
    
    def get_signature_progress(self) -> dict:
        """
        Get signature progress information.
        
        Returns:
            dict: Signature progress with counts and percentage.
        """
        if not self.signatories or not self.signatures:
            return {
                "required": 0,
                "completed": 0,
                "percentage": 0.0,
                "pending": [],
            }
        
        required_count = len(self.signatories)
        completed_count = len([s for s in self.signatures if s.get("status") == "signed"])
        
        pending_signatories = []
        signed_emails = {s.get("email") for s in self.signatures if s.get("status") == "signed"}
        
        for signatory in self.signatories:
            if signatory.get("email") not in signed_emails:
                pending_signatories.append(signatory)
        
        return {
            "required": required_count,
            "completed": completed_count,
            "percentage": (completed_count / required_count * 100) if required_count > 0 else 0,
            "pending": pending_signatories,
        }
    
    def days_until_expiration(self) -> int:
        """
        Calculate days until contract expiration.
        
        Returns:
            int: Days until expiration, negative if expired.
        """
        if not self.expiration_date:
            return 999999  # No expiration
        
        from datetime import datetime
        expiration = datetime.strptime(self.expiration_date, "%Y-%m-%d")
        return (expiration.date() - datetime.now().date()).days
    
    def should_send_reminder(self) -> bool:
        """Check if a reminder should be sent based on reminder dates."""
        if not self.reminder_dates:
            return False
        
        from datetime import datetime
        today = datetime.now().date()
        
        for reminder in self.reminder_dates:
            reminder_date = datetime.strptime(reminder["date"], "%Y-%m-%d").date()
            if reminder_date == today and not reminder.get("sent", False):
                return True
        
        return False