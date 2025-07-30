"""Law firm management API routes."""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.database import get_database_session
from ...models.database.law_firm import LawFirm, FirmSize, FirmType
from ...utils.logging import get_logger
from ..middleware.auth import require_permissions

logger = get_logger(__name__)
router = APIRouter()

class LawFirmCreate(BaseModel):
    name: str
    legal_name: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    contact_email: str
    contact_phone: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    firm_size: Optional[str] = None
    firm_type: Optional[str] = None
    practice_areas: Optional[List[str]] = None
    founded_year: Optional[int] = None
    number_of_attorneys: Optional[int] = None
    notes: Optional[str] = None

@router.get("/")
@require_permissions("read:law_firms")
async def list_law_firms(
    request: Request,
    page: int = 1,
    limit: int = 20,
    active_only: bool = True,
    search: Optional[str] = None
):
    """List law firms with pagination and filtering."""
    try:
        async with get_database_session() as session:
            stmt = select(LawFirm)
            
            # Apply filters
            if active_only:
                stmt = stmt.where(LawFirm.is_active == True)
            
            if search:
                stmt = stmt.where(LawFirm.name.ilike(f"%{search}%"))
            
            # Count total
            count_stmt = select(func.count(LawFirm.id))
            if active_only:
                count_stmt = count_stmt.where(LawFirm.is_active == True)
            if search:
                count_stmt = count_stmt.where(LawFirm.name.ilike(f"%{search}%"))
            
            total_result = await session.execute(count_stmt)
            total = total_result.scalar()
            
            # Apply pagination
            stmt = stmt.offset((page - 1) * limit).limit(limit)
            
            result = await session.execute(stmt)
            law_firms = result.scalars().all()
            
            law_firms_data = []
            for firm in law_firms:
                law_firms_data.append({
                    "id": str(firm.id),
                    "name": firm.name,
                    "legal_name": firm.legal_name,
                    "website": firm.website,
                    "contact_email": firm.contact_email,
                    "contact_phone": firm.contact_phone,
                    "full_address": firm.full_address,
                    "city": firm.city,
                    "state": firm.state,
                    "firm_size": firm.firm_size.value if firm.firm_size else None,
                    "firm_type": firm.firm_type.value if firm.firm_type else None,
                    "practice_areas": firm.practice_areas,
                    "founded_year": firm.founded_year,
                    "number_of_attorneys": firm.number_of_attorneys,
                    "total_cases_referred": firm.total_cases_referred,
                    "total_cases_funded": firm.total_cases_funded,
                    "approval_rate": firm.approval_rate,
                    "is_active": firm.is_active,
                    "is_preferred": firm.is_preferred,
                    "created_at": firm.created_at.isoformat(),
                    "updated_at": firm.updated_at.isoformat(),
                })
            
            return {
                "law_firms": law_firms_data,
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
            
    except Exception as e:
        logger.error(f"Failed to list law firms: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve law firms")

@router.post("/")
@require_permissions("write:law_firms")
async def create_law_firm(firm_data: LawFirmCreate, request: Request):
    """Create a new law firm."""
    try:
        async with get_database_session() as session:
            # Check if law firm with same name already exists
            existing_stmt = select(LawFirm).where(LawFirm.name == firm_data.name)
            existing_result = await session.execute(existing_stmt)
            existing_firm = existing_result.scalar_one_or_none()
            
            if existing_firm:
                raise HTTPException(status_code=400, detail="Law firm with this name already exists")
            
            # Create law firm
            law_firm = LawFirm(
                name=firm_data.name,
                legal_name=firm_data.legal_name,
                website=firm_data.website,
                description=firm_data.description,
                contact_email=firm_data.contact_email,
                contact_phone=firm_data.contact_phone,
                address_line_1=firm_data.address_line_1,
                address_line_2=firm_data.address_line_2,
                city=firm_data.city,
                state=firm_data.state,
                zip_code=firm_data.zip_code,
                firm_size=FirmSize(firm_data.firm_size) if firm_data.firm_size else None,
                firm_type=FirmType(firm_data.firm_type) if firm_data.firm_type else None,
                practice_areas=firm_data.practice_areas,
                founded_year=firm_data.founded_year,
                number_of_attorneys=firm_data.number_of_attorneys,
                notes=firm_data.notes,
                is_active=True,
            )
            
            session.add(law_firm)
            await session.commit()
            await session.refresh(law_firm)
            
            # Trigger Pipedrive sync if available
            if hasattr(request.app.state, 'agent_registry'):
                try:
                    from ...agents.base.agent import AgentTask
                    from ...agents.base.registry import AgentType
                    
                    task = AgentTask(
                        agent_type=AgentType.PIPEDRIVE_SYNC,
                        operation="sync_law_firm",
                        payload={
                            "law_firm_id": str(law_firm.id),
                            "sync_type": "create",
                            "priority": "medium",
                        }
                    )
                    
                    await request.app.state.agent_registry.submit_task(task)
                    logger.info(f"Law firm sync task submitted for {law_firm.id}")
                    
                except Exception as e:
                    logger.error(f"Failed to submit law firm sync task: {e}")
            
            return {
                "id": str(law_firm.id),
                "name": law_firm.name,
                "contact_email": law_firm.contact_email,
                "is_active": law_firm.is_active,
                "created_at": law_firm.created_at.isoformat(),
                "message": "Law firm created successfully"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create law firm: {e}")
        raise HTTPException(status_code=500, detail="Failed to create law firm")

@router.get("/{law_firm_id}")
@require_permissions("read:law_firms")
async def get_law_firm(law_firm_id: UUID, request: Request):
    """Get specific law firm details."""
    try:
        async with get_database_session() as session:
            stmt = select(LawFirm).where(LawFirm.id == law_firm_id)
            result = await session.execute(stmt)
            law_firm = result.scalar_one_or_none()
            
            if not law_firm:
                raise HTTPException(status_code=404, detail="Law firm not found")
            
            return {
                "id": str(law_firm.id),
                "name": law_firm.name,
                "legal_name": law_firm.legal_name,
                "website": law_firm.website,
                "description": law_firm.description,
                "contact_email": law_firm.contact_email,
                "contact_phone": law_firm.contact_phone,
                "full_address": law_firm.full_address,
                "address_line_1": law_firm.address_line_1,
                "address_line_2": law_firm.address_line_2,
                "city": law_firm.city,
                "state": law_firm.state,
                "zip_code": law_firm.zip_code,
                "firm_size": law_firm.firm_size.value if law_firm.firm_size else None,
                "firm_type": law_firm.firm_type.value if law_firm.firm_type else None,
                "practice_areas": law_firm.practice_areas,
                "founded_year": law_firm.founded_year,
                "number_of_attorneys": law_firm.number_of_attorneys,
                "total_cases_referred": law_firm.total_cases_referred,
                "total_cases_funded": law_firm.total_cases_funded,
                "approval_rate": law_firm.approval_rate,
                "is_active": law_firm.is_active,
                "is_preferred": law_firm.is_preferred,
                "created_at": law_firm.created_at.isoformat(),
                "updated_at": law_firm.updated_at.isoformat(),
                "notes": law_firm.notes,
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get law firm: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve law firm")