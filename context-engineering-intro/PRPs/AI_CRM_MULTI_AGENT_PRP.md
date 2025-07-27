name: "AI-Powered CRM Multi-Agent System Implementation PRP"
description: |
  Complete implementation plan for an AI-powered CRM system designed for pre-settlement funding business
  with 20+ specialized agents, Pipedrive integration, and comprehensive workflow automation.

## Purpose
Build a sophisticated multi-agent CRM system that transforms the pre-settlement funding business from manual 
lead processing to fully automated AI-driven workflows, integrating seamlessly with existing Pipedrive CRM.

## Core Principles
1. **Multi-Agent Architecture**: 20+ specialized agents handle distinct business functions
2. **Pipedrive Integration**: Bidirectional sync maintains workflow continuity
3. **AI-First Approach**: Document processing, risk assessment, and content generation powered by AI
4. **User-Friendly Interface**: Dedicated UI that works seamlessly with agent architecture
5. **Global Rules**: Follow all standards in CLAUDE.md for code quality and testing

---

## Goal
Implement a complete AI-powered CRM system that automates the lead-to-contract lifecycle for pre-settlement 
funding businesses through sophisticated multi-agent architecture, reducing manual data entry and accelerating 
the process from initial inquiry to signed funding agreement.

## Why
- **Efficiency Revolution**: Transform manual lead intake into automated AI-powered processing
- **Risk Mitigation**: AI-powered risk assessment and underwriting assistance for better decisions
- **Operational Excellence**: Reduce processing time from days to hours through agent automation
- **Scalability**: Multi-agent architecture allows independent scaling of business functions
- **Integration Continuity**: Seamless Pipedrive sync maintains existing workflow investments
- **Competitive Advantage**: Advanced AI capabilities differentiate from traditional CRM solutions

## What
A comprehensive CRM system featuring:
- 20+ specialized AI agents collaborating on distinct business functions
- Real-time bidirectional Pipedrive CRM synchronization
- AI-powered document intelligence and text extraction
- Automated risk assessment and underwriting assistance
- Multi-channel communication management (email, SMS, notifications)
- Contract generation and management with electronic signatures
- Comprehensive audit trail and compliance tracking
- Dedicated user interface optimized for pre-settlement funding workflows

### Success Criteria
- [ ] All 20+ agents operational and communicating effectively
- [ ] Complete lead intake automation with 95%+ accuracy
- [ ] Real-time Pipedrive synchronization with <30 second latency
- [ ] Document processing with 90%+ data extraction accuracy
- [ ] Automated risk assessment providing actionable insights
- [ ] Multi-channel communication system with full audit trail
- [ ] Contract generation reducing manual work by 80%
- [ ] User interface supporting all agent workflows
- [ ] System handling 1000+ leads per day without performance degradation
- [ ] Complete compliance and audit logging for regulatory requirements

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Core integration and framework documentation
- url: https://developers.pipedrive.com/docs/api/v1
  why: Primary CRM integration - deals, contacts, organizations, activities
  critical: Rate limiting (100 req/10sec), webhook setup, field mapping
  
- url: https://pipedrive.readme.io/docs/getting-started
  why: Authentication, webhook configuration, API best practices
  
- url: https://fastapi.tiangolo.com/
  why: Async web framework for agent coordination and API endpoints
  critical: Dependency injection, async/await patterns, middleware setup
  
- url: https://docs.celeryq.dev/en/stable/
  why: Background task processing for long-running agent operations
  critical: Task routing, error handling, result backends
  
- url: https://www.rabbitmq.com/docs
  why: Message broker for agent communication and task queuing
  critical: Queue durability, message acknowledgment patterns
  
- url: https://docs.pydantic.dev/latest/
  why: Data validation and serialization across all agents
  critical: V2 syntax changes, custom validators, field defaults
  
- url: https://docs.pydantic.dev/latest/api/base_model/
  why: Base model patterns for consistent data structures
  
- url: https://docs.agno.com/introduction
  why: Multi-agent framework for agent coordination and communication
  critical: Agent lifecycle, inter-agent messaging, error propagation
  
- url: https://platform.openai.com/docs/overview
  why: Primary AI service for document processing and content generation
  critical: Rate limits, token management, model selection
  
- url: https://docs.anthropic.com/claude
  why: Alternative AI service for complex reasoning and analysis
  
- file: context-engineering-intro/INITIAL.md
  why: Complete agent specifications and business requirements
  
- file: context-engineering-intro/CLAUDE.md
  why: Development standards, testing requirements, code patterns
  
- file: context-engineering-intro/examples/pics/
  why: UI mockups and design references for frontend development
