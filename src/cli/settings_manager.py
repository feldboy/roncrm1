"""CLI commands for managing application settings."""

import click
import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from ..database.connection import get_db_session
from ..models.database.settings import (
    SettingsCategory, Setting, UserSetting, AgentSetting, 
    SettingAuditLog, SettingsProfile
)
from ..utils.initialize_settings import initialize_default_settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


@click.group()
def settings():
    """Settings management commands."""
    pass


@settings.command()
def init():
    """Initialize default settings in the database."""
    try:
        db = next(get_db_session())
        
        click.echo("Initializing default settings...")
        initialize_default_settings(db)
        
        click.echo("✅ Default settings initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize settings: {str(e)}")
        click.echo(f"❌ Failed to initialize settings: {str(e)}")
        raise click.Abort()
    finally:
        if 'db' in locals():
            db.close()


@settings.command()
@click.option('--category', help='Filter by category name')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table')
def list(category: Optional[str], output_format: str):
    """List all settings or settings in a specific category."""
    try:
        db = next(get_db_session())
        
        query = db.query(Setting).join(SettingsCategory)
        
        if category:
            query = query.filter(SettingsCategory.name == category)
        
        settings_list = query.order_by(
            SettingsCategory.sort_order, 
            Setting.sort_order, 
            Setting.display_name
        ).all()
        
        if output_format == 'json':
            settings_data = []
            for setting in settings_list:
                settings_data.append({
                    'id': setting.id,
                    'category': setting.category.name,
                    'key': setting.key,
                    'display_name': setting.display_name,
                    'description': setting.description,
                    'data_type': setting.data_type,
                    'default_value': setting.default_value,
                    'current_value': setting.current_value,
                    'value': setting.value,
                    'is_active': setting.is_active
                })
            click.echo(json.dumps(settings_data, indent=2))
        else:
            # Table format
            if not settings_list:
                click.echo("No settings found.")
                return
            
            click.echo(f"{'ID':<4} {'Category':<15} {'Key':<25} {'Display Name':<25} {'Value':<20} {'Active':<6}")
            click.echo("-" * 95)
            
            for setting in settings_list:
                value_str = str(setting.value)[:18] + "..." if len(str(setting.value)) > 20 else str(setting.value)
                click.echo(f"{setting.id:<4} {setting.category.name:<15} {setting.key:<25} {setting.display_name:<25} {value_str:<20} {'✓' if setting.is_active else '✗':<6}")
        
    except Exception as e:
        logger.error(f"Failed to list settings: {str(e)}")
        click.echo(f"❌ Failed to list settings: {str(e)}")
        raise click.Abort()
    finally:
        if 'db' in locals():
            db.close()


@settings.command()
@click.argument('key')
@click.argument('value')
@click.option('--reason', help='Reason for the change')
def set(key: str, value: str, reason: Optional[str]):
    """Set a setting value by key."""
    try:
        db = next(get_db_session())
        
        setting = db.query(Setting).filter(Setting.key == key).first()
        
        if not setting:
            click.echo(f"❌ Setting with key '{key}' not found.")
            return
        
        if setting.is_readonly:
            click.echo(f"❌ Setting '{key}' is read-only and cannot be modified.")
            return
        
        # Type conversion based on data type
        typed_value = value
        if setting.data_type == 'boolean':
            typed_value = value.lower() in ('true', '1', 'yes', 'on')
        elif setting.data_type == 'integer':
            typed_value = int(value)
        elif setting.data_type == 'float':
            typed_value = float(value)
        elif setting.data_type == 'json':
            typed_value = json.loads(value)
        
        # Store old value for audit
        old_value = setting.current_value
        
        # Update setting
        setting.value = typed_value
        
        # Create audit log
        audit_log = SettingAuditLog(
            setting_id=setting.id,
            old_value=old_value,
            new_value=setting.current_value,
            change_reason=reason or f"Updated via CLI by setting key '{key}'"
        )
        db.add(audit_log)
        
        db.commit()
        
        click.echo(f"✅ Setting '{key}' updated successfully!")
        click.echo(f"   Old value: {old_value}")
        click.echo(f"   New value: {setting.current_value}")
        
        if setting.requires_restart:
            click.echo("⚠️  This setting requires a system restart to take effect.")
        
    except ValueError as e:
        click.echo(f"❌ Invalid value for setting '{key}': {str(e)}")
    except Exception as e:
        logger.error(f"Failed to set setting: {str(e)}")
        click.echo(f"❌ Failed to set setting: {str(e)}")
        raise click.Abort()
    finally:
        if 'db' in locals():
            db.close()


