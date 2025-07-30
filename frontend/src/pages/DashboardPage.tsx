import { useEffect } from 'react'
import { useQuery } from 'react-query'
import { api } from '../services/api'
import { wsService } from '../services/websocket'
import { StatsCard } from '../components/dashboard/StatsCard'
import { PipelineProgress } from '../components/dashboard/PipelineProgress'
import { UrgentTasks } from '../components/dashboard/UrgentTasks'
import { TopLawFirms } from '../components/dashboard/TopLawFirms'
import { AgentStatusCard } from '../components/dashboard/AgentStatusCard'

export function DashboardPage() {
  const { data: agentStatus, isLoading: agentsLoading } = useQuery(
    'agent-status',
    () => api.get('/agents/status').then(res => res.data),
    { refetchInterval: 30000 }
  )

  const { data: stats, isLoading: statsLoading } = useQuery(
    'dashboard-stats',
    () => api.get('/cases/dashboard-stats').then(res => res.data),
    { refetchInterval: 60000 }
  )

  useEffect(() => {
    wsService.connect()
    return () => wsService.disconnect()
  }, [])

  if (agentsLoading || statsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-heading">Dashboard Overview</h1>
        <p className="page-subtitle">
          Monitor your pre-settlement funding pipeline
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Cases"
          value={stats?.total_cases || 4}
          change={0}
          icon="folder"
        />
        <StatsCard
          title="Active Pipeline"
          value={stats?.active_pipeline || 4}
          change={8}
          icon="trending"
        />
        <StatsCard
          title="Total Funding"
          value={stats?.total_funding || 0}
          prefix="$"
          icon="currency"
        />
        <StatsCard
          title="Avg Processing"
          value={stats?.avg_processing_days || 12}
          suffix=" days"
          icon="clock"
        />
      </div>

      {/* AI Agent Status Section */}
      <div className="card p-6">
        <h2 className="section-heading mb-6">🤖 AI Agent Status</h2>
        {agentsLoading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <div className="space-y-3">
            {agentStatus?.stats ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{agentStatus.stats.healthy_agents}</div>
                    <div className="text-sm text-green-700">Healthy Agents</div>
                  </div>
                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-600">{agentStatus.stats.degraded_agents}</div>
                    <div className="text-sm text-yellow-700">Degraded Agents</div>
                  </div>
                  <div className="text-center p-4 bg-red-50 rounded-lg">
                    <div className="text-2xl font-bold text-red-600">{agentStatus.stats.unhealthy_agents}</div>
                    <div className="text-sm text-red-700">Unhealthy Agents</div>
                  </div>
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{agentStatus.stats.total_active_tasks}</div>
                    <div className="text-sm text-blue-700">Active Tasks</div>
                  </div>
                </div>
                <div className="text-sm text-gray-600 mb-4">
                  System Status: <span className={`font-medium ${agentStatus.system_status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                    {agentStatus.system_status}
                  </span>
                </div>
              </>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No agent data available</p>
                <p className="text-sm mt-2">Agents will appear here once they are started</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Pipeline Status Section */}
      <div className="card p-6">
        <h2 className="section-heading mb-6">Pipeline Status</h2>
        <PipelineProgress />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <div className="card p-6">
            <h2 className="section-heading mb-6">Recent Activity</h2>
            <div className="text-sm text-gray-500">
              No recent activity to display
            </div>
          </div>
        </div>
        <div className="space-y-6">
          <UrgentTasks />
          <TopLawFirms />
        </div>
      </div>
    </div>
  )
}