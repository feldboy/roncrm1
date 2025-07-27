"""Document model for the AI CRM system."""

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
    LargeBinary,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel, AuditMixin


class DocumentType(enum.Enum):
    """Enumeration of document types."""
    
    MEDICAL_RECORD = "medical_record"
    POLICE_REPORT = "police_report"
    CASE_SUMMARY = "case_summary"
    INSURANCE_CLAIM = "insurance_claim"
    CONTRACT = "contract"
    CORRESPONDENCE = "correspondence"
    LEGAL_FILING = "legal_filing"
    FINANCIAL_STATEMENT = "financial_statement"
    IDENTIFICATION = "identification"
    WITNESS_STATEMENT = "witness_statement"
    EXPERT_REPORT = "expert_report"
    SETTLEMENT_AGREEMENT = "settlement_agreement"
    OTHER = "other"


class DocumentStatus(enum.Enum):
    """Enumeration of document processing statuses."""
    
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    ERROR = "error"


class DocumentSecurity(enum.Enum):
    """Enumeration of document security levels."""
    
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class Document(BaseModel, AuditMixin):
    """
    Document model representing case-related files and documents.
    
    Manages all types of documents associated with cases, plaintiffs,
    and law firms with comprehensive metadata and AI processing capabilities.
    """
    
    __tablename__ = "documents"
    
    # Document Identification
    filename = Column(
        String(255),
        nullable=False,
        comment="Original filename",
    )
    
    title = Column(
        String(200),
        nullable=True,
        comment="Document title or description",
    )
    
    document_type = Column(
        SQLEnum(DocumentType),
        nullable=False,
        index=True,
        comment="Type of document",
    )
    
    mime_type = Column(
        String(100),
        nullable=False,
        comment="MIME type of the file",
    )
    
    file_extension = Column(
        String(10),
        nullable=True,
        comment="File extension",
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
    
    # File Information
    file_size = Column(
        Integer,
        nullable=False,
        comment="File size in bytes",
    )
    
    file_path = Column(
        String(500),
        nullable=False,
        comment="Storage path to the file",
    )
    
    file_hash = Column(
        String(64),
        nullable=True,
        unique=True,
        index=True,
        comment="SHA-256 hash of the file for integrity checking",
    )
    
    storage_provider = Column(
        String(50),
        nullable=False,
        default="local",
        comment="Storage provider (local, s3, azure, etc.)",
    )
    
    # Processing Status
    status = Column(
        SQLEnum(DocumentStatus),
        nullable=False,
        default=DocumentStatus.UPLOADED,
        index=True,
        comment="Current processing status",
    )
    
    processing_started_at = Column(
        "processing_started_at",
        String(19),  # YYYY-MM-DD HH:MM:SS format
        nullable=True,
        comment="When processing started",
    )
    
    processing_completed_at = Column(
        "processing_completed_at",
        String(19),  # YYYY-MM-DD HH:MM:SS format
        nullable=True,
        comment="When processing completed",
    )
    
    processing_error = Column(
        Text,
        nullable=True,
        comment="Error message if processing failed",
    )
    
    # AI Processing Results
    extracted_text = Column(
        Text,
        nullable=True,
        comment="Text extracted from the document",
    )
    
    text_extraction_confidence = Column(
        "text_extraction_confidence",
        String(5),  # Confidence as string (e.g., "0.95")
        nullable=True,
        comment="Confidence score for text extraction",
    )
    
    extracted_metadata = Column(
        JSON,
        nullable=True,
        comment="JSON object containing extracted metadata",
    )
    
    ai_summary = Column(
        Text,
        nullable=True,
        comment="AI-generated summary of the document",
    )
    
    ai_classification = Column(
        JSON,
        nullable=True,
        comment="JSON object containing AI classification results",
    )
    
    key_phrases = Column(
        JSON,
        nullable=True,
        comment="JSON array of extracted key phrases",
    )
    
    entities = Column(
        JSON,
        nullable=True,
        comment="JSON array of extracted entities",
    )
    
    # Security and Access Control
    security_level = Column(
        SQLEnum(DocumentSecurity),
        nullable=False,
        default=DocumentSecurity.CONFIDENTIAL,
        index=True,
        comment="Security classification level",
    )
    
    is_encrypted = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether the file is encrypted at rest",
    )
    
    encryption_key_id = Column(
        String(100),
        nullable=True,
        comment="ID of the encryption key used",
    )
    
    access_permissions = Column(
        JSON,
        nullable=True,
        comment="JSON object defining access permissions",
    )
    
    # Document Properties
    page_count = Column(
        Integer,
        nullable=True,
        comment="Number of pages (for documents)",
    )
    
    language = Column(
        String(10),
        nullable=True,
        comment="Detected language of the document",
    )
    
    is_signed = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether the document contains signatures",
    )
    
    signature_count = Column(
        Integer,
        nullable=True,
        comment="Number of signatures detected",
    )
    
    contains_pii = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether document contains personally identifiable information",
    )
    
    # Version Control
    version = Column(
        String(20),
        nullable=False,
        default="1.0",
        comment="Document version",
    )
    
    parent_document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=True,
        index=True,
        comment="Parent document for version tracking",
    )
    
    is_latest_version = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether this is the latest version",
    )
    
    # Compliance and Retention
    retention_date = Column(
        "retention_date",
        String(10),  # YYYY-MM-DD format
        nullable=True,
        comment="Date when document should be deleted",
    )
    
    legal_hold = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether document is under legal hold",
    )
    
    compliance_tags = Column(
        JSON,
        nullable=True,
        comment="JSON array of compliance-related tags",
    )
    
    # Review and Approval
    reviewed_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="ID of user who reviewed the document",
    )
    
    reviewed_at = Column(
        "reviewed_at",
        String(19),  # YYYY-MM-DD HH:MM:SS format
        nullable=True,
        comment="When the document was reviewed",
    )
    
    approved_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="ID of user who approved the document",
    )
    
    approved_at = Column(
        "approved_at",
        String(19),  # YYYY-MM-DD HH:MM:SS format
        nullable=True,
        comment="When the document was approved",
    )
    
    review_notes = Column(
        Text,
        nullable=True,
        comment="Notes from document review",
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
        comment="General notes about the document",
    )
    
    # Relationships
    plaintiff = relationship(
        "Plaintiff",
        back_populates="documents",
        lazy="select",
    )
    
    case = relationship(
        "Case",
        back_populates="documents",
        lazy="select",
    )
    
    law_firm = relationship(
        "LawFirm",
        lazy="select",
    )
    
    parent_document = relationship(
        "Document",
        remote_side="Document.id",
        lazy="select",
    )
    
    child_documents = relationship(
        "Document",
        lazy="select",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        """Return string representation of the document."""
        return (
            f"<Document(id={self.id}, "
            f"filename='{self.filename}', "
            f"type='{self.document_type.value}', "
            f"status='{self.status.value}')>"
        )
    
    def is_processed(self) -> bool:
        """Check if the document has been processed."""
        return self.status in [
            DocumentStatus.PROCESSED,
            DocumentStatus.REVIEWED,
            DocumentStatus.APPROVED,
        ]
    
    def is_approved(self) -> bool:
        """Check if the document has been approved."""
        return self.status == DocumentStatus.APPROVED
    
    def needs_review(self) -> bool:
        """Check if the document needs review."""
        return self.status == DocumentStatus.PROCESSED and not self.reviewed_at
    
    def is_under_legal_hold(self) -> bool:
        """Check if the document is under legal hold."""
        return self.legal_hold
    
    def should_be_retained(self) -> bool:
        """Check if the document should still be retained."""
        if self.legal_hold:
            return True
        
        if not self.retention_date:
            return True
        
        from datetime import datetime
        retention = datetime.strptime(self.retention_date, "%Y-%m-%d")
        return datetime.now() < retention
    
    def get_file_size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.file_size / (1024 * 1024)
    
    def has_sensitive_data(self) -> bool:
        """Check if document contains sensitive data."""
        return (
            self.contains_pii or
            self.security_level in [
                DocumentSecurity.CONFIDENTIAL,
                DocumentSecurity.RESTRICTED,
            ]
        )
    
    def get_processing_duration_seconds(self) -> int:
        """
        Calculate processing duration in seconds.
        
        Returns:
            int: Processing duration in seconds, 0 if not available.
        """
        if not self.processing_started_at or not self.processing_completed_at:
            return 0
        
        from datetime import datetime
        start = datetime.strptime(self.processing_started_at, "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(self.processing_completed_at, "%Y-%m-%d %H:%M:%S")
        return int((end - start).total_seconds())
    
    def can_be_accessed_by(self, user_id: str, user_role: str) -> bool:
        """
        Check if a user can access this document.
        
        Args:
            user_id: ID of the user requesting access.
            user_role: Role of the user.
            
        Returns:
            bool: True if access is allowed, False otherwise.
        """
        # System admins can access everything
        if user_role == "admin":
            return True
        
        # Check specific access permissions
        if self.access_permissions:
            allowed_users = self.access_permissions.get("users", [])
            allowed_roles = self.access_permissions.get("roles", [])
            
            if user_id in allowed_users or user_role in allowed_roles:
                return True
        
        # Default access based on security level
        if self.security_level == DocumentSecurity.PUBLIC:
            return True
        elif self.security_level == DocumentSecurity.INTERNAL:
            return user_role in ["internal", "lawyer", "admin"]
        elif self.security_level == DocumentSecurity.CONFIDENTIAL:
            return user_role in ["lawyer", "admin"]
        elif self.security_level == DocumentSecurity.RESTRICTED:
            return user_role == "admin"
        
        return False