@settings.command()
@click.argument('key')
def get(key: str):
    """Get a setting value by key."""
    try:
        db = next(get_db_session())
        
        setting = db.query(Setting).filter(Setting.key == key).first()
        
        if not setting:
            click.echo(f"❌ Setting with key '{key}' not found.")
            return
        
        click.echo(f"Setting: {setting.display_name}")
        click.echo(f"Key: {setting.key}")
        click.echo(f"Category: {setting.category.name}")
        click.echo(f"Description: {setting.description or 'N/A'}")
        click.echo(f"Data Type: {setting.data_type}")
        click.echo(f"Default Value: {setting.default_value}")
        click.echo(f"Current Value: {setting.current_value}")
        click.echo(f"Typed Value: {setting.value}")
        click.echo(f"Is Active: {'Yes' if setting.is_active else 'No'}")
        click.echo(f"Is Read-only: {'Yes' if setting.is_readonly else 'No'}")
        click.echo(f"Requires Restart: {'Yes' if setting.requires_restart else 'No'}")
        
    except Exception as e:
        logger.error(f"Failed to get setting: {str(e)}")
        click.echo(f"❌ Failed to get setting: {str(e)}")
        raise click.Abort()
    finally:
        if 'db' in locals():
            db.close()


@settings.command()
@click.option('--category', help='Reset only settings in this category')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
def reset(category: Optional[str], confirm: bool):
    """Reset settings to their default values."""
    if not confirm:
        if category:
            if not click.confirm(f"Are you sure you want to reset all settings in category '{category}' to their default values?"):
                return
        else:
            if not click.confirm("Are you sure you want to reset ALL settings to their default values?"):
                return
    
    try:
        db = next(get_db_session())
        
        query = db.query(Setting)
        
        if category:
            category_obj = db.query(SettingsCategory).filter(SettingsCategory.name == category).first()
            if not category_obj:
                click.echo(f"❌ Category '{category}' not found.")
                return
            query = query.filter(Setting.category_id == category_obj.id)
        
        settings_to_reset = query.filter(Setting.is_readonly == False).all()
        
        reset_count = 0
        for setting in settings_to_reset:
            old_value = setting.current_value
            setting.current_value = setting.default_value
            
            # Create audit log
            audit_log = SettingAuditLog(
                setting_id=setting.id,
                old_value=old_value,
                new_value=setting.current_value,
                change_reason=f"Reset to default via CLI {f'(category: {category})' if category else '(all settings)'}"
            )
            db.add(audit_log)
            
            reset_count += 1
        
        db.commit()
        
        click.echo(f"✅ Successfully reset {reset_count} settings to their default values!")
        
        # Check if any require restart
        restart_required = any(s.requires_restart for s in settings_to_reset)
        if restart_required:
            click.echo("⚠️  Some settings require a system restart to take effect.")
        
    except Exception as e:
        logger.error(f"Failed to reset settings: {str(e)}")
        click.echo(f"❌ Failed to reset settings: {str(e)}")
        raise click.Abort()
    finally:
        if 'db' in locals():
            db.close()


@settings.command()
@click.option('--agent-type', help='Filter by agent type')
@click.option('--agent-id', help='Filter by specific agent ID')
def list_agents(agent_type: Optional[str], agent_id: Optional[str]):
    """List agent-specific settings."""
    try:
        db = next(get_db_session())
        
        query = db.query(AgentSetting)
        
        if agent_type:
            query = query.filter(AgentSetting.agent_type == agent_type)
        
        if agent_id:
            query = query.filter(AgentSetting.agent_id == agent_id)
        
        agent_settings = query.order_by(AgentSetting.agent_type, AgentSetting.setting_key).all()
        
        if not agent_settings:
            click.echo("No agent settings found.")
            return
        
        click.echo(f"{'ID':<4} {'Agent Type':<20} {'Agent ID':<15} {'Key':<25} {'Value':<20} {'Enabled':<8}")
        click.echo("-" * 92)
        
        for setting in agent_settings:
            agent_id_str = setting.agent_id or 'N/A'
            value_str = str(setting.typed_value)[:18] + "..." if len(str(setting.typed_value)) > 20 else str(setting.typed_value)
            click.echo(f"{setting.id:<4} {setting.agent_type:<20} {agent_id_str:<15} {setting.setting_key:<25} {value_str:<20} {'✓' if setting.is_enabled else '✗':<8}")
        
    except Exception as e:
        logger.error(f"Failed to list agent settings: {str(e)}")
        click.echo(f"❌ Failed to list agent settings: {str(e)}")
        raise click.Abort()
    finally:
        if 'db' in locals():
            db.close()


