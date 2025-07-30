# Settings Management System

The AI CRM system includes a comprehensive settings management system that allows users to configure all aspects of the application through a web interface and CLI commands.

## Features

- **Hierarchical Settings**: Settings are organized into categories for better management
- **User Overrides**: Individual users can override system settings with their own preferences
- **Agent Configuration**: Specific settings for AI agents and their behaviors
- **Audit Logging**: Complete audit trail of all settings changes
- **Validation**: Built-in validation rules for setting values
- **UI Components**: Dynamic UI rendering based on setting types
- **Bulk Operations**: Reset multiple settings or entire categories to defaults
- **Import/Export**: Settings profiles for different environments

## Settings Categories

### System Settings
- **Log Level**: Control system logging verbosity
- **Performance**: Max concurrent tasks, timeouts, etc.
- **Monitoring**: Enable metrics collection and health checks
- **Backup**: Automated backup configuration

### Agent Management
- **Health Monitoring**: Agent health check intervals
- **Task Configuration**: Timeouts, retries, and failure handling
- **Auto-restart**: Automatically restart failed agents
- **Performance Monitoring**: Track agent performance metrics

### AI Configuration
- **Default Models**: Set default AI models for different tasks
- **Token Limits**: Configure maximum tokens per request
- **Temperature**: Set creativity level for AI responses
- **Caching**: Enable response caching to reduce API calls
- **Rate Limiting**: Control API request rates

### Integrations
- **Pipedrive Sync**: Configure CRM synchronization
- **Email Integration**: SMTP and email service settings
- **SMS Integration**: SMS provider configuration
- **Webhooks**: Retry policies and failure handling

### Security
- **Session Management**: Timeout and security policies
- **Multi-Factor Authentication**: MFA requirements
- **Password Policies**: Minimum length and complexity
- **Audit Logging**: Security event logging
- **Account Lockout**: Failed login attempt policies

## Web Interface

Access the settings through the main navigation menu:

1. **Settings Page**: `/settings` - Main settings interface
2. **Category Tabs**: Switch between different setting categories
3. **Dynamic Forms**: Settings render appropriate input controls
4. **Validation**: Real-time validation with error messages
5. **Reset Options**: Reset individual settings or entire categories
6. **Audit Trail**: View recent changes and who made them

### Setting Types and UI Components

- **Text Input**: String values, numbers, URLs
- **Select Dropdown**: Predefined options
- **Checkbox**: Boolean on/off settings
- **Textarea**: Multi-line text configuration
- **Password**: Sensitive values (masked in UI)
- **JSON Editor**: Complex configuration objects

## CLI Commands

Use the settings CLI for automation and scripting:

### Initialize Settings
```bash
python -m src.cli.settings_manager init
```

### List Settings
```bash
# List all settings
python -m src.cli.settings_manager list

# List settings in a category
python -m src.cli.settings_manager list --category system

# JSON output
python -m src.cli.settings_manager list --format json
```

### Get/Set Individual Settings
```bash
# Get a setting value
python -m src.cli.settings_manager get log_level

# Set a setting value
python -m src.cli.settings_manager set log_level DEBUG --reason "Enable debug logging"

# Set boolean values
python -m src.cli.settings_manager set enable_metrics true
```

### Reset Settings
```bash
# Reset all settings to defaults
python -m src.cli.settings_manager reset --confirm

# Reset specific category
python -m src.cli.settings_manager reset --category system --confirm
```

### Agent Settings
```bash
# List agent settings
python -m src.cli.settings_manager list-agents

# Filter by agent type
python -m src.cli.settings_manager list-agents --agent-type lead_intake

# Set agent-specific setting
python -m src.cli.settings_manager set-agent lead_intake auto_assign true --data-type boolean
```

### Audit Log
```bash
# View recent changes
python -m src.cli.settings_manager audit

# Show more entries
python -m src.cli.settings_manager audit --limit 100
```

## API Endpoints

The settings system provides RESTful API endpoints:

### Categories and Settings
- `GET /api/v1/settings/categories` - List all categories with settings
- `GET /api/v1/settings/category/{name}` - Get settings for specific category
- `PUT /api/v1/settings/setting/{id}` - Update individual setting
- `POST /api/v1/settings/reset-to-defaults` - Reset settings to defaults

### Agent Settings
- `GET /api/v1/settings/agents` - List agent settings
- `PUT /api/v1/settings/agents/{type}/{key}` - Update agent setting
- `DELETE /api/v1/settings/agents/{type}/{key}` - Delete agent setting

### Profiles
- `GET /api/v1/settings/profiles` - List settings profiles
- `POST /api/v1/settings/profiles` - Create new profile
- `PUT /api/v1/settings/profiles/{id}/apply` - Apply profile

## Database Schema

The settings system uses several database tables:

- **settings_categories**: Setting categories and organization
- **settings**: Individual setting definitions and values
- **user_settings**: User-specific setting overrides
- **agent_settings**: Agent-specific configuration
- **settings_audit_log**: Complete audit trail of changes
- **settings_profiles**: Saved settings configurations

## Setting Types

### Data Types
- `string`: Text values
- `integer`: Whole numbers
- `float`: Decimal numbers
- `boolean`: True/false values
- `json`: Complex objects or arrays
- `select`: Predefined options

### Validation Rules
Settings can include validation rules in JSON format:
```json
{
  "min": 1,
  "max": 100,
  "required": true,
  "pattern": "^[a-zA-Z0-9_]+$",
  "options": ["option1", "option2", "option3"]
}
```

### UI Options
Control how settings appear in the interface:
```json
{
  "component": "select",
  "options": ["DEBUG", "INFO", "WARNING", "ERROR"],
  "placeholder": "Select log level",
  "help_text": "Choose the minimum log level to display"
}
```

## User Permissions

Settings access can be controlled through user roles:

- **Admin**: Full access to all settings
- **Manager**: Access to non-security settings
- **User**: Access to personal preferences only
- **Read-only**: View settings but cannot modify

## Best Practices

1. **Categories**: Group related settings into logical categories
2. **Naming**: Use clear, descriptive names for settings
3. **Defaults**: Provide sensible default values
4. **Validation**: Include appropriate validation rules
5. **Documentation**: Add helpful descriptions for each setting
6. **Audit**: Monitor settings changes through audit logs
7. **Testing**: Test setting changes in non-production environments
8. **Backup**: Regular backup of settings before major changes

## Environment Variables

Settings can be overridden with environment variables using the format:
```
SETTING_CATEGORY_KEY=value
```

For example:
```bash
export SYSTEM_LOG_LEVEL=DEBUG
export AGENTS_MAX_RETRIES=5
export AI_DEFAULT_MODEL=gpt-4
```

## Troubleshooting

### Common Issues

1. **Settings not saving**: Check validation rules and permissions
2. **UI not updating**: Clear browser cache or refresh settings data
3. **Agent settings not applying**: Restart affected agents
4. **Permission denied**: Verify user role and access rights

### Debugging

Enable debug logging to troubleshoot settings issues:
```bash
python -m src.cli.settings_manager set log_level DEBUG --reason "Troubleshooting settings"
```

View recent changes:
```bash
python -m src.cli.settings_manager audit --limit 20
```

### Recovery

If settings become corrupted, reset to defaults:
```bash
python -m src.cli.settings_manager reset --confirm
python -m src.cli.settings_manager init
```