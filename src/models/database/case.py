"""Case model for the AI CRM system."""

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


class CaseType(enum.Enum):
    """Enumeration of case types."""
    
    PERSONAL_INJURY = "personal_injury"
    MEDICAL_MALPRACTICE = "medical_malpractice"
    WORKERS_COMPENSATION = "workers_compensation"
    PRODUCT_LIABILITY = "product_liability"
    WRONGFUL_DEATH = "wrongful_death"
    AUTO_ACCIDENT = "auto_accident"
    SLIP_AND_FALL = "slip_and_fall"
    EMPLOYMENT = "employment"
    OTHER = "other"


class CaseStatus(enum.Enum):
    """Enumeration of case statuses."""
    
    INITIAL = "initial"
    QUALIFYING = "qualifying"
    QUALIFIED = "qualified"
    DOCUMENT_COLLECTION = "document_collection"
    UNDERWRITING = "underwriting"
    APPROVED = "approved"
    FUNDED = "funded"
    SETTLED = "settled"
    CLOSED = "closed"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"


class CasePriority(enum.Enum):
    """Enumeration of case priorities."""
    
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class FundingStatus(enum.Enum):
    """Enumeration of funding statuses."""
    
    NOT_REQUESTED = "not_requested"
    REQUESTED = "requested"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    FUNDED = "funded"
    REPAID = "repaid"
    WRITTEN_OFF = "written_off"


