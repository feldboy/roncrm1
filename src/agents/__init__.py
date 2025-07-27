"""Multi-agent architecture core for the AI CRM system."""

from .base.agent import BaseAgent
from .base.registry import AgentRegistry
from .base.communication import AgentCommunication

__all__ = ["BaseAgent", "AgentRegistry", "AgentCommunication"]