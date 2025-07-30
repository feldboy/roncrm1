"""Simple settings API routes for testing the UI."""

from typing import List, Dict, Any
from fastapi import APIRouter

router = APIRouter(tags=["settings"])


@router.get("/categories")
async def get_settings_categories():
    """Get all settings categories with mock data."""
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


@router.get("/category/{category_name}")
async def get_settings_by_category(category_name: str):
    """Get settings for a specific category."""
    all_categories = await get_settings_categories()
    for category in all_categories:
        if category["name"] == category_name:
            return category
    return {"error": "Category not found"}


@router.get("/agents")
async def get_agent_settings():
    """Get agent-specific settings."""
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


@router.put("/setting/{setting_id}")
async def update_setting(setting_id: int, update_data: Dict[str, Any]):
    """Update a setting value."""
    return {
        "success": True,
        "message": "Setting updated successfully",
        "data": {
            "setting_id": setting_id,
            "requires_restart": False
        }
    }


@router.put("/agents/{agent_type}/{setting_key}")
async def update_agent_setting(agent_type: str, setting_key: str, update_data: Dict[str, Any]):
    """Update an agent-specific setting."""
    return {
        "success": True,
        "message": "Agent setting updated successfully",
        "data": {"agent_type": agent_type, "setting_key": setting_key}
    }


@router.post("/reset-to-defaults")
async def reset_settings_to_defaults():
    """Reset settings to default values."""
    return {
        "success": True,
        "message": "Successfully reset 5 settings to defaults",
        "data": {"reset_count": 5}
    }