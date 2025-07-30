import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { api } from '@/services/api'
import toast from 'react-hot-toast'
import { EnvelopeIcon, DevicePhoneMobileIcon } from '@heroicons/react/24/outline'

const emailSchema = z.object({
  type: z.literal('email'),
  recipient: z.string().email('Invalid email address'),
  subject: z.string().min(1, 'Subject is required'),
  content: z.string().min(1, 'Content is required'),
  case_id: z.string().optional(),
})

const smsSchema = z.object({
  type: z.literal('sms'),
  recipient: z.string().min(10, 'Phone number must be at least 10 digits'),
  content: z.string().min(1, 'Content is required').max(160, 'SMS content cannot exceed 160 characters'),
  case_id: z.string().optional(),
})

const communicationSchema = z.discriminatedUnion('type', [emailSchema, smsSchema])

type CommunicationFormData = z.infer<typeof communicationSchema>

interface CommunicationComposerProps {
  template?: any
  onSent: () => void
  onCancel: () => void
}

export function CommunicationComposer({ template, onSent, onCancel }: CommunicationComposerProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [communicationType, setCommunicationType] = useState<'email' | 'sms'>('email')

  const {
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors },
  } = useForm<CommunicationFormData>({
    resolver: zodResolver(communicationSchema),
    defaultValues: {
      type: 'email',
      recipient: '',
      subject: '',
      content: '',
      case_id: '',
    },
  })

  const watchedContent = watch('content')

  useEffect(() => {
    if (template) {
      setCommunicationType(template.type || 'email')
      reset({
        type: template.type || 'email',
        recipient: '',
        subject: template.subject || '',
        content: template.content || '',
        case_id: '',
      })
    }
  }, [template, reset])

  useEffect(() => {
    setValue('type', communicationType)
  }, [communicationType, setValue])

  const onSubmit = async (data: CommunicationFormData) => {
    setIsSubmitting(true)
    try {
      await api.post('/communications/send', data)
      toast.success(`${data.type === 'email' ? 'Email' : 'SMS'} sent successfully`)
      onSent()
    } catch (error) {
      console.error('Failed to send communication:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSaveDraft = async () => {
    setIsSubmitting(true)
    try {
      const data = watch()
      await api.post('/communications/draft', data)
      toast.success('Draft saved successfully')
      onSent()
    } catch (error) {
      console.error('Failed to save draft:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Communication Type
        </label>
        <div className="flex space-x-4">
          <button
            type="button"
            onClick={() => setCommunicationType('email')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-colors ${
              communicationType === 'email'
                ? 'bg-primary-50 border-primary-200 text-primary-700'
                : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            <EnvelopeIcon className="h-5 w-5" />
            <span>Email</span>
          </button>
          <button
            type="button"
            onClick={() => setCommunicationType('sms')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-colors ${
              communicationType === 'sms'
                ? 'bg-primary-50 border-primary-200 text-primary-700'
                : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            <DevicePhoneMobileIcon className="h-5 w-5" />
            <span>SMS</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <label htmlFor="recipient" className="block text-sm font-medium text-gray-700 mb-1">
            {communicationType === 'email' ? 'Email Address' : 'Phone Number'}
          </label>
          <input
            {...register('recipient')}
            type={communicationType === 'email' ? 'email' : 'tel'}
            className="input"
            placeholder={
              communicationType === 'email' ? 'recipient@example.com' : '+1 (555) 123-4567'
            }
          />
          {errors.recipient && (
            <p className="mt-1 text-sm text-red-600">{errors.recipient.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="case_id" className="block text-sm font-medium text-gray-700 mb-1">
            Case ID (Optional)
          </label>
          <input
            {...register('case_id')}
            className="input"
            placeholder="Associate with case"
          />
        </div>
      </div>

      {communicationType === 'email' && (
        <div>
          <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
            Subject
          </label>
          <input
            {...register('subject')}
            className="input"
            placeholder="Email subject"
          />
          {errors.subject && communicationType === 'email' && (
            <p className="mt-1 text-sm text-red-600">{(errors.subject as any)?.message}</p>
          )}
        </div>
      )}

      <div>
        <div className="flex justify-between items-center mb-1">
          <label htmlFor="content" className="block text-sm font-medium text-gray-700">
            {communicationType === 'email' ? 'Email Content' : 'Message'}
          </label>
          {communicationType === 'sms' && (
            <span className={`text-xs ${
              watchedContent?.length > 160 ? 'text-red-600' : 'text-gray-500'
            }`}>
              {watchedContent?.length || 0}/160
            </span>
          )}
        </div>
        <textarea
          {...register('content')}
          rows={communicationType === 'email' ? 8 : 4}
          className="input"
          placeholder={
            communicationType === 'email'
              ? 'Enter your email content...'
              : 'Enter your SMS message...'
          }
        />
        {errors.content && (
          <p className="mt-1 text-sm text-red-600">{errors.content.message}</p>
        )}
      </div>

      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="btn-secondary"
        >
          Cancel
        </button>
        <button
          type="button"
          onClick={handleSaveDraft}
          disabled={isSubmitting}
          className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
        >
          Save Draft
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="btn-primary"
        >
          {isSubmitting ? 'Sending...' : `Send ${communicationType === 'email' ? 'Email' : 'SMS'}`}
        </button>
      </div>
    </form>
  )
}