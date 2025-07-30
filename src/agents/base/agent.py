"""Base agent class implementation for the AI CRM Multi-Agent System."""

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, Field
import enum

from ...utils.logging import AgentLogger, TaskLogger
from ...config.settings import get_settings


class TaskStatus(enum.Enum):
    """Enumeration of task statuses."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


class TaskPriority(enum.Enum):
    """Enumeration of task priorities."""
    
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AgentType(enum.Enum):
    """Enumeration of agent types."""
    
    # Core business agents
    LEAD_INTAKE = "lead_intake"
    PLAINTIFF_MANAGEMENT = "plaintiff_management"
    LAW_FIRM_MANAGEMENT = "law_firm_management"
    LAWYER_MANAGEMENT = "lawyer_management"
    CASE_STATUS_MANAGER = "case_status_manager"
    
    # Document and AI agents
    TEXT_EXTRACTION = "text_extraction"
    DOCUMENT_INTELLIGENCE = "document_intelligence"
    CLASSIFICATION = "classification"
    CONTENT_GENERATION = "content_generation"
    RISK_ASSESSMENT = "risk_assessment"
    QUALITY_ASSURANCE = "quality_assurance"
    
    # Communication agents
    EMAIL_SERVICE = "email_service"
    SMS_SERVICE = "sms_service"
    NOTIFICATION_SERVICE = "notification_service"
    
    # Data management agents
    DATABASE_COORDINATOR = "database_coordinator"
    FILE_STORAGE = "file_storage"
    AUDIT_LOGGING = "audit_logging"
    DATA_VALIDATION = "data_validation"
    
    # Business logic agents
    UNDERWRITING_ASSISTANT = "underwriting_assistant"
    CONTRACT_MANAGEMENT = "contract_management"
    REPORTING_ANALYTICS = "reporting_analytics"
    
    # Integration agents
    PIPEDRIVE_SYNC = "pipedrive_sync"
    PIPEDRIVE_MIGRATION = "pipedrive_migration"
    
    # Operations agents
    OPERATIONS_SUPERVISOR = "operations_supervisor"


class HealthStatus(enum.Enum):
    """Enumeration of agent health statuses."""
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


class AgentStatus(enum.Enum):
    """Enumeration of agent statuses."""
    
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class AgentTask(BaseModel):
    """Standardized task format for inter-agent communication."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: AgentType = Field(..., description="Target agent type")
    operation: str = Field(..., description="Operation to perform")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL)
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    timeout_seconds: int = Field(default=300)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = Field(default=None)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    
    # Context and tracing
    correlation_id: Optional[str] = Field(default=None)
    parent_task_id: Optional[str] = Field(default=None)
    user_id: Optional[str] = Field(default=None)
    session_id: Optional[str] = Field(default=None)


class AgentResponse(BaseModel):
    """Standardized response format from agents."""
    
    task_id: str = Field(..., description="ID of the processed task")
    agent_id: str = Field(..., description="ID of the agent that processed the task")
    agent_type: AgentType = Field(..., description="Type of the agent")
    success: bool = Field(..., description="Whether the task was successful")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    execution_time_ms: Optional[int] = Field(default=None, description="Execution time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Performance metrics
    database_queries: Optional[int] = Field(default=None)
    memory_usage_mb: Optional[float] = Field(default=None)
    cpu_usage_percent: Optional[float] = Field(default=None)


class AgentConfig(BaseModel):
    """Configuration for agent instances."""
    
    agent_id: str = Field(..., description="Unique identifier for the agent")
    agent_type: AgentType = Field(..., description="Type of the agent")
    max_concurrent_tasks: int = Field(default=10, description="Maximum concurrent tasks")
    task_timeout: int = Field(default=300, description="Default task timeout in seconds")
    retry_delay_seconds: int = Field(default=30, description="Delay between retries")
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    
    # Resource limits
    max_memory_mb: Optional[int] = Field(default=None, description="Maximum memory usage")
    max_cpu_percent: Optional[float] = Field(default=None, description="Maximum CPU usage")
    
    # Specific configuration
    custom_config: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific configuration")


class PerformanceMetrics(BaseModel):
    """Performance metrics for agents."""
    
    tasks_processed: int = Field(default=0)
    tasks_successful: int = Field(default=0)
    tasks_failed: int = Field(default=0)
    average_execution_time_ms: float = Field(default=0.0)
    total_execution_time_ms: int = Field(default=0)
    last_execution_time_ms: Optional[int] = Field(default=None)
    
    # Resource usage
    peak_memory_mb: float = Field(default=0.0)
    average_memory_mb: float = Field(default=0.0)
    peak_cpu_percent: float = Field(default=0.0)
    average_cpu_percent: float = Field(default=0.0)
    
    # Error tracking
    consecutive_failures: int = Field(default=0)
    last_error: Optional[str] = Field(default=None)
    last_error_timestamp: Optional[datetime] = Field(default=None)
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)


