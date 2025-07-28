import { useState } from 'react'
import { useQuery } from 'react-query'
import { api } from '@/services/api'
import { ReportsDashboard } from '@/components/reports/ReportsDashboard'
import { ReportsFilters } from '@/components/reports/ReportsFilters'
import { ReportExport } from '@/components/reports/ReportExport'
import { ChartBarIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline'

export function ReportsPage() {
  const [filters, setFilters] = useState({
    date_range: '30',
    case_type: '',
    agent_type: '',
    metric_type: 'overview',
  })

  const { data: reportData, isLoading } = useQuery(
    ['reports', filters],
    () => api.get('/reports/analytics', { params: filters }).then(res => res.data),
    { keepPreviousData: true }
  )

  const { data: agentMetrics, isLoading: agentMetricsLoading } = useQuery(
    ['agent-metrics', filters],
    () => api.get('/reports/agent-metrics', { params: filters }).then(res => res.data),
    { keepPreviousData: true }
  )

  const handleFilterChange = (newFilters: any) => {
    setFilters(prev => ({ ...prev, ...newFilters }))
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics & Reports</h1>
          <p className="mt-2 text-sm text-gray-700">
            Monitor system performance and generate insights
          </p>
        </div>
        <div className="flex space-x-3">
          <ReportExport filters={filters} data={reportData} />
          <button className="btn-primary flex items-center space-x-2">
            <ArrowDownTrayIcon className="h-5 w-5" />
            <span>Export</span>
          </button>
        </div>
      </div>

      <ReportsFilters
        filters={filters}
        onFilterChange={handleFilterChange}
      />

      <ReportsDashboard
        reportData={reportData}
        agentMetrics={agentMetrics}
        isLoading={isLoading || agentMetricsLoading}
        filters={filters}
      />
    </div>
  )
}