"""Simple integration tests for agent workflows without complex dependencies."""

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestLeadIntakeWorkflow:
    """Test lead intake agent workflow."""
    
    @pytest.mark.asyncio
    async def test_lead_intake_agent_can_process_email(self):
        """Test that lead intake agent can process email leads."""
        with patch('src.agents.lead_intake.agent.OpenAIClient') as mock_openai:
            with patch('src.agents.lead_intake.agent.get_database_connection') as mock_db:
                # Mock OpenAI response
                mock_openai_instance = AsyncMock()
                mock_openai_instance.extract_case_info.return_value = {
                    "plaintiff_name": "John Doe",
                    "case_type": "personal_injury",
                    "estimated_value": 50000
                }
                mock_openai.return_value = mock_openai_instance
                
                # Mock database
                mock_db_instance = AsyncMock()
                mock_db.return_value = mock_db_instance
                
                from src.agents.lead_intake.agent import LeadIntakeAgent
                
                agent = LeadIntakeAgent()
                
                # Test processing email lead
                email_data = {
                    "subject": "New Personal Injury Case",
                    "body": "I was in a car accident and need funding",
                    "sender": "john.doe@example.com"
                }
                
                result = await agent.process_message("email_lead", email_data)
                
                assert result is not None
                assert "processed" in result or "status" in result
    
    @pytest.mark.asyncio
    async def test_lead_intake_agent_handles_invalid_data(self):
        """Test lead intake agent handles invalid data gracefully."""
        with patch('src.agents.lead_intake.agent.OpenAIClient'):
            with patch('src.agents.lead_intake.agent.get_database_connection'):
                from src.agents.lead_intake.agent import LeadIntakeAgent
                
                agent = LeadIntakeAgent()
                
                # Test with invalid data
                invalid_data = {"invalid": "data"}
                
                result = await agent.process_message("email_lead", invalid_data)
                
                # Should handle gracefully without crashing
                assert result is not None


class TestPipedriveSyncWorkflow:
    """Test Pipedrive sync agent workflow."""
    
    @pytest.mark.asyncio
    async def test_pipedrive_sync_agent_can_sync_person(self):
        """Test Pipedrive sync agent can sync person data."""
        with patch('src.agents.pipedrive_sync.agent.PipedriveClient') as mock_pipedrive:
            with patch('src.agents.pipedrive_sync.agent.get_database_connection') as mock_db:
                # Mock Pipedrive client
                mock_pipedrive_instance = AsyncMock()
                mock_pipedrive_instance.create_person.return_value = {"id": 123, "name": "John Doe"}
                mock_pipedrive.return_value = mock_pipedrive_instance
                
                # Mock database
                mock_db_instance = AsyncMock()
                mock_db.return_value = mock_db_instance
                
                from src.agents.pipedrive_sync.agent import PipedriveSyncAgent
                
                agent = PipedriveSyncAgent()
                
                # Test syncing person
                person_data = {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "phone": "+1234567890"
                }
                
                result = await agent.process_message("sync_person", person_data)
                
                assert result is not None
                mock_pipedrive_instance.create_person.assert_called_once()


class TestRiskAssessmentWorkflow:
    """Test risk assessment agent workflow."""
    
    @pytest.mark.asyncio
    async def test_risk_assessment_agent_can_assess_case(self):
        """Test risk assessment agent can assess case risk."""
        with patch('src.agents.risk_assessment.agent.OpenAIClient') as mock_openai:
            with patch('src.agents.risk_assessment.agent.get_database_connection') as mock_db:
                # Mock OpenAI response
                mock_openai_instance = AsyncMock()
                mock_openai_instance.generate_risk_assessment.return_value = {
                    "overall_risk": "medium",
                    "risk_factors": ["Limited documentation"],
                    "risk_score": 65,
                    "recommendations": ["Request additional medical records"]
                }
                mock_openai.return_value = mock_openai_instance
                
                # Mock database
                mock_db_instance = AsyncMock()
                mock_db.return_value = mock_db_instance
                
                from src.agents.risk_assessment.agent import RiskAssessmentAgent
                
                agent = RiskAssessmentAgent()
                
                # Test case assessment
                case_data = {
                    "case_id": 1,
                    "case_type": "personal_injury",
                    "settlement_amount_requested": 50000,
                    "documents": []
                }
                
                result = await agent.process_message("assess_case", case_data)
                
                assert result is not None
                mock_openai_instance.generate_risk_assessment.assert_called_once()


