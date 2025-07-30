"""Settings API routes for managing application configuration."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_

from ...config.database import get_database_session
from ...models.database.settings import (
    Setting, SettingsCategory, UserSetting, AgentSetting, 
    SettingAuditLog, SettingsProfile
)
from ...models.schemas.common import SuccessResponse
from ...config.settings import get_settings
from ...utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/settings", tags=["settings"])


# Pydantic models for API
from pydantic import BaseModel, Field
from datetime import datetime


class SettingResponse(BaseModel):
    id: int
    category_id: int
    key: str
    display_name: str
    description: Optional[str] = None
    data_type: str
    default_value: Optional[str] = None
    current_value: Optional[str] = None
    value: Any = None  # Typed value
    validation_rules: Optional[Dict[str, Any]] = None
    ui_component: Optional[str] = None
    ui_options: Optional[Dict[str, Any]] = None
    is_sensitive: bool = False
    is_readonly: bool = False
    is_required: bool = False
    requires_restart: bool = False
    sort_order: int = 0
    is_active: bool = True

    class Config:
        from_attributes = True


class SettingsCategoryResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    settings: List[SettingResponse] = []

    class Config:
        from_attributes = True


class SettingUpdateRequest(BaseModel):
    value: Any
    change_reason: Optional[str] = None


class AgentSettingResponse(BaseModel):
    id: int
    agent_type: str
    agent_id: Optional[str] = None
    setting_key: str
    setting_value: Optional[str] = None
    data_type: str = "string"
    is_enabled: bool = True
    typed_value: Any = None

    class Config:
        from_attributes = True


class AgentSettingUpdateRequest(BaseModel):
    setting_value: Any
    data_type: Optional[str] = "string"
    is_enabled: bool = True


# Settings API endpoints

@router.get("/categories", response_model=List[SettingsCategoryResponse])
async def get_settings_categories(
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all settings categories with their settings."""
    try:
        query = db.query(SettingsCategory)
        if not include_inactive:
            query = query.filter(SettingsCategory.is_active == True)
        
        categories = query.order_by(SettingsCategory.sort_order, SettingsCategory.display_name).all()
        
        # Build response with settings
        result = []
        for category in categories:
            category_dict = {
                "id": category.id,
                "name": category.name,
                "display_name": category.display_name,
                "description": category.description,
                "icon": category.icon,
                "sort_order": category.sort_order,
                "is_active": category.is_active,
                "settings": []
            }
            
            # Get settings for this category
            settings_query = db.query(Setting).filter(Setting.category_id == category.id)
            if not include_inactive:
                settings_query = settings_query.filter(Setting.is_active == True)
            
            category_settings = settings_query.order_by(Setting.sort_order, Setting.display_name).all()
            
            for setting in category_settings:
                setting_dict = {
                    "id": setting.id,
                    "category_id": setting.category_id,
                    "key": setting.key,
                    "display_name": setting.display_name,
                    "description": setting.description,
                    "data_type": setting.data_type,
                    "default_value": setting.default_value,
                    "current_value": setting.current_value,
                    "value": setting.value,  # This uses the hybrid property for type conversion
                    "validation_rules": setting.validation_rules,
                    "ui_component": setting.ui_component,
                    "ui_options": setting.ui_options,
                    "is_sensitive": setting.is_sensitive,
                    "is_readonly": setting.is_readonly,
                    "is_required": setting.is_required,
                    "requires_restart": setting.requires_restart,
                    "sort_order": setting.sort_order,
                    "is_active": setting.is_active
                }
                category_dict["settings"].append(setting_dict)
            
            result.append(category_dict)
        
        return result
    
    except Exception as e:
        logger.error(f"Error fetching settings categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch settings categories"
        )


