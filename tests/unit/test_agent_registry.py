"""Tests for agent registry functionality."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from src.agents.base.registry import AgentRegistry
from src.agents.base.agent import BaseAgent, AgentStatus


class MockAgent(BaseAgent):
    """Mock agent for testing."""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "Mock Agent", "Test agent for unit tests")
        self.start_called = False
        self.stop_called = False
        self.process_called = False
    
    async def start(self):
        """Start the mock agent."""
        self.start_called = True
        self.status = AgentStatus.RUNNING
    
    async def stop(self):
        """Stop the mock agent."""
        self.stop_called = True
        self.status = AgentStatus.STOPPED
    
    async def process_message(self, message_type: str, data: dict):
        """Process a message."""
        self.process_called = True
        return {"processed": True, "data": data}


class TestAgentRegistry:
    """Test agent registry functionality."""
    
    @pytest.fixture
    def registry(self):
        """Create agent registry for testing."""
        return AgentRegistry()
    
    @pytest.fixture
    def mock_agent(self):
        """Create mock agent for testing."""
        return MockAgent("test_agent")
    
    def test_register_agent(self, registry, mock_agent):
        """Test registering an agent."""
        registry.register_agent(mock_agent)
        
        assert "test_agent" in registry.agents
        assert registry.agents["test_agent"] == mock_agent
    
    def test_register_duplicate_agent(self, registry, mock_agent):
        """Test registering duplicate agent raises error."""
        registry.register_agent(mock_agent)
        
        duplicate_agent = MockAgent("test_agent")
        with pytest.raises(ValueError, match="Agent with ID 'test_agent' already registered"):
            registry.register_agent(duplicate_agent)
    
    def test_unregister_agent(self, registry, mock_agent):
        """Test unregistering an agent."""
        registry.register_agent(mock_agent)
        registry.unregister_agent("test_agent")
        
        assert "test_agent" not in registry.agents
    
    def test_unregister_nonexistent_agent(self, registry):
        """Test unregistering non-existent agent."""
        # Should not raise error
        registry.unregister_agent("nonexistent")
    
    def test_get_agent(self, registry, mock_agent):
        """Test getting an agent."""
        registry.register_agent(mock_agent)
        
        retrieved_agent = registry.get_agent("test_agent")
        assert retrieved_agent == mock_agent
    
    def test_get_nonexistent_agent(self, registry):
        """Test getting non-existent agent returns None."""
        agent = registry.get_agent("nonexistent")
        assert agent is None
    
    def test_get_all_agents(self, registry):
        """Test getting all agents."""
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        
        registry.register_agent(agent1)
        registry.register_agent(agent2)
        
        all_agents = registry.get_all_agents()
        assert len(all_agents) == 2
        assert agent1 in all_agents
        assert agent2 in all_agents
    
    @pytest.mark.asyncio
    async def test_start_agent(self, registry, mock_agent):
        """Test starting an agent."""
        registry.register_agent(mock_agent)
        
        result = await registry.start_agent("test_agent")
        
        assert result is True
        assert mock_agent.start_called is True
        assert mock_agent.status == AgentStatus.RUNNING
    
    @pytest.mark.asyncio
    async def test_start_nonexistent_agent(self, registry):
        """Test starting non-existent agent."""
        result = await registry.start_agent("nonexistent")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_stop_agent(self, registry, mock_agent):
        """Test stopping an agent."""
        registry.register_agent(mock_agent)
        mock_agent.status = AgentStatus.RUNNING
        
        result = await registry.stop_agent("test_agent")
        
        assert result is True
        assert mock_agent.stop_called is True
        assert mock_agent.status == AgentStatus.STOPPED
    
    @pytest.mark.asyncio
    async def test_stop_nonexistent_agent(self, registry):
        """Test stopping non-existent agent."""
        result = await registry.stop_agent("nonexistent")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_start_all_agents(self, registry):
        """Test starting all agents."""
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        
        registry.register_agent(agent1)
        registry.register_agent(agent2)
        
        await registry.start_all_agents()
        
        assert agent1.start_called is True
        assert agent2.start_called is True
        assert agent1.status == AgentStatus.RUNNING
        assert agent2.status == AgentStatus.RUNNING
    
    @pytest.mark.asyncio
    async def test_stop_all_agents(self, registry):
        """Test stopping all agents."""
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        agent1.status = AgentStatus.RUNNING
        agent2.status = AgentStatus.RUNNING
        
        registry.register_agent(agent1)
        registry.register_agent(agent2)
        
        await registry.stop_all_agents()
        
        assert agent1.stop_called is True
        assert agent2.stop_called is True
        assert agent1.status == AgentStatus.STOPPED
        assert agent2.status == AgentStatus.STOPPED
    
    @pytest.mark.asyncio
    async def test_start_core_agents(self, registry):
        """Test starting core agents."""
        with patch.object(registry, '_initialize_core_agents') as mock_init:
            with patch.object(registry, 'start_all_agents') as mock_start_all:
                await registry.start_core_agents()
                
                mock_init.assert_called_once()
                mock_start_all.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_shutdown_all_agents(self, registry):
        """Test shutting down all agents."""
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        agent1.status = AgentStatus.RUNNING
        agent2.status = AgentStatus.RUNNING
        
        registry.register_agent(agent1)
        registry.register_agent(agent2)
        
        await registry.shutdown_all_agents()
        
        assert agent1.stop_called is True
        assert agent2.stop_called is True
    
    @pytest.mark.asyncio
    async def test_send_message_to_agent(self, registry, mock_agent):
        """Test sending message to agent."""
        registry.register_agent(mock_agent)
        mock_agent.status = AgentStatus.RUNNING
        
        result = await registry.send_message_to_agent(
            "test_agent", 
            "test_message", 
            {"key": "value"}
        )
        
        assert result["processed"] is True
        assert result["data"]["key"] == "value"
        assert mock_agent.process_called is True
    
    @pytest.mark.asyncio
    async def test_send_message_to_stopped_agent(self, registry, mock_agent):
        """Test sending message to stopped agent."""
        registry.register_agent(mock_agent)
        mock_agent.status = AgentStatus.STOPPED
        
        result = await registry.send_message_to_agent(
            "test_agent", 
            "test_message", 
            {"key": "value"}
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_broadcast_message(self, registry):
        """Test broadcasting message to all agents."""
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        agent1.status = AgentStatus.RUNNING
        agent2.status = AgentStatus.RUNNING
        
        registry.register_agent(agent1)
        registry.register_agent(agent2)
        
        results = await registry.broadcast_message("test_message", {"key": "value"})
        
        assert len(results) == 2
        assert agent1.process_called is True
        assert agent2.process_called is True
    
    @pytest.mark.asyncio
    async def test_get_system_status(self, registry):
        """Test getting system status."""
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        agent1.status = AgentStatus.RUNNING
        agent2.status = AgentStatus.STOPPED
        agent1.last_activity = datetime.utcnow()
        agent2.last_activity = datetime.utcnow()
        
        registry.register_agent(agent1)
        registry.register_agent(agent2)
        
        status = await registry.get_system_status()
        
        assert status["total_agents"] == 2
        assert status["running_agents"] == 1
        assert status["stopped_agents"] == 1
        assert len(status["agents"]) == 2
        
        # Check individual agent status
        agent1_status = next(a for a in status["agents"] if a["id"] == "agent1")
        assert agent1_status["status"] == "running"
        
        agent2_status = next(a for a in status["agents"] if a["id"] == "agent2")
        assert agent2_status["status"] == "stopped"
    
    @pytest.mark.asyncio
    async def test_get_agent_status(self, registry, mock_agent):
        """Test getting individual agent status."""
        registry.register_agent(mock_agent)
        mock_agent.status = AgentStatus.RUNNING
        mock_agent.last_activity = datetime.utcnow()
        
        status = await registry.get_agent_status("test_agent")
        
        assert status["id"] == "test_agent"
        assert status["name"] == "Mock Agent"
        assert status["status"] == "running"
        assert "last_activity" in status
        assert "uptime" in status
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_agent_status(self, registry):
        """Test getting status of non-existent agent."""
        status = await registry.get_agent_status("nonexistent")
        assert status is None
    
    def test_initialize_core_agents(self, registry):
        """Test initializing core agents."""
        with patch('src.agents.lead_intake.agent.LeadIntakeAgent') as mock_lead_intake:
            with patch('src.agents.pipedrive_sync.agent.PipedriveSyncAgent') as mock_pipedrive:
                with patch('src.agents.risk_assessment.agent.RiskAssessmentAgent') as mock_risk:
                    with patch('src.agents.document_intelligence.agent.DocumentIntelligenceAgent') as mock_doc:
                        with patch('src.agents.email_service.agent.EmailServiceAgent') as mock_email:
                            with patch('src.agents.sms_service.agent.SMSServiceAgent') as mock_sms:
                                
                                # Mock agent instances
                                mock_agents = [
                                    Mock(agent_id="lead_intake"),
                                    Mock(agent_id="pipedrive_sync"),
                                    Mock(agent_id="risk_assessment"),
                                    Mock(agent_id="document_intelligence"),
                                    Mock(agent_id="email_service"),
                                    Mock(agent_id="sms_service"),
                                ]
                                
                                mock_lead_intake.return_value = mock_agents[0]
                                mock_pipedrive.return_value = mock_agents[1]
                                mock_risk.return_value = mock_agents[2]
                                mock_doc.return_value = mock_agents[3]
                                mock_email.return_value = mock_agents[4]
                                mock_sms.return_value = mock_agents[5]
                                
                                registry._initialize_core_agents()
                                
                                # Verify all agents were registered
                                assert len(registry.agents) == 6
                                for mock_agent in mock_agents:
                                    assert mock_agent.agent_id in registry.agents