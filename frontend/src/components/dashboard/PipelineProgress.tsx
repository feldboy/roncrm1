export function PipelineProgress() {
  const stages = [
    { name: 'Intake', count: 1, total: 4, color: 'bg-primary-500', percentage: 25 },
    { name: 'Documents', count: 1, total: 4, color: 'bg-yellow-500', percentage: 25 },
    { name: 'Review', count: 1, total: 4, color: 'bg-purple-500', percentage: 25 },
    { name: 'Underwriting', count: 1, total: 4, color: 'bg-orange-500', percentage: 25 },
    { name: 'Offer Extended', count: 0, total: 4, color: 'bg-green-500', percentage: 0 },
    { name: 'Signed', count: 0, total: 4, color: 'bg-blue-500', percentage: 0 },
    { name: 'Declined', count: 0, total: 4, color: 'bg-red-500', percentage: 0 },
  ]

  return (
    <div className="space-y-4">
      {stages.map((stage) => (
        <div key={stage.name} className="flex items-center justify-between">
          <div className="flex items-center space-x-3 min-w-0 flex-1">
            <div className={`w-3 h-3 rounded-full ${stage.color}`} />
            <span className="text-sm font-medium text-gray-900 truncate">{stage.name}</span>
            <span className="text-sm text-gray-500">{stage.count} case{stage.count !== 1 ? 's' : ''}</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-32 bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${stage.color}`}
                style={{ width: `${stage.percentage}%` }}
              />
            </div>
            <span className="text-sm text-gray-500 w-8 text-right">{stage.percentage}%</span>
          </div>
        </div>
      ))}
    </div>
  )
}