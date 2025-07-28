import { useState } from 'react'
import { useQuery } from 'react-query'
import { api } from '@/services/api'
import { DocumentIcon, EyeIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline'
import { formatDistanceToNow } from 'date-fns'

interface DocumentPreviewProps {
  document: any
}

export function DocumentPreview({ document }: DocumentPreviewProps) {
  const [activeTab, setActiveTab] = useState('details')

  const { data: analysisData, isLoading: analysisLoading } = useQuery(
    ['document-analysis', document.id],
    () => api.get(`/documents/${document.id}/analysis`).then(res => res.data),
    { enabled: !!document.id }
  )

  const handleDownload = async () => {
    try {
      const response = await api.get(`/documents/${document.id}/download`, {
        responseType: 'blob',
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', document.filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  const handlePreview = () => {
    window.open(`/api/documents/${document.id}/preview`, '_blank')
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

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

  const tabs = [
    { id: 'details', name: 'Details', count: null },
    { id: 'analysis', name: 'AI Analysis', count: analysisData?.entities?.length || null },
    { id: 'extracted', name: 'Extracted Data', count: null },
  ]

  return (
    <div className="card">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <DocumentIcon className="h-10 w-10 text-gray-400" />
            <div>
              <h2 className="text-lg font-medium text-gray-900">{document.filename}</h2>
              <div className="flex items-center space-x-2 mt-1">
                <span className="text-sm text-gray-500">{document.document_type}</span>
                <span className="text-sm text-gray-400">•</span>
                <span className="text-sm text-gray-500">{formatFileSize(document.file_size)}</span>
              </div>
            </div>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={handlePreview}
              className="p-2 text-gray-400 hover:text-gray-500"
              title="Preview"
            >
              <EyeIcon className="h-5 w-5" />
            </button>
            <button
              onClick={handleDownload}
              className="p-2 text-gray-400 hover:text-gray-500"
              title="Download"
            >
              <ArrowDownTrayIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8 px-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.name}
              {tab.count !== null && (
                <span className="ml-2 bg-gray-100 text-gray-900 rounded-full py-0.5 px-2.5 text-xs">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      <div className="p-6">
        {activeTab === 'details' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-2">Processing Status</h3>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(document.processing_status)}`}>
                {document.processing_status}
              </span>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-2">Upload Information</h3>
              <dl className="grid grid-cols-1 gap-x-4 gap-y-3 sm:grid-cols-2">
                <div>
                  <dt className="text-sm text-gray-500">Uploaded</dt>
                  <dd className="text-sm text-gray-900">
                    {formatDistanceToNow(new Date(document.created_at), { addSuffix: true })}
                  </dd>
                </div>
                {document.case_id && (
                  <div>
                    <dt className="text-sm text-gray-500">Associated Case</dt>
                    <dd className="text-sm text-gray-900">{document.case_id}</dd>
                  </div>
                )}
                <div>
                  <dt className="text-sm text-gray-500">File Type</dt>
                  <dd className="text-sm text-gray-900">{document.mime_type || 'Unknown'}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">File Size</dt>
                  <dd className="text-sm text-gray-900">{formatFileSize(document.file_size)}</dd>
                </div>
              </dl>
            </div>

            {document.ai_summary && (
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-2">AI Summary</h3>
                <p className="text-sm text-gray-700">{document.ai_summary}</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="space-y-4">
            {analysisLoading ? (
              <div className="animate-pulse space-y-3">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3"></div>
              </div>
            ) : analysisData ? (
              <>
                {analysisData.entities && analysisData.entities.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 mb-2">Extracted Entities</h3>
                    <div className="space-y-2">
                      {analysisData.entities.map((entity: any, index: number) => (
                        <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                          <span className="text-sm text-gray-900">{entity.text}</span>
                          <span className="text-xs text-gray-500 bg-white px-2 py-1 rounded">
                            {entity.label}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {analysisData.confidence_score && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 mb-2">Confidence Score</h3>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full"
                          style={{ width: `${analysisData.confidence_score}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-600">{analysisData.confidence_score}%</span>
                    </div>
                  </div>
                )}

                {analysisData.classification && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 mb-2">Document Classification</h3>
                    <p className="text-sm text-gray-700">{analysisData.classification}</p>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-8">
                <p className="text-sm text-gray-500">No analysis data available</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'extracted' && (
          <div className="space-y-4">
            {analysisData?.extracted_data ? (
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-2">Extracted Text</h3>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                    {analysisData.extracted_data.text || 'No text extracted'}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-sm text-gray-500">No extracted data available</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}