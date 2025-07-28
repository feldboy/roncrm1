import { useState, useEffect } from 'react'
import { wsService } from '@/services/websocket'

interface Agent {
  id: string
  name: string
  type: string
  status: 'active' | 'idle' | 'error' | 'stopped'
  last_activity: string
  tasks_completed: number
  tasks_pending: number
}

interface AgentStatusCardProps {
  agent: Agent
}

export function AgentStatusCard({ agent: initialAgent }: AgentStatusCardProps) {
  const [agent, setAgent] = useState(initialAgent)

  useEffect(() => {
    const handleAgentUpdate = (data: any) => {
      if (data.agent_id === agent.id) {
        setAgent(prev => ({ ...prev, ...data }))
      }
    }

    wsService.on('agent_status_update', handleAgentUpdate)
    return () => wsService.off('agent_status_update', handleAgentUpdate)
  }, [agent.id])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'idle':
        return 'bg-yellow-100 text-yellow-800'
      case 'error':
        return 'bg-red-100 text-red-800'
      case 'stopped':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return '🟢'
      case 'idle':
        return '🟡'
      case 'error':
        return '🔴'
      case 'stopped':
        return '⚫'
      default:
        return '⚫'
    }
  }

  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <div className="flex items-center space-x-3">
        <span className="text-lg">{getStatusIcon(agent.status)}</span>
        <div>
          <h3 className="text-sm font-medium text-gray-900">{agent.name}</h3>
          <p className="text-xs text-gray-500">{agent.type}</p>
        </div>
      </div>
      <div className="flex items-center space-x-3">
        <div className="text-right">
          <div className="text-xs text-gray-500">
            {agent.tasks_pending} pending
          </div>
          <div className="text-xs text-gray-500">
            {agent.tasks_completed} completed
          </div>
        </div>
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(agent.status)}`}>
          {agent.status}
        </span>
      </div>
    </div>
  )
}