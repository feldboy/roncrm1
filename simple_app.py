#!/usr/bin/env python3
"""Simplified FastAPI app for development testing."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

# Create FastAPI app without complex dependencies
app = FastAPI(
    title="AI CRM Multi-Agent System",
    description="AI-powered CRM system for pre-settlement funding",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "development",
    }

@app.get("/api/v1/health")
async def api_health_check():
    """API Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "development",
    }

# Simplified auth endpoint for testing
@app.post("/api/v1/auth/login")
async def login(credentials: dict):
    """Simplified login endpoint for testing."""
    email = credentials.get("email")
    password = credentials.get("password")
    
    # Simple credential check
    if email in ["admin@example.com", "user@example.com"] and password in ["admin123", "user123"]:
        return {
            "access_token": "test-token-12345",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "email": email,
                "role": "admin" if email == "admin@example.com" else "user"
            }
        }
    else:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid credentials"}
        )

# Simple user info endpoint
@app.get("/api/v1/auth/me")
async def get_current_user():
    """Get current user info."""
    return {
        "id": 1,
        "email": "admin@example.com",
        "role": "admin"
    }

# Simple settings endpoint
@app.get("/api/v1/settings")
async def get_settings():
    """Get application settings."""
    return {
        "app_name": "AI CRM System",
        "version": "1.0.0",
        "features": {
            "websockets": False,
            "real_time_updates": False,
            "file_upload": False
        }
    }

# Dashboard endpoints
@app.get("/api/v1/agents")
async def get_agents():
    """Get agents status."""
    return [
        {"id": 1, "name": "Document Processor", "status": "active", "tasks_completed": 42},
        {"id": 2, "name": "Communication Handler", "status": "active", "tasks_completed": 18},
        {"id": 3, "name": "Case Analyzer", "status": "idle", "tasks_completed": 8}
    ]

@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics."""
    return {
        "active_cases": 156,
        "cases_change": 12,
        "pending_documents": 23,
        "documents_change": -3,
        "communication_queue": 8,
        "queue_change": 5,
        "system_health": 98,
        "health_change": 1
    }

# Other common endpoints
@app.get("/api/v1/cases")
async def get_cases():
    """Get cases list."""
    return {
        "cases": [],
        "total": 0,
        "page": 1,
        "per_page": 20
    }

@app.post("/api/v1/cases")
async def create_case(case_data: dict):
    """Create a new case."""
    # Simulate creating a case with a new ID
    new_case = {
        "id": 12345,
        "case_number": f"CASE-{datetime.utcnow().strftime('%Y%m%d')}-001",
        "plaintiff_name": case_data.get("plaintiff_name", ""),
        "status": case_data.get("status", "pending"),
        "case_type": case_data.get("case_type", "personal_injury"),
        "accident_date": case_data.get("accident_date"),
        "description": case_data.get("description", ""),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    return new_case

@app.get("/api/v1/communications")
async def get_communications():
    """Get communications list."""
    return {
        "communications": [],
        "total": 0,
        "page": 1,
        "per_page": 20
    }

@app.get("/api/v1/documents")
async def get_documents():
    """Get documents list."""
    return {
        "documents": [],
        "total": 0,
        "page": 1,
        "per_page": 20
    }

@app.get("/api/v1/reports/performance")
async def get_performance_reports():
    """Get performance reports."""
    return {
        "summary": {
            "total_cases": 156,
            "cases_resolved": 142,
            "avg_resolution_time": 4.2,
            "success_rate": 91.0
        },
        "trends": []
    }

@app.get("/api/v1/reports/agent-metrics")
async def get_agent_metrics():
    """Get agent metrics."""
    return {
        "agents": [
            {"name": "Document Processor", "efficiency": 95, "uptime": 98},
            {"name": "Communication Handler", "efficiency": 88, "uptime": 100},
            {"name": "Case Analyzer", "efficiency": 92, "uptime": 96}
        ]
    }

@app.get("/api/v1/activity/recent")
async def get_recent_activity():
    """Get recent activity."""
    return {
        "activities": [
            {
                "id": 1,
                "type": "case_update",
                "message": "Case #123 status updated to 'In Review'",
                "timestamp": datetime.utcnow().isoformat(),
                "user": "System"
            },
            {
                "id": 2,
                "type": "document_processed",
                "message": "Medical record processed for Case #124",
                "timestamp": datetime.utcnow().isoformat(),
                "user": "Document Processor"
            }
        ]
    }

# Agent management endpoints
@app.get("/api/v1/agents/settings")
async def get_agent_settings():
    """Get agent settings."""
    return {
        "agents": [
            {"id": 1, "name": "Document Processor", "enabled": True, "config": {}},
            {"id": 2, "name": "Communication Handler", "enabled": True, "config": {}},
            {"id": 3, "name": "Case Analyzer", "enabled": False, "config": {}}
        ]
    }

@app.put("/api/v1/agents/{agent_id}")
async def update_agent(agent_id: int, agent_data: dict):
    """Update agent configuration."""
    return {
        "id": agent_id,
        "name": agent_data.get("name", "Updated Agent"),
        "enabled": agent_data.get("enabled", True),
        "config": agent_data.get("config", {}),
        "updated_at": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/agents/{agent_id}/start")
async def start_agent(agent_id: int):
    """Start an agent."""
    return {"id": agent_id, "status": "started", "message": "Agent started successfully"}

@app.post("/api/v1/agents/{agent_id}/stop")
async def stop_agent(agent_id: int):
    """Stop an agent."""
    return {"id": agent_id, "status": "stopped", "message": "Agent stopped successfully"}

# Communications templates
@app.get("/api/v1/communications/templates")
async def get_communication_templates():
    """Get communication templates."""
    return {
        "templates": [
            {"id": 1, "name": "Case Update", "content": "Your case has been updated..."},
            {"id": 2, "name": "Document Request", "content": "We need additional documents..."}
        ]
    }

# Reports analytics
@app.get("/api/v1/reports/analytics")
async def get_reports_analytics():
    """Get reports analytics."""
    return {
        "overview": {
            "total_cases": 156,
            "resolved_cases": 142,
            "pending_cases": 14,
            "success_rate": 91.0
        },
        "trends": []
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)