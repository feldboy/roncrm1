import {
  FolderIcon,
  DocumentIcon,
  ShieldCheckIcon,
  ChatBubbleLeftRightIcon,
} from '@heroicons/react/24/outline'

interface StatsCardProps {
  title: string
  value: number
  change: number
  icon: 'folder' | 'document' | 'shield' | 'chat'
}

export function StatsCard({ title, value, change, icon }: StatsCardProps) {
  const icons = {
    folder: FolderIcon,
    document: DocumentIcon,
    shield: ShieldCheckIcon,
    chat: ChatBubbleLeftRightIcon,
  }

  const Icon = icons[icon]

  return (
    <div className="card p-6">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <Icon className="h-8 w-8 text-primary-600" />
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
            <dd className="flex items-baseline">
              <div className="text-2xl font-semibold text-gray-900">{value.toLocaleString()}</div>
              <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                change >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {change >= 0 ? '+' : ''}{change}%
              </div>
            </dd>
          </dl>
        </div>
      </div>
    </div>
  )
}