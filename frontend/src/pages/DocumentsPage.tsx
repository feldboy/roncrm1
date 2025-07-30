import { useState } from 'react'
import { useQuery } from 'react-query'
import { api } from '../services/api'
import { DocumentUpload } from '../components/documents/DocumentUpload'
import { DocumentList } from '../components/documents/DocumentList'
import { DocumentPreview } from '../components/documents/DocumentPreview'
import { CloudArrowUpIcon } from '@heroicons/react/24/outline'

export function DocumentsPage() {
  const [selectedDocument, setSelectedDocument] = useState(null)
  const [filters, setFilters] = useState({
    search: '',
    document_type: '',
    status: '',
    page: 1,
    limit: 20,
  })

  const { data: documentsData, isLoading, refetch } = useQuery(
    ['documents', filters],
    () => api.get('/documents', { params: filters }).then(res => res.data),
    { keepPreviousData: true }
  )

  const handleUploadSuccess = () => {
    refetch()
  }

  const handleDocumentClick = (document: any) => {
    setSelectedDocument(document)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-heading">Document Center</h1>
        <p className="page-subtitle">
          Upload and manage case documents
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="card p-6">
            <h2 className="section-heading mb-4">Upload New Document</h2>
            <DocumentUpload onUploadSuccess={handleUploadSuccess} />
          </div>

          <DocumentList
            documents={documentsData?.documents || []}
            isLoading={isLoading}
            onDocumentClick={handleDocumentClick}
            filters={filters}
            onFilterChange={setFilters}
            pagination={{
              page: filters.page,
              limit: filters.limit,
              total: documentsData?.total || 0,
            }}
          />
        </div>

        <div className="space-y-6">
          {selectedDocument ? (
            <DocumentPreview document={selectedDocument} />
          ) : (
            <div className="card p-6">
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-sm font-medium text-gray-900">No document selected</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Select a document to view details and processing results
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}