```

### Current Codebase Tree
```bash
roncrm1/
├── context-engineering-intro/
│   ├── INITIAL.md                    # Complete feature specification
│   ├── CLAUDE.md                     # Development guidelines
│   ├── PRPs/                         # Planning documents
│   │   └── templates/                # PRP templates
│   ├── examples/                     # UI mockups and samples
│   │   └── pics/                     # Frontend design files
│   │       ├── dashboard.png
│   │       ├── add_law_firm.png
│   │       ├── new_case.png
│   │       ├── plantiffs.png
│   │       └── docs_center.png
│   └── use-cases/                    # Implementation examples
└── (new implementation starts here)
```

### Desired Codebase Tree
```bash
roncrm1/
├── src/
│   ├── agents/                       # Multi-agent architecture core
│   │   ├── __init__.py
│   │   ├── base/                     # Base agent classes and utilities
│   │   │   ├── agent.py             # BaseAgent class with common functionality
│   │   │   ├── communication.py     # Inter-agent messaging protocols
│   │   │   └── registry.py          # Agent discovery and lifecycle management
│   │   ├── lead_intake/             # Lead Intake Coordinator Agent
│   │   │   ├── agent.py
│   │   │   ├── parsers.py           # Email/form parsing logic
│   │   │   └── validators.py        # Lead data validation
│   │   ├── plaintiff_management/    # Plaintiff Management Agent
│   │   │   ├── agent.py
│   │   │   ├── crud.py              # CRUD operations
│   │   │   └── tracking.py          # Status and history tracking
│   │   ├── law_firm_management/     # Law Firm Management Agent
│   │   │   ├── agent.py
│   │   │   ├── bulk_operations.py   # Bulk plaintiff operations
│   │   │   └── preferences.py       # Firm-specific settings
│   │   ├── lawyer_management/       # Lawyer Management Agent
│   │   │   ├── agent.py
│   │   │   ├── assignments.py       # Case assignment logic
│   │   │   └── performance.py       # Performance tracking
│   │   ├── pipedrive_sync/          # Pipedrive Synchronization Agent
│   │   │   ├── agent.py
│   │   │   ├── mapping.py           # Data mapping between systems
│   │   │   └── webhooks.py          # Webhook handling
│   │   ├── pipedrive_migration/     # Pipedrive Migration Agent
│   │   │   ├── agent.py
│   │   │   ├── migrator.py          # Data migration logic
│   │   │   └── validation.py        # Migration validation
│   │   ├── text_extraction/         # Text Extraction Agent
│   │   │   ├── agent.py
│   │   │   ├── ocr.py               # OCR processing
│   │   │   └── parsers.py           # Document parsing
│   │   ├── content_generation/      # Content Generation Agent
│   │   │   ├── agent.py
│   │   │   ├── templates.py         # Email/document templates
│   │   │   └── personalization.py   # Content personalization
│   │   ├── classification/          # Classification Agent
│   │   │   ├── agent.py
│   │   │   ├── models.py            # ML classification models
│   │   │   └── routing.py           # Content routing logic
│   │   ├── risk_assessment/         # Risk Assessment Agent
│   │   │   ├── agent.py
│   │   │   ├── scoring.py           # Risk scoring algorithms
│   │   │   └── analysis.py          # Case analysis
│   │   ├── document_intelligence/   # Document Intelligence Agent
│   │   │   ├── agent.py
│   │   │   ├── extractors.py        # Data extraction
│   │   │   └── analyzers.py         # Document analysis
│   │   ├── communication/           # Communication agents
│   │   │   ├── email_service/
│   │   │   │   ├── agent.py
│   │   │   │   ├── sender.py        # Email sending logic
│   │   │   │   └── tracking.py      # Email tracking
│   │   │   ├── sms_service/
│   │   │   │   ├── agent.py
│   │   │   │   ├── sender.py        # SMS sending logic
│   │   │   │   └── compliance.py    # SMS compliance
│   │   │   └── notification_service/
│   │   │       ├── agent.py
│   │   │       ├── channels.py      # Multi-channel notifications
│   │   │       └── preferences.py   # User notification preferences
│   │   ├── data_management/         # Data management agents
│   │   │   ├── database_coordinator/
│   │   │   │   ├── agent.py
│   │   │   │   ├── operations.py    # Database operations
│   │   │   │   └── migrations.py    # Schema migrations
│   │   │   ├── file_storage/
│   │   │   │   ├── agent.py
│   │   │   │   ├── storage.py       # File storage operations
│   │   │   │   └── security.py      # Access control
│   │   │   ├── audit_logging/
│   │   │   │   ├── agent.py
│   │   │   │   ├── logger.py        # Audit logging
│   │   │   │   └── compliance.py    # Compliance reporting
│   │   │   └── data_validation/
│   │   │       ├── agent.py
│   │   │       ├── validators.py    # Data integrity checks
│   │   │       └── consistency.py   # Cross-system consistency
│   │   ├── business_logic/          # Business-specific agents
│   │   │   ├── underwriting_assistant/
│   │   │   │   ├── agent.py
│   │   │   │   ├── insights.py      # Data insights
│   │   │   │   └── recommendations.py # Funding recommendations
│   │   │   ├── contract_management/
│   │   │   │   ├── agent.py
│   │   │   │   ├── generator.py     # Contract generation
│   │   │   │   └── lifecycle.py     # Contract lifecycle
│   │   │   ├── reporting_analytics/
│   │   │   │   ├── agent.py
│   │   │   │   ├── reports.py       # Report generation
│   │   │   │   └── analytics.py     # Predictive analytics
│   │   │   └── case_status_manager/
│   │   │       ├── agent.py
│   │   │       ├── tracker.py       # Status tracking
│   │   │       └── automation.py    # Status automation
│   │   └── operations/              # Operational agents
│   │       ├── operations_supervisor/
│   │       │   ├── agent.py
│   │       │   ├── monitoring.py    # Agent monitoring
│   │       │   └── health.py        # System health checks
│   │       └── quality_assurance/
│   │           ├── agent.py
│   │           ├── validators.py    # Output validation
│   │           └── quality_metrics.py # Quality scoring
│   ├── api/                         # FastAPI application
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app initialization
│   │   ├── routes/                  # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── plaintiffs.py        # Plaintiff endpoints
│   │   │   ├── law_firms.py         # Law firm endpoints
│   │   │   ├── lawyers.py           # Lawyer endpoints
│   │   │   ├── documents.py         # Document endpoints
│   │   │   ├── communications.py    # Communication endpoints
│   │   │   ├── analytics.py         # Analytics endpoints
│   │   │   └── system.py            # System/health endpoints
│   │   ├── middleware/              # Request/response middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # Authentication middleware
│   │   │   ├── cors.py              # CORS configuration
│   │   │   ├── logging.py           # Request logging
│   │   │   └── rate_limiting.py     # Rate limiting
│   │   └── dependencies/            # Dependency injection
│   │       ├── __init__.py
│   │       ├── database.py          # Database session management
│   │       ├── auth.py              # Authentication dependencies
│   │       └── agents.py            # Agent access dependencies
│   ├── models/                      # Data models
│   │   ├── __init__.py
│   │   ├── database/                # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # Base model class
│   │   │   ├── plaintiff.py         # Plaintiff model
│   │   │   ├── law_firm.py          # Law firm model
│   │   │   ├── lawyer.py            # Lawyer model
│   │   │   ├── case.py              # Case model
│   │   │   ├── document.py          # Document model
│   │   │   ├── communication.py     # Communication model
│   │   │   ├── contract.py          # Contract model
│   │   │   └── audit_log.py         # Audit log model
│   │   └── schemas/                 # Pydantic schemas
│   │       ├── __init__.py
│   │       ├── plaintiff.py         # Plaintiff schemas
│   │       ├── law_firm.py          # Law firm schemas
│   │       ├── lawyer.py            # Lawyer schemas
│   │       ├── case.py              # Case schemas
│   │       ├── document.py          # Document schemas
│   │       ├── communication.py     # Communication schemas
│   │       ├── contract.py          # Contract schemas
│   │       └── common.py            # Common/shared schemas
│   ├── services/                    # Business logic layer
│   │   ├── __init__.py
│   │   ├── pipedrive/               # Pipedrive integration services
│   │   │   ├── __init__.py
│   │   │   ├── client.py            # Pipedrive API client
│   │   │   ├── sync.py              # Synchronization logic
│   │   │   └── webhook_handler.py   # Webhook processing
│   │   ├── ai/                      # AI service integrations
│   │   │   ├── __init__.py
│   │   │   ├── openai_client.py     # OpenAI integration
│   │   │   ├── anthropic_client.py  # Claude integration
│   │   │   └── model_router.py      # AI model routing
│   │   ├── storage/                 # File storage services
│   │   │   ├── __init__.py
│   │   │   ├── file_manager.py      # File management
│   │   │   └── security.py          # Storage security
│   │   └── notification/            # Notification services
│   │       ├── __init__.py
│   │       ├── email.py             # Email service
│   │       ├── sms.py               # SMS service
│   │       └── push.py              # Push notifications
│   ├── utils/                       # Shared utilities
│   │   ├── __init__.py
│   │   ├── logging.py               # Logging configuration
│   │   ├── encryption.py            # Data encryption utilities
│   │   ├── validators.py            # Custom validators
│   │   ├── formatters.py            # Data formatting utilities
│   │   └── exceptions.py            # Custom exceptions
│   ├── config/                      # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py              # Application settings
│   │   ├── database.py              # Database configuration
│   │   └── logging.py               # Logging configuration
│   └── worker/                      # Celery worker configuration
│       ├── __init__.py
│       ├── celery_app.py            # Celery application
│       ├── tasks.py                 # Background tasks
│       └── routing.py               # Task routing
├── frontend/                        # Frontend application
│   ├── src/
│   │   ├── components/              # React/Vue components
│   │   │   ├── Dashboard/           # Main dashboard
│   │   │   ├── Plaintiffs/          # Plaintiff management
│   │   │   ├── LawFirms/            # Law firm management
│   │   │   ├── Documents/           # Document management
│   │   │   ├── Communications/      # Communication center
│   │   │   ├── Analytics/           # Analytics dashboard
│   │   │   └── Common/              # Shared components
│   │   ├── services/                # Frontend services
│   │   ├── utils/                   # Frontend utilities
│   │   └── assets/                  # Static assets
│   ├── package.json
│   └── vite.config.js
├── tests/                           # Comprehensive test suite
│   ├── unit/                        # Unit tests
│   │   ├── agents/                  # Agent unit tests
│   │   ├── api/                     # API unit tests
│   │   ├── models/                  # Model unit tests
│   │   └── services/                # Service unit tests
│   ├── integration/                 # Integration tests
│   │   ├── agent_workflows/         # Multi-agent workflow tests
│   │   ├── pipedrive_sync/          # Pipedrive integration tests
│   │   └── end_to_end/              # Complete workflow tests
│   ├── fixtures/                    # Test data fixtures
│   ├── mocks/                       # Mock objects and services
│   └── conftest.py                  # Pytest configuration
├── migrations/                      # Database migrations
│   └── alembic/                     # Alembic migration files
├── docker/                          # Container configuration
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.dev.yml
├── docs/                            # Documentation
│   ├── api/                         # API documentation
│   ├── agents/                      # Agent documentation
│   └── deployment/                  # Deployment guides
├── requirements.txt                 # Python dependencies
├── pyproject.toml                   # Project configuration
├── .env.example                     # Environment variables template
└── README.md                        # Project overview
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: Pipedrive API rate limiting
# Maximum 100 requests per 10 seconds per company
# Must implement exponential backoff and request queuing
# Use aiohttp with ClientSession for connection pooling

