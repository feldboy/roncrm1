import { formatDistanceToNow } from 'date-fns'
import { MagnifyingGlassIcon, EnvelopeIcon, DevicePhoneMobileIcon } from '@heroicons/react/24/outline'

interface Communication {
  id: string
  type: 'email' | 'sms'
  recipient: string
  subject?: string
  content: string
  status: string
  sent_at?: string
  created_at: string
  case_id?: string
  template_name?: string
}

interface CommunicationListProps {
  communications: Communication[]
  isLoading: boolean
  filters: any
  onFilterChange: (filters: any) => void
  pagination: {
    page: number
    limit: number
    total: number
  }
}

export function CommunicationList({
  communications,
  isLoading,
  filters,
  onFilterChange,
  pagination,
}: CommunicationListProps) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'sent':
        return 'bg-green-100 text-green-800'
      case 'delivered':
        return 'bg-blue-100 text-blue-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'draft':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getTypeIcon = (type: string) => {
    return type === 'email' ? EnvelopeIcon : DevicePhoneMobileIcon
  }

  const typeOptions = [
    { value: '', label: 'All Types' },
    { value: 'email', label: 'Email' },
    { value: 'sms', label: 'SMS' },
  ]

  const statusOptions = [
    { value: '', label: 'All Status' },
    { value: 'draft', label: 'Draft' },
    { value: 'pending', label: 'Pending' },
    { value: 'sent', label: 'Sent' },
    { value: 'delivered', label: 'Delivered' },
    { value: 'failed', label: 'Failed' },
  ]

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-20 bg-gray-200 rounded"></div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search communications..."
              value={filters.search}
              onChange={(e) => onFilterChange({ ...filters, search: e.target.value, page: 1 })}
              className="input pl-10"
            />
          </div>
        </div>
        <div>
          <select
            value={filters.type}
            onChange={(e) => onFilterChange({ ...filters, type: e.target.value, page: 1 })}
            className="input"
          >
            {typeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <select
            value={filters.status}
            onChange={(e) => onFilterChange({ ...filters, status: e.target.value, page: 1 })}
            className="input"
          >
            {statusOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="space-y-3">
        {communications.map((communication) => {
          const TypeIcon = getTypeIcon(communication.type)
          return (
            <div
              key={communication.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <TypeIcon className="h-6 w-6 text-gray-400 mt-1" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-sm font-medium text-gray-900">
                        {communication.type === 'email' ? communication.subject : 'SMS Message'}
                      </h3>
                      {communication.template_name && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {communication.template_name}
                        </span>
                      )}
                    </div>
                    <div className="mt-1 flex items-center space-x-2 text-sm text-gray-500">
                      <span>To: {communication.recipient}</span>
                      {communication.case_id && (
                        <>
                          <span>•</span>
                          <span>Case: {communication.case_id}</span>
                        </>
                      )}
                    </div>
                    <p className="mt-2 text-sm text-gray-700 line-clamp-2">
                      {communication.content}
                    </p>
                  </div>
                </div>
                <div className="flex-shrink-0 flex items-center space-x-4">
                  <div className="text-right">
                    <div className="text-xs text-gray-500">
                      {communication.sent_at
                        ? formatDistanceToNow(new Date(communication.sent_at), { addSuffix: true })
                        : formatDistanceToNow(new Date(communication.created_at), { addSuffix: true })}
                    </div>
                  </div>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(communication.status)}`}>
                    {communication.status}
                  </span>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {communications.length === 0 && (
        <div className="text-center py-12">
          <EnvelopeIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No communications</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by sending your first message.</p>
        </div>
      )}
    </div>
  )
}