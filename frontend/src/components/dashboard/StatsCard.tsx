import {
  FolderIcon,
  ArrowTrendingUpIcon,
  CurrencyDollarIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'

interface StatsCardProps {
  title: string
  value: number
  change?: number
  icon: 'folder' | 'trending' | 'currency' | 'clock'
  prefix?: string
  suffix?: string
}

export function StatsCard({ title, value, change, icon, prefix, suffix }: StatsCardProps) {
  const icons = {
    folder: FolderIcon,
    trending: ArrowTrendingUpIcon,
    currency: CurrencyDollarIcon,
    clock: ClockIcon,
  }

  const Icon = icons[icon]

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">
            {prefix}{value.toLocaleString()}{suffix}
          </p>
          {change !== undefined && (
            <p className={`text-sm font-medium ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {change >= 0 ? '+' : ''}{change}%
            </p>
          )}
        </div>
        <div className="p-3 bg-primary-50 rounded-full">
          <Icon className="h-6 w-6 text-primary-600" />
        </div>
      </div>
    </div>
  )
}