"""Pydantic schemas for API validation and serialization."""

from .common import BaseSchema, PaginationParams, PaginationResponse
from .plaintiff import (
    PlaintiffBase,
    PlaintiffCreate,
    PlaintiffUpdate,
    PlaintiffResponse,
    PlaintiffList,
)
from .law_firm import (
    LawFirmBase,
    LawFirmCreate,
    LawFirmUpdate,
    LawFirmResponse,
    LawFirmList,
)
from .lawyer import (
    LawyerBase,
    LawyerCreate,
    LawyerUpdate,
    LawyerResponse,
    LawyerList,
)
from .case import (
    CaseBase,
    CaseCreate,
    CaseUpdate,
    CaseResponse,
    CaseList,
)
from .document import (
    DocumentBase,
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentList,
)
from .communication import (
    CommunicationBase,
    CommunicationCreate,
    CommunicationUpdate,
    CommunicationResponse,
    CommunicationList,
)
from .contract import (
    ContractBase,
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractList,
)

__all__ = [
    # Common schemas
    "BaseSchema",
    "PaginationParams",
    "PaginationResponse",
    
    # Plaintiff schemas
    "PlaintiffBase",
    "PlaintiffCreate",
    "PlaintiffUpdate",
    "PlaintiffResponse",
    "PlaintiffList",
    
    # Law firm schemas
    "LawFirmBase",
    "LawFirmCreate",
    "LawFirmUpdate",
    "LawFirmResponse",
    "LawFirmList",
    
    # Lawyer schemas
    "LawyerBase",
    "LawyerCreate",
    "LawyerUpdate",
    "LawyerResponse",
    "LawyerList",
    
    # Case schemas
    "CaseBase",
    "CaseCreate",
    "CaseUpdate",
    "CaseResponse",
    "CaseList",
    
    # Document schemas
    "DocumentBase",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentList",
    
    # Communication schemas
    "CommunicationBase",
    "CommunicationCreate",
    "CommunicationUpdate",
    "CommunicationResponse",
    "CommunicationList",
    
    # Contract schemas
    "ContractBase",
    "ContractCreate",
    "ContractUpdate",
    "ContractResponse",
    "ContractList",
]