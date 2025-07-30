import { useState } from 'react'
import { useQuery } from 'react-query'
import { PlusIcon } from '@heroicons/react/24/outline'
import { api } from '../services/api'
import { FormModal } from '../components/forms/FormModal'
import { NewCaseForm } from '../components/forms/NewCaseForm'

export function PlaintiffsPage() {
  const [isNewCaseModalOpen, setIsNewCaseModalOpen] = useState(false)

  // Fetch plaintiffs data
  const { data: plaintiffsData, isLoading } = useQuery(
    'plaintiffs',
    () => api.get('/plaintiffs').then(res => res.data),
    { refetchInterval: 30000 }
  )
  const plaintiffCases = [
    {
      id: 1,
      name: 'Michael Rodriguez',
      caseType: 'Auto Accident',
      stage: 'document collection',
      priority: 'medium',
      phone: '(555) 111-2222',
      email: 'm.rodriguez@email.com',
      appliedDate: 'Nov 1, 2024',
      requestedAmount: 25000,
      description: 'Rear-ended at traffic light, sustained neck and back injuries. Other driver at fault. Currently undergoing physical therapy.',
      documentsNeeded: ['Police Report', 'Medical Records', 'Insurance Claim'],
      documentsReceived: ['Initial Application', 'Photo ID']
    },
    {
      id: 2,
      name: 'Sarah Thompson',
      caseType: 'Slip & Fall',
      stage: 'under review',
      priority: 'low',
      phone: '(555) 333-4444',
      email: 'sarah.t@email.com',
      appliedDate: 'Oct 25, 2024',
      requestedAmount: 15000,
      description: 'Slipped on wet floor at grocery store, fractured wrist. Store had no warning signs posted.',
      documentsNeeded: ['Incident Report'],
      documentsReceived: ['Medical Records']
    }
  ]

  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'document collection':
        return 'bg-yellow-100 text-yellow-800'
      case 'under review':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800'
      case 'medium':
        return 'bg-blue-100 text-blue-800'
      case 'low':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="page-heading">Plaintiff Cases</h1>
          <p className="page-subtitle">
            Manage your pre-settlement funding leads
          </p>
        </div>
        <button 
          onClick={() => setIsNewCaseModalOpen(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <PlusIcon className="h-5 w-5" />
          <span>New Case</span>
        </button>
      </div>

      {/* Filters */}
      <div className="flex space-x-4">
        <select className="input max-w-48">
          <option>All Stages</option>
          <option>Intake</option>
          <option>Document Collection</option>
          <option>Under Review</option>
          <option>Approved</option>
        </select>
        <select className="input max-w-48">
          <option>All Priority</option>
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
        </select>
        <select className="input max-w-48">
          <option>All Types</option>
          <option>Auto Accident</option>
          <option>Slip & Fall</option>
          <option>Medical Malpractice</option>
        </select>
      </div>

      {/* Case Cards */}
      <div className="space-y-4">
        {isLoading && (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        )}
        
        {plaintiffsData?.plaintiffs?.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">No plaintiff cases found</p>
            <button 
              onClick={() => setIsNewCaseModalOpen(true)}
              className="btn-primary"
            >
              Create your first case
            </button>
          </div>
        )}

        {plaintiffsData?.plaintiffs?.map((plaintiff: any) => (
          <div key={plaintiff.id} className="case-card">
            <div className="flex justify-between items-start mb-4">
              <div className="flex space-x-3">
                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getStageColor(plaintiff.case_status)}`}>
                  {plaintiff.case_status.replace('_', ' ')}
                </span>
                <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-gray-100 text-gray-800">
                  {plaintiff.case_type.replace('_', ' ')}
                </span>
              </div>
              <button className="text-gray-400 hover:text-gray-600">
                <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                </svg>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{plaintiff.full_name}</h3>
                <div className="space-y-1 text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <span>📞</span>
                    <span>{plaintiff.phone || 'No phone'}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>✉️</span>
                    <span>{plaintiff.email}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>📅</span>
                    <span>Applied: {new Date(plaintiff.created_at).toLocaleDateString()}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>🏢</span>
                    <span>{plaintiff.law_firm_name || 'No law firm assigned'}</span>
                  </div>
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-700 mb-4">{plaintiff.case_description || 'No description available'}</p>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Income:</h4>
                    <p className="text-sm text-green-600">
                      ${plaintiff.monthly_income ? plaintiff.monthly_income.toLocaleString() : 'Not provided'}
                    </p>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Risk Score:</h4>
                    <p className={`text-sm ${plaintiff.risk_score && plaintiff.risk_score > 0.7 
                      ? 'text-red-600' 
                      : plaintiff.risk_score && plaintiff.risk_score > 0.4 
                      ? 'text-yellow-600' 
                      : 'text-green-600'
                    }`}>
                      {plaintiff.risk_score ? `${(plaintiff.risk_score * 100).toFixed(0)}%` : 'Not assessed'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Keep the old mock data temporarily for UI reference */}
        {!plaintiffsData && !isLoading && plaintiffCases.map((case_) => (
          <div key={case_.id} className="case-card">
            <div className="flex justify-between items-start mb-4">
              <div className="flex space-x-3">
                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getStageColor(case_.stage)}`}>
                  {case_.stage}
                </span>
                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getPriorityColor(case_.priority)}`}>
                  {case_.priority} Priority
                </span>
                <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-gray-100 text-gray-800">
                  {case_.caseType}
                </span>
              </div>
              <button className="text-gray-400 hover:text-gray-600">
                <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                </svg>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{case_.name}</h3>
                <div className="space-y-1 text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <span>📞</span>
                    <span>{case_.phone}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>✉️</span>
                    <span>{case_.email}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>📅</span>
                    <span>Applied: {case_.appliedDate}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>💰</span>
                    <span>Requested: ${case_.requestedAmount.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-700 mb-4">{case_.description}</p>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Documents Needed:</h4>
                    <ul className="space-y-1">
                      {case_.documentsNeeded.map((doc, index) => (
                        <li key={index} className="text-sm text-red-600">• {doc}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Documents Received:</h4>
                    <ul className="space-y-1">
                      {case_.documentsReceived.map((doc, index) => (
                        <li key={index} className="text-sm text-green-600">• {doc}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* New Case Modal */}
      <FormModal
        isOpen={isNewCaseModalOpen}
        onClose={() => setIsNewCaseModalOpen(false)}
        title="New Case"
        subtitle="Create a new case for pre-settlement funding"
      >
        <NewCaseForm
          onSuccess={() => setIsNewCaseModalOpen(false)}
          onCancel={() => setIsNewCaseModalOpen(false)}
        />
      </FormModal>
    </div>
  )
}