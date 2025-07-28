import { useEffect } from 'react'
import { useQuery } from 'react-query'
import { api } from '@/services/api'
import { wsService } from '@/services/websocket'
import { AgentStatusCard } from '@/components/dashboard/AgentStatusCard'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { RecentActivity } from '@/components/dashboard/RecentActivity'
import { SystemHealth } from '@/components/dashboard/SystemHealth'

export function DashboardPage() {
  const { data: agents, isLoading: agentsLoading } = useQuery(
    'agents',
    () => api.get('/agents').then(res => res.data),
    { refetchInterval: 30000 }
  )

  const { data: stats, isLoading: statsLoading } = useQuery(
    'dashboard-stats',
    () => api.get('/dashboard/stats').then(res => res.data),
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
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-sm text-gray-700">
          Monitor agent status and system performance
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Active Cases"
          value={stats?.active_cases || 0}
          change={stats?.cases_change || 0}
          icon="folder"
        />
        <StatsCard
          title="Processed Today"
          value={stats?.processed_today || 0}
          change={stats?.processed_change || 0}
          icon="document"
        />
        <StatsCard
          title="Risk Assessments"
          value={stats?.risk_assessments || 0}
          change={stats?.risk_change || 0}
          icon="shield"
        />
        <StatsCard
          title="Communications"
          value={stats?.communications || 0}
          change={stats?.comm_change || 0}
          icon="chat"
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="space-y-6">
          <div className="card p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Agent Status</h2>
            <div className="space-y-4">
              {agents?.map((agent: any) => (
                <AgentStatusCard key={agent.id} agent={agent} />
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <SystemHealth />
          <RecentActivity />
        </div>
      </div>
    </div>
  )
}