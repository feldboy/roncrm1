interface ReportsFiltersProps {
  filters: {
    date_range: string
    case_type: string
    agent_type: string
    metric_type: string
  }
  onFilterChange: (filters: any) => void
}

export function ReportsFilters({ filters, onFilterChange }: ReportsFiltersProps) {
  const dateRangeOptions = [
    { value: '7', label: 'Last 7 days' },
    { value: '30', label: 'Last 30 days' },
    { value: '90', label: 'Last 90 days' },
    { value: '365', label: 'Last year' },
    { value: 'custom', label: 'Custom range' },
  ]

  const caseTypeOptions = [
    { value: '', label: 'All Case Types' },
    { value: 'personal_injury', label: 'Personal Injury' },
    { value: 'medical_malpractice', label: 'Medical Malpractice' },
    { value: 'product_liability', label: 'Product Liability' },
    { value: 'workers_compensation', label: 'Workers Compensation' },
    { value: 'wrongful_death', label: 'Wrongful Death' },
  ]

  const agentTypeOptions = [
    { value: '', label: 'All Agents' },
    { value: 'lead_intake', label: 'Lead Intake' },
    { value: 'document_intelligence', label: 'Document Intelligence' },
    { value: 'risk_assessment', label: 'Risk Assessment' },
    { value: 'email_service', label: 'Email Service' },
    { value: 'sms_service', label: 'SMS Service' },
    { value: 'pipedrive_sync', label: 'Pipedrive Sync' },
  ]

  const metricTypeOptions = [
    { value: 'overview', label: 'Overview' },
    { value: 'performance', label: 'Performance' },
    { value: 'efficiency', label: 'Efficiency' },
    { value: 'compliance', label: 'Compliance' },
  ]

  return (
    <div className="card p-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <label htmlFor="date_range" className="block text-sm font-medium text-gray-700 mb-2">
            Date Range
          </label>
          <select
            id="date_range"
            value={filters.date_range}
            onChange={(e) => onFilterChange({ ...filters, date_range: e.target.value })}
            className="input"
          >
            {dateRangeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="case_type" className="block text-sm font-medium text-gray-700 mb-2">
            Case Type
          </label>
          <select
            id="case_type"
            value={filters.case_type}
            onChange={(e) => onFilterChange({ ...filters, case_type: e.target.value })}
            className="input"
          >
            {caseTypeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="agent_type" className="block text-sm font-medium text-gray-700 mb-2">
            Agent Type
          </label>
          <select
            id="agent_type"
            value={filters.agent_type}
            onChange={(e) => onFilterChange({ ...filters, agent_type: e.target.value })}
            className="input"
          >
            {agentTypeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="metric_type" className="block text-sm font-medium text-gray-700 mb-2">
            Metric Type
          </label>
          <select
            id="metric_type"
            value={filters.metric_type}
            onChange={(e) => onFilterChange({ ...filters, metric_type: e.target.value })}
            className="input"
          >
            {metricTypeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {filters.date_range === 'custom' && (
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="start_date" className="block text-sm font-medium text-gray-700 mb-2">
              Start Date
            </label>
            <input
              type="date"
              id="start_date"
              className="input"
              onChange={(e) => onFilterChange({ ...filters, start_date: e.target.value })}
            />
          </div>
          <div>
            <label htmlFor="end_date" className="block text-sm font-medium text-gray-700 mb-2">
              End Date
            </label>
            <input
              type="date"
              id="end_date"
              className="input"
              onChange={(e) => onFilterChange({ ...filters, end_date: e.target.value })}
            />
          </div>
        </div>
      )}
    </div>
  )
}