# CRITICAL: Agno framework patterns
# Agents must be async and use proper context managers
# Inter-agent communication requires message serialization
# Agent lifecycle management critical for system stability

# CRITICAL: FastAPI async patterns
# All database operations must be async with asyncio
# Use dependency injection for database sessions
# Middleware must handle async context properly

# CRITICAL: Celery task management
# Task serialization must be JSON-compatible (no complex objects)
# Long-running tasks need progress tracking and cancellation
# Use result backends for task status monitoring

# CRITICAL: Pydantic v2 syntax changes
# Field() replaces ... for field definitions
# Validator decorators syntax changed from v1
# ConfigDict replaces Config class

# CRITICAL: Multi-agent coordination
# Avoid circular dependencies between agents
# Implement proper error propagation across agent boundaries
# Use message queues for loose coupling between agents

# CRITICAL: Database transaction boundaries
# Each agent operation should be in separate transaction
# Use database connection pooling for performance
# Implement proper rollback mechanisms for failed operations
```

## Implementation Blueprint

### Data Models and Structure

Core business entities with comprehensive validation and relationships:

```python
# Core business entities
class Plaintiff(BaseModel):
    """Central entity representing funding recipients"""
    id: UUID = Field(default_factory=uuid4)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(regex=r'^\+?[\d\s\-\(\)]+$')
    case_type: CaseType
    case_status: CaseStatus = CaseStatus.INITIAL
    law_firm_id: Optional[UUID]
    lawyer_id: Optional[UUID]
    pipedrive_person_id: Optional[int]
    financial_info: Optional[FinancialInfo]
    risk_score: Optional[float] = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LawFirm(BaseModel):
    """Law firm entity with bulk operation capabilities"""
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1, max_length=200)
    contact_email: EmailStr
    contact_phone: Optional[str]
    address: Optional[Address]
    preferences: FirmPreferences = Field(default_factory=FirmPreferences)
    pipedrive_org_id: Optional[int]
    lawyers: List[Lawyer] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AgentTask(BaseModel):
    """Standardized task format for inter-agent communication"""
    id: UUID = Field(default_factory=uuid4)
    agent_type: AgentType
    operation: str
    priority: TaskPriority = TaskPriority.NORMAL
    payload: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime]
    completed_at: Optional[datetime]

