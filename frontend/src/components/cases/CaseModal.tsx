import { useState, useEffect } from 'react'
import { Dialog } from '@headlessui/react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { api } from '@/services/api'
import toast from 'react-hot-toast'

const caseSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  email: z.string().email('Invalid email address'),
  phone: z.string().min(1, 'Phone is required'),
  case_type: z.string().min(1, 'Case type is required'),
  incident_date: z.string().min(1, 'Incident date is required'),
  description: z.string().min(10, 'Description must be at least 10 characters'),
})

type CaseFormData = z.infer<typeof caseSchema>

interface CaseModalProps {
  case_: any
  isOpen: boolean
  onClose: () => void
  onSave: () => void
}

export function CaseModal({ case_, isOpen, onClose, onSave }: CaseModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const isEditing = !!case_

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CaseFormData>({
    resolver: zodResolver(caseSchema),
  })

  useEffect(() => {
    if (case_) {
      reset({
        first_name: case_.first_name || '',
        last_name: case_.last_name || '',
        email: case_.email || '',
        phone: case_.phone || '',
        case_type: case_.case_type || '',
        incident_date: case_.incident_date ? case_.incident_date.split('T')[0] : '',
        description: case_.description || '',
      })
    } else {
      reset({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        case_type: '',
        incident_date: '',
        description: '',
      })
    }
  }, [case_, reset])

  const onSubmit = async (data: CaseFormData) => {
    setIsSubmitting(true)
    try {
      if (isEditing) {
        await api.put(`/cases/${case_.id}`, data)
        toast.success('Case updated successfully')
      } else {
        await api.post('/cases', data)
        toast.success('Case created successfully')
      }
      onSave()
    } catch (error) {
      console.error('Error saving case:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const caseTypeOptions = [
    { value: 'personal_injury', label: 'Personal Injury' },
    { value: 'medical_malpractice', label: 'Medical Malpractice' },
    { value: 'product_liability', label: 'Product Liability' },
    { value: 'workers_compensation', label: 'Workers Compensation' },
    { value: 'wrongful_death', label: 'Wrongful Death' },
  ]

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black bg-opacity-25" />
      <div className="fixed inset-0 overflow-y-auto">
        <div className="flex min-h-full items-center justify-center p-4">
          <Dialog.Panel className="mx-auto max-w-md w-full bg-white rounded-lg shadow-lg">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <Dialog.Title className="text-lg font-medium">
                {isEditing ? 'Edit Case' : 'New Case'}
              </Dialog.Title>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-500"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    First Name
                  </label>
                  <input
                    {...register('first_name')}
                    className="input"
                    placeholder="John"
                  />
                  {errors.first_name && (
                    <p className="mt-1 text-sm text-red-600">{errors.first_name.message}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Last Name
                  </label>
                  <input
                    {...register('last_name')}
                    className="input"
                    placeholder="Doe"
                  />
                  {errors.last_name && (
                    <p className="mt-1 text-sm text-red-600">{errors.last_name.message}</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  {...register('email')}
                  type="email"
                  className="input"
                  placeholder="john.doe@example.com"
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone
                </label>
                <input
                  {...register('phone')}
                  className="input"
                  placeholder="(555) 123-4567"
                />
                {errors.phone && (
                  <p className="mt-1 text-sm text-red-600">{errors.phone.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Case Type
                </label>
                <select {...register('case_type')} className="input">
                  <option value="">Select case type</option>
                  {caseTypeOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                {errors.case_type && (
                  <p className="mt-1 text-sm text-red-600">{errors.case_type.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Incident Date
                </label>
                <input
                  {...register('incident_date')}
                  type="date"
                  className="input"
                />
                {errors.incident_date && (
                  <p className="mt-1 text-sm text-red-600">{errors.incident_date.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  {...register('description')}
                  rows={4}
                  className="input"
                  placeholder="Describe the incident and injuries..."
                />
                {errors.description && (
                  <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
                )}
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={onClose}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="btn-primary"
                >
                  {isSubmitting ? 'Saving...' : isEditing ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </Dialog.Panel>
        </div>
      </div>
    </Dialog>
  )
}