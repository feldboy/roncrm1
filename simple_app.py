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

@app.get("/api/v1/agents/status")
async def get_agents_status_v2():
    """Get agent status - API v1 version."""
    return [
        {
            "id": "agent-1",
            "name": "Document Processor",
            "type": "document_intelligence",
            "status": "active",
            "tasks_completed": 42,
            "success_rate": 95,
            "last_activity": "2 minutes ago",
            "config": {
                "max_retries": 3,
                "timeout": 120,
                "enabled": True
            }
        },
        {
            "id": "agent-2", 
            "name": "Communication Handler",
            "type": "email_service",
            "status": "active",
            "tasks_completed": 18,
            "success_rate": 88,
            "last_activity": "5 minutes ago",
            "config": {
                "max_retries": 2,
                "timeout": 60,
                "enabled": True
            }
        },
        {
            "id": "agent-3",
            "name": "Case Analyzer", 
            "type": "risk_assessment",
            "status": "idle",
            "tasks_completed": 8,
            "success_rate": 92,
            "last_activity": "1 hour ago",
            "config": {
                "max_retries": 3,
                "timeout": 180,
                "enabled": False
            }
        }
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

@app.get("/api/v1/cases/dashboard-stats")
async def get_cases_dashboard_stats():
    """Get cases dashboard statistics."""
    return {
        "total_cases": 156,
        "active_cases": 89,
        "pending_cases": 45,
        "closed_cases": 22,
        "cases_this_month": 34,
        "cases_change": 12,
        "avg_case_value": 25000,
        "success_rate": 78.5
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

@app.get("/api/v1/plaintiffs")
async def get_plaintiffs():
    """Get plaintiffs list."""
    return {
        "plaintiffs": [
            {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-0123",
                "status": "active",
                "cases_count": 2,
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": 2,
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@example.com",
                "phone": "+1-555-0456",
                "status": "active",
                "cases_count": 1,
                "created_at": "2024-02-20T14:45:00Z"
            }
        ],
        "total": 2,
        "page": 1,
        "per_page": 20
    }

@app.get("/api/v1/law-firms")
async def get_law_firms():
    """Get law firms list."""
    return {
        "law_firms": [
            {
                "id": 1,
                "name": "Smith & Associates",
                "contact_person": "Robert Smith",
                "email": "contact@smithlaw.com",
                "phone": "+1-555-1000",
                "address": "123 Legal St, Law City, LC 12345",
                "status": "active",
                "cases_count": 15,
                "success_rate": 85.5,
                "created_at": "2023-06-10T09:00:00Z"
            },
            {
                "id": 2,
                "name": "Johnson Legal Group",
                "contact_person": "Mary Johnson",
                "email": "info@johnsonlegal.com",
                "phone": "+1-555-2000",
                "address": "456 Court Ave, Justice Town, JT 67890",
                "status": "active",
                "cases_count": 23,
                "success_rate": 92.1,
                "created_at": "2023-08-15T11:30:00Z"
            }
        ],
        "total": 2,
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

# Settings endpoints - these are the missing endpoints causing the frontend errors
@app.get("/api/v1/settings/categories")
async def get_settings_categories():
    """Get settings categories."""
    return [
        {
            "id": 1,
            "name": "system",
            "display_name": "System Settings",
            "description": "Core system configuration and performance settings",
            "icon": "cog",
            "sort_order": 1,
            "is_active": True,
            "settings": [
                {
                    "id": 1,
                    "category_id": 1,
                    "key": "log_level",
                    "display_name": "Log Level",
                    "description": "Minimum log level for system logging",
                    "data_type": "select",
                    "default_value": "INFO",
                    "current_value": "INFO",
                    "value": "INFO",
                    "validation_rules": {"options": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                    "ui_component": "select",
                    "ui_options": {"options": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                    "is_sensitive": False,
                    "is_readonly": False,
                    "is_required": True,
                    "requires_restart": False,
                    "sort_order": 1,
                    "is_active": True
                },
                {
                    "id": 2,
                    "category_id": 1,
                    "key": "enable_metrics",
                    "display_name": "Enable Metrics Collection",
                    "description": "Collect system performance metrics",
                    "data_type": "boolean",
                    "default_value": "true",
                    "current_value": "true",
                    "value": True,
                    "validation_rules": {},
                    "ui_component": "checkbox",
                    "ui_options": {},
                    "is_sensitive": False,
                    "is_readonly": False,
                    "is_required": False,
                    "requires_restart": False,
                    "sort_order": 2,
                    "is_active": True
                }
            ]
        },
        {
            "id": 2,
            "name": "agents",
            "display_name": "Agent Management",
            "description": "AI agent configuration and control settings",
            "icon": "beaker",
            "sort_order": 2,
            "is_active": True,
            "settings": [
                {
                    "id": 3,
                    "category_id": 2,
                    "key": "agent_health_check_interval",
                    "display_name": "Agent Health Check Interval (seconds)",
                    "description": "How often to check agent health status",
                    "data_type": "integer",
                    "default_value": "30",
                    "current_value": "30",
                    "value": 30,
                    "validation_rules": {"min": 10, "max": 300},
                    "ui_component": "input",
                    "ui_options": {},
                    "is_sensitive": False,
                    "is_readonly": False,
                    "is_required": True,
                    "requires_restart": True,
                    "sort_order": 1,
                    "is_active": True
                }
            ]
        }
    ]

@app.get("/api/v1/settings/agents")
async def get_agent_settings():
    """Get agent settings."""
    return [
        {
            "id": 1,
            "agent_type": "lead_intake",
            "agent_id": None,
            "setting_key": "auto_assign",
            "setting_value": "true",
            "data_type": "boolean",
            "is_enabled": True,
            "typed_value": True
        },
        {
            "id": 2,
            "agent_type": "risk_assessment",
            "agent_id": None,
            "setting_key": "ai_model",
            "setting_value": "gpt-3.5-turbo",
            "data_type": "string",
            "is_enabled": True,
            "typed_value": "gpt-3.5-turbo"
        }
    ]

@app.get("/agents/status")
async def get_agents_status():
    """Get agent status - this endpoint was being called directly without /api/v1."""
    return [
        {
            "id": "agent-1",
            "name": "Document Processor",
            "type": "document_intelligence",
            "status": "active",
            "tasks_completed": 42,
            "success_rate": 95,
            "last_activity": "2 minutes ago",
            "config": {
                "max_retries": 3,
                "timeout": 120,
                "enabled": True
            }
        },
        {
            "id": "agent-2", 
            "name": "Communication Handler",
            "type": "email_service",
            "status": "active",
            "tasks_completed": 18,
            "success_rate": 88,
            "last_activity": "5 minutes ago",
            "config": {
                "max_retries": 2,
                "timeout": 60,
                "enabled": True
            }
        },
        {
            "id": "agent-3",
            "name": "Case Analyzer", 
            "type": "risk_assessment",
            "status": "idle",
            "tasks_completed": 8,
            "success_rate": 92,
            "last_activity": "1 hour ago",
            "config": {
                "max_retries": 3,
                "timeout": 180,
                "enabled": False
            }
        }
    ]

# Agent management endpoints
@app.get("/api/v1/agents/settings")
async def get_agent_settings_v2():
    """Get agent settings - alternative endpoint."""
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