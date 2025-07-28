import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useAuth } from '@/contexts/AuthContext'
import { api } from '@/services/api'
import toast from 'react-hot-toast'

interface UserSettingsProps {
  settings: any
  onUpdate: () => void
}

export function UserSettings({ settings, onUpdate }: UserSettingsProps) {
  const { user } = useAuth()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [activeSection, setActiveSection] = useState('profile')

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm({
    defaultValues: {
      email_notifications: settings?.email_notifications || true,
      sms_notifications: settings?.sms_notifications || false,
      dashboard_refresh_interval: settings?.dashboard_refresh_interval || 30,
      timezone: settings?.timezone || 'UTC',
      date_format: settings?.date_format || 'MM/DD/YYYY',
      theme: settings?.theme || 'light',
    },
  })

  const onSubmit = async (data: any) => {
    setIsSubmitting(true)
    try {
      await api.put('/settings/user', data)
      toast.success('User settings updated successfully')
      onUpdate()
    } catch (error) {
      console.error('Failed to update settings:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const timezoneOptions = [
    { value: 'UTC', label: 'UTC' },
    { value: 'America/New_York', label: 'Eastern Time' },
    { value: 'America/Chicago', label: 'Central Time' },
    { value: 'America/Denver', label: 'Mountain Time' },
    { value: 'America/Los_Angeles', label: 'Pacific Time' },
  ]

  const dateFormatOptions = [
    { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY' },
    { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY' },
    { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD' },
  ]

  const themeOptions = [
    { value: 'light', label: 'Light' },
    { value: 'dark', label: 'Dark' },
    { value: 'auto', label: 'Auto' },
  ]

  const refreshIntervalOptions = [
    { value: 10, label: '10 seconds' },
    { value: 30, label: '30 seconds' },
    { value: 60, label: '1 minute' },
    { value: 300, label: '5 minutes' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Profile Information</h3>
        <div className="bg-gray-50 p-4 rounded-lg">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-3 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Email</dt>
              <dd className="text-sm text-gray-900">{user?.email}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Role</dt>
              <dd className="text-sm text-gray-900">{user?.role}</dd>
            </div>
          </dl>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Notifications</h3>
          <div className="space-y-4">
            <label className="flex items-center">
              <input
                {...register('email_notifications')}
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700">Email notifications</span>
            </label>

            <label className="flex items-center">
              <input
                {...register('sms_notifications')}
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700">SMS notifications</span>
            </label>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Interface Preferences</h3>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label htmlFor="theme" className="block text-sm font-medium text-gray-700 mb-2">
                Theme
              </label>
              <select
                {...register('theme')}
                className="input"
              >
                {themeOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="dashboard_refresh_interval" className="block text-sm font-medium text-gray-700 mb-2">
                Dashboard Refresh
              </label>
              <select
                {...register('dashboard_refresh_interval', { valueAsNumber: true })}
                className="input"
              >
                {refreshIntervalOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Regional Settings</h3>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label htmlFor="timezone" className="block text-sm font-medium text-gray-700 mb-2">
                Timezone
              </label>
              <select
                {...register('timezone')}
                className="input"
              >
                {timezoneOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="date_format" className="block text-sm font-medium text-gray-700 mb-2">
                Date Format
              </label>
              <select
                {...register('date_format')}
                className="input"
              >
                {dateFormatOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
          <button
            type="submit"
            disabled={!isDirty || isSubmitting}
            className="btn-primary"
          >
            {isSubmitting ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  )
}