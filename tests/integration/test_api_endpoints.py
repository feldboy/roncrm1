"""Integration tests for API endpoints."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.database.connection import get_db


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client with overridden dependencies."""
        app = create_app()
        
        # Override database dependency
        async def override_get_db():
            mock_session = AsyncMock()
            yield mock_session
        
        app.dependency_overrides[get_db] = override_get_db
        
        return TestClient(app)
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert "environment" in data
    
    def test_agent_status_endpoint_no_registry(self, client):
        """Test agent status endpoint when registry not available."""
        response = client.get("/agents/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"] == "Agent registry not available"
    
    @patch('src.api.app.AuthMiddleware')
    def test_login_endpoint(self, mock_auth_middleware, client):
        """Test login endpoint."""
        # Mock authentication
        mock_auth_middleware.return_value = Mock()
        
        login_data = {
            "username": "testuser",
            "password": "testpass"
        }
        
        with patch('src.api.routes.auth.authenticate_user') as mock_auth:
            with patch('src.api.routes.auth.create_access_token') as mock_token:
                mock_auth.return_value = {"id": 1, "username": "testuser"}
                mock_token.return_value = "fake-jwt-token"
                
                response = client.post("/api/v1/auth/login", json=login_data)
                
                # Should return token on successful authentication
                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert data["token_type"] == "bearer"