class AgentResponse(BaseModel):
    """Standardized response format from agents"""
    task_id: UUID
    agent_id: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    execution_time_ms: Optional[int]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

### List of Tasks (Implementation Order)

```yaml
Task 1: Foundation and Project Setup
CREATE project structure with proper Python packaging
SETUP virtual environment with uv or poetry
CONFIGURE development tools (ruff, mypy, black, pytest)
IMPLEMENT configuration management with Pydantic settings
CREATE database setup with SQLAlchemy and Alembic migrations
SETUP logging configuration with structured logging

Task 2: Core Data Models and Database Layer
CREATE SQLAlchemy ORM models for all entities
IMPLEMENT Pydantic schemas with comprehensive validation
SETUP database migrations with Alembic
CREATE database utility functions and connection pooling
IMPLEMENT audit logging at database level
CREATE data seeding scripts for development

Task 3: Agent Framework Foundation
SETUP Agno framework integration
CREATE BaseAgent class with standardized interface
IMPLEMENT agent registry and discovery system
CREATE inter-agent communication protocols
SETUP agent task queue with Celery and RabbitMQ
IMPLEMENT agent lifecycle management and health monitoring

Task 4: Pipedrive Integration Layer
CREATE Pipedrive API client with rate limiting
IMPLEMENT authentication and webhook setup
CREATE bidirectional data mapping system
SETUP error handling and retry mechanisms
IMPLEMENT webhook processing for real-time sync
CREATE Pipedrive migration agent for data import

Task 5: Core Business Logic Agents
IMPLEMENT Lead Intake Coordinator Agent
CREATE Plaintiff Management Agent with CRUD operations
BUILD Law Firm Management Agent with bulk operations
DEVELOP Lawyer Management Agent with assignment logic
IMPLEMENT Case Status Manager Agent
CREATE Database Coordinator Agent for data operations

Task 6: Document Processing and AI Agents
CREATE Text Extraction Agent with OCR capabilities
IMPLEMENT Document Intelligence Agent for legal docs
BUILD Classification Agent for content routing
CREATE Content Generation Agent for personalized communications
IMPLEMENT Risk Assessment Agent for underwriting
SETUP Quality Assurance Agent for output validation

Task 7: Communication System
IMPLEMENT Email Service Agent with template system
CREATE SMS Service Agent with compliance tracking
BUILD Notification Service Agent for cross-channel messaging
SETUP communication audit and delivery tracking
IMPLEMENT preference management for notifications
CREATE communication template management

Task 8: Data Management and Storage Agents
CREATE File Storage Agent with security controls
IMPLEMENT Audit & Logging Agent for compliance
BUILD Data Validation Agent for integrity checks
SETUP secure file upload and access control
IMPLEMENT data retention and archival policies
CREATE backup and recovery mechanisms

Task 9: Advanced Business Logic Agents
CREATE Underwriting Assistant Agent with insights
IMPLEMENT Contract Management Agent with lifecycle tracking
BUILD Reporting & Analytics Agent with dashboards
SETUP Operations Supervisor Agent for monitoring
IMPLEMENT Pipedrive Synchronization Agent for real-time sync
CREATE data migration and validation workflows

Task 10: FastAPI Application Layer
CREATE FastAPI application with async endpoints
IMPLEMENT authentication and authorization middleware
SETUP API routing for all entity operations
CREATE request/response validation
IMPLEMENT rate limiting and security headers
SETUP API documentation with OpenAPI

Task 11: Frontend Application
CREATE React/Vue.js application structure
IMPLEMENT responsive design matching mockups
BUILD dashboard with real-time updates
CREATE entity management interfaces (plaintiffs, law firms, lawyers)
IMPLEMENT document upload and management
SETUP communication center with multi-channel support
CREATE analytics and reporting dashboards

Task 12: Integration and Workflow Testing
CREATE comprehensive unit tests for all agents
IMPLEMENT integration tests for multi-agent workflows
SETUP end-to-end testing for complete business processes
CREATE performance tests for high-load scenarios
IMPLEMENT security testing for data protection
SETUP automated testing pipeline with CI/CD

Task 13: Security and Compliance Implementation
IMPLEMENT data encryption for sensitive information
CREATE role-based access control system
SETUP audit logging for compliance requirements
IMPLEMENT data retention and privacy controls
CREATE security monitoring and alerting
SETUP vulnerability scanning and dependency management

Task 14: Deployment and Operations
CREATE Docker containers for all services
SETUP container orchestration with docker-compose
IMPLEMENT monitoring with health checks and metrics
CREATE deployment scripts and automation
SETUP log aggregation and analysis
IMPLEMENT backup and disaster recovery procedures
CREATE operational runbooks and documentation
```

