import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { api } from '../../services/api'
import { settingsService } from '../../services/settingsService'
import toast from 'react-hot-toast'
import { PlayIcon, PauseIcon, StopIcon, CogIcon, ChartBarIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'

interface AgentSettingsProps {
  settings: any
  onUpdate: () => void
}

export function AgentSettings({ settings, onUpdate }: AgentSettingsProps) {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data: agents, isLoading, refetch } = useQuery(
    'agent-settings',
    () => settingsService.getAgentSettings(),
    {
      retry: false,
      onError: (error) => {
        console.log('Agent settings query failed, using fallback:', error)
      }
    }
  )

  const { data: agentStatus } = useQuery(
    'agent-status',
    () => api.get('/agents/status').then(res => res.data),
    { 
      refetchInterval: 5000, // Refresh every 5 seconds
      retry: false,
      onError: (error) => {
        console.log('Agent status query failed:', error)
      }
    }
  )

  const agentActionMutation = useMutation(
    async ({ agentId, action }: { agentId: string; action: 'start' | 'stop' | 'restart' }) => {
      return api.post(`/api/v1/agents/${agentId}/${action}`)
    },
    {
      onSuccess: (_, variables) => {
        toast.success(`Agent ${variables.action}ed successfully`)
        queryClient.invalidateQueries('agent-settings')
        queryClient.invalidateQueries('agent-status')
        onUpdate()
      },
      onError: (error: any, variables) => {
        toast.error(`Failed to ${variables.action} agent: ${error.response?.data?.detail || error.message}`)
      }
    }
  )

  const handleAgentAction = (agentId: string, action: 'start' | 'stop' | 'restart') => {
    agentActionMutation.mutate({ agentId, action })
  }

  const configUpdateMutation = useMutation(
    async ({ agentType, settingKey, config }: { agentType: string; settingKey: string; config: any }) => {
      return api.put(`/api/v1/settings/agents/${agentType}/${settingKey}`, config)
    },
    {
      onSuccess: () => {
        toast.success('Agent configuration updated successfully')
        queryClient.invalidateQueries('agent-settings')
        onUpdate()
      },
      onError: (error: any) => {
        toast.error(`Failed to update configuration: ${error.response?.data?.detail || error.message}`)
      }
    }
  )

  const handleConfigUpdate = (agentType: string, settingKey: string, config: any) => {
    configUpdateMutation.mutate({ agentType, settingKey, config })
  }

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

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-20 bg-gray-200 rounded-lg"></div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Agent Management</h3>
        <p className="text-sm text-gray-600 mb-4">
          Configure and monitor AI agents in the system
        </p>
      </div>

      <div className="space-y-4">
        {agents?.map((agent: any) => (
          <div key={agent.id} className="border border-gray-200 rounded-lg">
            <div className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">{agent.name}</h4>
                    <p className="text-sm text-gray-500">{agent.type}</p>
                  </div>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(agent.status)}`}>
                    {agent.status}
                  </span>
                </div>
                
                <div className="flex items-center space-x-2">
                  {agent.status === 'stopped' ? (
                    <button
                      onClick={() => handleAgentAction(agent.id, 'start')}
                      className="p-2 text-green-600 hover:text-green-700"
                      title="Start agent"
                    >
                      <PlayIcon className="h-5 w-5" />
                    </button>
                  ) : (
                    <button
                      onClick={() => handleAgentAction(agent.id, 'stop')}
                      className="p-2 text-red-600 hover:text-red-700"
                      title="Stop agent"
                    >
                      <StopIcon className="h-5 w-5" />
                    </button>
                  )}
                  
                  <button
                    onClick={() => handleAgentAction(agent.id, 'restart')}
                    className="p-2 text-blue-600 hover:text-blue-700"
                    title="Restart agent"
                  >
                    <PauseIcon className="h-5 w-5" />
                  </button>
                  
                  <button
                    onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
                    className="p-2 text-gray-600 hover:text-gray-700"
                    title="Configure agent"
                  >
                    <CogIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>

              <div className="mt-2 grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div>
                  <span className="text-xs text-gray-500">Tasks Completed</span>
                  <div className="text-sm font-medium">{agent.tasks_completed || 0}</div>
                </div>
                <div>
                  <span className="text-xs text-gray-500">Success Rate</span>
                  <div className="text-sm font-medium">{agent.success_rate || 0}%</div>
                </div>
                <div>
                  <span className="text-xs text-gray-500">Last Activity</span>
                  <div className="text-sm font-medium">{agent.last_activity || 'Never'}</div>
                </div>
              </div>
            </div>

            {selectedAgent === agent.id && (
              <div className="border-t border-gray-200 p-4 bg-gray-50">
                <h5 className="text-sm font-medium text-gray-900 mb-3">Configuration</h5>
                <AgentConfigForm
                  agent={agent}
                  onUpdate={(config) => handleConfigUpdate(agent.id, config)}
                />
              </div>
            )}
          </div>
        ))}
      </div>

      {(!agents || agents.length === 0) && (
        <div className="text-center py-12">
          <CogIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No agents configured</h3>
          <p className="mt-1 text-sm text-gray-500">
            Agents will appear here once the system is initialized.
          </p>
        </div>
      )}
    </div>
  )
}

interface AgentConfigFormProps {
  agent: any
  onUpdate: (config: any) => void
}

function AgentConfigForm({ agent, onUpdate }: AgentConfigFormProps) {
  const [config, setConfig] = useState(agent.config || {})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      await onUpdate(config)
    } finally {
      setIsSubmitting(false)
    }
  }

  const commonConfigFields = [
    { key: 'max_retries', label: 'Max Retries', type: 'number', min: 0, max: 10 },
    { key: 'timeout', label: 'Timeout (seconds)', type: 'number', min: 30, max: 3600 },
    { key: 'enabled', label: 'Enabled', type: 'checkbox' },
  ]

  const typeSpecificFields: { [key: string]: any[] } = {
    'lead_intake': [
      { key: 'auto_assign', label: 'Auto Assign Cases', type: 'checkbox' },
      { key: 'validation_level', label: 'Validation Level', type: 'select', options: ['basic', 'standard', 'strict'] },
    ],
    'risk_assessment': [
      { key: 'ai_model', label: 'AI Model', type: 'select', options: ['gpt-3.5-turbo', 'gpt-4', 'claude-3'] },
      { key: 'score_threshold', label: 'Score Threshold', type: 'number', min: 0, max: 100 },
    ],
    'email_service': [
      { key: 'smtp_host', label: 'SMTP Host', type: 'text' },
      { key: 'smtp_port', label: 'SMTP Port', type: 'number', min: 1, max: 65535 },
      { key: 'use_tls', label: 'Use TLS', type: 'checkbox' },
    ],
    'sms_service': [
      { key: 'provider', label: 'SMS Provider', type: 'select', options: ['twilio', 'aws_sns'] },
      { key: 'rate_limit', label: 'Rate Limit (per minute)', type: 'number', min: 1, max: 1000 },
    ],
  }

  const fields = [...commonConfigFields, ...(typeSpecificFields[agent.type] || [])]

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {fields.map((field) => (
          <div key={field.key}>
            <label htmlFor={field.key} className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}
            </label>
            {field.type === 'checkbox' ? (
              <input
                type="checkbox"
                id={field.key}
                checked={config[field.key] || false}
                onChange={(e) => setConfig({ ...config, [field.key]: e.target.checked })}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
            ) : field.type === 'select' ? (
              <select
                id={field.key}
                value={config[field.key] || ''}
                onChange={(e) => setConfig({ ...config, [field.key]: e.target.value })}
                className="input"
              >
                <option value="">Select {field.label}</option>
                {field.options?.map((option: string) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type={field.type}
                id={field.key}
                value={config[field.key] || ''}
                onChange={(e) => setConfig({ 
                  ...config, 
                  [field.key]: field.type === 'number' ? Number(e.target.value) : e.target.value 
                })}
                min={field.min}
                max={field.max}
                className="input"
              />
            )}
          </div>
        ))}
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isSubmitting}
          className="btn-primary"
        >
          {isSubmitting ? 'Saving...' : 'Save Configuration'}
        </button>
      </div>
    </form>
  )
}