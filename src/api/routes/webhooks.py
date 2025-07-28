"""Webhook API routes for external integrations."""

from fastapi import APIRouter, Request, HTTPException, status
from ...utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/pipedrive")
async def pipedrive_webhook(request: Request):
    """Handle Pipedrive webhooks."""
    try:
        body = await request.json()
        logger.info("Pipedrive webhook received", webhook_data=body)
        
        # Process webhook through agent system
        if hasattr(request.app.state, 'agent_registry'):
            registry = request.app.state.agent_registry
            # Submit webhook task to Pipedrive Sync Agent
            # Implementation would handle webhook processing
        
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Pipedrive webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/twilio")
async def twilio_webhook(request: Request):
    """Handle Twilio SMS webhooks."""
    try:
        # Process Twilio webhook for SMS delivery status
        form_data = await request.form()
        logger.info("Twilio webhook received", webhook_data=dict(form_data))
        
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Twilio webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")