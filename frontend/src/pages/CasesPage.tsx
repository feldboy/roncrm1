import { useState } from 'react'
import { useQuery } from 'react-query'
import { api } from '@/services/api'
import { CaseTable } from '@/components/cases/CaseTable'
import { CaseFilters } from '@/components/cases/CaseFilters'
import { CaseModal } from '@/components/cases/CaseModal'
import { PlusIcon } from '@heroicons/react/24/outline'

export function CasesPage() {
  const [filters, setFilters] = useState({
    status: '',
    case_type: '',
    search: '',
    page: 1,
    limit: 20,
  })
  const [selectedCase, setSelectedCase] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const { data: casesData, isLoading, refetch } = useQuery(
    ['cases', filters],
    () => api.get('/cases', { params: filters }).then(res => res.data),
    { keepPreviousData: true }
  )

  const handleFilterChange = (newFilters: any) => {
    setFilters(prev => ({ ...prev, ...newFilters, page: 1 }))
  }

  const handleCaseClick = (case_: any) => {
    setSelectedCase(case_)
    setIsModalOpen(true)
  }

  const handleNewCase = () => {
    setSelectedCase(null)
    setIsModalOpen(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Cases</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage plaintiff cases and track progress
          </p>
        </div>
        <button
          onClick={handleNewCase}
          className="btn-primary flex items-center space-x-2"
        >
          <PlusIcon className="h-5 w-5" />
          <span>New Case</span>
        </button>
      </div>

      <CaseFilters
        filters={filters}
        onFilterChange={handleFilterChange}
      />

      <div className="card">
        <CaseTable
          cases={casesData?.cases || []}
          isLoading={isLoading}
          onCaseClick={handleCaseClick}
          pagination={{
            page: filters.page,
            limit: filters.limit,
            total: casesData?.total || 0,
          }}
          onPageChange={(page) => setFilters(prev => ({ ...prev, page }))}
        />
      </div>

      <CaseModal
        case_={selectedCase}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={() => {
          refetch()
          setIsModalOpen(false)
        }}
      />
    </div>
  )
}