class TestPlaintiffEndpoints:
    """Test plaintiff endpoints."""
    
    @pytest.fixture
    def client_with_auth(self):
        """Create test client with authentication."""
        app = create_app()
        
        # Override database dependency
        async def override_get_db():
            mock_session = AsyncMock()
            yield mock_session
        
        app.dependency_overrides[get_db] = override_get_db
        
        client = TestClient(app)
        
        # Add authorization header
        client.headers = {"Authorization": "Bearer fake-jwt-token"}
        
        return client
    
    @patch('src.api.middleware.auth.AuthMiddleware.__call__')
    def test_create_plaintiff(self, mock_auth, client_with_auth):
        """Test creating a plaintiff."""
        mock_auth.return_value = Mock()
        
        plaintiff_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "case_type": "personal_injury"
        }
        
        with patch('src.api.routes.plaintiffs.create_plaintiff_service') as mock_service:
            mock_service.return_value = {"id": 1, **plaintiff_data}
            
            response = client_with_auth.post("/api/v1/plaintiffs/", json=plaintiff_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["first_name"] == "John"
            assert data["last_name"] == "Doe"
    
    @patch('src.api.middleware.auth.AuthMiddleware.__call__')
    def test_get_plaintiff(self, mock_auth, client_with_auth):
        """Test getting a plaintiff."""
        mock_auth.return_value = Mock()
        
        with patch('src.api.routes.plaintiffs.get_plaintiff_service') as mock_service:
            mock_service.return_value = {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com"
            }
            
            response = client_with_auth.get("/api/v1/plaintiffs/1")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["first_name"] == "John"
    
    @patch('src.api.middleware.auth.AuthMiddleware.__call__')
    def test_get_nonexistent_plaintiff(self, mock_auth, client_with_auth):
        """Test getting non-existent plaintiff."""
        mock_auth.return_value = Mock()
        
        with patch('src.api.routes.plaintiffs.get_plaintiff_service') as mock_service:
            mock_service.return_value = None
            
            response = client_with_auth.get("/api/v1/plaintiffs/999")
            
            assert response.status_code == 404


class TestCaseEndpoints:
    """Test case endpoints."""
    
    @pytest.fixture
    def client_with_auth(self):
        """Create authenticated test client."""
        app = create_app()
        
        async def override_get_db():
            mock_session = AsyncMock()
            yield mock_session
        
        app.dependency_overrides[get_db] = override_get_db
        
        client = TestClient(app)
        client.headers = {"Authorization": "Bearer fake-jwt-token"}
        
        return client
    
    @patch('src.api.middleware.auth.AuthMiddleware.__call__')
    def test_create_case(self, mock_auth, client_with_auth):
        """Test creating a case."""
        mock_auth.return_value = Mock()
        
        case_data = {
            "case_number": "CASE-2024-001",
            "case_type": "personal_injury",
            "status": "active",
            "plaintiff_id": 1,
            "settlement_amount_requested": 50000.00
        }
        
        with patch('src.api.routes.cases.create_case_service') as mock_service:
            mock_service.return_value = {"id": 1, **case_data}
            
            response = client_with_auth.post("/api/v1/cases/", json=case_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["case_number"] == "CASE-2024-001"
            assert data["case_type"] == "personal_injury"
    
    @patch('src.api.middleware.auth.AuthMiddleware.__call__')
    def test_update_case_status(self, mock_auth, client_with_auth):
        """Test updating case status."""
        mock_auth.return_value = Mock()
        
        status_update = {
            "status": "approved",
            "notes": "Case approved for funding"
        }
        
        with patch('src.api.routes.cases.update_case_status_service') as mock_service:
            mock_service.return_value = {
                "id": 1,
                "status": "approved",
                "notes": "Case approved for funding"
            }
            
            response = client_with_auth.patch("/api/v1/cases/1/status", json=status_update)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "approved"


class TestDocumentEndpoints:
    """Test document endpoints."""
    
    @pytest.fixture
    def client_with_auth(self):
        """Create authenticated test client."""
        app = create_app()
        
        async def override_get_db():
            mock_session = AsyncMock()
            yield mock_session
        
        app.dependency_overrides[get_db] = override_get_db
        
        client = TestClient(app)
        client.headers = {"Authorization": "Bearer fake-jwt-token"}
        
        return client
    
    @patch('src.api.middleware.auth.AuthMiddleware.__call__')
    def test_upload_document(self, mock_auth, client_with_auth):
        """Test document upload."""
        mock_auth.return_value = Mock()
        
        # Mock file upload
        files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
        data = {
            "case_id": "1",
            "document_type": "medical",
            "title": "Medical Records"
        }
        
        with patch('src.api.routes.documents.upload_document_service') as mock_service:
            mock_service.return_value = {
                "id": 1,
                "title": "Medical Records",
                "document_type": "medical",
                "file_path": "/documents/test.pdf"
            }
            
            response = client_with_auth.post(
                "/api/v1/documents/upload",
                files=files,
                data=data
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Medical Records"
            assert data["document_type"] == "medical"
    
    @patch('src.api.middleware.auth.AuthMiddleware.__call__')
    def test_get_document_analysis(self, mock_auth, client_with_auth):
        """Test getting document analysis."""
        mock_auth.return_value = Mock()
        
        with patch('src.api.routes.documents.get_document_analysis_service') as mock_service:
            mock_service.return_value = {
                "document_id": 1,
                "analysis": {
                    "risk_level": "low",
                    "key_findings": ["No major issues found"],
                    "confidence": 0.85
                }
            }
            
            response = client_with_auth.get("/api/v1/documents/1/analysis")
            
            assert response.status_code == 200
            data = response.json()
            assert data["analysis"]["risk_level"] == "low"
            assert "key_findings" in data["analysis"]


class TestAgentEndpoints:
    """Test agent management endpoints."""
    
    @pytest.fixture
    def client_with_auth(self):
        """Create authenticated test client."""
        app = create_app()
        
        async def override_get_db():
            mock_session = AsyncMock()
            yield mock_session
        
        app.dependency_overrides[get_db] = override_get_db
        
        client = TestClient(app)
        client.headers = {"Authorization": "Bearer fake-jwt-token"}
        
        return client
    
    @patch('src.api.middleware.auth.AuthMiddleware.__call__')
    def test_trigger_agent_action(self, mock_auth, client_with_auth):
        """Test triggering agent action."""
        mock_auth.return_value = Mock()
        
        action_data = {
            "action": "process_case",
            "case_id": 1,
            "priority": "high"
        }
        
        with patch('src.api.routes.agents.trigger_agent_action_service') as mock_service:
            mock_service.return_value = {
                "agent_id": "risk_assessment",
                "action": "process_case",
                "status": "queued",
                "message": "Action queued for processing"
            }
            
            response = client_with_auth.post(
                "/api/v1/agents/risk_assessment/actions",
                json=action_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "queued"
            assert data["action"] == "process_case"
    
    @patch('src.api.middleware.auth.AuthMiddleware.__call__')
    def test_get_agent_logs(self, mock_auth, client_with_auth):
        """Test getting agent logs."""
        mock_auth.return_value = Mock()
        
        with patch('src.api.routes.agents.get_agent_logs_service') as mock_service:
            mock_service.return_value = {
                "agent_id": "lead_intake",
                "logs": [
                    {
                        "timestamp": "2024-01-15T10:00:00Z",
                        "level": "INFO",
                        "message": "Processing new lead"
                    },
                    {
                        "timestamp": "2024-01-15T10:01:00Z",
                        "level": "SUCCESS",
                        "message": "Lead processed successfully"
                    }
                ]
            }
            
            response = client_with_auth.get("/api/v1/agents/lead_intake/logs")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["logs"]) == 2
            assert data["logs"][0]["level"] == "INFO"