@settings.command()
@click.argument('agent_type')
@click.argument('setting_key')
@click.argument('value')
@click.option('--agent-id', help='Specific agent ID (optional)')
@click.option('--data-type', default='string', help='Data type for the value')
def set_agent(agent_type: str, setting_key: str, value: str, agent_id: Optional[str], data_type: str):
    """Set an agent-specific setting."""
    try:
        db = next(get_db_session())
        
        # Find existing setting or create new one
        query = db.query(AgentSetting).filter(
            AgentSetting.agent_type == agent_type,
            AgentSetting.setting_key == setting_key
        )
        
        if agent_id:
            query = query.filter(AgentSetting.agent_id == agent_id)
        
        agent_setting = query.first()
        
        # Type conversion
        typed_value = value
        if data_type == 'boolean':
            typed_value = value.lower() in ('true', '1', 'yes', 'on')
        elif data_type == 'integer':
            typed_value = int(value)
        elif data_type == 'float':
            typed_value = float(value)
        elif data_type == 'json':
            typed_value = json.loads(value)
        
        if agent_setting:
            # Update existing
            agent_setting.typed_value = typed_value
            agent_setting.data_type = data_type
            action = "updated"
        else:
            # Create new
            agent_setting = AgentSetting(
                agent_type=agent_type,
                agent_id=agent_id,
                setting_key=setting_key,
                data_type=data_type,
                is_enabled=True
            )
            agent_setting.typed_value = typed_value
            db.add(agent_setting)
            action = "created"
        
        db.commit()
        
        click.echo(f"✅ Agent setting {action} successfully!")
        click.echo(f"   Agent Type: {agent_type}")
        click.echo(f"   Agent ID: {agent_id or 'All instances'}")
        click.echo(f"   Setting: {setting_key}")
        click.echo(f"   Value: {agent_setting.setting_value}")
        
    except ValueError as e:
        click.echo(f"❌ Invalid value: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to set agent setting: {str(e)}")
        click.echo(f"❌ Failed to set agent setting: {str(e)}")
        raise click.Abort()
    finally:
        if 'db' in locals():
            db.close()


@settings.command()
@click.option('--limit', default=50, help='Number of recent changes to show')
def audit(limit: int):
    """Show recent settings changes audit log."""
    try:
        db = next(get_db_session())
        
        audit_logs = db.query(SettingAuditLog).join(Setting).order_by(
            SettingAuditLog.created_at.desc()
        ).limit(limit).all()
        
        if not audit_logs:
            click.echo("No audit log entries found.")
            return
        
        click.echo(f"{'Date':<20} {'Setting Key':<25} {'Old Value':<15} {'New Value':<15} {'Reason':<30}")
        click.echo("-" * 105)
        
        for log in audit_logs:
            date_str = log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else 'N/A'
            old_val = (str(log.old_value)[:13] + "...") if log.old_value and len(str(log.old_value)) > 15 else (log.old_value or 'N/A')
            new_val = (str(log.new_value)[:13] + "...") if log.new_value and len(str(log.new_value)) > 15 else (log.new_value or 'N/A')
            reason = (log.change_reason[:28] + "...") if log.change_reason and len(log.change_reason) > 30 else (log.change_reason or 'N/A')
            
            click.echo(f"{date_str:<20} {log.setting.key:<25} {old_val:<15} {new_val:<15} {reason:<30}")
        
    except Exception as e:
        logger.error(f"Failed to show audit log: {str(e)}")
        click.echo(f"❌ Failed to show audit log: {str(e)}")
        raise click.Abort()
    finally:
        if 'db' in locals():
            db.close()


if __name__ == '__main__':
    settings()