"""Settings database models for user-configurable application settings."""

from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import json

from .base import Base


class SettingsCategory(Base):
    """Settings categories for organizing settings."""
    
    __tablename__ = "settings_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    icon = Column(String(50))  # Icon name for UI
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    settings = relationship("Setting", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SettingsCategory(name='{self.name}', display_name='{self.display_name}')>"


class Setting(Base):
    """Individual settings that can be configured by users."""
    
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("settings_categories.id"), nullable=False)
    key = Column(String(200), nullable=False, index=True)
    display_name = Column(String(300), nullable=False)
    description = Column(Text)
    data_type = Column(String(50), nullable=False)  # string, integer, float, boolean, json, select
    default_value = Column(Text)
    current_value = Column(Text)
    validation_rules = Column(JSON)  # JSON schema for validation
    ui_component = Column(String(50))  # input, textarea, select, checkbox, switch, slider, etc.
    ui_options = Column(JSON)  # Additional UI configuration
    is_sensitive = Column(Boolean, default=False)  # For passwords, API keys, etc.
    is_readonly = Column(Boolean, default=False)
    is_required = Column(Boolean, default=False)
    requires_restart = Column(Boolean, default=False)  # If changing this requires app restart
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("SettingsCategory", back_populates="settings")
    user_settings = relationship("UserSetting", back_populates="setting", cascade="all, delete-orphan")
    audit_logs = relationship("SettingAuditLog", back_populates="setting", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_settings_category_key', 'category_id', 'key'),
        Index('idx_settings_active', 'is_active'),
    )
    
    @hybrid_property
    def value(self):
        """Get the current value with proper type conversion."""
        value = self.current_value if self.current_value is not None else self.default_value
        if value is None:
            return None
            
        if self.data_type == 'boolean':
            return str(value).lower() in ('true', '1', 'yes', 'on')
        elif self.data_type == 'integer':
            return int(value)
        elif self.data_type == 'float':
            return float(value)
        elif self.data_type == 'json':
            return json.loads(value) if isinstance(value, str) else value
        else:
            return str(value)
    
    @value.setter
    def value(self, new_value):
        """Set the current value with proper serialization."""
        if new_value is None:
            self.current_value = None
        elif self.data_type == 'json':
            self.current_value = json.dumps(new_value) if not isinstance(new_value, str) else new_value
        else:
            self.current_value = str(new_value)
    
    def __repr__(self):
        return f"<Setting(key='{self.key}', value='{self.value}')>"


class UserSetting(Base):
    """User-specific setting overrides."""
    
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Reference to user (not FK to avoid circular dependency)
    setting_id = Column(Integer, ForeignKey("settings.id"), nullable=False)
    value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    setting = relationship("Setting", back_populates="user_settings")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_settings_user_setting', 'user_id', 'setting_id', unique=True),
    )
    
    @hybrid_property
    def typed_value(self):
        """Get the value with proper type conversion based on setting data type."""
        if self.value is None:
            return None
            
        if self.setting.data_type == 'boolean':
            return str(self.value).lower() in ('true', '1', 'yes', 'on')
        elif self.setting.data_type == 'integer':
            return int(self.value)
        elif self.setting.data_type == 'float':
            return float(self.value)
        elif self.setting.data_type == 'json':
            return json.loads(self.value) if isinstance(self.value, str) else self.value
        else:
            return str(self.value)
    
    def __repr__(self):
        return f"<UserSetting(user_id={self.user_id}, setting='{self.setting.key}', value='{self.value}')>"


class AgentSetting(Base):
    """Agent-specific configuration settings."""
    
    __tablename__ = "agent_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_type = Column(String(100), nullable=False, index=True)
    agent_id = Column(String(100), nullable=True, index=True)  # For specific agent instances
    setting_key = Column(String(200), nullable=False)
    setting_value = Column(Text)
    data_type = Column(String(50), default='string')
    is_enabled = Column(Boolean, default=True)
    validation_schema = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_agent_settings_type_key', 'agent_type', 'setting_key'),
        Index('idx_agent_settings_instance', 'agent_id', 'setting_key'),
    )
    
    @hybrid_property
    def typed_value(self):
        """Get the value with proper type conversion."""
        if self.setting_value is None:
            return None
            
        if self.data_type == 'boolean':
            return str(self.setting_value).lower() in ('true', '1', 'yes', 'on')
        elif self.data_type == 'integer':
            return int(self.setting_value)
        elif self.data_type == 'float':
            return float(self.setting_value)
        elif self.data_type == 'json':
            return json.loads(self.setting_value) if isinstance(self.setting_value, str) else self.setting_value
        else:
            return str(self.setting_value)
    
    @typed_value.setter
    def typed_value(self, value):
        """Set the value with proper serialization."""
        if value is None:
            self.setting_value = None
        elif self.data_type == 'json':
            self.setting_value = json.dumps(value) if not isinstance(value, str) else value
        else:
            self.setting_value = str(value)
    
    def __repr__(self):
        return f"<AgentSetting(agent_type='{self.agent_type}', key='{self.setting_key}', value='{self.setting_value}')>"


class SettingAuditLog(Base):
    """Audit log for settings changes."""
    
    __tablename__ = "settings_audit_log"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_id = Column(Integer, ForeignKey("settings.id"), nullable=False)
    user_id = Column(Integer, nullable=True, index=True)  # Who made the change
    old_value = Column(Text)
    new_value = Column(Text)
    change_reason = Column(String(500))
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    setting = relationship("Setting", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<SettingAuditLog(setting_id={self.setting_id}, user_id={self.user_id}, created_at='{self.created_at}')>"


class SettingsProfile(Base):
    """Settings profiles for different environments or user groups."""
    
    __tablename__ = "settings_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    settings_data = Column(JSON)  # Complete settings snapshot
    created_by = Column(Integer, nullable=True)  # User who created this profile
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SettingsProfile(name='{self.name}', display_name='{self.display_name}')>"