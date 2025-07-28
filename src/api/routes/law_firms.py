"""Law firm management API routes."""

from fastapi import APIRouter, Request
from ...utils.logging import get_logger
from ..middleware.auth import require_permissions

logger = get_logger(__name__)
router = APIRouter()

@router.get("/")
@require_permissions("read:law_firms")
async def list_law_firms(request: Request):
    """List law firms."""
    return {"law_firms": [], "total": 0}