import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'

interface CaseFiltersProps {
  filters: {
    status: string
    case_type: string
    search: string
  }
  onFilterChange: (filters: any) => void
}

export function CaseFilters({ filters, onFilterChange }: CaseFiltersProps) {
  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'active', label: 'Active' },
    { value: 'pending', label: 'Pending' },
    { value: 'closed', label: 'Closed' },
    { value: 'rejected', label: 'Rejected' },
  ]

  const caseTypeOptions = [
    { value: '', label: 'All Types' },
    { value: 'personal_injury', label: 'Personal Injury' },
    { value: 'medical_malpractice', label: 'Medical Malpractice' },
    { value: 'product_liability', label: 'Product Liability' },
    { value: 'workers_compensation', label: 'Workers Compensation' },
    { value: 'wrongful_death', label: 'Wrongful Death' },
  ]

  return (
    <div className="card p-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div>
          <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
            Search
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              id="search"
              placeholder="Search by name, email, or phone..."
              value={filters.search}
              onChange={(e) => onFilterChange({ search: e.target.value })}
              className="input pl-10"
            />
          </div>
        </div>

        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-2">
            Status
          </label>
          <select
            id="status"
            value={filters.status}
            onChange={(e) => onFilterChange({ status: e.target.value })}
            className="input"
          >
            {statusOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="case_type" className="block text-sm font-medium text-gray-700 mb-2">
            Case Type
          </label>
          <select
            id="case_type"
            value={filters.case_type}
            onChange={(e) => onFilterChange({ case_type: e.target.value })}
            className="input"
          >
            {caseTypeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  )
}