### Per Task Pseudocode

```python
# Task 3: Agent Framework Foundation
class BaseAgent:
    """Foundation class for all CRM agents with standardized interface"""
    
    def __init__(self, agent_id: str, config: AgentConfig):
        self.agent_id = agent_id
        self.config = config
        self.task_queue = AsyncQueue()
        self.health_status = HealthStatus.HEALTHY
        self.performance_metrics = PerformanceMetrics()
    
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """
        PATTERN: Standardized task processing with comprehensive error handling
        CRITICAL: All agents must implement this interface for consistency
        """
        start_time = time.time()
        
        try:
            # PATTERN: Always validate task before processing
            validated_task = await self.validate_task(task)
            
            # PATTERN: Update task status and log start
            await self.update_task_status(task.id, TaskStatus.IN_PROGRESS)
            logger.info(f"Agent {self.agent_id} starting task {task.id}")
            
            # PATTERN: Route to specific handler based on operation
            handler = self.get_operation_handler(validated_task.operation)
            if not handler:
                raise ValueError(f"Unknown operation: {validated_task.operation}")
            
            # PATTERN: Execute with timeout and resource monitoring
            result = await asyncio.wait_for(
                handler(validated_task),
                timeout=self.config.task_timeout
            )
            
            # PATTERN: Standardized success response with metrics
            execution_time = int((time.time() - start_time) * 1000)
            await self.update_performance_metrics(execution_time, success=True)
            
            return AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                success=True,
                data=result,
                execution_time_ms=execution_time
            )
            
        except ValidationError as e:
            # PATTERN: Handle validation errors specifically
            logger.warning(f"Validation error in agent {self.agent_id}: {e}")
            return self.create_error_response(task.id, f"Validation failed: {e}")
            
        except asyncio.TimeoutError:
            # PATTERN: Handle timeouts with retry logic
            logger.error(f"Timeout in agent {self.agent_id} for task {task.id}")
            await self.schedule_retry(task)
            return self.create_error_response(task.id, "Task timeout - scheduled for retry")
            
        except Exception as e:
            # PATTERN: Comprehensive error logging with context
            logger.error(f"Unexpected error in agent {self.agent_id}: {e}", 
                        extra={"task_id": task.id, "agent_id": self.agent_id})
            await self.update_performance_metrics(0, success=False)
            return self.create_error_response(task.id, f"Internal error: {str(e)}")

# Task 4: Pipedrive Integration Layer
class PipedriveClient:
    """Rate-limited Pipedrive API client with comprehensive error handling"""
    
    def __init__(self, api_token: str, company_domain: str):
        self.api_token = api_token
        self.base_url = f"https://{company_domain}.pipedrive.com/api/v1"
        # CRITICAL: Pipedrive rate limit is 100 requests per 10 seconds
        self.rate_limiter = AsyncRateLimiter(max_calls=90, period=10)  # Buffer for safety
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=20)  # Connection pooling
        )
        self.retry_config = RetryConfig(max_attempts=3, backoff_factor=2)
    
    @retry(attempts=3, backoff=exponential_backoff)
    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        CRITICAL: Must respect Pipedrive rate limits to avoid API suspension
        PATTERN: Use rate limiter before every request, handle 429 responses
        """
        # PATTERN: Always acquire rate limit before request
        await self.rate_limiter.acquire()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        params = kwargs.get('params', {})
        params['api_token'] = self.api_token
        kwargs['params'] = params
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                # CRITICAL: Handle rate limiting with exponential backoff
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 10))
                    logger.warning(f"Rate limited, waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    raise RateLimitError("Pipedrive API rate limit exceeded")
                
                # PATTERN: Handle common HTTP errors
                if response.status == 401:
                    raise AuthenticationError("Invalid Pipedrive API token")
                elif response.status == 403:
                    raise AuthorizationError("Insufficient Pipedrive permissions")
                elif response.status >= 500:
                    raise ServiceUnavailableError("Pipedrive service unavailable")
                
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"Pipedrive API client error: {e}")
            raise ConnectionError(f"Failed to connect to Pipedrive: {e}")

# Task 5: Lead Intake Coordinator Agent
class LeadIntakeCoordinatorAgent(BaseAgent):
    """Manages complete lead intake process from submission to first contact"""
    
    async def process_lead_submission(self, task: AgentTask) -> Dict[str, Any]:
        """
        PATTERN: Complete lead processing workflow with validation and routing
        CRITICAL: Must handle various input formats (email, web form, API)
        """
        lead_data = task.payload.get('lead_data')
        source = task.payload.get('source', 'unknown')
        
        # PATTERN: Parse and extract structured data from lead
        if source == 'email':
            parsed_data = await self.parse_email_lead(lead_data)
        elif source == 'web_form':
            parsed_data = await self.parse_form_lead(lead_data)
        else:
            parsed_data = await self.parse_generic_lead(lead_data)
        
        # PATTERN: Validate and enrich lead data
        validated_lead = await self.validate_lead_data(parsed_data)
        enriched_lead = await self.enrich_lead_data(validated_lead)
        
        # PATTERN: Create plaintiff record
        plaintiff = await self.create_plaintiff_record(enriched_lead)
        
        # PATTERN: Route to appropriate agents for further processing
        await self.route_to_classification_agent(plaintiff.id, enriched_lead)
        await self.route_to_risk_assessment_agent(plaintiff.id, enriched_lead)
        
        # PATTERN: Sync with Pipedrive
        await self.sync_with_pipedrive(plaintiff.id, enriched_lead)
        
        # PATTERN: Trigger initial communication
        await self.trigger_initial_contact(plaintiff.id, enriched_lead)
        
        return {
            'plaintiff_id': str(plaintiff.id),
            'status': 'processed',
            'next_steps': ['risk_assessment', 'initial_contact', 'document_collection']
        }
```

