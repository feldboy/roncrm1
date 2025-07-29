"""Application settings and configuration management."""

from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    url: str = Field("sqlite+aiosqlite:///./app.db", env="DATABASE_URL")
    echo: bool = Field(False, env="DATABASE_ECHO")
    pool_size: int = Field(20, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(30, env="DATABASE_MAX_OVERFLOW")
    pool_timeout: int = Field(30, env="DATABASE_POOL_TIMEOUT")
    pool_recycle: int = Field(3600, env="DATABASE_POOL_RECYCLE")


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    max_connections: int = Field(20, env="REDIS_MAX_CONNECTIONS")


class CelerySettings(BaseSettings):
    """Celery configuration settings."""
    
    broker_url: str = Field("redis://localhost:6379/0", env="CELERY_BROKER_URL")
    result_backend: str = Field("redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    task_serializer: str = "json"
    accept_content: List[str] = ["json"]
    result_serializer: str = "json"
    timezone: str = "UTC"
    enable_utc: bool = True


class PipedriveSettings(BaseSettings):
    """Pipedrive API configuration settings."""
    
    api_token: str = Field("test-token", env="PIPEDRIVE_API_TOKEN")
    company_domain: str = Field("test-company", env="PIPEDRIVE_COMPANY_DOMAIN")
    webhook_secret: str = Field("test-secret", env="PIPEDRIVE_WEBHOOK_SECRET")
    rate_limit_per_10_seconds: int = Field(90, env="PIPEDRIVE_RATE_LIMIT_PER_10_SECONDS")
    
    @property
    def base_url(self) -> str:
        """Generate Pipedrive API base URL."""
        return f"https://{self.company_domain}.pipedrive.com/api/v1"


class AISettings(BaseSettings):
    """AI service configuration settings."""
    
    openai_api_key: str = Field("test-key", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field("test-key", env="ANTHROPIC_API_KEY")
    openai_model: str = Field("gpt-3.5-turbo", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(2000, env="OPENAI_MAX_TOKENS")
    default_model: str = "gpt-3.5-turbo"
    max_tokens: int = 2000
    temperature: float = 0.7


class EmailSettings(BaseSettings):
    """Email configuration settings."""
    
    smtp_host: str = Field("localhost", env="SMTP_HOST")
    smtp_port: int = Field(587, env="SMTP_PORT")
    smtp_username: str = Field("test@example.com", env="SMTP_USERNAME")
    smtp_password: str = Field("test-password", env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(True, env="SMTP_USE_TLS")


class SMSSettings(BaseSettings):
    """SMS configuration settings."""
    
    twilio_account_sid: str = Field("test-sid", env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = Field("test-token", env="TWILIO_AUTH_TOKEN")
    twilio_phone_number: str = Field("+1234567890", env="TWILIO_PHONE_NUMBER")


class SecuritySettings(BaseSettings):
    """Security and authentication settings."""
    
    secret_key: str = Field("test-secret-key-12345", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    algorithm: str = Field("HS256", env="ALGORITHM")


class FileStorageSettings(BaseSettings):
    """File storage configuration settings."""
    
    upload_dir: str = Field("./uploads", env="UPLOAD_DIR")
    max_file_size: str = Field("50MB", env="MAX_FILE_SIZE")
    allowed_file_types: str = Field("pdf,doc,docx,txt,png,jpg,jpeg", env="ALLOWED_FILE_TYPES")
    email_templates_path: str = Field("./templates/email", env="EMAIL_TEMPLATES_PATH")
    
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
    
    # Server
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    allowed_origins: List[str] = Field(["http://localhost:3000"], env="ALLOWED_ORIGINS")
    
    # Company information
    company_name: str = Field("Legal Funding Company", env="COMPANY_NAME")
    company_email: str = Field("info@legalfunding.com", env="COMPANY_EMAIL")
    company_phone: str = Field("(555) 123-4567", env="COMPANY_PHONE")
    company_address: str = Field("123 Legal Street, Law City, LC 12345", env="COMPANY_ADDRESS")
    
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
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        valid_environments = ["development", "staging", "production", "testing", "test"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v.lower()
    
    # Convenience properties for OpenAI client
    @property
    def OPENAI_API_KEY(self) -> str:
        return self.ai.openai_api_key
    
    @property
    def OPENAI_MODEL(self) -> str:
        return self.ai.openai_model
    
    @property
    def OPENAI_MAX_TOKENS(self) -> int:
        return self.ai.openai_max_tokens
    
    # Convenience properties for database
    @property
    def DATABASE_URL(self) -> str:
        return self.database.url
    
    @property
    def DATABASE_ECHO(self) -> bool:
        return self.database.echo
    
    @property
    def DATABASE_POOL_SIZE(self) -> int:
        return self.database.pool_size
    
    @property
    def DATABASE_MAX_OVERFLOW(self) -> int:
        return self.database.max_overflow
    
    @property
    def DATABASE_POOL_TIMEOUT(self) -> int:
        return self.database.pool_timeout
    
    @property
    def DATABASE_POOL_RECYCLE(self) -> int:
        return self.database.pool_recycle
    
    @property
    def TEST_DATABASE_URL(self) -> str:
        return "sqlite+aiosqlite:///./test.db"
    
    # Convenience properties for server
    @property
    def API_HOST(self) -> str:
        return self.api_host
    
    @property
    def API_PORT(self) -> int:
        return self.api_port
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        return self.allowed_origins
    
    @property
    def ENVIRONMENT(self) -> str:
        return self.environment
        
    @property
    def LOG_LEVEL(self) -> str:
        return self.log_level
    
    # Convenience properties for company info
    @property
    def COMPANY_NAME(self) -> str:
        return self.company_name
    
    @property
    def COMPANY_EMAIL(self) -> str:
        return self.company_email
    
    @property
    def COMPANY_PHONE(self) -> str:
        return self.company_phone
    
    @property
    def COMPANY_ADDRESS(self) -> str:
        return self.company_address
    
    @property
    def EMAIL_TEMPLATES_PATH(self) -> str:
        return self.file_storage.email_templates_path


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