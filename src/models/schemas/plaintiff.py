"""Pydantic schemas for Plaintiff entity."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field, EmailStr, validator

from ..database.plaintiff import CaseType, CaseStatus, ContactMethod
from .common import (
    BaseSchema,
    UUIDMixin,
    TimestampMixin,
    Address,
    ContactInfo,
    FinancialInfo,
    RiskAssessment,
    PaginationResponse,
)


class PlaintiffBase(BaseSchema):
    """Base schema for Plaintiff with common fields."""
    
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Plaintiff's first name",
    )
    
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Plaintiff's last name",
    )
    
    middle_name: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Plaintiff's middle name",
    )
    
    email: EmailStr = Field(
        ...,
        description="Primary email address",
    )
    
    phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Primary phone number",
    )
    
    secondary_phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Secondary phone number",
    )
    
    date_of_birth: Optional[str] = Field(
        default=None,
        regex="^\\d{4}-\\d{2}-\\d{2}$",
        description="Date of birth in YYYY-MM-DD format",
    )
    
    # Address information
    address_line_1: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Primary address line",
    )
    
    address_line_2: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Secondary address line",
    )
    
    city: Optional[str] = Field(
        default=None,
        max_length=100,
        description="City",
    )
    
    state: Optional[str] = Field(
        default=None,
        max_length=2,
        regex="^[A-Z]{2}$",
        description="State abbreviation",
    )
    
    zip_code: Optional[str] = Field(
        default=None,
        max_length=10,
        regex="^[0-9]{5}(-[0-9]{4})?$",
        description="ZIP code",
    )
    
    country: Optional[str] = Field(
        default="USA",
        max_length=3,
        description="Country code",
    )
    
    # Case information
    case_type: CaseType = Field(
        ...,
        description="Type of legal case",
    )
    
    case_status: Optional[CaseStatus] = Field(
        default=CaseStatus.INITIAL,
        description="Current status of the case",
    )
    
    case_description: Optional[str] = Field(
        default=None,
        description="Detailed description of the case",
    )
    
    incident_date: Optional[str] = Field(
        default=None,
        regex="^\\d{4}-\\d{2}-\\d{2}$",
        description="Date of the incident in YYYY-MM-DD format",
    )
    
    # Legal representation
    law_firm_id: Optional[UUID] = Field(
        default=None,
        description="Associated law firm ID",
    )
    
    lawyer_id: Optional[UUID] = Field(
        default=None,
        description="Primary lawyer ID",
    )
    
    # Financial information
    employment_status: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Current employment status",
    )
    
    monthly_income: Optional[float] = Field(
        default=None,
        ge=0,
        description="Monthly income in USD",
    )
    
    monthly_expenses: Optional[float] = Field(
        default=None,
        ge=0,
        description="Monthly expenses in USD",
    )
    
    credit_score: Optional[int] = Field(
        default=None,
        ge=300,
        le=850,
        description="Credit score",
    )
    
    bank_account_verified: Optional[bool] = Field(
        default=False,
        description="Whether bank account is verified",
    )
    
    # Communication preferences
    preferred_contact_method: Optional[ContactMethod] = Field(
        default=ContactMethod.EMAIL,
        description="Preferred contact method",
    )
    
    communication_notes: Optional[str] = Field(
        default=None,
        description="Special communication instructions",
    )
    
    opt_in_marketing: Optional[bool] = Field(
        default=False,
        description="Marketing opt-in status",
    )
    
    # Lead source
    lead_source: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Source of the lead",
    )
    
    notes: Optional[str] = Field(
        default=None,
        description="General notes",
    )
    
    @validator("email")
    def validate_email(cls, v):
        """Validate email format."""
        if v:
            v = v.lower().strip()
        return v
    
    @validator("phone", "secondary_phone")
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v:
            # Remove non-digit characters for validation
            digits_only = "".join(filter(str.isdigit, v))
            if len(digits_only) < 10:
                raise ValueError("Phone number must have at least 10 digits")
        return v


class PlaintiffCreate(PlaintiffBase):
    """Schema for creating a new plaintiff."""
    
    # Override to make case_type required for creation
    case_type: CaseType = Field(
        ...,
        description="Type of legal case (required for creation)",
    )
    
    # SSN only for creation (encrypted storage)
    social_security_number: Optional[str] = Field(
        default=None,
        regex="^\\d{3}-\\d{2}-\\d{4}$",
        description="Social Security Number in XXX-XX-XXXX format",
    )


class PlaintiffUpdate(BaseSchema):
    """Schema for updating an existing plaintiff."""
    
    first_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Plaintiff's first name",
    )
    
    last_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Plaintiff's last name",
    )
    
    middle_name: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Plaintiff's middle name",
    )
    
    email: Optional[EmailStr] = Field(
        default=None,
        description="Primary email address",
    )
    
    phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Primary phone number",
    )
    
    secondary_phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Secondary phone number",
    )
    
    date_of_birth: Optional[str] = Field(
        default=None,
        regex="^\\d{4}-\\d{2}-\\d{2}$",
        description="Date of birth in YYYY-MM-DD format",
    )
    
    # Address fields
    address_line_1: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Primary address line",
    )
    
    address_line_2: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Secondary address line",
    )
    
    city: Optional[str] = Field(
        default=None,
        max_length=100,
        description="City",
    )
    
    state: Optional[str] = Field(
        default=None,
        max_length=2,
        regex="^[A-Z]{2}$",
        description="State abbreviation",
    )
    
    zip_code: Optional[str] = Field(
        default=None,
        max_length=10,
        regex="^[0-9]{5}(-[0-9]{4})?$",
        description="ZIP code",
    )
    
    case_type: Optional[CaseType] = Field(
        default=None,
        description="Type of legal case",
    )
    
    case_status: Optional[CaseStatus] = Field(
        default=None,
        description="Current status of the case",
    )
    
    case_description: Optional[str] = Field(
        default=None,
        description="Detailed description of the case",
    )
    
    incident_date: Optional[str] = Field(
        default=None,
        regex="^\\d{4}-\\d{2}-\\d{2}$",
        description="Date of the incident",
    )
    
    law_firm_id: Optional[UUID] = Field(
        default=None,
        description="Associated law firm ID",
    )
    
    lawyer_id: Optional[UUID] = Field(
        default=None,
        description="Primary lawyer ID",
    )
    
    employment_status: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Current employment status",
    )
    
    monthly_income: Optional[float] = Field(
        default=None,
        ge=0,
        description="Monthly income in USD",
    )
    
    monthly_expenses: Optional[float] = Field(
        default=None,
        ge=0,
        description="Monthly expenses in USD",
    )
    
    credit_score: Optional[int] = Field(
        default=None,
        ge=300,
        le=850,
        description="Credit score",
    )
    
    bank_account_verified: Optional[bool] = Field(
        default=None,
        description="Whether bank account is verified",
    )
    
    preferred_contact_method: Optional[ContactMethod] = Field(
        default=None,
        description="Preferred contact method",
    )
    
    communication_notes: Optional[str] = Field(
        default=None,
        description="Special communication instructions",
    )
    
    opt_in_marketing: Optional[bool] = Field(
        default=None,
        description="Marketing opt-in status",
    )
    
    notes: Optional[str] = Field(
        default=None,
        description="General notes",
    )


class PlaintiffResponse(PlaintiffBase, UUIDMixin, TimestampMixin):
    """Schema for plaintiff responses."""
    
    # Computed fields
    full_name: Optional[str] = Field(
        default=None,
        description="Full name of the plaintiff",
    )
    
    full_address: Optional[str] = Field(
        default=None,
        description="Full formatted address",
    )
    
    # Risk assessment
    risk_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="AI-calculated risk score",
    )
    
    risk_factors: Optional[List[str]] = Field(
        default=None,
        description="Identified risk factors",
    )
    
    # Integration fields
    pipedrive_person_id: Optional[int] = Field(
        default=None,
        description="Pipedrive person ID",
    )
    
    pipedrive_deal_id: Optional[int] = Field(
        default=None,
        description="Pipedrive deal ID",
    )
    
    # Relationship data (optional nested objects)
    law_firm: Optional["LawFirmResponse"] = Field(
        default=None,
        description="Associated law firm details",
    )
    
    lawyer: Optional["LawyerResponse"] = Field(
        default=None,
        description="Primary lawyer details",
    )


class PlaintiffSummary(UUIDMixin):
    """Summary schema for plaintiff lists."""
    
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: EmailStr = Field(..., description="Email address")
    case_type: CaseType = Field(..., description="Case type")
    case_status: CaseStatus = Field(..., description="Case status")
    risk_score: Optional[float] = Field(default=None, description="Risk score")
    created_at: datetime = Field(..., description="Creation timestamp")


class PlaintiffList(PaginationResponse[PlaintiffSummary]):
    """Schema for paginated plaintiff lists."""
    pass


class PlaintiffSearch(BaseSchema):
    """Schema for plaintiff search parameters."""
    
    query: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Search query (name, email, case description)",
    )
    
    case_type: Optional[CaseType] = Field(
        default=None,
        description="Filter by case type",
    )
    
    case_status: Optional[CaseStatus] = Field(
        default=None,
        description="Filter by case status",
    )
    
    law_firm_id: Optional[UUID] = Field(
        default=None,
        description="Filter by law firm",
    )
    
    lawyer_id: Optional[UUID] = Field(
        default=None,
        description="Filter by lawyer",
    )
    
    state: Optional[str] = Field(
        default=None,
        max_length=2,
        description="Filter by state",
    )
    
    risk_score_min: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Minimum risk score",
    )
    
    risk_score_max: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Maximum risk score",
    )
    
    created_after: Optional[datetime] = Field(
        default=None,
        description="Filter by creation date (after)",
    )
    
    created_before: Optional[datetime] = Field(
        default=None,
        description="Filter by creation date (before)",
    )


class PlaintiffStats(BaseSchema):
    """Schema for plaintiff statistics."""
    
    total_count: int = Field(..., description="Total number of plaintiffs")
    
    by_status: dict = Field(
        ...,
        description="Count by case status",
    )
    
    by_case_type: dict = Field(
        ...,
        description="Count by case type",
    )
    
    by_state: dict = Field(
        ...,
        description="Count by state",
    )
    
    average_risk_score: Optional[float] = Field(
        default=None,
        description="Average risk score",
    )
    
    high_risk_count: int = Field(
        default=0,
        description="Number of high-risk plaintiffs",
    )
    
    qualified_count: int = Field(
        default=0,
        description="Number of qualified plaintiffs",
    )


# Forward references for relationship models
from .law_firm import LawFirmResponse  # noqa: E402
from .lawyer import LawyerResponse  # noqa: E402

# Update forward references
PlaintiffResponse.model_rebuild()