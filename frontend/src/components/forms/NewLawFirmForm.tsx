import { useState } from 'react'
import { useMutation, useQueryClient } from 'react-query'
import { api } from '../../services/api'
import toast from 'react-hot-toast'

interface NewLawFirmFormProps {
  onSuccess?: () => void
  onCancel?: () => void
}

interface LawFirmFormData {
  name: string
  legal_name: string
  website: string
  description: string
  contact_email: string
  contact_phone: string
  address_line_1: string
  address_line_2: string
  city: string
  state: string
  zip_code: string
  firm_size: string
  firm_type: string
  practice_areas: string[]
  founded_year: number
  number_of_attorneys: number
  notes: string
}

export function NewLawFirmForm({ onSuccess, onCancel }: NewLawFirmFormProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState<LawFirmFormData>({
    name: '',
    legal_name: '',
    website: '',
    description: '',
    contact_email: '',
    contact_phone: '',
    address_line_1: '',
    address_line_2: '',
    city: '',
    state: '',
    zip_code: '',
    firm_size: '',
    firm_type: '',
    practice_areas: [],
    founded_year: new Date().getFullYear(),
    number_of_attorneys: 0,
    notes: ''
  })

  // Create law firm mutation
  const createLawFirmMutation = useMutation(
    (data: LawFirmFormData) => api.post('/law-firms', {
      ...data,
      practice_areas: data.practice_areas.length > 0 ? data.practice_areas : null,
      firm_size: data.firm_size || null,
      firm_type: data.firm_type || null,
      founded_year: data.founded_year || null,
      number_of_attorneys: data.number_of_attorneys || null
    }),
    {
      onSuccess: (response) => {
        queryClient.invalidateQueries('law-firms')
        toast.success('Law firm created successfully! Pipedrive sync agent is updating CRM records.')
        console.log('Law firm created:', response.data)
        onSuccess?.()
      },
      onError: (error: any) => {
        console.error('Failed to create law firm:', error)
      }
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name || !formData.contact_email) {
      toast.error('Please fill in all required fields')
      return
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(formData.contact_email)) {
      toast.error('Please enter a valid email address')
      return
    }

    createLawFirmMutation.mutate(formData)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'founded_year' || name === 'number_of_attorneys' 
        ? parseInt(value) || 0 
        : value
    }))
  }

  const handlePracticeAreasChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const areas = e.target.value.split(',').map(area => area.trim()).filter(area => area)
    setFormData(prev => ({ ...prev, practice_areas: areas }))
  }

  const firmSizes = [
    { value: '', label: 'Select firm size...' },
    { value: 'solo', label: 'Solo Practice' },
    { value: 'small', label: 'Small (2-10 lawyers)' },
    { value: 'medium', label: 'Medium (11-50 lawyers)' },
    { value: 'large', label: 'Large (51-200 lawyers)' },
    { value: 'national', label: 'National (200+ lawyers)' }
  ]

  const firmTypes = [
    { value: '', label: 'Select practice area...' },
    { value: 'personal_injury', label: 'Personal Injury' },
    { value: 'medical_malpractice', label: 'Medical Malpractice' },
    { value: 'workers_compensation', label: 'Workers Compensation' },
    { value: 'employment', label: 'Employment Law' },
    { value: 'product_liability', label: 'Product Liability' },
    { value: 'mass_tort', label: 'Mass Tort' },
    { value: 'general_practice', label: 'General Practice' },
    { value: 'other', label: 'Other' }
  ]

  const states = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
  ]

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* AI Processing Status */}
      {createLawFirmMutation.isLoading && (
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            <div>
              <h3 className="text-sm font-medium text-blue-900">AI Processing</h3>
              <p className="text-sm text-blue-700">
                Creating law firm record and syncing with Pipedrive CRM...
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Basic Information */}
      <div>
        <h3 className="section-heading mb-4">Basic Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Firm Name *
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="input"
              placeholder="Enter firm name"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Legal Name
            </label>
            <input
              type="text"
              name="legal_name"
              value={formData.legal_name}
              onChange={handleChange}
              className="input"
              placeholder="Official legal name (if different)"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Website
            </label>
            <input
              type="url"
              name="website"
              value={formData.website}
              onChange={handleChange}
              className="input"
              placeholder="https://www.example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Founded Year
            </label>
            <input
              type="number"
              name="founded_year"
              value={formData.founded_year}
              onChange={handleChange}
              className="input"
              min="1900"
              max={new Date().getFullYear()}
            />
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description
          </label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={3}
            className="input"
            placeholder="Brief description of the law firm"
          />
        </div>
      </div>

      {/* Contact Information */}
      <div>
        <h3 className="section-heading mb-4">Contact Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Contact Email *
            </label>
            <input
              type="email"
              name="contact_email"
              value={formData.contact_email}
              onChange={handleChange}
              className="input"
              placeholder="contact@lawfirm.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Phone Number
            </label>
            <input
              type="tel"
              name="contact_phone"
              value={formData.contact_phone}
              onChange={handleChange}
              className="input"
              placeholder="(555) 123-4567"
            />
          </div>
        </div>
      </div>

      {/* Address Information */}
      <div>
        <h3 className="section-heading mb-4">Address</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Street Address
            </label>
            <input
              type="text"
              name="address_line_1"
              value={formData.address_line_1}
              onChange={handleChange}
              className="input"
              placeholder="123 Main Street"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Address Line 2
            </label>
            <input
              type="text"
              name="address_line_2"
              value={formData.address_line_2}
              onChange={handleChange}
              className="input"
              placeholder="Suite 100 (optional)"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                City
              </label>
              <input
                type="text"
                name="city"
                value={formData.city}
                onChange={handleChange}
                className="input"
                placeholder="City"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                State
              </label>
              <select
                name="state"
                value={formData.state}
                onChange={handleChange}
                className="input"
              >
                <option value="">Select state...</option>
                {states.map(state => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ZIP Code
              </label>
              <input
                type="text"
                name="zip_code"
                value={formData.zip_code}
                onChange={handleChange}
                className="input"
                placeholder="12345"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Firm Details */}
      <div>
        <h3 className="section-heading mb-4">Firm Details</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Firm Size
            </label>
            <select
              name="firm_size"
              value={formData.firm_size}
              onChange={handleChange}
              className="input"
            >
              {firmSizes.map(size => (
                <option key={size.value} value={size.value}>
                  {size.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Primary Practice Area
            </label>
            <select
              name="firm_type"
              value={formData.firm_type}
              onChange={handleChange}
              className="input"
            >
              {firmTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of Attorneys
            </label>
            <input
              type="number"
              name="number_of_attorneys"
              value={formData.number_of_attorneys}
              onChange={handleChange}
              className="input"
              min="0"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Practice Areas (comma-separated)
            </label>
            <input
              type="text"
              value={formData.practice_areas.join(', ')}
              onChange={handlePracticeAreasChange}
              className="input"
              placeholder="Personal Injury, Medical Malpractice, Auto Accidents"
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
          placeholder="Any additional information about this law firm"
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
          disabled={createLawFirmMutation.isLoading}
          className="btn-primary"
        >
          {createLawFirmMutation.isLoading ? 'Creating...' : 'Save Firm'}
        </button>
      </div>
    </form>
  )
}