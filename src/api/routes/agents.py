"""Agent management API routes."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel

from ...utils.logging import get_logger
from ..middleware.auth import require_permissions, require_role

logger = get_logger(__name__)

router = APIRouter()


class AgentTaskRequest(BaseModel):
    """Agent task request schema."""
    agent_type: str
    operation: str
    payload: Dict[str, Any]
    priority: Optional[str] = "medium"


class AgentTaskResponse(BaseModel):
    """Agent task response schema."""
    task_id: str
    agent_type: str
    operation: str
    status: str
    created_at: str
    result: Optional[Dict[str, Any]] = None


@router.get("/status")
@require_permissions("admin:agents")
async def get_agents_status(request: Request) -> Dict[str, Any]:
    """
    Get status of all agents in the system.
    
    Returns:
        Dict: System status including all agents.
    """
    try:
        if hasattr(request.app.state, 'agent_registry'):
            registry = request.app.state.agent_registry
            return await registry.get_system_status()
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent registry not available"
            )
            
    except Exception as e:
        logger.error(f"Failed to get agents status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent status"
        )


@router.get("/{agent_type}/status")
@require_permissions("admin:agents")
async def get_agent_status(agent_type: str, request: Request) -> Dict[str, Any]:
    """
    Get status of a specific agent type.
    
    Args:
        agent_type: Type of agent to check.
        
    Returns:
        Dict: Agent status information.
    """
    try:
        if hasattr(request.app.state, 'agent_registry'):
            registry = request.app.state.agent_registry
            return await registry.get_agent_status(agent_type)
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent registry not available"
            )
            
    except Exception as e:
        logger.error(f"Failed to get agent status for {agent_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve status for agent type: {agent_type}"
        )


@router.post("/task", response_model=AgentTaskResponse)
@require_permissions("write:agents")
async def submit_agent_task(
    task_request: AgentTaskRequest,
    request: Request
) -> AgentTaskResponse:
    """
    Submit a task to an agent.
    
    Args:
        task_request: Task details.
        
    Returns:
        AgentTaskResponse: Task submission result.
    """
    try:
        if not hasattr(request.app.state, 'agent_registry'):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent registry not available"
            )
        
        registry = request.app.state.agent_registry
        
        # Create agent task
        from ...agents.base.agent import AgentTask
        
        task = AgentTask(
            agent_type=task_request.agent_type,
            operation=task_request.operation,
            payload=task_request.payload,
            priority=task_request.priority,
        )
        
        # Submit task to agent
        result = await registry.submit_task(task)
        
        logger.info(
            "Agent task submitted",
            task_id=str(task.id),
            agent_type=task_request.agent_type,
            operation=task_request.operation,
            user_id=request.state.user_id,
        )
        
        return AgentTaskResponse(
            task_id=str(task.id),
            agent_type=task_request.agent_type,
            operation=task_request.operation,
            status="submitted",
            created_at=task.created_at.isoformat(),
            result=result if result else None,
        )
        
    except Exception as e:
        logger.error(f"Failed to submit agent task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit task to agent"
        )


@router.get("/task/{task_id}")
@require_permissions("read:agents")
async def get_task_status(task_id: str, request: Request) -> Dict[str, Any]:
    """
    Get status of a specific task.
    
    Args:
        task_id: Task ID to check.
        
    Returns:
        Dict: Task status information.
    """
    try:
        if not hasattr(request.app.state, 'agent_registry'):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent registry not available"
            )
        
        registry = request.app.state.agent_registry
        
        # Get task status
        task_status = await registry.get_task_status(UUID(task_id))
        
        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return task_status
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task status"
        )


@router.post("/{agent_type}/start")
@require_role("admin")
async def start_agent(agent_type: str, request: Request) -> Dict[str, Any]:
    """
    Start a specific agent type.
    
    Args:
        agent_type: Type of agent to start.
        
    Returns:
        Dict: Start operation result.
    """
    try:
        if not hasattr(request.app.state, 'agent_registry'):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent registry not available"
            )
        
        registry = request.app.state.agent_registry
        
        # Start agent
        result = await registry.start_agent(agent_type)
        
        logger.info(
            "Agent start requested",
            agent_type=agent_type,
            user_id=request.state.user_id,
            result=result,
        )
        
        return {
            "agent_type": agent_type,
            "action": "start",
            "success": result,
            "message": f"Agent {agent_type} start {'successful' if result else 'failed'}",
        }
        
    except Exception as e:
        logger.error(f"Failed to start agent {agent_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start agent: {agent_type}"
        )


@router.post("/{agent_type}/stop")
@require_role("admin")
async def stop_agent(agent_type: str, request: Request) -> Dict[str, Any]:
    """
    Stop a specific agent type.
    
    Args:
        agent_type: Type of agent to stop.
        
    Returns:
        Dict: Stop operation result.
    """
    try:
        if not hasattr(request.app.state, 'agent_registry'):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent registry not available"
            )
        
        registry = request.app.state.agent_registry
        
        # Stop agent
        result = await registry.stop_agent(agent_type)
        
        logger.info(
            "Agent stop requested",
            agent_type=agent_type,
            user_id=request.state.user_id,
            result=result,
        )
        
        return {
            "agent_type": agent_type,
            "action": "stop",
            "success": result,
            "message": f"Agent {agent_type} stop {'successful' if result else 'failed'}",
        }
        
    except Exception as e:
        logger.error(f"Failed to stop agent {agent_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop agent: {agent_type}"
        )


@router.post("/{agent_type}/restart")
@require_role("admin")
async def restart_agent(agent_type: str, request: Request) -> Dict[str, Any]:
    """
    Restart a specific agent type.
    
    Args:
        agent_type: Type of agent to restart.
        
    Returns:
        Dict: Restart operation result.
    """
    try:
        if not hasattr(request.app.state, 'agent_registry'):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent registry not available"
            )
        
        registry = request.app.state.agent_registry
        
        # Restart agent (stop then start)
        stop_result = await registry.stop_agent(agent_type)
        if stop_result:
            start_result = await registry.start_agent(agent_type)
        else:
            start_result = False
        
        success = stop_result and start_result
        
        logger.info(
            "Agent restart requested",
            agent_type=agent_type,
            user_id=request.state.user_id,
            success=success,
        )
        
        return {
            "agent_type": agent_type,
            "action": "restart",
            "success": success,
            "message": f"Agent {agent_type} restart {'successful' if success else 'failed'}",
        }
        
    except Exception as e:
        logger.error(f"Failed to restart agent {agent_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restart agent: {agent_type}"
        )


@router.get("/{agent_type}/metrics")
@require_permissions("read:agents")
async def get_agent_metrics(agent_type: str, request: Request) -> Dict[str, Any]:
    """
    Get performance metrics for a specific agent type.
    
    Args:
        agent_type: Type of agent to get metrics for.
        
    Returns:
        Dict: Agent performance metrics.
    """
    try:
        if not hasattr(request.app.state, 'agent_registry'):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent registry not available"
            )
        
        registry = request.app.state.agent_registry
        
        # Get agent metrics
        metrics = await registry.get_agent_metrics(agent_type)
        
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent type not found: {agent_type}"
            )
        
        return {
            "agent_type": agent_type,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Failed to get agent metrics for {agent_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve metrics for agent: {agent_type}"
        )


@router.get("/types")
@require_permissions("read:agents")
async def get_agent_types() -> Dict[str, Any]:
    """
    Get list of available agent types.
    
    Returns:
        Dict: Available agent types and their descriptions.
    """
    try:
        # This would typically be retrieved from the agent registry
        agent_types = {
            "lead_intake_coordinator": {
                "name": "Lead Intake Coordinator",
                "description": "Handles incoming leads and routes them appropriately",
                "operations": ["process_lead", "validate_lead", "route_lead"],
            },
            "pipedrive_sync": {
                "name": "Pipedrive Sync Agent",
                "description": "Synchronizes data with Pipedrive CRM",
                "operations": ["sync_plaintiff", "sync_law_firm", "sync_from_pipedrive"],
            },
            "risk_assessment": {
                "name": "Risk Assessment Agent",
                "description": "Analyzes case risk using AI and data analytics",
                "operations": ["assess_risk", "analyze_case_documents", "generate_risk_report"],
            },
            "document_intelligence": {
                "name": "Document Intelligence Agent",
                "description": "Processes and analyzes documents using OCR and AI",
                "operations": ["process_document", "extract_text", "classify_document"],
            },
            "email_service": {
                "name": "Email Service Agent",
                "description": "Handles email communication and templates",
                "operations": ["send_email", "send_templated_email", "send_bulk_emails"],
            },
            "sms_service": {
                "name": "SMS Service Agent",
                "description": "Manages SMS communication with compliance tracking",
                "operations": ["send_sms", "send_templated_sms", "handle_inbound_sms"],
            },
        }
        
        return {"agent_types": agent_types}
        
    except Exception as e:
        logger.error(f"Failed to get agent types: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent types"
        )