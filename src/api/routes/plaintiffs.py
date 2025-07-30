"""Plaintiff management API routes."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.database import get_database_session
from ...models.database.plaintiff import Plaintiff, CaseType, CaseStatus, ContactMethod
from ...models.database.law_firm import LawFirm
from ...utils.logging import get_logger
from ..middleware.auth import require_permissions

logger = get_logger(__name__)
router = APIRouter()

class PlaintiffCreate(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    secondary_phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    case_type: str
    case_description: Optional[str] = None
    incident_date: Optional[str] = None
    law_firm_id: Optional[UUID] = None
    employment_status: Optional[str] = None
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    preferred_contact_method: str = "email"
    lead_source: Optional[str] = None
    notes: Optional[str] = None

@router.get("/")
@require_permissions("read:plaintiffs")
async def list_plaintiffs(
    request: Request,
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    case_type: Optional[str] = None,
    search: Optional[str] = None
):
    """List plaintiffs with pagination and filtering."""
    try:
        async with get_database_session() as session:
            stmt = select(Plaintiff).outerjoin(LawFirm)
            
            # Apply filters
            if status:
                stmt = stmt.where(Plaintiff.case_status == status)
            if case_type:
                stmt = stmt.where(Plaintiff.case_type == case_type)
            if search:
                search_term = f"%{search}%"
                stmt = stmt.where(
                    (Plaintiff.first_name.ilike(search_term)) |
                    (Plaintiff.last_name.ilike(search_term)) |
                    (Plaintiff.email.ilike(search_term))
                )
            
            # Count total
            count_stmt = select(func.count(Plaintiff.id))
            if status:
                count_stmt = count_stmt.where(Plaintiff.case_status == status)
            if case_type:
                count_stmt = count_stmt.where(Plaintiff.case_type == case_type)
            if search:
                search_term = f"%{search}%"
                count_stmt = count_stmt.where(
                    (Plaintiff.first_name.ilike(search_term)) |
                    (Plaintiff.last_name.ilike(search_term)) |
                    (Plaintiff.email.ilike(search_term))
                )
            
            total_result = await session.execute(count_stmt)
            total = total_result.scalar()
            
            # Apply pagination
            stmt = stmt.offset((page - 1) * limit).limit(limit)
            
            result = await session.execute(stmt)
            plaintiffs = result.scalars().all()
            
            plaintiffs_data = []
            for plaintiff in plaintiffs:
                plaintiffs_data.append({
                    "id": str(plaintiff.id),
                    "full_name": plaintiff.full_name,
                    "first_name": plaintiff.first_name,
                    "last_name": plaintiff.last_name,
                    "email": plaintiff.email,
                    "phone": plaintiff.phone,
                    "full_address": plaintiff.full_address,
                    "case_type": plaintiff.case_type.value,
                    "case_status": plaintiff.case_status.value,
                    "case_description": plaintiff.case_description,
                    "incident_date": plaintiff.incident_date,
                    "law_firm_name": plaintiff.law_firm.name if plaintiff.law_firm else None,
                    "employment_status": plaintiff.employment_status,
                    "monthly_income": plaintiff.monthly_income,
                    "risk_score": plaintiff.risk_score,
                    "preferred_contact_method": plaintiff.preferred_contact_method.value,
                    "lead_source": plaintiff.lead_source,
                    "created_at": plaintiff.created_at.isoformat(),
                    "updated_at": plaintiff.updated_at.isoformat(),
                })
            
            return {
                "plaintiffs": plaintiffs_data,
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
            
    except Exception as e:
        logger.error(f"Failed to list plaintiffs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve plaintiffs")

@router.post("/")
@require_permissions("write:plaintiffs")
async def create_plaintiff(plaintiff_data: PlaintiffCreate, request: Request):
    """Create a new plaintiff."""
    try:
        async with get_database_session() as session:
            # Check if plaintiff with same email already exists
            existing_stmt = select(Plaintiff).where(Plaintiff.email == plaintiff_data.email)
            existing_result = await session.execute(existing_stmt)
            existing_plaintiff = existing_result.scalar_one_or_none()
            
            if existing_plaintiff:
                raise HTTPException(status_code=400, detail="Plaintiff with this email already exists")
            
            # Verify law firm exists if provided
            if plaintiff_data.law_firm_id:
                law_firm_stmt = select(LawFirm).where(LawFirm.id == plaintiff_data.law_firm_id)
                law_firm_result = await session.execute(law_firm_stmt)
                law_firm = law_firm_result.scalar_one_or_none()
                
                if not law_firm:
                    raise HTTPException(status_code=404, detail="Law firm not found")
            
            # Create plaintiff
            plaintiff = Plaintiff(
                first_name=plaintiff_data.first_name,
                last_name=plaintiff_data.last_name,
                middle_name=plaintiff_data.middle_name,
                email=plaintiff_data.email,
                phone=plaintiff_data.phone,
                secondary_phone=plaintiff_data.secondary_phone,
                date_of_birth=plaintiff_data.date_of_birth,
                address_line_1=plaintiff_data.address_line_1,
                address_line_2=plaintiff_data.address_line_2,
                city=plaintiff_data.city,
                state=plaintiff_data.state,
                zip_code=plaintiff_data.zip_code,
                case_type=CaseType(plaintiff_data.case_type),
                case_status=CaseStatus.INITIAL,
                case_description=plaintiff_data.case_description,
                incident_date=plaintiff_data.incident_date,
                law_firm_id=plaintiff_data.law_firm_id,
                employment_status=plaintiff_data.employment_status,
                monthly_income=plaintiff_data.monthly_income,
                monthly_expenses=plaintiff_data.monthly_expenses,
                preferred_contact_method=ContactMethod(plaintiff_data.preferred_contact_method),
                lead_source=plaintiff_data.lead_source or "web_form",
                notes=plaintiff_data.notes,
            )
            
            session.add(plaintiff)
            await session.commit()
            await session.refresh(plaintiff)
            
            # Trigger lead intake agent for processing
            if hasattr(request.app.state, 'agent_registry'):
                try:
                    from ...agents.base.agent import AgentTask
                    from ...agents.base.registry import AgentType
                    
                    task = AgentTask(
                        agent_type=AgentType.LEAD_INTAKE_COORDINATOR,
                        operation="process_lead_submission",
                        payload={
                            "lead_data": {
                                "first_name": plaintiff.first_name,
                                "last_name": plaintiff.last_name,
                                "email": plaintiff.email,
                                "phone": plaintiff.phone,
                                "case_type": plaintiff.case_type.value,
                                "case_description": plaintiff.case_description,
                                "incident_date": plaintiff.incident_date,
                                "monthly_income": plaintiff.monthly_income,
                                "monthly_expenses": plaintiff.monthly_expenses,
                                "employment_status": plaintiff.employment_status,
                            },
                            "source": "web_form",
                            "plaintiff_id": str(plaintiff.id)
                        }
                    )
                    
                    await request.app.state.agent_registry.submit_task(task)
                    logger.info(f"Lead intake task submitted for plaintiff {plaintiff.id}")
                    
                except Exception as e:
                    logger.error(f"Failed to submit lead intake task: {e}")
            
            return {
                "id": str(plaintiff.id),
                "full_name": plaintiff.full_name,
                "email": plaintiff.email,
                "case_type": plaintiff.case_type.value,
                "case_status": plaintiff.case_status.value,
                "created_at": plaintiff.created_at.isoformat(),
                "message": "Plaintiff created successfully"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create plaintiff: {e}")
        raise HTTPException(status_code=500, detail="Failed to create plaintiff")

@router.get("/{plaintiff_id}")
@require_permissions("read:plaintiffs")
async def get_plaintiff(plaintiff_id: UUID, request: Request):
    """Get specific plaintiff details."""
    try:
        async with get_database_session() as session:
            stmt = select(Plaintiff).where(Plaintiff.id == plaintiff_id)
            result = await session.execute(stmt)
            plaintiff = result.scalar_one_or_none()
            
            if not plaintiff:
                raise HTTPException(status_code=404, detail="Plaintiff not found")
            
            return {
                "id": str(plaintiff.id),
                "full_name": plaintiff.full_name,
                "first_name": plaintiff.first_name,
                "last_name": plaintiff.last_name,
                "middle_name": plaintiff.middle_name,
                "email": plaintiff.email,
                "phone": plaintiff.phone,
                "secondary_phone": plaintiff.secondary_phone,
                "date_of_birth": plaintiff.date_of_birth,
                "full_address": plaintiff.full_address,
                "address_line_1": plaintiff.address_line_1,
                "address_line_2": plaintiff.address_line_2,
                "city": plaintiff.city,
                "state": plaintiff.state,
                "zip_code": plaintiff.zip_code,
                "case_type": plaintiff.case_type.value,
                "case_status": plaintiff.case_status.value,
                "case_description": plaintiff.case_description,
                "incident_date": plaintiff.incident_date,
                "law_firm_id": str(plaintiff.law_firm_id) if plaintiff.law_firm_id else None,
                "employment_status": plaintiff.employment_status,
                "monthly_income": plaintiff.monthly_income,
                "monthly_expenses": plaintiff.monthly_expenses,
                "bank_account_verified": plaintiff.bank_account_verified,
                "credit_score": plaintiff.credit_score,
                "risk_score": plaintiff.risk_score,
                "risk_factors": plaintiff.risk_factors,
                "preferred_contact_method": plaintiff.preferred_contact_method.value,
                "lead_source": plaintiff.lead_source,
                "created_at": plaintiff.created_at.isoformat(),
                "updated_at": plaintiff.updated_at.isoformat(),
                "notes": plaintiff.notes,
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get plaintiff: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve plaintiff")