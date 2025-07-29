"""Simple test configuration without complex dependencies."""

import asyncio
import os
import pytest
from unittest.mock import Mock, AsyncMock

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["OPENAI_API_KEY"] = "test-openai-key"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = Mock()
    settings.ENVIRONMENT = "test"
    settings.DATABASE_URL = "sqlite+aiosqlite:///./test.db"
    settings.SECRET_KEY = "test-secret-key"
    settings.API_HOST = "localhost"
    settings.API_PORT = 8000
    settings.ALLOWED_ORIGINS = ["http://localhost:3000"]
    settings.LOG_LEVEL = "INFO"
    settings.OPENAI_API_KEY = "test-openai-key"
    settings.PIPEDRIVE_API_TOKEN = "test-pipedrive-token"
    settings.PIPEDRIVE_BASE_URL = "https://api.pipedrive.com/v1"
    return settings


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    client = AsyncMock()
    client.chat.completions.create = AsyncMock()
    return client


@pytest.fixture
def sample_plaintiff_data():
    """Sample plaintiff data for testing."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "address": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "case_type": "personal_injury",
        "accident_date": "2024-01-15",
        "attorney_name": "Jane Smith",
        "law_firm_name": "Smith & Associates",
    }


@pytest.fixture
def sample_case_data():
    """Sample case data for testing."""
    return {
        "case_number": "CASE-2024-001",
        "case_type": "personal_injury",
        "status": "active",
        "accident_date": "2024-01-15",
        "settlement_amount_requested": 50000.00,
        "description": "Car accident case",
        "attorney_name": "Jane Smith",
        "law_firm_name": "Smith & Associates",
    }