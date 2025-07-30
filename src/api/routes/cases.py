"""Case management API routes."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.database import get_database_session
from ...models.database.case import Case, CaseType, CaseStatus, CasePriority
from ...models.database.plaintiff import Plaintiff
from ...models.database.law_firm import LawFirm
from ...utils.logging import get_logger
from ..middleware.auth import require_permissions

logger = get_logger(__name__)
router = APIRouter()

class CaseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    plaintiff_id: UUID
    law_firm_id: UUID
    case_type: str
    incident_date: Optional[str] = None
    incident_location: Optional[str] = None
    incident_description: Optional[str] = None
    estimated_case_value: Optional[int] = None
    funding_amount_requested: Optional[int] = None
    priority: str = "normal"
    notes: Optional[str] = None

@router.get("/")
@require_permissions("read:cases")
async def list_cases(
    request: Request,
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    case_type: Optional[str] = None
):
    """List cases with pagination and filtering."""
    try:
        async with get_database_session() as session:
            stmt = select(Case).join(Plaintiff).join(LawFirm)
            
            # Apply filters
            if status:
                stmt = stmt.where(Case.case_status == status)
            if case_type:
                stmt = stmt.where(Case.case_type == case_type)
            
            # Count total
            count_stmt = select(func.count(Case.id))
            if status:
                count_stmt = count_stmt.where(Case.case_status == status)
            if case_type:
                count_stmt = count_stmt.where(Case.case_type == case_type)
            
            total_result = await session.execute(count_stmt)
            total = total_result.scalar()
            
            # Apply pagination
            stmt = stmt.offset((page - 1) * limit).limit(limit)
            
            result = await session.execute(stmt)
            cases = result.scalars().all()
            
            cases_data = []
            for case in cases:
                cases_data.append({
                    "id": str(case.id),
                    "title": case.title,
                    "description": case.description,
                    "case_type": case.case_type.value,
                    "case_status": case.case_status.value,
                    "priority": case.priority.value,
                    "plaintiff_name": case.plaintiff.full_name if case.plaintiff else None,
                    "law_firm_name": case.law_firm.name if case.law_firm else None,
                    "funding_amount_requested": case.funding_amount_requested,
                    "estimated_case_value": case.estimated_case_value,
                    "incident_date": case.incident_date,
                    "created_at": case.created_at.isoformat(),
                    "updated_at": case.updated_at.isoformat(),
                })
            
            return {
                "cases": cases_data,
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
            
    except Exception as e:
        logger.error(f"Failed to list cases: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cases")

@router.post("/")
@require_permissions("write:cases")
async def create_case(case_data: CaseCreate, request: Request):
    """Create a new case."""
    try:
        async with get_database_session() as session:
            # Verify plaintiff exists
            plaintiff_stmt = select(Plaintiff).where(Plaintiff.id == case_data.plaintiff_id)
            plaintiff_result = await session.execute(plaintiff_stmt)
            plaintiff = plaintiff_result.scalar_one_or_none()
            
            if not plaintiff:
                raise HTTPException(status_code=404, detail="Plaintiff not found")
            
            # Verify law firm exists
            law_firm_stmt = select(LawFirm).where(LawFirm.id == case_data.law_firm_id)
            law_firm_result = await session.execute(law_firm_stmt)
            law_firm = law_firm_result.scalar_one_or_none()
            
            if not law_firm:
                raise HTTPException(status_code=404, detail="Law firm not found")
            
            # Create case
            case = Case(
                title=case_data.title,
                description=case_data.description,
                plaintiff_id=case_data.plaintiff_id,
                law_firm_id=case_data.law_firm_id,
                case_type=CaseType(case_data.case_type),
                case_status=CaseStatus.INITIAL,
                priority=CasePriority(case_data.priority),
                incident_date=case_data.incident_date,
                incident_location=case_data.incident_location,
                incident_description=case_data.incident_description,
                estimated_case_value=case_data.estimated_case_value,
                funding_amount_requested=case_data.funding_amount_requested,
                notes=case_data.notes,
            )
            
            session.add(case)
            await session.commit()
            await session.refresh(case)
            
            # Trigger lead intake agent for case processing
            if hasattr(request.app.state, 'agent_registry'):
                try:
                    from ...agents.base.agent import AgentTask
                    from ...agents.base.registry import AgentType
                    
                    task = AgentTask(
                        agent_type=AgentType.LEAD_INTAKE_COORDINATOR,
                        operation="process_case_creation",
                        payload={
                            "case_id": str(case.id),
                            "plaintiff_id": str(case.plaintiff_id),
                            "law_firm_id": str(case.law_firm_id),
                            "case_data": {
                                "title": case.title,
                                "case_type": case.case_type.value,
                                "incident_description": case.incident_description,
                                "funding_requested": case.funding_amount_requested
                            }
                        }
                    )
                    
                    await request.app.state.agent_registry.submit_task(task)
                    logger.info(f"Case processing task submitted for case {case.id}")
                    
                except Exception as e:
                    logger.error(f"Failed to submit case processing task: {e}")
            
            return {
                "id": str(case.id),
                "title": case.title,
                "case_type": case.case_type.value,
                "case_status": case.case_status.value,
                "created_at": case.created_at.isoformat(),
                "message": "Case created successfully"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create case: {e}")
        raise HTTPException(status_code=500, detail="Failed to create case")

@router.get("/stats")
@require_permissions("read:cases")
async def get_case_stats(request: Request):
    """Get case statistics for dashboard."""
    try:
        async with get_database_session() as session:
            # Total cases
            total_stmt = select(func.count(Case.id))
            total_result = await session.execute(total_stmt)
            total_cases = total_result.scalar()
            
            # Active pipeline (not closed/rejected/settled)
            active_stmt = select(func.count(Case.id)).where(
                Case.case_status.in_([
                    CaseStatus.INITIAL,
                    CaseStatus.QUALIFYING,
                    CaseStatus.QUALIFIED,
                    CaseStatus.DOCUMENT_COLLECTION,
                    CaseStatus.UNDERWRITING,
                    CaseStatus.APPROVED
                ])
            )
            active_result = await session.execute(active_stmt)
            active_pipeline = active_result.scalar()
            
            # Total funding requested
            funding_stmt = select(func.sum(Case.funding_amount_requested)).where(
                Case.funding_amount_requested.isnot(None)
            )
            funding_result = await session.execute(funding_stmt)
            total_funding = funding_result.scalar() or 0
            
            # Average processing days (mock data for now)
            avg_processing_days = 12
            
            return {
                "total_cases": total_cases,
                "active_pipeline": active_pipeline,
                "total_funding": total_funding // 100 if total_funding else 0,  # Convert cents to dollars
                "avg_processing_days": avg_processing_days
            }
            
    except Exception as e:
        logger.error(f"Failed to get case stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve case statistics")