@router.get("/category/{category_name}", response_model=SettingsCategoryResponse)
async def get_settings_by_category(
    category_name: str,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get settings for a specific category with user overrides."""
    try:
        category = db.query(SettingsCategory).filter(
            SettingsCategory.name == category_name,
            SettingsCategory.is_active == True
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Settings category '{category_name}' not found"
            )
        
        # Get settings for this category
        settings_list = db.query(Setting).filter(
            Setting.category_id == category.id,
            Setting.is_active == True
        ).order_by(Setting.sort_order, Setting.display_name).all()
        
        # Apply user overrides if user_id is provided
        settings_response = []
        for setting in settings_list:
            setting_dict = {
                "id": setting.id,
                "category_id": setting.category_id,
                "key": setting.key,
                "display_name": setting.display_name,
                "description": setting.description,
                "data_type": setting.data_type,
                "default_value": setting.default_value,
                "current_value": setting.current_value,
                "value": setting.value,
                "validation_rules": setting.validation_rules,
                "ui_component": setting.ui_component,
                "ui_options": setting.ui_options,
                "is_sensitive": setting.is_sensitive,
                "is_readonly": setting.is_readonly,
                "is_required": setting.is_required,
                "requires_restart": setting.requires_restart,
                "sort_order": setting.sort_order,
                "is_active": setting.is_active
            }
            
            # Check for user override
            if user_id:
                user_setting = db.query(UserSetting).filter(
                    UserSetting.user_id == user_id,
                    UserSetting.setting_id == setting.id
                ).first()
                
                if user_setting:
                    setting_dict["current_value"] = user_setting.value
                    setting_dict["value"] = user_setting.typed_value
            
            settings_response.append(setting_dict)
        
        return {
            "id": category.id,
            "name": category.name,
            "display_name": category.display_name,
            "description": category.description,
            "icon": category.icon,
            "sort_order": category.sort_order,
            "is_active": category.is_active,
            "settings": settings_response
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching settings for category {category_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch category settings"
        )


@router.put("/setting/{setting_id}", response_model=SuccessResponse)
async def update_setting(
    setting_id: int,
    update_request: SettingUpdateRequest,
    request: Request,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Update a setting value."""
    try:
        setting = db.query(Setting).filter(Setting.id == setting_id).first()
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Setting not found"
            )
        
        if setting.is_readonly:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Setting is read-only"
            )
        
        # Store old value for audit
        old_value = setting.current_value
        
        # Update the setting
        setting.value = update_request.value
        setting.updated_at = datetime.utcnow()
        
        # Create audit log entry
        audit_log = SettingAuditLog(
            setting_id=setting_id,
            user_id=user_id,
            old_value=old_value,
            new_value=setting.current_value,
            change_reason=update_request.change_reason,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        db.add(audit_log)
        
        db.commit()
        
        logger.info(f"Setting {setting.key} updated by user {user_id}")
        
        return SuccessResponse(
            message="Setting updated successfully",
            data={
                "setting_id": setting_id,
                "requires_restart": setting.requires_restart
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating setting {setting_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update setting"
        )


@router.get("/agents", response_model=List[AgentSettingResponse])
async def get_agent_settings(
    agent_type: Optional[str] = None,
    agent_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get agent-specific settings."""
    try:
        query = db.query(AgentSetting)
        
        if agent_type:
            query = query.filter(AgentSetting.agent_type == agent_type)
        
        if agent_id:
            query = query.filter(AgentSetting.agent_id == agent_id)
        
        agent_settings = query.all()
        
        result = []
        for setting in agent_settings:
            result.append({
                "id": setting.id,
                "agent_type": setting.agent_type,
                "agent_id": setting.agent_id,
                "setting_key": setting.setting_key,
                "setting_value": setting.setting_value,
                "data_type": setting.data_type,
                "is_enabled": setting.is_enabled,
                "typed_value": setting.typed_value
            })
        
        return result
    
    except Exception as e:
        logger.error(f"Error fetching agent settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch agent settings"
        )


@router.put("/agents/{agent_type}/{setting_key}", response_model=SuccessResponse)
async def update_agent_setting(
    agent_type: str,
    setting_key: str,
    update_request: AgentSettingUpdateRequest,
    agent_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update an agent-specific setting."""
    try:
        # Find existing setting or create new one
        query = db.query(AgentSetting).filter(
            AgentSetting.agent_type == agent_type,
            AgentSetting.setting_key == setting_key
        )
        
        if agent_id:
            query = query.filter(AgentSetting.agent_id == agent_id)
        
        agent_setting = query.first()
        
        if agent_setting:
            # Update existing setting
            agent_setting.typed_value = update_request.setting_value
            agent_setting.data_type = update_request.data_type
            agent_setting.is_enabled = update_request.is_enabled
            agent_setting.updated_at = datetime.utcnow()
        else:
            # Create new setting
            agent_setting = AgentSetting(
                agent_type=agent_type,
                agent_id=agent_id,
                setting_key=setting_key,
                data_type=update_request.data_type,
                is_enabled=update_request.is_enabled
            )
            agent_setting.typed_value = update_request.setting_value
            db.add(agent_setting)
        
        db.commit()
        
        logger.info(f"Agent setting {agent_type}.{setting_key} updated")
        
        return SuccessResponse(
            message="Agent setting updated successfully",
            data={"agent_type": agent_type, "setting_key": setting_key}
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating agent setting {agent_type}.{setting_key}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update agent setting"
        )


@router.delete("/agents/{agent_type}/{setting_key}", response_model=SuccessResponse)
async def delete_agent_setting(
    agent_type: str,
    setting_key: str,
    agent_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Delete an agent-specific setting."""
    try:
        query = db.query(AgentSetting).filter(
            AgentSetting.agent_type == agent_type,
            AgentSetting.setting_key == setting_key
        )
        
        if agent_id:
            query = query.filter(AgentSetting.agent_id == agent_id)
        
        agent_setting = query.first()
        
        if not agent_setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent setting not found"
            )
        
        db.delete(agent_setting)
        db.commit()
        
        logger.info(f"Agent setting {agent_type}.{setting_key} deleted")
        
        return SuccessResponse(
            message="Agent setting deleted successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting agent setting {agent_type}.{setting_key}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete agent setting"
        )


@router.get("/profiles", response_model=List[Dict[str, Any]])
async def get_settings_profiles(db: Session = Depends(get_db)):
    """Get all settings profiles."""
    try:
        profiles = db.query(SettingsProfile).filter(
            SettingsProfile.is_active == True
        ).order_by(SettingsProfile.name).all()
        
        return [
            {
                "id": profile.id,
                "name": profile.name,
                "display_name": profile.display_name,
                "description": profile.description,
                "is_default": profile.is_default,
                "created_at": profile.created_at
            }
            for profile in profiles
        ]
    
    except Exception as e:
        logger.error(f"Error fetching settings profiles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch settings profiles"
        )


@router.post("/reset-to-defaults", response_model=SuccessResponse)
async def reset_settings_to_defaults(
    category_name: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Reset settings to default values."""
    try:
        query = db.query(Setting)
        
        if category_name:
            category = db.query(SettingsCategory).filter(
                SettingsCategory.name == category_name
            ).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category '{category_name}' not found"
                )
            query = query.filter(Setting.category_id == category.id)
        
        settings_to_reset = query.all()
        
        reset_count = 0
        for setting in settings_to_reset:
            if not setting.is_readonly:
                setting.current_value = setting.default_value
                setting.updated_at = datetime.utcnow()
                reset_count += 1
        
        # Also reset user-specific settings if user_id provided
        if user_id:
            user_settings_query = db.query(UserSetting).filter(UserSetting.user_id == user_id)
            if category_name:
                setting_ids = [s.id for s in settings_to_reset]
                user_settings_query = user_settings_query.filter(UserSetting.setting_id.in_(setting_ids))
            
            user_settings_to_delete = user_settings_query.all()
            for user_setting in user_settings_to_delete:
                db.delete(user_setting)
        
        db.commit()
        
        logger.info(f"Reset {reset_count} settings to defaults")
        
        return SuccessResponse(
            message=f"Successfully reset {reset_count} settings to defaults",
            data={"reset_count": reset_count}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting settings to defaults: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset settings to defaults"
        )