### Integration Points
```yaml
DATABASE:
  - migrations: "Initial schema for all entities with proper relationships"
  - indexes: "Performance indexes for frequent queries (plaintiff status, firm lookups)"
  - constraints: "Foreign key constraints maintaining referential integrity"
  - audit: "Audit logging tables for compliance and tracking"
  
CONFIG:
  - settings: src/config/settings.py with Pydantic BaseSettings
  - env_vars: All secrets via environment variables (API keys, database URLs)
  - agent_config: Individual agent configurations with timeouts and retries
  - pipedrive_config: API tokens, webhook URLs, field mappings
  
ROUTES:
  - api_structure: RESTful endpoints following OpenAPI 3.0 standards
  - authentication: JWT token-based auth for all endpoints
  - rate_limiting: Per-endpoint rate limiting to prevent abuse
  - validation: Request/response validation with Pydantic models
  
AGENTS:
  - registry: Central agent registry for discovery and health monitoring
  - communication: Message queue system with proper error handling
  - coordination: Workflow orchestration for multi-agent processes
  - monitoring: Performance metrics and health checks for all agents
  
EXTERNAL_INTEGRATIONS:
  - pipedrive: Bidirectional sync with webhook processing
  - ai_services: OpenAI, Claude for document processing and generation
  - email_service: SMTP/SendGrid for email communications
  - sms_service: Twilio for SMS messaging with compliance
  - storage: Secure file storage with encryption and access control
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
ruff check src/ --fix              # Auto-fix code style issues
ruff format src/                   # Format code consistently
mypy src/                          # Type checking across all modules
pytest --collect-only tests/       # Verify test discovery

# Expected: No errors. If errors exist, read carefully and fix root causes.
# Pay special attention to async/await patterns and Pydantic v2 syntax
```

