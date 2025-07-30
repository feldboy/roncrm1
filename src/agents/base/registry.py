"""Agent registry for discovery and lifecycle management."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Type

from ...utils.logging import get_logger
from .agent import BaseAgent, AgentConfig, AgentType, HealthStatus

logger = get_logger(__name__)


class AgentRegistry:
    """
    Central registry for agent discovery and lifecycle management.
    
    Manages all agents in the multi-agent system, providing discovery,
    health monitoring, load balancing, and coordination capabilities.
    """
    
    def __init__(self):
        """Initialize the agent registry."""
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_configs: Dict[str, AgentConfig] = {}
        self._agent_classes: Dict[AgentType, Type[BaseAgent]] = {}
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._running = False
        
        logger.info("Agent registry initialized")
    
    def register_agent_class(
        self,
        agent_type: AgentType,
        agent_class: Type[BaseAgent]
    ) -> None:
        """
        Register an agent class for a specific agent type.
        
        Args:
            agent_type: The type of agent.
            agent_class: The agent class to register.
        """
        self._agent_classes[agent_type] = agent_class
        logger.info(
            f"Registered agent class",
            agent_type=agent_type.value,
            class_name=agent_class.__name__,
        )
    
    async def start_agent(self, config: AgentConfig) -> str:
        """
        Start a new agent instance.
        
        Args:
            config: Agent configuration.
            
        Returns:
            str: The agent ID.
            
        Raises:
            ValueError: If agent type is not registered or agent already exists.
        """
        if config.agent_type not in self._agent_classes:
            raise ValueError(f"Agent type {config.agent_type.value} not registered")
        
        if config.agent_id in self._agents:
            raise ValueError(f"Agent {config.agent_id} already exists")
        
        # Create agent instance
        agent_class = self._agent_classes[config.agent_type]
        agent = agent_class(config)
        
        # Store agent and config
        self._agents[config.agent_id] = agent
        self._agent_configs[config.agent_id] = config
        
        # Start the agent
        await agent.start()
        
        logger.info(
            f"Started agent",
            agent_id=config.agent_id,
            agent_type=config.agent_type.value,
        )
        
        return config.agent_id
    
    async def stop_agent(self, agent_id: str) -> None:
        """
        Stop an agent instance.
        
        Args:
            agent_id: The agent ID to stop.
            
        Raises:
            ValueError: If agent does not exist.
        """
        if agent_id not in self._agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = self._agents[agent_id]
        await agent.stop()
        
        # Remove from registry
        del self._agents[agent_id]
        del self._agent_configs[agent_id]
        
        logger.info(f"Stopped agent", agent_id=agent_id)
    
    async def restart_agent(self, agent_id: str) -> None:
        """
        Restart an agent instance.
        
        Args:
            agent_id: The agent ID to restart.
        """
        if agent_id not in self._agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        config = self._agent_configs[agent_id]
        
        # Stop the current agent
        await self.stop_agent(agent_id)
        
        # Start a new instance with the same config
        await self.start_agent(config)
        
        logger.info(f"Restarted agent", agent_id=agent_id)
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent instance by ID.
        
        Args:
            agent_id: The agent ID.
            
        Returns:
            BaseAgent: The agent instance or None if not found.
        """
        return self._agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: AgentType) -> List[BaseAgent]:
        """
        Get all agents of a specific type.
        
        Args:
            agent_type: The agent type.
            
        Returns:
            List[BaseAgent]: List of agents of the specified type.
        """
        return [
            agent for agent in self._agents.values()
            if agent.agent_type == agent_type
        ]
    
    def get_healthy_agents_by_type(self, agent_type: AgentType) -> List[BaseAgent]:
        """
        Get all healthy agents of a specific type.
        
        Args:
            agent_type: The agent type.
            
        Returns:
            List[BaseAgent]: List of healthy agents of the specified type.
        """
        return [
            agent for agent in self.get_agents_by_type(agent_type)
            if agent.health_status == HealthStatus.HEALTHY
        ]
    
    def get_least_loaded_agent(self, agent_type: AgentType) -> Optional[BaseAgent]:
        """
        Get the least loaded healthy agent of a specific type.
        
        Args:
            agent_type: The agent type.
            
        Returns:
            BaseAgent: The least loaded agent or None if none available.
        """
        healthy_agents = self.get_healthy_agents_by_type(agent_type)
        
        if not healthy_agents:
            return None
        
        # Find agent with the fewest active tasks
        return min(
            healthy_agents,
            key=lambda agent: len(agent.active_tasks)
        )
    
    def list_agents(self) -> Dict[str, Dict]:
        """
        List all registered agents with their status.
        
        Returns:
            dict: Dictionary of agent information.
        """
        return {
            agent_id: agent.get_health_status()
            for agent_id, agent in self._agents.items()
        }
    
    def get_agent_types(self) -> List[AgentType]:
        """
        Get all registered agent types.
        
        Returns:
            List[AgentType]: List of registered agent types.
        """
        return list(self._agent_classes.keys())
    
    def get_registry_stats(self) -> Dict:
        """
        Get registry statistics.
        
        Returns:
            dict: Registry statistics.
        """
        total_agents = len(self._agents)
        healthy_agents = sum(
            1 for agent in self._agents.values()
            if agent.health_status == HealthStatus.HEALTHY
        )
        degraded_agents = sum(
            1 for agent in self._agents.values()
            if agent.health_status == HealthStatus.DEGRADED
        )
        unhealthy_agents = sum(
            1 for agent in self._agents.values()
            if agent.health_status == HealthStatus.UNHEALTHY
        )
        
        total_active_tasks = sum(
            len(agent.active_tasks) for agent in self._agents.values()
        )
        
        total_tasks_processed = sum(
            agent.performance_metrics.tasks_processed
            for agent in self._agents.values()
        )
        
        return {
            "total_agents": total_agents,
            "healthy_agents": healthy_agents,
            "degraded_agents": degraded_agents,
            "unhealthy_agents": unhealthy_agents,
            "total_active_tasks": total_active_tasks,
            "total_tasks_processed": total_tasks_processed,
            "registered_agent_types": [t.value for t in self._agent_classes.keys()],
        }
    
    async def start_monitoring(self) -> None:
        """Start the health monitoring background task."""
        if self._running:
            logger.warning("Registry monitoring is already running")
            return
        
        self._running = True
        self._health_monitor_task = asyncio.create_task(self._health_monitor())
        
        logger.info("Started registry health monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop the health monitoring background task."""
        if not self._running:
            logger.warning("Registry monitoring is not running")
            return
        
        self._running = False
        
        if self._health_monitor_task:
            self._health_monitor_task.cancel()
            try:
                await self._health_monitor_task
            except asyncio.CancelledError:
                pass
            self._health_monitor_task = None
        
        logger.info("Stopped registry health monitoring")
    
    async def stop_all_agents(self) -> None:
        """Stop all registered agents."""
        logger.info(f"Stopping {len(self._agents)} agents")
        
        # Stop monitoring first
        await self.stop_monitoring()
        
        # Stop all agents
        stop_tasks = [agent.stop() for agent in self._agents.values()]
        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        # Clear registry
        self._agents.clear()
        self._agent_configs.clear()
        
        logger.info("All agents stopped")
    
    async def _health_monitor(self) -> None:
        """Background health monitoring task."""
        while self._running:
            try:
                await self._check_agent_health()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(30)
    
    async def _check_agent_health(self) -> None:
        """Check health of all agents and take corrective actions."""
        unhealthy_agents = []
        
        for agent_id, agent in self._agents.items():
            # Check if agent is unresponsive
            time_since_activity = datetime.utcnow() - agent.performance_metrics.last_activity
            
            if time_since_activity > timedelta(minutes=5):
                logger.warning(
                    f"Agent appears unresponsive",
                    agent_id=agent_id,
                    last_activity=agent.performance_metrics.last_activity.isoformat(),
                )
                unhealthy_agents.append(agent_id)
            
            # Check for too many consecutive failures
            if agent.performance_metrics.consecutive_failures >= 10:
                logger.error(
                    f"Agent has too many consecutive failures",
                    agent_id=agent_id,
                    consecutive_failures=agent.performance_metrics.consecutive_failures,
                )
                unhealthy_agents.append(agent_id)
        
        # Restart unhealthy agents
        for agent_id in unhealthy_agents:
            try:
                logger.info(f"Attempting to restart unhealthy agent", agent_id=agent_id)
                await self.restart_agent(agent_id)
            except Exception as e:
                logger.error(f"Failed to restart agent {agent_id}: {e}")
    
    def is_agent_available(self, agent_type: AgentType) -> bool:
        """
        Check if at least one healthy agent of the specified type is available.
        
        Args:
            agent_type: The agent type to check.
            
        Returns:
            bool: True if at least one healthy agent is available.
        """
        return len(self.get_healthy_agents_by_type(agent_type)) > 0
    
    async def get_system_status(self) -> Dict:
        """
        Get the current system status including all agents.
        
        Returns:
            dict: System status information.
        """
        return {
            "system_status": "healthy" if self._running else "stopped",
            "agents": self.list_agents(),
            "stats": self.get_registry_stats(),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def scale_agents(self, agent_type: AgentType, target_count: int) -> None:
        """
        Scale agents of a specific type to the target count.
        
        Args:
            agent_type: The agent type to scale.
            target_count: The target number of agents.
        """
        current_agents = self.get_agents_by_type(agent_type)
        current_count = len(current_agents)
        
        if current_count == target_count:
            logger.info(
                f"Agent count already at target",
                agent_type=agent_type.value,
                count=current_count,
            )
            return
        
        if current_count < target_count:
            # Scale up
            agents_to_add = target_count - current_count
            logger.info(
                f"Scaling up agents",
                agent_type=agent_type.value,
                current=current_count,
                target=target_count,
                adding=agents_to_add,
            )
            
            for i in range(agents_to_add):
                agent_id = f"{agent_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{i}"
                config = AgentConfig(
                    agent_id=agent_id,
                    agent_type=agent_type,
                )
                await self.start_agent(config)
        
        else:
            # Scale down
            agents_to_remove = current_count - target_count
            logger.info(
                f"Scaling down agents",
                agent_type=agent_type.value,
                current=current_count,
                target=target_count,
                removing=agents_to_remove,
            )
            
            # Remove agents with the fewest active tasks first
            agents_by_load = sorted(
                current_agents,
                key=lambda agent: len(agent.active_tasks)
            )
            
            for agent in agents_by_load[:agents_to_remove]:
                await self.stop_agent(agent.agent_id)


# Global registry instance
agent_registry = AgentRegistry()