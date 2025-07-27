"""Logging configuration and utilities."""

import logging
import sys
from functools import lru_cache
from typing import Any, Dict

import structlog
from structlog.typing import FilteringBoundLogger

from ..config.settings import get_settings


def setup_logging() -> None:
    """
    Configure structured logging for the application.
    
    Sets up structlog with JSON output for production and
    development-friendly output for local development.
    """
    settings = get_settings()
    
    # Configure timestamper
    timestamper = structlog.processors.TimeStamper(fmt="ISO")
    
    # Common processors for all environments
    common_processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if settings.log_format == "json":
        # Production JSON logging
        processors = common_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development console logging
        processors = common_processors + [
            structlog.processors.dict_tracebacks,
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


@lru_cache()
def get_logger(name: str = __name__) -> FilteringBoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name, defaults to module name.
        
    Returns:
        FilteringBoundLogger: Configured structlog logger.
    """
    return structlog.get_logger(name)


class AgentLogger:
    """Enhanced logger for agent operations with context tracking."""
    
    def __init__(self, agent_id: str, agent_type: str):
        """
        Initialize agent logger.
        
        Args:
            agent_id: Unique identifier for the agent instance.
            agent_type: Type/class of the agent.
        """
        self.logger = get_logger(f"agent.{agent_type}")
        self.agent_id = agent_id
        self.agent_type = agent_type
    
    def bind_context(self, **kwargs: Any) -> FilteringBoundLogger:
        """
        Bind additional context to the logger.
        
        Args:
            **kwargs: Additional context fields.
            
        Returns:
            FilteringBoundLogger: Logger with bound context.
        """
        return self.logger.bind(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            **kwargs
        )
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with agent context."""
        self.bind_context(**kwargs).info(message)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with agent context."""
        self.bind_context(**kwargs).warning(message)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message with agent context."""
        self.bind_context(**kwargs).error(message)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with agent context."""
        self.bind_context(**kwargs).debug(message)
    
    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message with agent context."""
        self.bind_context(**kwargs).critical(message)


class TaskLogger:
    """Enhanced logger for task operations with task context tracking."""
    
    def __init__(self, task_id: str, operation: str, agent_id: str):
        """
        Initialize task logger.
        
        Args:
            task_id: Unique identifier for the task.
            operation: The operation being performed.
            agent_id: ID of the agent processing the task.
        """
        self.logger = get_logger("task")
        self.task_id = task_id
        self.operation = operation
        self.agent_id = agent_id
    
    def bind_context(self, **kwargs: Any) -> FilteringBoundLogger:
        """
        Bind additional context to the logger.
        
        Args:
            **kwargs: Additional context fields.
            
        Returns:
            FilteringBoundLogger: Logger with bound context.
        """
        return self.logger.bind(
            task_id=self.task_id,
            operation=self.operation,
            agent_id=self.agent_id,
            **kwargs
        )
    
    def start(self, **kwargs: Any) -> None:
        """Log task start."""
        self.bind_context(**kwargs).info("Task started")
    
    def progress(self, message: str, **kwargs: Any) -> None:
        """Log task progress."""
        self.bind_context(**kwargs).info(f"Task progress: {message}")
    
    def complete(self, **kwargs: Any) -> None:
        """Log task completion."""
        self.bind_context(**kwargs).info("Task completed")
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log task error."""
        self.bind_context(**kwargs).error(f"Task error: {message}")
    
    def retry(self, retry_count: int, **kwargs: Any) -> None:
        """Log task retry."""
        self.bind_context(retry_count=retry_count, **kwargs).warning("Task retry")


class AuditLogger:
    """Specialized logger for audit and compliance events."""
    
    def __init__(self):
        """Initialize audit logger."""
        self.logger = get_logger("audit")
    
    def log_user_action(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Dict[str, Any] = None,
    ) -> None:
        """
        Log user action for audit purposes.
        
        Args:
            user_id: ID of the user performing the action.
            action: Action being performed (create, update, delete, etc.).
            resource_type: Type of resource being acted upon.
            resource_id: ID of the resource.
            details: Additional details about the action.
        """
        self.logger.bind(
            event_type="user_action",
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
        ).info("User action recorded")
    
    def log_system_event(
        self,
        event_type: str,
        component: str,
        details: Dict[str, Any] = None,
    ) -> None:
        """
        Log system event for audit purposes.
        
        Args:
            event_type: Type of system event.
            component: System component that triggered the event.
            details: Additional details about the event.
        """
        self.logger.bind(
            event_type="system_event",
            system_event_type=event_type,
            component=component,
            details=details or {},
        ).info("System event recorded")
    
    def log_data_access(
        self,
        user_id: str,
        data_type: str,
        data_id: str,
        access_type: str,
        ip_address: str = None,
    ) -> None:
        """
        Log data access for compliance purposes.
        
        Args:
            user_id: ID of the user accessing the data.
            data_type: Type of data being accessed.
            data_id: ID of the data being accessed.
            access_type: Type of access (read, write, delete).
            ip_address: IP address of the request.
        """
        self.logger.bind(
            event_type="data_access",
            user_id=user_id,
            data_type=data_type,
            data_id=data_id,
            access_type=access_type,
            ip_address=ip_address,
        ).info("Data access recorded")


# Global logger instances
audit_logger = AuditLogger()