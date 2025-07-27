"""Law firm model for the AI CRM system."""

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel, AuditMixin


class FirmSize(enum.Enum):
    """Enumeration of law firm sizes."""
    
    SOLO = "solo"
    SMALL = "small"  # 2-10 lawyers
    MEDIUM = "medium"  # 11-50 lawyers
    LARGE = "large"  # 51-200 lawyers
    NATIONAL = "national"  # 200+ lawyers


class FirmType(enum.Enum):
    """Enumeration of law firm types."""
    
    PERSONAL_INJURY = "personal_injury"
    MEDICAL_MALPRACTICE = "medical_malpractice"
    WORKERS_COMPENSATION = "workers_compensation"
    EMPLOYMENT = "employment"
    PRODUCT_LIABILITY = "product_liability"
    MASS_TORT = "mass_tort"
    GENERAL_PRACTICE = "general_practice"
    OTHER = "other"


class LawFirm(BaseModel, AuditMixin):
    """
    Law firm model representing legal practices.
    
    Represents law firms that refer clients for pre-settlement funding
    and manages bulk operations for firm-wide preferences and settings.
    """
    
    __tablename__ = "law_firms"
    
    # Basic Information
    name = Column(
        String(200),
        nullable=False,
        index=True,
        comment="Law firm name",
    )
    
    legal_name = Column(
        String(250),
        nullable=True,
        comment="Official legal name (if different from display name)",
    )
    
    website = Column(
        String(255),
        nullable=True,
        comment="Law firm website URL",
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Description of the law firm and practice areas",
    )
    
    # Contact Information
    contact_email = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Primary contact email",
    )
    
    contact_phone = Column(
        String(20),
        nullable=True,
        comment="Primary contact phone number",
    )
    
    fax = Column(
        String(20),
        nullable=True,
        comment="Fax number",
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
        comment="Secondary address line (suite, floor, etc.)",
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
    
    # Firm Details
    firm_size = Column(
        SQLEnum(FirmSize),
        nullable=True,
        index=True,
        comment="Size category of the law firm",
    )
    
    firm_type = Column(
        SQLEnum(FirmType),
        nullable=True,
        index=True,
        comment="Primary practice area of the law firm",
    )
    
    practice_areas = Column(
        JSON,
        nullable=True,
        comment="JSON array of practice areas",
    )
    
    founded_year = Column(
        Integer,
        nullable=True,
        comment="Year the firm was founded",
    )
    
    number_of_attorneys = Column(
        Integer,
        nullable=True,
        comment="Total number of attorneys at the firm",
    )
    
    bar_license_states = Column(
        JSON,
        nullable=True,
        comment="JSON array of states where firm is licensed",
    )
    
    # Business Information
    tax_id = Column(
        String(20),
        nullable=True,
        comment="Tax identification number (encrypted)",
    )
    
    state_bar_number = Column(
        String(50),
        nullable=True,
        comment="State bar registration number",
    )
    
    # Firm Preferences and Settings
    funding_preferences = Column(
        JSON,
        nullable=True,
        comment="JSON object containing funding preferences",
    )
    
    communication_preferences = Column(
        JSON,
        nullable=True,
        comment="JSON object containing communication preferences",
    )
    
    document_preferences = Column(
        JSON,
        nullable=True,
        comment="JSON object containing document handling preferences",
    )
    
    # Operational Settings
    bulk_operations_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether bulk operations are enabled for this firm",
    )
    
    auto_approval_limit = Column(
        Integer,
        nullable=True,
        comment="Automatic approval limit for funding requests",
    )
    
    requires_approval = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether all cases require firm approval",
    )
    
    # Performance Metrics
    total_cases_referred = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Total number of cases referred by this firm",
    )
    
    total_cases_funded = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Total number of cases funded from this firm",
    )
    
    average_case_value = Column(
        Integer,
        nullable=True,
        comment="Average case value in cents",
    )
    
    approval_rate = Column(
        "approval_rate",
        String(5),  # Percentage as string (e.g., "85.5")
        nullable=True,
        comment="Approval rate percentage",
    )
    
    # Status and Flags
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether the law firm is active",
    )
    
    is_preferred = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether this is a preferred law firm",
    )
    
    is_verified = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether the law firm has been verified",
    )
    
    credit_limit = Column(
        Integer,
        nullable=True,
        comment="Credit limit for the firm in cents",
    )
    
    # Integration Fields
    pipedrive_org_id = Column(
        Integer,
        nullable=True,
        unique=True,
        index=True,
        comment="Pipedrive organization ID for synchronization",
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
        comment="General notes about the law firm",
    )
    
    # Relationships
    lawyers = relationship(
        "Lawyer",
        back_populates="law_firm",
        lazy="select",
        cascade="all, delete-orphan",
    )
    
    plaintiffs = relationship(
        "Plaintiff",
        back_populates="law_firm",
        lazy="select",
    )
    
    cases = relationship(
        "Case",
        back_populates="law_firm",
        lazy="select",
    )
    
    communications = relationship(
        "Communication",
        back_populates="law_firm",
        lazy="select",
    )
    
    def __repr__(self) -> str:
        """Return string representation of the law firm."""
        return (
            f"<LawFirm(id={self.id}, "
            f"name='{self.name}', "
            f"active={self.is_active})>"
        )
    
    @property
    def full_address(self) -> str:
        """Get the law firm's full address."""
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
    
    def get_default_preferences(self) -> dict:
        """Get default preferences for the law firm."""
        return {
            "communication": {
                "preferred_method": "email",
                "business_hours": "9AM-5PM EST",
                "timezone": "EST",
                "cc_emails": [],
            },
            "funding": {
                "min_case_value": 5000,
                "max_funding_amount": 50000,
                "auto_approval": False,
                "required_documents": [
                    "case_summary",
                    "medical_records",
                    "police_report",
                ],
            },
            "documents": {
                "preferred_format": "pdf",
                "require_signatures": True,
                "retention_period": "7_years",
            },
        }
    
    def calculate_approval_rate(self) -> float:
        """Calculate the current approval rate."""
        if self.total_cases_referred == 0:
            return 0.0
        return (self.total_cases_funded / self.total_cases_referred) * 100
    
    def is_high_volume(self) -> bool:
        """Check if this is a high-volume law firm."""
        return self.total_cases_referred >= 100
    
    def has_credit_available(self, amount: int) -> bool:
        """
        Check if the firm has available credit for a funding amount.
        
        Args:
            amount: Funding amount in cents.
            
        Returns:
            bool: True if credit is available, False otherwise.
        """
        if self.credit_limit is None:
            return True  # No limit set
        return amount <= self.credit_limit