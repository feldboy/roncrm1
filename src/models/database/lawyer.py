"""Lawyer model for the AI CRM system."""

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


class LawyerRole(enum.Enum):
    """Enumeration of lawyer roles within a firm."""
    
    PARTNER = "partner"
    ASSOCIATE = "associate"
    OF_COUNSEL = "of_counsel"
    PARALEGAL = "paralegal"
    LEGAL_ASSISTANT = "legal_assistant"
    CASE_MANAGER = "case_manager"
    OTHER = "other"


class LawyerStatus(enum.Enum):
    """Enumeration of lawyer status."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"
    RETIRED = "retired"


class Lawyer(BaseModel, AuditMixin):
    """
    Lawyer model representing legal professionals.
    
    Represents individual lawyers within law firms who handle cases
    and manage case assignments with performance tracking.
    """
    
    __tablename__ = "lawyers"
    
    # Personal Information
    first_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Lawyer's first name",
    )
    
    last_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Lawyer's last name",
    )
    
    middle_name = Column(
        String(50),
        nullable=True,
        comment="Lawyer's middle name",
    )
    
    title = Column(
        String(100),
        nullable=True,
        comment="Professional title (e.g., Esq., J.D.)",
    )
    
    # Contact Information
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
    
    mobile_phone = Column(
        String(20),
        nullable=True,
        comment="Mobile phone number",
    )
    
    direct_line = Column(
        String(20),
        nullable=True,
        comment="Direct office line",
    )
    
    # Professional Information
    law_firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("law_firms.id"),
        nullable=False,
        index=True,
        comment="Associated law firm",
    )
    
    role = Column(
        SQLEnum(LawyerRole),
        nullable=False,
        index=True,
        comment="Role within the law firm",
    )
    
    status = Column(
        SQLEnum(LawyerStatus),
        nullable=False,
        default=LawyerStatus.ACTIVE,
        index=True,
        comment="Current status of the lawyer",
    )
    
    bar_number = Column(
        String(50),
        nullable=True,
        comment="State bar number",
    )
    
    bar_admission_states = Column(
        JSON,
        nullable=True,
        comment="JSON array of states where lawyer is admitted to practice",
    )
    
    license_expiration_date = Column(
        "license_expiration_date",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Bar license expiration date",
    )
    
    # Education and Credentials
    law_school = Column(
        String(200),
        nullable=True,
        comment="Law school attended",
    )
    
    graduation_year = Column(
        Integer,
        nullable=True,
        comment="Year of law school graduation",
    )
    
    undergraduate_school = Column(
        String(200),
        nullable=True,
        comment="Undergraduate school attended",
    )
    
    certifications = Column(
        JSON,
        nullable=True,
        comment="JSON array of professional certifications",
    )
    
    # Practice Areas and Specializations
    practice_areas = Column(
        JSON,
        nullable=True,
        comment="JSON array of practice areas",
    )
    
    specializations = Column(
        JSON,
        nullable=True,
        comment="JSON array of legal specializations",
    )
    
    years_of_experience = Column(
        Integer,
        nullable=True,
        comment="Total years of legal experience",
    )
    
    # Assignment and Workload Management
    max_active_cases = Column(
        Integer,
        nullable=True,
        default=50,
        comment="Maximum number of active cases this lawyer can handle",
    )
    
    current_case_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Current number of active cases assigned",
    )
    
    availability_status = Column(
        String(50),
        nullable=False,
        default="available",
        comment="Current availability for new cases",
    )
    
    assignment_preferences = Column(
        JSON,
        nullable=True,
        comment="JSON object containing case assignment preferences",
    )
    
    # Performance Metrics
    total_cases_handled = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Total number of cases handled",
    )
    
    cases_won = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of cases won",
    )
    
    average_case_duration = Column(
        Integer,
        nullable=True,
        comment="Average case duration in days",
    )
    
    client_satisfaction_score = Column(
        "client_satisfaction_score",
        String(5),  # Rating as string (e.g., "4.5")
        nullable=True,
        comment="Average client satisfaction score",
    )
    
    settlement_success_rate = Column(
        "settlement_success_rate",
        String(5),  # Percentage as string (e.g., "85.5")
        nullable=True,
        comment="Settlement success rate percentage",
    )
    
    # Communication and Preferences
    preferred_communication_method = Column(
        String(50),
        nullable=False,
        default="email",
        comment="Preferred method of communication",
    )
    
    business_hours = Column(
        JSON,
        nullable=True,
        comment="JSON object defining business hours",
    )
    
    timezone = Column(
        String(50),
        nullable=True,
        default="EST",
        comment="Timezone for scheduling",
    )
    
    auto_assignment_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether automatic case assignment is enabled",
    )
    
    # Status and Flags
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether the lawyer is active",
    )
    
    is_primary_contact = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this lawyer is the primary contact for the firm",
    )
    
    accepts_new_cases = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether the lawyer accepts new case assignments",
    )
    
    # Integration Fields
    pipedrive_person_id = Column(
        Integer,
        nullable=True,
        unique=True,
        index=True,
        comment="Pipedrive person ID for synchronization",
    )
    
    # Metadata
    bio = Column(
        Text,
        nullable=True,
        comment="Professional biography",
    )
    
    profile_photo_url = Column(
        String(500),
        nullable=True,
        comment="URL to profile photo",
    )
    
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
        comment="General notes about the lawyer",
    )
    
    # Relationships
    law_firm = relationship(
        "LawFirm",
        back_populates="lawyers",
        lazy="select",
    )
    
    plaintiffs = relationship(
        "Plaintiff",
        back_populates="lawyer",
        lazy="select",
    )
    
    cases = relationship(
        "Case",
        back_populates="primary_lawyer",
        lazy="select",
    )
    
    communications = relationship(
        "Communication",
        back_populates="lawyer",
        lazy="select",
    )
    
    def __repr__(self) -> str:
        """Return string representation of the lawyer."""
        return (
            f"<Lawyer(id={self.id}, "
            f"name='{self.first_name} {self.last_name}', "
            f"role='{self.role.value}', "
            f"active={self.is_active})>"
        )
    
    @property
    def full_name(self) -> str:
        """Get the lawyer's full name."""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)
    
    @property
    def professional_name(self) -> str:
        """Get the lawyer's professional name with title."""
        name = self.full_name
        if self.title:
            name += f", {self.title}"
        return name
    
    def is_available_for_new_cases(self) -> bool:
        """Check if the lawyer is available for new case assignments."""
        if not self.is_active or not self.accepts_new_cases:
            return False
        
        if self.status != LawyerStatus.ACTIVE:
            return False
        
        if self.max_active_cases and self.current_case_count >= self.max_active_cases:
            return False
        
        return True
    
    def calculate_capacity_percentage(self) -> float:
        """Calculate the current capacity percentage."""
        if not self.max_active_cases or self.max_active_cases == 0:
            return 0.0
        
        return (self.current_case_count / self.max_active_cases) * 100
    
    def get_win_rate(self) -> float:
        """Calculate the win rate percentage."""
        if self.total_cases_handled == 0:
            return 0.0
        
        return (self.cases_won / self.total_cases_handled) * 100
    
    def is_high_performer(self) -> bool:
        """Check if this lawyer is a high performer based on metrics."""
        win_rate = self.get_win_rate()
        
        # High performer criteria (can be customized)
        return (
            win_rate >= 80.0 and
            self.total_cases_handled >= 10 and
            (
                self.client_satisfaction_score is None or
                float(self.client_satisfaction_score or "0") >= 4.0
            )
        )
    
    def assign_case(self) -> bool:
        """
        Assign a new case to this lawyer.
        
        Returns:
            bool: True if assignment was successful, False otherwise.
        """
        if not self.is_available_for_new_cases():
            return False
        
        self.current_case_count += 1
        
        # Update availability status if at capacity
        if (
            self.max_active_cases and
            self.current_case_count >= self.max_active_cases
        ):
            self.availability_status = "at_capacity"
        
        return True
    
    def unassign_case(self) -> bool:
        """
        Unassign a case from this lawyer.
        
        Returns:
            bool: True if unassignment was successful, False otherwise.
        """
        if self.current_case_count <= 0:
            return False
        
        self.current_case_count -= 1
        
        # Update availability status if below capacity
        if self.availability_status == "at_capacity":
            self.availability_status = "available"
        
        return True