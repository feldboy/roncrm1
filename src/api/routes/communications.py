"""Communication management API routes."""

from fastapi import APIRouter, Request
from ...utils.logging import get_logger
from ..middleware.auth import require_permissions

logger = get_logger(__name__)
router = APIRouter()

@router.get("/")
@require_permissions("read:communications")
async def list_communications(request: Request):
    """List communications."""
    return {"communications": [], "total": 0}