import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

interface ReportsDashboardProps {
  reportData: any
  agentMetrics: any
  isLoading: boolean
  filters: any
}

export function ReportsDashboard({ reportData, agentMetrics, isLoading, filters }: ReportsDashboardProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="card p-6">
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
              <div className="h-64 bg-gray-200 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

  const caseStatusData = reportData?.case_status_distribution || []
  const dailyActivityData = reportData?.daily_activity || []
  const agentPerformanceData = agentMetrics?.agent_performance || []
  const processingTimeData = reportData?.processing_times || []

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 text-lg">📊</span>
              </div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Total Cases</dt>
                <dd className="text-lg font-medium text-gray-900">
                  {reportData?.total_cases?.toLocaleString() || 0}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 bg-green-100 rounded-lg flex items-center justify-center">
                <span className="text-green-600 text-lg">✅</span>
              </div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Success Rate</dt>
                <dd className="text-lg font-medium text-gray-900">
                  {reportData?.success_rate?.toFixed(1) || 0}%
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                <span className="text-yellow-600 text-lg">⏱️</span>
              </div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Avg Processing Time</dt>
                <dd className="text-lg font-medium text-gray-900">
                  {reportData?.avg_processing_time || '0h'}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 bg-purple-100 rounded-lg flex items-center justify-center">
                <span className="text-purple-600 text-lg">🤖</span>
              </div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Active Agents</dt>
                <dd className="text-lg font-medium text-gray-900">
                  {agentMetrics?.active_agents || 0}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Daily Activity Chart */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Daily Activity</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={dailyActivityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area
                type="monotone"
                dataKey="cases_created"
                stackId="1"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.6}
                name="Cases Created"
              />
              <Area
                type="monotone"
                dataKey="documents_processed"
                stackId="1"
                stroke="#10b981"
                fill="#10b981"
                fillOpacity={0.6}
                name="Documents Processed"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Case Status Distribution */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Case Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={caseStatusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {caseStatusData.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Agent Performance */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Agent Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={agentPerformanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="agent_name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="tasks_completed" fill="#3b82f6" name="Tasks Completed" />
              <Bar dataKey="success_rate" fill="#10b981" name="Success Rate %" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Processing Times */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Processing Times</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={processingTimeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="avg_time"
                stroke="#3b82f6"
                strokeWidth={2}
                name="Average Time (min)"
              />
              <Line
                type="monotone"
                dataKey="median_time"
                stroke="#10b981"
                strokeWidth={2}
                name="Median Time (min)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Agent Details Table */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Agent Details</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Agent
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tasks Completed
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Success Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Response Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Activity
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {agentPerformanceData.map((agent: any) => (
                <tr key={agent.agent_id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{agent.agent_name}</div>
                    <div className="text-sm text-gray-500">{agent.agent_type}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      agent.status === 'active' ? 'bg-green-100 text-green-800' :
                      agent.status === 'idle' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {agent.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {agent.tasks_completed?.toLocaleString() || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {agent.success_rate?.toFixed(1) || 0}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {agent.avg_response_time || '0s'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {agent.last_activity || 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}