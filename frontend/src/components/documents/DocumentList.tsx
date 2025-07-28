import { formatDistanceToNow } from 'date-fns'
import { MagnifyingGlassIcon, DocumentIcon } from '@heroicons/react/24/outline'

interface Document {
  id: string
  filename: string
  document_type: string
  file_size: number
  processing_status: string
  created_at: string
  case_id?: string
  ai_summary?: string
}

interface DocumentListProps {
  documents: Document[]
  isLoading: boolean
  onDocumentClick: (document: Document) => void
  filters: any
  onFilterChange: (filters: any) => void
  pagination: {
    page: number
    limit: number
    total: number
  }
}

export function DocumentList({
  documents,
  isLoading,
  onDocumentClick,
  filters,
  onFilterChange,
  pagination,
}: DocumentListProps) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'processing':
        return 'bg-yellow-100 text-yellow-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'pending':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return '✅'
      case 'processing':
        return '⏳'
      case 'failed':
        return '❌'
      case 'pending':
        return '⏸️'
      default:
        return '❓'
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const documentTypeOptions = [
    { value: '', label: 'All Types' },
    { value: 'medical_record', label: 'Medical Record' },
    { value: 'legal_document', label: 'Legal Document' },
    { value: 'insurance_form', label: 'Insurance Form' },
    { value: 'incident_report', label: 'Incident Report' },
    { value: 'other', label: 'Other' },
  ]

  const statusOptions = [
    { value: '', label: 'All Status' },
    { value: 'pending', label: 'Pending' },
    { value: 'processing', label: 'Processing' },
    { value: 'completed', label: 'Completed' },
    { value: 'failed', label: 'Failed' },
  ]

  if (isLoading) {
    return (
      <div className="card p-6">
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="p-4 border-b border-gray-200">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Search documents..."
                value={filters.search}
                onChange={(e) => onFilterChange({ ...filters, search: e.target.value, page: 1 })}
                className="input pl-10"
              />
            </div>
          </div>
          <div>
            <select
              value={filters.document_type}
              onChange={(e) => onFilterChange({ ...filters, document_type: e.target.value, page: 1 })}
              className="input"
            >
              {documentTypeOptions.map((option) => (
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
      </div>

      <div className="divide-y divide-gray-200">
        {documents.map((document) => (
          <div
            key={document.id}
            onClick={() => onDocumentClick(document)}
            className="p-4 hover:bg-gray-50 cursor-pointer"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <DocumentIcon className="h-8 w-8 text-gray-400" />
                <div>
                  <h3 className="text-sm font-medium text-gray-900">{document.filename}</h3>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-xs text-gray-500">{document.document_type}</span>
                    <span className="text-xs text-gray-400">•</span>
                    <span className="text-xs text-gray-500">{formatFileSize(document.file_size)}</span>
                    {document.case_id && (
                      <>
                        <span className="text-xs text-gray-400">•</span>
                        <span className="text-xs text-gray-500">Case: {document.case_id}</span>
                      </>
                    )}
                  </div>
                  {document.ai_summary && (
                    <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                      {document.ai_summary}
                    </p>
                  )}
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className="text-xs text-gray-500">
                    {formatDistanceToNow(new Date(document.created_at), { addSuffix: true })}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm">{getStatusIcon(document.processing_status)}</span>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(document.processing_status)}`}>
                    {document.processing_status}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {documents.length === 0 && (
        <div className="text-center py-12">
          <DocumentIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No documents</h3>
          <p className="mt-1 text-sm text-gray-500">Upload your first document to get started.</p>
        </div>
      )}
    </div>
  )
}