"""Application settings and configuration management."""

from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    url: str = Field(..., env="DATABASE_URL")
    echo: bool = Field(False, env="DATABASE_ECHO")
    pool_size: int = Field(20, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(30, env="DATABASE_MAX_OVERFLOW")


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    max_connections: int = Field(20, env="REDIS_MAX_CONNECTIONS")


class CelerySettings(BaseSettings):
    """Celery configuration settings."""
    
    broker_url: str = Field(..., env="CELERY_BROKER_URL")
    result_backend: str = Field(..., env="CELERY_RESULT_BACKEND")
    task_serializer: str = "json"
    accept_content: List[str] = ["json"]
    result_serializer: str = "json"
    timezone: str = "UTC"
    enable_utc: bool = True


class PipedriveSettings(BaseSettings):
    """Pipedrive API configuration settings."""
    
    api_token: str = Field(..., env="PIPEDRIVE_API_TOKEN")
    company_domain: str = Field(..., env="PIPEDRIVE_COMPANY_DOMAIN")
    webhook_secret: str = Field(..., env="PIPEDRIVE_WEBHOOK_SECRET")
    rate_limit_per_10_seconds: int = Field(90, env="PIPEDRIVE_RATE_LIMIT_PER_10_SECONDS")
    
    @property
    def base_url(self) -> str:
        """Generate Pipedrive API base URL."""
        return f"https://{self.company_domain}.pipedrive.com/api/v1"


class AISettings(BaseSettings):
    """AI service configuration settings."""
    
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    default_model: str = "gpt-3.5-turbo"
    max_tokens: int = 2000
    temperature: float = 0.7


class EmailSettings(BaseSettings):
    """Email configuration settings."""
    
    smtp_host: str = Field(..., env="SMTP_HOST")
    smtp_port: int = Field(587, env="SMTP_PORT")
    smtp_username: str = Field(..., env="SMTP_USERNAME")
    smtp_password: str = Field(..., env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(True, env="SMTP_USE_TLS")


class SMSSettings(BaseSettings):
    """SMS configuration settings."""
    
    twilio_account_sid: str = Field(..., env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = Field(..., env="TWILIO_AUTH_TOKEN")
    twilio_phone_number: str = Field(..., env="TWILIO_PHONE_NUMBER")


class SecuritySettings(BaseSettings):
    """Security and authentication settings."""
    
    secret_key: str = Field(..., env="SECRET_KEY")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    algorithm: str = Field("HS256", env="ALGORITHM")


class FileStorageSettings(BaseSettings):
    """File storage configuration settings."""
    
    upload_dir: str = Field("./uploads", env="UPLOAD_DIR")
    max_file_size: str = Field("50MB", env="MAX_FILE_SIZE")
    allowed_file_types: str = Field("pdf,doc,docx,txt,png,jpg,jpeg", env="ALLOWED_FILE_TYPES")
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as a list."""
        return [ext.strip() for ext in self.allowed_file_types.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size to bytes."""
        size_str = self.max_file_size.upper()
        if size_str.endswith("MB"):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith("KB"):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith("GB"):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)


class AgentSettings(BaseSettings):
    """Agent configuration settings."""
    
    task_timeout: int = Field(300, env="AGENT_TASK_TIMEOUT")
    max_retries: int = Field(3, env="AGENT_MAX_RETRIES")
    health_check_interval: int = Field(30, env="AGENT_HEALTH_CHECK_INTERVAL")


class Settings(BaseSettings):
    """Main application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    api_v1_str: str = Field("/api/v1", env="API_V1_STR")
    project_name: str = Field("AI CRM Multi-Agent System", env="PROJECT_NAME")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(60, env="RATE_LIMIT_PER_MINUTE")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    log_format: str = Field("json", env="LOG_FORMAT")
    enable_metrics: bool = Field(True, env="ENABLE_METRICS")
    
    # Component settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    celery: CelerySettings = Field(default_factory=CelerySettings)
    pipedrive: PipedriveSettings = Field(default_factory=PipedriveSettings)
    ai: AISettings = Field(default_factory=AISettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    sms: SMSSettings = Field(default_factory=SMSSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    file_storage: FileStorageSettings = Field(default_factory=FileStorageSettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        valid_environments = ["development", "staging", "production", "testing"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v.lower()


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: The application settings instance.
    """
    return Settings()


# Global settings instance
settings = get_settings()