class TestDocumentIntelligenceWorkflow:
    """Test document intelligence agent workflow."""
    
    @pytest.mark.asyncio
    async def test_document_intelligence_agent_can_analyze_document(self):
        """Test document intelligence agent can analyze documents."""
        with patch('src.agents.document_intelligence.agent.OpenAIClient') as mock_openai:
            with patch('src.agents.document_intelligence.agent.get_database_connection') as mock_db:
                # Mock OpenAI response
                mock_openai_instance = AsyncMock()
                mock_openai_instance.analyze_document.return_value = {
                    "document_type": "medical_record",
                    "key_findings": ["Patient diagnosed with whiplash"],
                    "risk_indicators": [],
                    "confidence": 0.9
                }
                mock_openai.return_value = mock_openai_instance
                
                # Mock database
                mock_db_instance = AsyncMock()
                mock_db.return_value = mock_db_instance
                
                from src.agents.document_intelligence.agent import DocumentIntelligenceAgent
                
                agent = DocumentIntelligenceAgent()
                
                # Test document analysis
                document_data = {
                    "document_id": 1,
                    "file_path": "/documents/medical_record.pdf",
                    "extracted_text": "Patient: John Doe. Diagnosis: Whiplash injury."
                }
                
                result = await agent.process_message("analyze_document", document_data)
                
                assert result is not None
                mock_openai_instance.analyze_document.assert_called_once()


class TestEmailServiceWorkflow:
    """Test email service agent workflow."""
    
    @pytest.mark.asyncio
    async def test_email_service_agent_can_send_email(self):
        """Test email service agent can send emails."""
        with patch('src.agents.email_service.agent.OpenAIClient') as mock_openai:
            with patch('src.agents.email_service.agent.EmailService') as mock_email:
                with patch('src.agents.email_service.agent.get_database_connection') as mock_db:
                    # Mock OpenAI response
                    mock_openai_instance = AsyncMock()
                    mock_openai_instance.generate_email_content.return_value = "Subject: Test\n\nBody: Test email"
                    mock_openai.return_value = mock_openai_instance
                    
                    # Mock email service
                    mock_email_instance = AsyncMock()
                    mock_email_instance.send_email.return_value = True
                    mock_email.return_value = mock_email_instance
                    
                    # Mock database
                    mock_db_instance = AsyncMock()
                    mock_db.return_value = mock_db_instance
                    
                    from src.agents.email_service.agent import EmailServiceAgent
                    
                    agent = EmailServiceAgent()
                    
                    # Test sending email
                    email_data = {
                        "recipient": "john.doe@example.com",
                        "template_type": "case_update",
                        "context": {"case_number": "CASE-001", "status": "approved"}
                    }
                    
                    result = await agent.process_message("send_email", email_data)
                    
                    assert result is not None
                    mock_openai_instance.generate_email_content.assert_called_once()
                    mock_email_instance.send_email.assert_called_once()


class TestSMSServiceWorkflow:
    """Test SMS service agent workflow."""
    
    @pytest.mark.asyncio
    async def test_sms_service_agent_can_send_sms(self):
        """Test SMS service agent can send SMS messages."""
        with patch('src.agents.sms_service.agent.OpenAIClient') as mock_openai:
            with patch('src.agents.sms_service.agent.SMSService') as mock_sms:
                with patch('src.agents.sms_service.agent.get_database_connection') as mock_db:
                    # Mock OpenAI response
                    mock_openai_instance = AsyncMock()
                    mock_openai_instance.generate_sms_content.return_value = "Your case CASE-001 has been approved."
                    mock_openai.return_value = mock_openai_instance
                    
                    # Mock SMS service
                    mock_sms_instance = AsyncMock()
                    mock_sms_instance.send_sms.return_value = {"sid": "test_sid", "status": "sent"}
                    mock_sms.return_value = mock_sms_instance
                    
                    # Mock database
                    mock_db_instance = AsyncMock()
                    mock_db.return_value = mock_db_instance
                    
                    from src.agents.sms_service.agent import SMSServiceAgent
                    
                    agent = SMSServiceAgent()
                    
                    # Test sending SMS
                    sms_data = {
                        "recipient": "+1234567890",
                        "template_type": "case_update",
                        "context": {"case_number": "CASE-001", "status": "approved"}
                    }
                    
                    result = await agent.process_message("send_sms", sms_data)
                    
                    assert result is not None
                    mock_openai_instance.generate_sms_content.assert_called_once()
                    mock_sms_instance.send_sms.assert_called_once()