class Case(BaseModel, AuditMixin):
    """
    Case model representing legal cases for funding.
    
    Represents individual legal cases that plaintiffs are seeking
    pre-settlement funding for, with comprehensive tracking of
    case details, funding status, and progression.
    """
    
    __tablename__ = "cases"
    
    # Case Identification
    case_number = Column(
        String(50),
        nullable=True,
        unique=True,
        index=True,
        comment="Unique case number",
    )
    
    title = Column(
        String(200),
        nullable=False,
        comment="Case title or brief description",
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Detailed case description",
    )
    
    # Relationships
    plaintiff_id = Column(
        UUID(as_uuid=True),
        ForeignKey("plaintiffs.id"),
        nullable=False,
        index=True,
        comment="Associated plaintiff",
    )
    
    law_firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("law_firms.id"),
        nullable=False,
        index=True,
        comment="Associated law firm",
    )
    
    primary_lawyer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lawyers.id"),
        nullable=True,
        index=True,
        comment="Primary lawyer handling the case",
    )
    
    # Case Details
    case_type = Column(
        SQLEnum(CaseType),
        nullable=False,
        index=True,
        comment="Type of legal case",
    )
    
    case_status = Column(
        SQLEnum(CaseStatus),
        nullable=False,
        default=CaseStatus.INITIAL,
        index=True,
        comment="Current status of the case",
    )
    
    priority = Column(
        SQLEnum(CasePriority),
        nullable=False,
        default=CasePriority.NORMAL,
        index=True,
        comment="Case priority level",
    )
    
    # Incident Information
    incident_date = Column(
        "incident_date",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Date of the incident",
    )
    
    incident_location = Column(
        String(500),
        nullable=True,
        comment="Location where the incident occurred",
    )
    
    incident_description = Column(
        Text,
        nullable=True,
        comment="Detailed description of the incident",
    )
    
    # Legal Information
    court_name = Column(
        String(200),
        nullable=True,
        comment="Name of the court handling the case",
    )
    
    court_case_number = Column(
        String(100),
        nullable=True,
        comment="Court-assigned case number",
    )
    
    filing_date = Column(
        "filing_date",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Date the case was filed",
    )
    
    statute_of_limitations = Column(
        "statute_of_limitations",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Statute of limitations expiration date",
    )
    
    # Defendant Information
    defendants = Column(
        JSON,
        nullable=True,
        comment="JSON array of defendant information",
    )
    
    insurance_companies = Column(
        JSON,
        nullable=True,
        comment="JSON array of insurance companies involved",
    )
    
    # Financial Information
    estimated_case_value = Column(
        Integer,
        nullable=True,
        comment="Estimated case value in cents",
    )
    
    settlement_demand = Column(
        Integer,
        nullable=True,
        comment="Settlement demand amount in cents",
    )
    
    current_offer = Column(
        Integer,
        nullable=True,
        comment="Current settlement offer in cents",
    )
    
    medical_expenses = Column(
        Integer,
        nullable=True,
        comment="Total medical expenses in cents",
    )
    
    lost_wages = Column(
        Integer,
        nullable=True,
        comment="Lost wages amount in cents",
    )
    
    property_damage = Column(
        Integer,
        nullable=True,
        comment="Property damage amount in cents",
    )
    
    # Funding Information
    funding_status = Column(
        SQLEnum(FundingStatus),
        nullable=False,
        default=FundingStatus.NOT_REQUESTED,
        index=True,
        comment="Current funding status",
    )
    
    funding_amount_requested = Column(
        Integer,
        nullable=True,
        comment="Requested funding amount in cents",
    )
    
    funding_amount_approved = Column(
        Integer,
        nullable=True,
        comment="Approved funding amount in cents",
    )
    
    funding_amount_disbursed = Column(
        Integer,
        nullable=True,
        comment="Actually disbursed funding amount in cents",
    )
    
    funding_fee_rate = Column(
        Float,
        nullable=True,
        comment="Funding fee rate as decimal (e.g., 0.15 for 15%)",
    )
    
    repayment_amount = Column(
        Integer,
        nullable=True,
        comment="Total repayment amount in cents",
    )
    
    funding_date = Column(
        "funding_date",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Date funding was disbursed",
    )
    
    # Risk Assessment
    risk_score = Column(
        Float,
        nullable=True,
        comment="AI-calculated risk score (0.0 to 1.0)",
    )
    
    risk_factors = Column(
        JSON,
        nullable=True,
        comment="JSON array of identified risk factors",
    )
    
    underwriting_notes = Column(
        Text,
        nullable=True,
        comment="Underwriting notes and analysis",
    )
    
    # Progress Tracking
    discovery_complete = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether discovery phase is complete",
    )
    
    depositions_complete = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether depositions are complete",
    )
    
    expert_witnesses_secured = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether expert witnesses are secured",
    )
    
    trial_date = Column(
        "trial_date",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Scheduled trial date",
    )
    
    expected_resolution_date = Column(
        "expected_resolution_date",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Expected case resolution date",
    )
    
    # Settlement Information
    settlement_date = Column(
        "settlement_date",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Date of settlement",
    )
    
    settlement_amount = Column(
        Integer,
        nullable=True,
        comment="Final settlement amount in cents",
    )
    
    attorney_fees = Column(
        Integer,
        nullable=True,
        comment="Attorney fees in cents",
    )
    
    # Integration Fields
    pipedrive_deal_id = Column(
        Integer,
        nullable=True,
        unique=True,
        index=True,
        comment="Pipedrive deal ID for synchronization",
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
        comment="General notes about the case",
    )
    
    # Relationships
    plaintiff = relationship(
        "Plaintiff",
        back_populates="cases",
        lazy="select",
    )
    
    law_firm = relationship(
        "LawFirm",
        back_populates="cases",
        lazy="select",
    )
    
    primary_lawyer = relationship(
        "Lawyer",
        back_populates="cases",
        lazy="select",
    )
    
    documents = relationship(
        "Document",
        back_populates="case",
        lazy="select",
        cascade="all, delete-orphan",
    )
    
    communications = relationship(
        "Communication",
        back_populates="case",
        lazy="select",
        cascade="all, delete-orphan",
    )
    
    contracts = relationship(
        "Contract",
        back_populates="case",
        lazy="select",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        """Return string representation of the case."""
        return (
            f"<Case(id={self.id}, "
            f"case_number='{self.case_number}', "
            f"title='{self.title}', "
            f"status='{self.case_status.value}')>"
        )
    
    def is_active(self) -> bool:
        """Check if the case is currently active."""
        return self.case_status not in [
            CaseStatus.CLOSED,
            CaseStatus.REJECTED,
            CaseStatus.SETTLED,
        ]
    
    def is_funded(self) -> bool:
        """Check if the case has been funded."""
        return self.funding_status == FundingStatus.FUNDED
    
    def is_eligible_for_funding(self) -> bool:
        """Check if the case is eligible for funding consideration."""
        return (
            self.case_status in [
                CaseStatus.QUALIFIED,
                CaseStatus.DOCUMENT_COLLECTION,
                CaseStatus.UNDERWRITING,
            ] and
            self.funding_status in [
                FundingStatus.NOT_REQUESTED,
                FundingStatus.REQUESTED,
            ]
        )
    
    def calculate_funding_fee(self, amount: int) -> int:
        """
        Calculate the funding fee for a given amount.
        
        Args:
            amount: Funding amount in cents.
            
        Returns:
            int: Funding fee in cents.
        """
        if not self.funding_fee_rate:
            return 0
        return int(amount * self.funding_fee_rate)
    
    def calculate_total_repayment(self, funding_amount: int = None) -> int:
        """
        Calculate the total repayment amount.
        
        Args:
            funding_amount: Funding amount in cents (uses approved amount if not provided).
            
        Returns:
            int: Total repayment amount in cents.
        """
        amount = funding_amount or self.funding_amount_approved or 0
        fee = self.calculate_funding_fee(amount)
        return amount + fee
    
    def get_roi_percentage(self) -> float:
        """
        Calculate the return on investment percentage.
        
        Returns:
            float: ROI percentage.
        """
        if not self.funding_amount_disbursed or not self.repayment_amount:
            return 0.0
        
        profit = self.repayment_amount - self.funding_amount_disbursed
        return (profit / self.funding_amount_disbursed) * 100
    
    def days_since_filing(self) -> int:
        """
        Calculate days since the case was filed.
        
        Returns:
            int: Number of days since filing.
        """
        if not self.filing_date:
            return 0
        
        from datetime import datetime
        filing = datetime.strptime(self.filing_date, "%Y-%m-%d")
        return (datetime.now() - filing).days
    
    def is_high_value(self) -> bool:
        """Check if this is a high-value case."""
        return (
            self.estimated_case_value is not None and
            self.estimated_case_value >= 10000000  # $100,000+
        )
    
    def has_high_risk(self) -> bool:
        """Check if the case has a high risk score."""
        return self.risk_score is not None and self.risk_score > 0.7