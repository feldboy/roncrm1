import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { api } from '../../services/api'
import toast from 'react-hot-toast'

interface NewCaseFormProps {
  onSuccess?: () => void
  onCancel?: () => void
}

interface CaseFormData {
  title: string
  description: string
  plaintiff_id: string
  law_firm_id: string
  case_type: string
  incident_date: string
  incident_location: string
  incident_description: string
  estimated_case_value: number
  funding_amount_requested: number
  priority: string
  notes: string
}

export function NewCaseForm({ onSuccess, onCancel }: NewCaseFormProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState<CaseFormData>({
    title: '',
    description: '',
    plaintiff_id: '',
    law_firm_id: '',
    case_type: 'auto_accident',
    incident_date: '',
    incident_location: '',
    incident_description: '',
    estimated_case_value: 0,
    funding_amount_requested: 0,
    priority: 'normal',
    notes: ''
  })

  // Fetch plaintiffs for dropdown
  const { data: plaintiffsData } = useQuery(
    'plaintiffs',
    () => api.get('/plaintiffs').then(res => res.data),
    { staleTime: 5 * 60 * 1000 }
  )

  // Fetch law firms for dropdown
  const { data: lawFirmsData } = useQuery(
    'law-firms',
    () => api.get('/law-firms').then(res => res.data),
    { staleTime: 5 * 60 * 1000 }
  )

  // Create case mutation
  const createCaseMutation = useMutation(
    (data: CaseFormData) => api.post('/cases', {
      ...data,
      estimated_case_value: data.estimated_case_value * 100, // Convert to cents
      funding_amount_requested: data.funding_amount_requested * 100 // Convert to cents
    }),
    {
      onSuccess: (response) => {
        queryClient.invalidateQueries('cases')
        queryClient.invalidateQueries('dashboard-stats')
        toast.success('Case created successfully! AI agents are now processing this case.')
        console.log('Case created:', response.data)
        onSuccess?.()
      },
      onError: (error: any) => {
        console.error('Failed to create case:', error)
      }
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.title || !formData.plaintiff_id || !formData.law_firm_id) {
      toast.error('Please fill in all required fields')
      return
    }

    createCaseMutation.mutate(formData)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name.includes('amount') || name.includes('value') ? parseFloat(value) || 0 : value
    }))
  }

  const caseTypes = [
    { value: 'auto_accident', label: 'Auto Accident' },
    { value: 'slip_and_fall', label: 'Slip & Fall' },
    { value: 'medical_malpractice', label: 'Medical Malpractice' },
    { value: 'workers_compensation', label: 'Workers Compensation' },
    { value: 'product_liability', label: 'Product Liability' },
    { value: 'wrongful_death', label: 'Wrongful Death' },
    { value: 'employment', label: 'Employment' },
    { value: 'personal_injury', label: 'Personal Injury' },
    { value: 'other', label: 'Other' }
  ]

  const priorities = [
    { value: 'low', label: 'Low' },
    { value: 'normal', label: 'Normal' },
    { value: 'high', label: 'High' },
    { value: 'urgent', label: 'Urgent' }
  ]

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* AI Intake Helper */}
      <div className="p-4 bg-primary-50 rounded-lg border border-primary-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-primary-900">🤖 AI Intake Helper</h3>
            <p className="text-sm text-primary-700 mt-1">
              Paste case details from an email or form, and let AI populate the fields below
            </p>
          </div>
          <button
            type="button"
            className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            Parse with AI
          </button>
        </div>
      </div>

      {/* AI Processing Status */}
      {createCaseMutation.isLoading && (
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            <div>
              <h3 className="text-sm font-medium text-blue-900">AI Processing</h3>
              <p className="text-sm text-blue-700">
                Lead Intake Agent is analyzing this case and will trigger appropriate workflows...
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Basic Information */}
      <div>
        <h3 className="section-heading mb-4">Case Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Case Title *
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              className="input"
              placeholder="Enter case title"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Case Type *
            </label>
            <select
              name="case_type"
              value={formData.case_type}
              onChange={handleChange}
              className="input"
              required
            >
              {caseTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Plaintiff *
            </label>
            <select
              name="plaintiff_id"
              value={formData.plaintiff_id}
              onChange={handleChange}
              className="input"
              required
            >
              <option value="">Select a plaintiff...</option>
              {plaintiffsData?.plaintiffs?.map((plaintiff: any) => (
                <option key={plaintiff.id} value={plaintiff.id}>
                  {plaintiff.full_name} ({plaintiff.email})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Law Firm *
            </label>
            <select
              name="law_firm_id"
              value={formData.law_firm_id}
              onChange={handleChange}
              className="input"
              required
            >
              <option value="">Select law firm...</option>
              {lawFirmsData?.law_firms?.map((firm: any) => (
                <option key={firm.id} value={firm.id}>
                  {firm.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Priority
            </label>
            <select
              name="priority"
              value={formData.priority}
              onChange={handleChange}
              className="input"
            >
              {priorities.map(priority => (
                <option key={priority.value} value={priority.value}>
                  {priority.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Incident Date
            </label>
            <input
              type="date"
              name="incident_date"
              value={formData.incident_date}
              onChange={handleChange}
              className="input"
            />
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Case Description
          </label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={3}
            className="input"
            placeholder="Brief description of the case"
          />
        </div>
      </div>

      {/* Incident Details */}
      <div>
        <h3 className="section-heading mb-4">Incident Details</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Incident Location
            </label>
            <input
              type="text"
              name="incident_location"
              value={formData.incident_location}
              onChange={handleChange}
              className="input"
              placeholder="Where did the incident occur?"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Incident Description
            </label>
            <textarea
              name="incident_description"
              value={formData.incident_description}
              onChange={handleChange}
              rows={4}
              className="input"
              placeholder="Detailed description of what happened"
            />
          </div>
        </div>
      </div>

      {/* Financial Information */}
      <div>
        <h3 className="section-heading mb-4">Financial Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Estimated Case Value ($)
            </label>
            <input
              type="number"
              name="estimated_case_value"
              value={formData.estimated_case_value}
              onChange={handleChange}
              className="input"
              placeholder="0"
              min="0"
              step="100"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Requested Funding Amount ($)
            </label>
            <input
              type="number"
              name="funding_amount_requested"
              value={formData.funding_amount_requested}
              onChange={handleChange}
              className="input"
              placeholder="0"
              min="0"
              step="100"
            />
          </div>
        </div>
      </div>

      {/* Notes */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Additional Notes
        </label>
        <textarea
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows={3}
          className="input"
          placeholder="Any additional information about this case"
        />
      </div>

      {/* Actions */}
      <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        <button
          type="button"
          onClick={onCancel}
          className="btn-secondary"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={createCaseMutation.isLoading}
          className="btn-primary"
        >
          {createCaseMutation.isLoading ? 'Creating...' : 'Create Case'}
        </button>
      </div>
    </form>
  )
}