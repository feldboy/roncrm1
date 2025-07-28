import { useQuery } from 'react-query'
import { api } from '@/services/api'

export function SystemHealth() {
  const { data: health, isLoading } = useQuery(
    'system-health',
    () => api.get('/health').then(res => res.data),
    { refetchInterval: 10000 }
  )

  if (isLoading) {
    return (
      <div className="card p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">System Health</h2>
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    )
  }

  const getHealthColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600'
      case 'warning':
        return 'text-yellow-600'
      case 'error':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  const getHealthIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return '✅'
      case 'warning':
        return '⚠️'
      case 'error':
        return '❌'
      default:
        return '❓'
    }
  }

  return (
    <div className="card p-6">
      <h2 className="text-lg font-medium text-gray-900 mb-4">System Health</h2>
      <div className="space-y-3">
        {health?.services?.map((service: any) => (
          <div key={service.name} className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span>{getHealthIcon(service.status)}</span>
              <span className="text-sm text-gray-900">{service.name}</span>
            </div>
            <span className={`text-sm font-medium ${getHealthColor(service.status)}`}>
              {service.status}
            </span>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}