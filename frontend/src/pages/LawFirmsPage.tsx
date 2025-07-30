import { useState } from 'react'
import { useQuery } from 'react-query'
import { PlusIcon } from '@heroicons/react/24/outline'
import { api } from '../services/api'
import { FormModal } from '../components/forms/FormModal'
import { NewLawFirmForm } from '../components/forms/NewLawFirmForm'

export function LawFirmsPage() {
  const [isNewLawFirmModalOpen, setIsNewLawFirmModalOpen] = useState(false)

  // Fetch law firms data
  const { data: lawFirmsData, isLoading } = useQuery(
    'law-firms',
    () => api.get('/law-firms').then(res => res.data),
    { refetchInterval: 30000 }
  )
  const lawFirms = [
    {
      id: 1,
      name: 'Johnson & Associates',
      email: 'contact@johnsonlaw.com',
      phone: '(555) 123-4567',
      website: 'www.johnsonlaw.com',
      address: '123 Legal Street, Law City, LC 12345',
      practiceAreas: 'Personal Injury, Auto Accidents, Slip & Fall',
      partnershipStatus: 'Active',
      referralFee: '15%',
      totalReferrals: 25,
      activeReferrals: 8
    },
    {
      id: 2,
      name: 'Smith Legal Group',
      email: 'info@smithlegal.com',
      phone: '(555) 987-6543',
      website: 'www.smithlegal.com',
      address: '456 Attorney Ave, Legal Town, LT 67890',
      practiceAreas: 'Medical Malpractice, Workers Compensation',
      partnershipStatus: 'Active',
      referralFee: '12%',
      totalReferrals: 18,
      activeReferrals: 3
    },
    {
      id: 3,
      name: 'Davis & Partners LLP',
      email: 'admin@davispartners.com',
      phone: '(555) 555-0123',
      website: 'www.davispartners.com',
      address: '789 Lawyer Lane, Court City, CC 54321',
      practiceAreas: 'Mass Torts, Class Action, Product Liability',
      partnershipStatus: 'Pending',
      referralFee: '20%',
      totalReferrals: 0,
      activeReferrals: 0
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'inactive':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="page-heading">Law Firms</h1>
          <p className="page-subtitle">
            Manage partner firms and legal professionals
          </p>
        </div>
        <button 
          onClick={() => setIsNewLawFirmModalOpen(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <PlusIcon className="h-5 w-5" />
          <span>Add Law Firm</span>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="flex space-x-4">
        <div className="flex-1 max-w-md">
          <input
            type="text"
            placeholder="Search by firm name or practice area..."
            className="input"
          />
        </div>
        <select className="input max-w-48">
          <option>All Statuses</option>
          <option>Active</option>
          <option>Pending</option>
          <option>Inactive</option>
        </select>
      </div>

      {/* Law Firm Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {isLoading && (
          <div className="col-span-full flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        )}
        
        {lawFirmsData?.law_firms?.length === 0 && !isLoading && (
          <div className="col-span-full text-center py-12">
            <p className="text-gray-500 mb-4">No law firms found</p>
            <button 
              onClick={() => setIsNewLawFirmModalOpen(true)}
              className="btn-primary"
            >
              Add your first law firm
            </button>
          </div>
        )}

        {lawFirmsData?.law_firms?.map((firm: any) => (
          <div key={firm.id} className="case-card">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{firm.name}</h3>
                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusColor(firm.is_active ? 'active' : 'inactive')} mt-1`}>
                  {firm.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <button className="text-gray-400 hover:text-gray-600">
                <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                </svg>
              </button>
            </div>

            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Phone:</span>
                  <div className="font-medium">{firm.contact_phone || 'Not provided'}</div>
                </div>
                <div>
                  <span className="text-gray-500">Email:</span>
                  <div className="font-medium">{firm.contact_email}</div>
                </div>
              </div>

              {firm.website && (
                <div className="text-sm">
                  <span className="text-gray-500">Website:</span>
                  <div className="font-medium text-primary-600">{firm.website}</div>
                </div>
              )}

              {firm.full_address && (
                <div className="text-sm">
                  <span className="text-gray-500">Address:</span>
                  <div className="font-medium">{firm.full_address}</div>
                </div>
              )}

              {firm.practice_areas && firm.practice_areas.length > 0 && (
                <div className="text-sm">
                  <span className="text-gray-500">Practice Areas:</span>
                  <div className="font-medium">{firm.practice_areas.join(', ')}</div>
                </div>
              )}

              <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
                <div className="text-center">
                  <div className="text-lg font-bold text-gray-900">{firm.approval_rate || 'N/A'}</div>
                  <div className="text-xs text-gray-500">Approval Rate</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-gray-900">{firm.total_cases_referred || 0}</div>
                  <div className="text-xs text-gray-500">Total Referrals</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-primary-600">{firm.total_cases_funded || 0}</div>
                  <div className="text-xs text-gray-500">Funded Cases</div>
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Keep old mock data for reference */}
        {!lawFirmsData && !isLoading && lawFirms.map((firm) => (
          <div key={firm.id} className="case-card">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{firm.name}</h3>
                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusColor(firm.partnershipStatus)} mt-1`}>
                  {firm.partnershipStatus}
                </span>
              </div>
              <button className="text-gray-400 hover:text-gray-600">
                <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                </svg>
              </button>
            </div>

            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Phone:</span>
                  <div className="font-medium">{firm.phone}</div>
                </div>
                <div>
                  <span className="text-gray-500">Email:</span>
                  <div className="font-medium">{firm.email}</div>
                </div>
              </div>

              <div className="text-sm">
                <span className="text-gray-500">Website:</span>
                <div className="font-medium text-primary-600">{firm.website}</div>
              </div>

              <div className="text-sm">
                <span className="text-gray-500">Address:</span>
                <div className="font-medium">{firm.address}</div>
              </div>

              <div className="text-sm">
                <span className="text-gray-500">Practice Areas:</span>
                <div className="font-medium">{firm.practiceAreas}</div>
              </div>

              <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
                <div className="text-center">
                  <div className="text-lg font-bold text-gray-900">{firm.referralFee}</div>
                  <div className="text-xs text-gray-500">Referral Fee</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-gray-900">{firm.totalReferrals}</div>
                  <div className="text-xs text-gray-500">Total Referrals</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-primary-600">{firm.activeReferrals}</div>
                  <div className="text-xs text-gray-500">Active Cases</div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* New Law Firm Modal */}
      <FormModal
        isOpen={isNewLawFirmModalOpen}
        onClose={() => setIsNewLawFirmModalOpen(false)}
        title="New Law Firm"
        subtitle="Add a new law firm partner"
      >
        <NewLawFirmForm
          onSuccess={() => setIsNewLawFirmModalOpen(false)}
          onCancel={() => setIsNewLawFirmModalOpen(false)}
        />
      </FormModal>
    </div>
  )
}