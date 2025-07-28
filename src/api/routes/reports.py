"""Reporting and analytics API routes."""

from fastapi import APIRouter, Request
from ...utils.logging import get_logger
from ..middleware.auth import require_permissions

logger = get_logger(__name__)
router = APIRouter()

@router.get("/")
@require_permissions("read:reports")
async def list_reports(request: Request):
    """List available reports."""
    return {"reports": [], "total": 0}