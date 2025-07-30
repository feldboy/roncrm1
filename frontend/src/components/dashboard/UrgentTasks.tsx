export function UrgentTasks() {
  const urgentTasks = [
    {
      id: 1,
      name: 'Lisa Chen',
      stage: 'intake',
      task: 'Review',
      priority: 'high'
    }
  ]

  return (
    <div className="card">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="section-heading text-red-600">Urgent Tasks</h2>
          <span className="inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800">
            1
          </span>
        </div>
      </div>
      <div className="p-6">
        {urgentTasks.map((task) => (
          <div key={task.id} className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                  <span className="text-xs font-medium text-red-600">LC</span>
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">{task.name}</p>
                <p className="text-xs text-gray-500">Stage: {task.stage}</p>
              </div>
            </div>
            <span className="inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-600">
              {task.task}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}