### Level 2: Unit Tests
```python
# CREATE comprehensive test suite for each agent and component
def test_lead_intake_agent_email_parsing():
    """Test lead intake agent can parse email submissions correctly"""
    agent = LeadIntakeCoordinatorAgent("test_agent", test_config)
    email_data = {
        "subject": "Personal Injury Case - John Doe",
        "body": "Client details: John Doe, john@email.com, car accident",
        "attachments": []
    }
    task = AgentTask(
        agent_type=AgentType.LEAD_INTAKE,
        operation="process_lead_submission",
        payload={"lead_data": email_data, "source": "email"}
    )
    
    response = await agent.process_task(task)
    
    assert response.success is True
    assert "plaintiff_id" in response.data
    assert response.data["status"] == "processed"

def test_pipedrive_client_rate_limiting():
    """Test Pipedrive client respects rate limits"""
    client = PipedriveClient("test_token", "test_company")
    
    # Simulate rapid requests
    start_time = time.time()
    tasks = [client.make_request("GET", "/persons") for _ in range(10)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    elapsed = time.time() - start_time
    
    # Should take at least 1 second due to rate limiting
    assert elapsed >= 1.0
    assert all(not isinstance(r, RateLimitError) for r in results)

def test_agent_error_handling():
    """Test agent handles errors gracefully with proper retry logic"""
    agent = TestAgent("test_agent", test_config)
    
    # Simulate failing task
    task = AgentTask(
        agent_type=AgentType.TEST,
        operation="failing_operation",
        payload={"should_fail": True}
    )
    
    response = await agent.process_task(task)
    
    assert response.success is False
    assert len(response.errors) > 0
    assert "Internal error" in response.errors[0]

def test_multi_agent_workflow():
    """Test complete workflow involving multiple agents"""
    # Test lead intake -> risk assessment -> communication workflow
    lead_data = create_test_lead_data()
    
    # Process through lead intake
    intake_response = await lead_intake_agent.process_lead_submission(lead_data)
    assert intake_response.success
    
    # Verify risk assessment was triggered
    risk_tasks = await get_pending_tasks(AgentType.RISK_ASSESSMENT)
    assert len(risk_tasks) > 0
    
    # Process risk assessment
    risk_response = await risk_agent.process_task(risk_tasks[0])
    assert risk_response.success
    
    # Verify communication was triggered
    comm_tasks = await get_pending_tasks(AgentType.EMAIL_SERVICE)
    assert len(comm_tasks) > 0
```

