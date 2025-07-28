import { useQuery } from 'react-query'
import { api } from '@/services/api'
import { formatDistanceToNow } from 'date-fns'

export function RecentActivity() {
  const { data: activities, isLoading } = useQuery(
    'recent-activity',
    () => api.get('/activity/recent').then(res => res.data),
    { refetchInterval: 30000 }
  )

  if (isLoading) {
    return (
      <div className="card p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h2>
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex space-x-3">
              <div className="h-2 w-2 bg-gray-200 rounded-full mt-2"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'case_created':
        return '📁'
      case 'document_processed':
        return '📄'
      case 'risk_assessment':
        return '🛡️'
      case 'communication_sent':
        return '📧'
      case 'agent_error':
        return '⚠️'
      default:
        return '📋'
    }
  }

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'agent_error':
        return 'text-red-600'
      case 'risk_assessment':
        return 'text-yellow-600'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className="card p-6">
      <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h2>
      <div className="flow-root">
        <ul className="-mb-8">
          {activities?.map((activity: any, index: number) => (
            <li key={activity.id}>
              <div className="relative pb-8">
                {index !== activities.length - 1 && (
                  <span
                    className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                    aria-hidden="true"
                  />
                )}
                <div className="relative flex space-x-3">
                  <div>
                    <span className="text-lg">
                      {getActivityIcon(activity.type)}
                    </span>
                  </div>
                  <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                    <div>
                      <p className="text-sm text-gray-900">{activity.description}</p>
                      {activity.details && (
                        <p className="text-xs text-gray-500 mt-1">{activity.details}</p>
                      )}
                    </div>
                    <div className="whitespace-nowrap text-right text-sm text-gray-500">
                      <time dateTime={activity.timestamp}>
                        {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                      </time>
                    </div>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
      
      {(!activities || activities.length === 0) && (
        <div className="text-center py-8">
          <p className="text-sm text-gray-500">No recent activity</p>
        </div>
      )}
    </div>
  )
}