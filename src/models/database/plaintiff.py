"""Plaintiff model for the AI CRM system."""

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    Boolean,
    ForeignKey,
    Enum as SQLEnum,
    JSON,
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


class ContactMethod(enum.Enum):
    """Enumeration of preferred contact methods."""
    
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"
    MAIL = "mail"


class Plaintiff(BaseModel, AuditMixin):
    """
    Plaintiff model representing funding recipients.
    
    Central entity in the CRM system representing individuals
    seeking pre-settlement funding for their legal cases.
    """
    
    __tablename__ = "plaintiffs"
    
    # Personal Information
    first_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Plaintiff's first name",
    )
    
    last_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Plaintiff's last name",
    )
    
    middle_name = Column(
        String(50),
        nullable=True,
        comment="Plaintiff's middle name",
    )
    
    email = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Primary email address",
    )
    
    phone = Column(
        String(20),
        nullable=True,
        comment="Primary phone number",
    )
    
    secondary_phone = Column(
        String(20),
        nullable=True,
        comment="Secondary phone number",
    )
    
    date_of_birth = Column(
        "date_of_birth",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Date of birth in YYYY-MM-DD format",
    )
    
    social_security_number = Column(
        String(11),  # Encrypted
        nullable=True,
        comment="Encrypted social security number",
    )
    
    # Address Information
    address_line_1 = Column(
        String(255),
        nullable=True,
        comment="Primary address line",
    )
    
    address_line_2 = Column(
        String(255),
        nullable=True,
        comment="Secondary address line (apt, suite, etc.)",
    )
    
    city = Column(
        String(100),
        nullable=True,
        index=True,
        comment="City",
    )
    
    state = Column(
        String(2),
        nullable=True,
        index=True,
        comment="State abbreviation",
    )
    
    zip_code = Column(
        String(10),
        nullable=True,
        index=True,
        comment="ZIP/postal code",
    )
    
    country = Column(
        String(3),
        nullable=True,
        default="USA",
        comment="Country code",
    )
    
    # Case Information
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
    
    case_description = Column(
        Text,
        nullable=True,
        comment="Detailed description of the case",
    )
    
    incident_date = Column(
        "incident_date",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Date of the incident",
    )
    
    # Legal Representation
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
        comment="Primary lawyer handling the case",
    )
    
    # Financial Information
    employment_status = Column(
        String(50),
        nullable=True,
        comment="Current employment status",
    )
    
    monthly_income = Column(
        Float,
        nullable=True,
        comment="Monthly income in USD",
    )
    
    monthly_expenses = Column(
        Float,
        nullable=True,
        comment="Monthly expenses in USD",
    )
    
    bank_account_verified = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether bank account has been verified",
    )
    
    credit_score = Column(
        Integer,
        nullable=True,
        comment="Credit score (if available)",
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
        comment="Underwriting notes and comments",
    )
    
    # Communication Preferences
    preferred_contact_method = Column(
        SQLEnum(ContactMethod),
        nullable=False,
        default=ContactMethod.EMAIL,
        comment="Preferred method of contact",
    )
    
    communication_notes = Column(
        Text,
        nullable=True,
        comment="Special communication instructions",
    )
    
    opt_in_marketing = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether plaintiff opted in to marketing communications",
    )
    
    # Integration Fields
    pipedrive_person_id = Column(
        Integer,
        nullable=True,
        unique=True,
        index=True,
        comment="Pipedrive person ID for synchronization",
    )
    
    pipedrive_deal_id = Column(
        Integer,
        nullable=True,
        index=True,
        comment="Pipedrive deal ID for synchronization",
    )
    
    lead_source = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Source of the lead (website, referral, etc.)",
    )
    
    lead_source_details = Column(
        JSON,
        nullable=True,
        comment="Additional details about the lead source",
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
        comment="General notes about the plaintiff",
    )
    
    # Relationships
    law_firm = relationship(
        "LawFirm",
        back_populates="plaintiffs",
        lazy="select",
    )
    
    lawyer = relationship(
        "Lawyer",
        back_populates="plaintiffs",
        lazy="select",
    )
    
    cases = relationship(
        "Case",
        back_populates="plaintiff",
        lazy="select",
        cascade="all, delete-orphan",
    )
    
    documents = relationship(
        "Document",
        back_populates="plaintiff",
        lazy="select",
        cascade="all, delete-orphan",
    )
    
    communications = relationship(
        "Communication",
        back_populates="plaintiff",
        lazy="select",
        cascade="all, delete-orphan",
    )
    
    contracts = relationship(
        "Contract",
        back_populates="plaintiff",
        lazy="select",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        """Return string representation of the plaintiff."""
        return (
            f"<Plaintiff(id={self.id}, "
            f"name='{self.first_name} {self.last_name}', "
            f"email='{self.email}', "
            f"status='{self.case_status.value}')>"
        )
    
    @property
    def full_name(self) -> str:
        """Get the plaintiff's full name."""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)
    
    @property
    def full_address(self) -> str:
        """Get the plaintiff's full address."""
        if not self.address_line_1:
            return ""
        
        parts = [self.address_line_1]
        if self.address_line_2:
            parts.append(self.address_line_2)
        
        if self.city and self.state:
            parts.append(f"{self.city}, {self.state}")
        
        if self.zip_code:
            parts.append(self.zip_code)
        
        return ", ".join(parts)
    
    def is_qualified(self) -> bool:
        """Check if the plaintiff is qualified for funding."""
        return self.case_status in [
            CaseStatus.QUALIFIED,
            CaseStatus.DOCUMENT_COLLECTION,
            CaseStatus.UNDERWRITING,
            CaseStatus.APPROVED,
            CaseStatus.FUNDED,
        ]
    
    def has_high_risk(self) -> bool:
        """Check if the plaintiff has a high risk score."""
        return self.risk_score is not None and self.risk_score > 0.7