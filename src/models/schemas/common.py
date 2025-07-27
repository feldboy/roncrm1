"""Common Pydantic schemas and base classes."""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

# Type variable for generic pagination
T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )


class TimestampMixin(BaseSchema):
    """Mixin for schemas with timestamp fields."""
    
    created_at: datetime = Field(
        ...,
        description="Timestamp when the record was created",
    )
    
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the record was last updated",
    )


class UUIDMixin(BaseSchema):
    """Mixin for schemas with UUID primary key."""
    
    id: UUID = Field(
        ...,
        description="Unique identifier",
    )


class PaginationParams(BaseSchema):
    """Schema for pagination parameters."""
    
    page: int = Field(
        default=1,
        ge=1,
        description="Page number (1-based)",
    )
    
    size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page",
    )
    
    sort_by: Optional[str] = Field(
        default=None,
        description="Field to sort by",
    )
    
    sort_order: Optional[str] = Field(
        default="asc",
        regex="^(asc|desc)$",
        description="Sort order (asc or desc)",
    )


class PaginationResponse(BaseSchema, Generic[T]):
    """Generic schema for paginated responses."""
    
    items: List[T] = Field(
        ...,
        description="List of items",
    )
    
    total: int = Field(
        ...,
        ge=0,
        description="Total number of items",
    )
    
    page: int = Field(
        ...,
        ge=1,
        description="Current page number",
    )
    
    size: int = Field(
        ...,
        ge=1,
        description="Items per page",
    )
    
    pages: int = Field(
        ...,
        ge=0,
        description="Total number of pages",
    )
    
    has_next: bool = Field(
        ...,
        description="Whether there is a next page",
    )
    
    has_prev: bool = Field(
        ...,
        description="Whether there is a previous page",
    )


class ErrorResponse(BaseSchema):
    """Schema for error responses."""
    
    error: str = Field(
        ...,
        description="Error type or code",
    )
    
    message: str = Field(
        ...,
        description="Human-readable error message",
    )
    
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details",
    )


class SuccessResponse(BaseSchema):
    """Schema for success responses."""
    
    success: bool = Field(
        default=True,
        description="Indicates successful operation",
    )
    
    message: str = Field(
        ...,
        description="Success message",
    )
    
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional response data",
    )


class Address(BaseSchema):
    """Schema for address information."""
    
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
        description="State abbreviation (e.g., CA, NY)",
    )
    
    zip_code: Optional[str] = Field(
        default=None,
        max_length=10,
        regex="^[0-9]{5}(-[0-9]{4})?$",
        description="ZIP code (12345 or 12345-6789)",
    )
    
    country: Optional[str] = Field(
        default="USA",
        max_length=3,
        description="Country code",
    )


class ContactInfo(BaseSchema):
    """Schema for contact information."""
    
    email: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Email address",
    )
    
    phone: Optional[str] = Field(
        default=None,
        max_length=20,
        regex="^\\+?[1-9]\\d{1,14}$",
        description="Phone number in E.164 format",
    )
    
    secondary_phone: Optional[str] = Field(
        default=None,
        max_length=20,
        regex="^\\+?[1-9]\\d{1,14}$",
        description="Secondary phone number",
    )


class FinancialInfo(BaseSchema):
    """Schema for financial information."""
    
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
    
    bank_account_verified: bool = Field(
        default=False,
        description="Whether bank account is verified",
    )


class RiskAssessment(BaseSchema):
    """Schema for risk assessment information."""
    
    risk_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Risk score from 0.0 (low) to 1.0 (high)",
    )
    
    risk_factors: Optional[List[str]] = Field(
        default=None,
        description="List of identified risk factors",
    )
    
    underwriting_notes: Optional[str] = Field(
        default=None,
        description="Underwriting notes and analysis",
    )


class Preferences(BaseSchema):
    """Schema for user preferences."""
    
    communication: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Communication preferences",
    )
    
    notifications: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Notification preferences",
    )
    
    privacy: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Privacy preferences",
    )


class SearchParams(BaseSchema):
    """Schema for search parameters."""
    
    query: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Search query string",
    )
    
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Search filters",
    )
    
    date_from: Optional[datetime] = Field(
        default=None,
        description="Start date for date range filter",
    )
    
    date_to: Optional[datetime] = Field(
        default=None,
        description="End date for date range filter",
    )


class BulkOperationParams(BaseSchema):
    """Schema for bulk operation parameters."""
    
    ids: List[UUID] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of entity IDs to operate on",
    )
    
    operation: str = Field(
        ...,
        description="Operation to perform",
    )
    
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional parameters for the operation",
    )


class BulkOperationResponse(BaseSchema):
    """Schema for bulk operation responses."""
    
    total: int = Field(
        ...,
        ge=0,
        description="Total number of items processed",
    )
    
    successful: int = Field(
        ...,
        ge=0,
        description="Number of successful operations",
    )
    
    failed: int = Field(
        ...,
        ge=0,
        description="Number of failed operations",
    )
    
    errors: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="List of errors that occurred",
    )
    
    results: Optional[List[Any]] = Field(
        default=None,
        description="Results of successful operations",
    )


class FileUpload(BaseSchema):
    """Schema for file upload information."""
    
    filename: str = Field(
        ...,
        max_length=255,
        description="Original filename",
    )
    
    content_type: str = Field(
        ...,
        max_length=100,
        description="MIME type of the file",
    )
    
    size: int = Field(
        ...,
        ge=0,
        description="File size in bytes",
    )
    
    file_hash: Optional[str] = Field(
        default=None,
        max_length=64,
        description="SHA-256 hash of the file",
    )


class ExportParams(BaseSchema):
    """Schema for data export parameters."""
    
    format: str = Field(
        ...,
        regex="^(csv|json|xlsx|pdf)$",
        description="Export format",
    )
    
    fields: Optional[List[str]] = Field(
        default=None,
        description="Specific fields to export",
    )
    
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Filters to apply to exported data",
    )
    
    include_metadata: bool = Field(
        default=False,
        description="Whether to include metadata in export",
    )