class BaseAgent(ABC):
    """
    Foundation class for all CRM agents with standardized interface.
    
    All agents in the multi-agent system inherit from this class to ensure
    consistent behavior, error handling, monitoring, and communication patterns.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the base agent.
        
        Args:
            config: Agent configuration object.
        """
        self.config = config
        self.agent_id = config.agent_id
        self.agent_type = config.agent_type
        
        # Initialize logging
        self.logger = AgentLogger(self.agent_id, self.agent_type.value)
        
        # Task management
        self.task_queue: asyncio.Queue[AgentTask] = asyncio.Queue()
        self.active_tasks: Dict[str, AgentTask] = {}
        self.running = False
        
        # Health and performance
        self.health_status = HealthStatus.HEALTHY
        self.performance_metrics = PerformanceMetrics()
        self.last_health_check = datetime.utcnow()
        
        # Get global settings
        self.settings = get_settings()
        
        self.logger.info(
            f"Agent initialized",
            agent_type=self.agent_type.value,
            max_concurrent_tasks=config.max_concurrent_tasks,
        )
    
    @abstractmethod
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """
        Process a task. Must be implemented by each agent.
        
        Args:
            task: The task to process.
            
        Returns:
            AgentResponse: The result of processing the task.
        """
        pass
    
    @abstractmethod
    def get_operation_handler(self, operation: str) -> Optional[callable]:
        """
        Get the handler function for a specific operation.
        
        Args:
            operation: The operation name.
            
        Returns:
            callable: The handler function or None if not found.
        """
        pass
    
    async def start(self) -> None:
        """Start the agent and begin processing tasks."""
        if self.running:
            self.logger.warning("Agent is already running")
            return
        
        self.running = True
        self.health_status = HealthStatus.HEALTHY
        
        self.logger.info("Agent started")
        
        # Start background tasks
        asyncio.create_task(self._task_processor())
        asyncio.create_task(self._health_monitor())
    
    async def stop(self) -> None:
        """Stop the agent gracefully."""
        if not self.running:
            self.logger.warning("Agent is not running")
            return
        
        self.running = False
        
        # Wait for active tasks to complete (with timeout)
        if self.active_tasks:
            self.logger.info(f"Waiting for {len(self.active_tasks)} active tasks to complete")
            
            timeout = 30  # seconds
            start_time = time.time()
            
            while self.active_tasks and (time.time() - start_time) < timeout:
                await asyncio.sleep(1)
            
            if self.active_tasks:
                self.logger.warning(f"Force stopping with {len(self.active_tasks)} active tasks")
        
        self.health_status = HealthStatus.OFFLINE
        self.logger.info("Agent stopped")
    
    async def submit_task(self, task: AgentTask) -> None:
        """
        Submit a task for processing.
        
        Args:
            task: The task to submit.
        """
        if not self.running:
            raise RuntimeError("Agent is not running")
        
        await self.task_queue.put(task)
        
        self.logger.info(
            "Task submitted",
            task_id=task.id,
            operation=task.operation,
            priority=task.priority.value,
        )
    
    async def _task_processor(self) -> None:
        """Background task processor."""
        while self.running:
            try:
                # Get task from queue with timeout
                try:
                    task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Check if we can handle more tasks
                if len(self.active_tasks) >= self.config.max_concurrent_tasks:
                    # Put task back and wait
                    await self.task_queue.put(task)
                    await asyncio.sleep(0.1)
                    continue
                
                # Process task in background
                asyncio.create_task(self._execute_task(task))
                
            except Exception as e:
                self.logger.error(f"Error in task processor: {e}")
                await asyncio.sleep(1)
    
    async def _execute_task(self, task: AgentTask) -> None:
        """
        Execute a single task with error handling and metrics.
        
        Args:
            task: The task to execute.
        """
        task_logger = TaskLogger(task.id, task.operation, self.agent_id)
        start_time = time.time()
        
        try:
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.utcnow()
            self.active_tasks[task.id] = task
            
            task_logger.start(
                operation=task.operation,
                priority=task.priority.value,
                correlation_id=task.correlation_id,
            )
            
            # Validate task
            await self._validate_task(task)
            
            # Execute with timeout
            response = await asyncio.wait_for(
                self.process_task(task),
                timeout=task.timeout_seconds
            )
            
            # Update metrics
            execution_time = int((time.time() - start_time) * 1000)
            await self._update_performance_metrics(execution_time, success=True)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
            task_logger.complete(
                execution_time_ms=execution_time,
                success=response.success,
            )
            
        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error_message = "Task timeout"
            
            self.logger.error(
                f"Task timeout after {task.timeout_seconds}s",
                task_id=task.id,
                operation=task.operation,
            )
            
            await self._handle_task_retry(task)
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            
            execution_time = int((time.time() - start_time) * 1000)
            await self._update_performance_metrics(execution_time, success=False)
            
            self.logger.error(
                f"Task execution failed: {e}",
                task_id=task.id,
                operation=task.operation,
                error=str(e),
            )
            
            await self._handle_task_retry(task)
            
        finally:
            # Remove from active tasks
            self.active_tasks.pop(task.id, None)
    
    async def _validate_task(self, task: AgentTask) -> None:
        """
        Validate a task before processing.
        
        Args:
            task: The task to validate.
            
        Raises:
            ValueError: If the task is invalid.
        """
        if not task.operation:
            raise ValueError("Task operation is required")
        
        if task.agent_type != self.agent_type:
            raise ValueError(f"Task is for {task.agent_type.value}, but this is {self.agent_type.value}")
        
        handler = self.get_operation_handler(task.operation)
        if not handler:
            raise ValueError(f"Unknown operation: {task.operation}")
    
    async def _handle_task_retry(self, task: AgentTask) -> None:
        """
        Handle task retry logic.
        
        Args:
            task: The failed task.
        """
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.RETRY
            
            # Schedule retry with exponential backoff
            delay = self.config.retry_delay_seconds * (2 ** (task.retry_count - 1))
            
            self.logger.info(
                f"Scheduling task retry {task.retry_count}/{task.max_retries}",
                task_id=task.id,
                delay_seconds=delay,
            )
            
            # Schedule retry
            asyncio.create_task(self._schedule_retry(task, delay))
        else:
            self.logger.error(
                f"Task failed after {task.max_retries} retries",
                task_id=task.id,
                operation=task.operation,
            )
    
    async def _schedule_retry(self, task: AgentTask, delay_seconds: int) -> None:
        """
        Schedule a task retry after a delay.
        
        Args:
            task: The task to retry.
            delay_seconds: Delay before retry.
        """
        await asyncio.sleep(delay_seconds)
        
        if self.running:
            task.status = TaskStatus.PENDING
            await self.task_queue.put(task)
    
    async def _update_performance_metrics(self, execution_time_ms: int, success: bool) -> None:
        """
        Update performance metrics.
        
        Args:
            execution_time_ms: Execution time in milliseconds.
            success: Whether the task was successful.
        """
        metrics = self.performance_metrics
        
        metrics.tasks_processed += 1
        metrics.last_activity = datetime.utcnow()
        metrics.last_execution_time_ms = execution_time_ms
        
        if success:
            metrics.tasks_successful += 1
            metrics.consecutive_failures = 0
        else:
            metrics.tasks_failed += 1
            metrics.consecutive_failures += 1
            metrics.last_error_timestamp = datetime.utcnow()
        
        # Update average execution time
        metrics.total_execution_time_ms += execution_time_ms
        metrics.average_execution_time_ms = (
            metrics.total_execution_time_ms / metrics.tasks_processed
        )
        
        # Update health status based on consecutive failures
        if metrics.consecutive_failures >= 5:
            self.health_status = HealthStatus.UNHEALTHY
        elif metrics.consecutive_failures >= 3:
            self.health_status = HealthStatus.DEGRADED
        else:
            self.health_status = HealthStatus.HEALTHY
    
    async def _health_monitor(self) -> None:
        """Background health monitoring."""
        while self.running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.config.health_check_interval)
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")
                await asyncio.sleep(self.config.health_check_interval)
    
    async def _perform_health_check(self) -> None:
        """Perform health check and update status."""
        self.last_health_check = datetime.utcnow()
        
        # Check memory usage (if configured)
        if self.config.max_memory_mb:
            # This would integrate with actual memory monitoring
            pass
        
        # Check task queue size
        queue_size = self.task_queue.qsize()
        if queue_size > 100:  # Configurable threshold
            self.logger.warning(f"High task queue size: {queue_size}")
            if self.health_status == HealthStatus.HEALTHY:
                self.health_status = HealthStatus.DEGRADED
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get current health status and metrics.
        
        Returns:
            dict: Health status information.
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "status": self.health_status.value,
            "running": self.running,
            "last_health_check": self.last_health_check.isoformat(),
            "active_tasks": len(self.active_tasks),
            "queue_size": self.task_queue.qsize(),
            "performance_metrics": self.performance_metrics.dict(),
        }
    
    def create_error_response(self, task_id: str, error_message: str) -> AgentResponse:
        """
        Create a standardized error response.
        
        Args:
            task_id: ID of the failed task.
            error_message: Error message.
            
        Returns:
            AgentResponse: Error response.
        """
        return AgentResponse(
            task_id=task_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            success=False,
            errors=[error_message],
        )