```bash
# Run comprehensive testing with coverage
uv run pytest tests/ -v --cov=src --cov-report=html --cov-min=85
# Coverage should be >85% for core business logic
# Integration tests should cover all agent workflows
# Performance tests should validate system under load
```

### Level 3: Integration Testing
```bash
# Start all required services
docker-compose up -d postgres rabbitmq redis
export DATABASE_URL="postgresql://test:test@localhost:5432/test_crm"
export CELERY_BROKER_URL="amqp://localhost:5672"

# Start the application in test mode
uv run python -m src.main --env=test

# Test complete lead processing workflow
curl -X POST http://localhost:8000/api/v1/leads \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TEST_JWT_TOKEN" \
  -d '{
    "lead_data": {
      "first_name": "John",
      "last_name": "Doe", 
      "email": "john.doe@email.com",
      "case_type": "personal_injury",
      "description": "Car accident case"
    },
    "source": "web_form"
  }'

# Expected response:
# {
#   "status": "success",
#   "plaintiff_id": "uuid-here",
#   "next_steps": ["risk_assessment", "initial_contact", "document_collection"],
#   "estimated_processing_time": "2-4 hours"
# }

# Test Pipedrive synchronization
curl -X GET http://localhost:8000/api/v1/plaintiffs/{plaintiff_id}/pipedrive-sync \
  -H "Authorization: Bearer $TEST_JWT_TOKEN"

# Expected: Pipedrive person/deal created and synced

# Test agent health and monitoring
curl -X GET http://localhost:8000/api/v1/system/agents/health \
  -H "Authorization: Bearer $TEST_JWT_TOKEN"

# Expected: All agents reporting healthy status
```

## Final Validation Checklist
- [ ] All unit tests pass: `uv run pytest tests/unit/ -v`
- [ ] All integration tests pass: `uv run pytest tests/integration/ -v`
- [ ] No linting errors: `uv run ruff check src/`
- [ ] No type errors: `uv run mypy src/`
- [ ] Code coverage >85%: `uv run pytest --cov=src --cov-min=85`
- [ ] All 20+ agents operational and communicating
- [ ] Pipedrive sync working bidirectionally with <30s latency
- [ ] Document processing achieving >90% accuracy
- [ ] Multi-agent workflows completing successfully
- [ ] API endpoints responding within SLA (<2s for standard operations)
- [ ] Security measures active: authentication, authorization, audit logging
- [ ] Performance acceptable under load (1000+ leads/day)
- [ ] Frontend interface fully functional with real-time updates
- [ ] Comprehensive documentation complete

---

## Anti-Patterns to Avoid
- ❌ Don't bypass Pipedrive rate limiting "just for testing" - always respect limits
- ❌ Don't create agents without proper error handling and retry logic
- ❌ Don't ignore agent task validation - always validate inputs and outputs
- ❌ Don't use synchronous database calls in async agent context
- ❌ Don't hardcode API tokens, database URLs, or sensitive configuration
- ❌ Don't create circular dependencies between agents - use event-driven communication
- ❌ Don't skip database transaction boundaries - each operation should be atomic
- ❌ Don't ignore webhook signature validation - always verify Pipedrive webhooks
- ❌ Don't mock external services in integration tests - use real test environments
- ❌ Don't deploy without comprehensive monitoring and alerting
- ❌ Don't skip data validation - validate at every system boundary
- ❌ Don't ignore performance implications of agent coordination overhead