"""Tests for OpenAI client service."""

import pytest
from unittest.mock import AsyncMock, patch, Mock

from src.services.ai.openai_client import OpenAIClient, OpenAIError


class TestOpenAIClient:
    """Test OpenAI client functionality."""
    
    @pytest.fixture
    def client(self):
        """Create OpenAI client for testing."""
        with patch('src.services.ai.openai_client.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            return OpenAIClient()
    
    @pytest.mark.asyncio
    async def test_analyze_document_success(self, client):
        """Test successful document analysis."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content='{"risk_level": "low", "key_findings": ["No major issues"]}'))
        ]
        
        with patch.object(client.client.chat.completions, 'create', return_value=mock_response):
            result = await client.analyze_document("Sample document text", "medical")
            
            assert "risk_level" in result
            assert "key_findings" in result
            assert result["risk_level"] == "low"
    
    @pytest.mark.asyncio
    async def test_analyze_document_api_error(self, client):
        """Test document analysis with API error."""
        with patch.object(client.client.chat.completions, 'create', side_effect=Exception("API Error")):
            with pytest.raises(OpenAIError):
                await client.analyze_document("Sample text", "medical")
    
    @pytest.mark.asyncio
    async def test_generate_risk_assessment_success(self, client):
        """Test successful risk assessment generation."""
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content='{"overall_risk": "medium", "factors": ["Factor 1"]}'))
        ]
        
        case_data = {
            "case_type": "personal_injury",
            "settlement_amount_requested": 50000,
            "attorney_name": "John Smith"
        }
        
        with patch.object(client.client.chat.completions, 'create', return_value=mock_response):
            result = await client.generate_risk_assessment(case_data, [])
            
            assert "overall_risk" in result
            assert result["overall_risk"] == "medium"
    
    @pytest.mark.asyncio
    async def test_generate_email_content_success(self, client):
        """Test email content generation."""
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="Subject: Test Email\n\nBody: This is a test email."))
        ]
        
        context = {
            "plaintiff_name": "John Doe",
            "case_number": "CASE-001"
        }
        
        with patch.object(client.client.chat.completions, 'create', return_value=mock_response):
            result = await client.generate_email_content("follow_up", context)
            
            assert "Subject:" in result
            assert "Body:" in result
    
    @pytest.mark.asyncio
    async def test_generate_sms_content_success(self, client):
        """Test SMS content generation."""
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="Your case CASE-001 has been updated."))
        ]
        
        context = {
            "plaintiff_name": "John Doe",
            "case_number": "CASE-001"
        }
        
        with patch.object(client.client.chat.completions, 'create', return_value=mock_response):
            result = await client.generate_sms_content("case_update", context)
            
            assert "CASE-001" in result
            assert len(result) <= 160  # SMS length limit
    
    @pytest.mark.asyncio
    async def test_extract_case_info_success(self, client):
        """Test case information extraction."""
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content='{"case_type": "personal_injury", "estimated_value": 50000}'))
        ]
        
        with patch.object(client.client.chat.completions, 'create', return_value=mock_response):
            result = await client.extract_case_info("Car accident on Main St")
            
            assert "case_type" in result
            assert result["case_type"] == "personal_injury"
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self, client):
        """Test retry mechanism on transient failures."""
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content='{"success": true}'))
        ]
        
        # Fail twice, then succeed
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Transient error")
            return mock_response
        
        with patch.object(client.client.chat.completions, 'create', side_effect=side_effect):
            result = await client.analyze_document("Test", "medical")
            assert result["success"] is True
            assert call_count == 3  # Failed twice, succeeded on third try
    
    def test_token_usage_tracking(self, client):
        """Test token usage tracking."""
        # Initial token count should be 0
        assert client.get_token_usage()["total_tokens"] == 0
        
        # Simulate token usage
        client._track_token_usage(100, 50)
        usage = client.get_token_usage()
        
        assert usage["prompt_tokens"] == 100
        assert usage["completion_tokens"] == 50
        assert usage["total_tokens"] == 150
    
    def test_reset_token_usage(self, client):
        """Test token usage reset."""
        client._track_token_usage(100, 50)
        client.reset_token_usage()
        
        usage = client.get_token_usage()
        assert usage["total_tokens"] == 0