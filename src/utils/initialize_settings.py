"""Initialize default settings in the database."""

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from ..models.database.settings import SettingsCategory, Setting
from ..models.database.base import Base
from ..config.settings import get_settings
from ..utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


def initialize_default_settings(db: Session):
    """Initialize default settings categories and settings."""
    
    # System Settings Category
    system_category = db.query(SettingsCategory).filter(
        SettingsCategory.name == "system"
    ).first()
    
    if not system_category:
        system_category = SettingsCategory(
            name="system",
            display_name="System Settings",
            description="Core system configuration and performance settings",
            icon="cog",
            sort_order=1
        )
        db.add(system_category)
        db.flush()  # Get the ID
        
        # System settings
        system_settings = [
            {
                "key": "log_level",
                "display_name": "Log Level",
                "description": "Minimum log level for system logging",
                "data_type": "select",
                "default_value": "INFO",
                "validation_rules": {"options": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                "ui_component": "select",
                "ui_options": {"options": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                "sort_order": 1
            },
            {
                "key": "max_concurrent_tasks",
                "display_name": "Max Concurrent Tasks",
                "description": "Maximum number of tasks that can run concurrently",
                "data_type": "integer",
                "default_value": "10",
                "validation_rules": {"min": 1, "max": 100},
                "ui_component": "input",
                "sort_order": 2
            },
            {
                "key": "task_timeout",
                "display_name": "Task Timeout (seconds)",
                "description": "Default timeout for long-running tasks",
                "data_type": "integer",
                "default_value": "300",
                "validation_rules": {"min": 30, "max": 3600},
                "ui_component": "input",
                "sort_order": 3
            },
            {
                "key": "enable_metrics",
                "display_name": "Enable Metrics Collection",
                "description": "Collect system performance metrics",
                "data_type": "boolean",
                "default_value": "true",
                "ui_component": "checkbox",
                "sort_order": 4
            },
            {
                "key": "enable_health_checks",
                "display_name": "Enable Health Checks",
                "description": "Enable automatic system health monitoring",
                "data_type": "boolean",
                "default_value": "true",
                "ui_component": "checkbox",
                "sort_order": 5
            },
            {
                "key": "cleanup_logs_after_days",
                "display_name": "Log Retention (days)",
                "description": "Number of days to keep system logs",
                "data_type": "integer",
                "default_value": "30",
                "validation_rules": {"min": 1, "max": 365},
                "ui_component": "input",
                "sort_order": 6
            },
            {
                "key": "enable_auto_backup",
                "display_name": "Enable Auto Backup",
                "description": "Automatically backup database and files",
                "data_type": "boolean",
                "default_value": "true",
                "ui_component": "checkbox",
                "sort_order": 7
            },
            {
                "key": "backup_retention_days",
                "display_name": "Backup Retention (days)",
                "description": "Number of days to keep backups",
                "data_type": "integer",
                "default_value": "7",
                "validation_rules": {"min": 1, "max": 90},
                "ui_component": "input",
                "sort_order": 8
            }
        ]
        
        for setting_data in system_settings:
            setting = Setting(
                category_id=system_category.id,
                **setting_data
            )
            db.add(setting)
    
    # Agent Settings Category
    agent_category = db.query(SettingsCategory).filter(
        SettingsCategory.name == "agents"
    ).first()
    
    if not agent_category:
        agent_category = SettingsCategory(
            name="agents",
            display_name="Agent Management",
            description="AI agent configuration and control settings",
            icon="beaker",
            sort_order=2
        )
        db.add(agent_category)
        db.flush()
        
        # Agent settings
        agent_settings = [
            {
                "key": "agent_health_check_interval",
                "display_name": "Agent Health Check Interval (seconds)",
                "description": "How often to check agent health status",
                "data_type": "integer",
                "default_value": "30",
                "validation_rules": {"min": 10, "max": 300},
                "ui_component": "input",
                "sort_order": 1
            },
            {
                "key": "agent_task_timeout",
                "display_name": "Agent Task Timeout (seconds)",
                "description": "Default timeout for agent tasks",
                "data_type": "integer",
                "default_value": "300",
                "validation_rules": {"min": 30, "max": 3600},
                "ui_component": "input",
                "sort_order": 2
            },
            {
                "key": "agent_max_retries",
                "display_name": "Agent Max Retries",
                "description": "Maximum retry attempts for failed agent tasks",
                "data_type": "integer",
                "default_value": "3",
                "validation_rules": {"min": 0, "max": 10},
                "ui_component": "input",
                "sort_order": 3
            },
            {
                "key": "enable_agent_monitoring",
                "display_name": "Enable Agent Monitoring",
                "description": "Monitor agent performance and status",
                "data_type": "boolean",
                "default_value": "true",
                "ui_component": "checkbox",
                "sort_order": 4
            },
            {
                "key": "agent_auto_restart",
                "display_name": "Auto-restart Failed Agents",
                "description": "Automatically restart agents that crash or become unresponsive",
                "data_type": "boolean",
                "default_value": "true",
                "ui_component": "checkbox",
                "sort_order": 5
            }
        ]
        
        for setting_data in agent_settings:
            setting = Setting(
                category_id=agent_category.id,
                **setting_data
            )
            db.add(setting)
    
    # AI Settings Category
    ai_category = db.query(SettingsCategory).filter(
        SettingsCategory.name == "ai"
    ).first()
    
    if not ai_category:
        ai_category = SettingsCategory(
            name="ai",
            display_name="AI Configuration",
            description="AI service and model configuration settings",
            icon="cpu-chip",
            sort_order=3
        )
        db.add(ai_category)
        db.flush()
        
        # AI settings
        ai_settings = [
            {
                "key": "default_ai_model",
                "display_name": "Default AI Model",
                "description": "Default AI model for text generation",
                "data_type": "select",
                "default_value": "gpt-3.5-turbo",
                "validation_rules": {"options": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "claude-3-sonnet", "claude-3-opus"]},
                "ui_component": "select",
                "ui_options": {"options": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "claude-3-sonnet", "claude-3-opus"]},
                "sort_order": 1
            },
            {
                "key": "ai_max_tokens",
                "display_name": "Max Tokens",
                "description": "Maximum tokens per AI request",
                "data_type": "integer",
                "default_value": "2000",
                "validation_rules": {"min": 100, "max": 32000},
                "ui_component": "input",
                "sort_order": 2
            },
            {
                "key": "ai_temperature",
                "display_name": "AI Temperature",
                "description": "Creativity level for AI responses (0.0 - 2.0)",
                "data_type": "float",
                "default_value": "0.7",
                "validation_rules": {"min": 0.0, "max": 2.0},
                "ui_component": "input",
                "sort_order": 3
            },
            {
                "key": "enable_ai_caching",
                "display_name": "Enable AI Response Caching",
                "description": "Cache AI responses to reduce API calls",
                "data_type": "boolean",
                "default_value": "true",
                "ui_component": "checkbox",
                "sort_order": 4
            },
            {
                "key": "ai_rate_limit_per_minute",
                "display_name": "AI Rate Limit (per minute)",
                "description": "Maximum AI API calls per minute",
                "data_type": "integer",
                "default_value": "60",
                "validation_rules": {"min": 1, "max": 1000},
                "ui_component": "input",
                "sort_order": 5
            }
        ]
        
        for setting_data in ai_settings:
            setting = Setting(
                category_id=ai_category.id,
                **setting_data
            )
            db.add(setting)
    
    # Integrations Settings Category
    integrations_category = db.query(SettingsCategory).filter(
        SettingsCategory.name == "integrations"
    ).first()
    
    if not integrations_category:
        integrations_category = SettingsCategory(
            name="integrations",
            display_name="Integrations",
            description="Third-party service integration settings",
            icon="link",
            sort_order=4
        )
        db.add(integrations_category)
        db.flush()
        
        # Integration settings
        integration_settings = [
            {
                "key": "enable_pipedrive_sync",
                "display_name": "Enable Pipedrive Sync",
                "description": "Synchronize data with Pipedrive CRM",
                "data_type": "boolean",
                "default_value": "false",
                "ui_component": "checkbox",
                "sort_order": 1
            },
            {
                "key": "pipedrive_sync_interval",
                "display_name": "Pipedrive Sync Interval (minutes)",
                "description": "How often to sync with Pipedrive",
                "data_type": "integer",
                "default_value": "15",
                "validation_rules": {"min": 1, "max": 1440},
                "ui_component": "input",
                "sort_order": 2
            },
            {
                "key": "enable_email_integration",
                "display_name": "Enable Email Integration",
                "description": "Enable automated email sending",
                "data_type": "boolean",
                "default_value": "true",
                "ui_component": "checkbox",
                "sort_order": 3
            },
            {
                "key": "enable_sms_integration",
                "display_name": "Enable SMS Integration",
                "description": "Enable automated SMS messaging",
                "data_type": "boolean",
                "default_value": "false",
                "ui_component": "checkbox",
                "sort_order": 4
            },
            {
                "key": "webhook_retry_attempts",
                "display_name": "Webhook Retry Attempts",
                "description": "Number of retry attempts for failed webhooks",
                "data_type": "integer",
                "default_value": "3",
                "validation_rules": {"min": 0, "max": 10},
                "ui_component": "input",
                "sort_order": 5
            }
        ]
        
        for setting_data in integration_settings:
            setting = Setting(
                category_id=integrations_category.id,
                **setting_data
            )
            db.add(setting)
    
    # Security Settings Category
    security_category = db.query(SettingsCategory).filter(
        SettingsCategory.name == "security"
    ).first()
    
    if not security_category:
        security_category = SettingsCategory(
            name="security",
            display_name="Security",
            description="Security and authentication settings",
            icon="shield-check",
            sort_order=5
        )
        db.add(security_category)
        db.flush()
        
        # Security settings
        security_settings = [
            {
                "key": "session_timeout_minutes",
                "display_name": "Session Timeout (minutes)",
                "description": "User session timeout duration",
                "data_type": "integer",
                "default_value": "60",
                "validation_rules": {"min": 5, "max": 480},
                "ui_component": "input",
                "sort_order": 1
            },
            {
                "key": "require_mfa",
                "display_name": "Require Multi-Factor Authentication",
                "description": "Require MFA for all users",
                "data_type": "boolean",
                "default_value": "false",
                "ui_component": "checkbox",
                "sort_order": 2
            },
            {
                "key": "password_min_length",
                "display_name": "Minimum Password Length",
                "description": "Minimum required password length",
                "data_type": "integer",
                "default_value": "8",
                "validation_rules": {"min": 6, "max": 128},
                "ui_component": "input",
                "sort_order": 3
            },
            {
                "key": "enable_audit_logging",
                "display_name": "Enable Audit Logging",
                "description": "Log all user actions for security auditing",
                "data_type": "boolean",
                "default_value": "true",
                "ui_component": "checkbox",
                "sort_order": 4
            },
            {
                "key": "failed_login_lockout_attempts",
                "display_name": "Failed Login Lockout Attempts",
                "description": "Number of failed attempts before account lockout",
                "data_type": "integer",
                "default_value": "5",
                "validation_rules": {"min": 3, "max": 20},
                "ui_component": "input",
                "sort_order": 5
            }
        ]
        
        for setting_data in security_settings:
            setting = Setting(
                category_id=security_category.id,
                **setting_data
            )
            db.add(setting)
    
    try:
        db.commit()
        logger.info("Successfully initialized default settings")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to initialize default settings: {str(e)}")
        raise


def main():
    """Run settings initialization as standalone script."""
    from ..database.connection import get_db_session
    
    try:
        # Create database session
        db = next(get_db_session())
        
        # Initialize settings
        initialize_default_settings(db)
        
        logger.info("Settings initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Settings initialization failed: {str(e)}")
        raise
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    main()