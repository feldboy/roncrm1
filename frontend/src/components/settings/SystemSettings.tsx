import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { api } from '@/services/api'
import toast from 'react-hot-toast'

interface SystemSettingsProps {
  settings: any
  onUpdate: () => void
}

export function SystemSettings({ settings, onUpdate }: SystemSettingsProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm({
    defaultValues: {
      log_level: settings?.log_level || 'INFO',
      max_concurrent_tasks: settings?.max_concurrent_tasks || 10,
      task_timeout: settings?.task_timeout || 300,
      enable_metrics: settings?.enable_metrics || true,
      enable_health_checks: settings?.enable_health_checks || true,
      cleanup_logs_after_days: settings?.cleanup_logs_after_days || 30,
      enable_auto_backup: settings?.enable_auto_backup || true,
      backup_retention_days: settings?.backup_retention_days || 7,
    },
  })

  const onSubmit = async (data: any) => {
    setIsSubmitting(true)
    try {
      await api.put('/settings/system', data)
      toast.success('System settings updated successfully')
      onUpdate()
    } catch (error) {
      console.error('Failed to update settings:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const logLevelOptions = [
    { value: 'DEBUG', label: 'Debug' },
    { value: 'INFO', label: 'Info' },
    { value: 'WARNING', label: 'Warning' },
    { value: 'ERROR', label: 'Error' },
  ]

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Logging & Monitoring</h3>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <label htmlFor="log_level" className="block text-sm font-medium text-gray-700 mb-2">
              Log Level
            </label>
            <select
              {...register('log_level')}
              className="input"
            >
              {logLevelOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="cleanup_logs_after_days" className="block text-sm font-medium text-gray-700 mb-2">
              Log Retention (days)
            </label>
            <input
              {...register('cleanup_logs_after_days', { 
                valueAsNumber: true,
                min: { value: 1, message: 'Must be at least 1 day' },
                max: { value: 365, message: 'Cannot exceed 365 days' }
              })}
              type="number"
              min="1"
              max="365"
              className="input"
            />
            {errors.cleanup_logs_after_days && (
              <p className="mt-1 text-sm text-red-600">{errors.cleanup_logs_after_days.message}</p>
            )}
          </div>
        </div>

        <div className="mt-4 space-y-3">
          <label className="flex items-center">
            <input
              {...register('enable_metrics')}
              type="checkbox"
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <span className="ml-2 text-sm text-gray-700">Enable metrics collection</span>
          </label>

          <label className="flex items-center">
            <input
              {...register('enable_health_checks')}
              type="checkbox"
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <span className="ml-2 text-sm text-gray-700">Enable health checks</span>
          </label>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Performance</h3>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <label htmlFor="max_concurrent_tasks" className="block text-sm font-medium text-gray-700 mb-2">
              Max Concurrent Tasks
            </label>
            <input
              {...register('max_concurrent_tasks', { 
                valueAsNumber: true,
                min: { value: 1, message: 'Must be at least 1' },
                max: { value: 100, message: 'Cannot exceed 100' }
              })}
              type="number"
              min="1"
              max="100"
              className="input"
            />
            {errors.max_concurrent_tasks && (
              <p className="mt-1 text-sm text-red-600">{errors.max_concurrent_tasks.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="task_timeout" className="block text-sm font-medium text-gray-700 mb-2">
              Task Timeout (seconds)
            </label>
            <input
              {...register('task_timeout', { 
                valueAsNumber: true,
                min: { value: 30, message: 'Must be at least 30 seconds' },
                max: { value: 3600, message: 'Cannot exceed 1 hour' }
              })}
              type="number"
              min="30"
              max="3600"
              className="input"
            />
            {errors.task_timeout && (
              <p className="mt-1 text-sm text-red-600">{errors.task_timeout.message}</p>
            )}
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Backup & Recovery</h3>
        <div className="space-y-4">
          <label className="flex items-center">
            <input
              {...register('enable_auto_backup')}
              type="checkbox"
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <span className="ml-2 text-sm text-gray-700">Enable automatic backups</span>
          </label>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label htmlFor="backup_retention_days" className="block text-sm font-medium text-gray-700 mb-2">
                Backup Retention (days)
              </label>
              <input
                {...register('backup_retention_days', { 
                  valueAsNumber: true,
                  min: { value: 1, message: 'Must be at least 1 day' },
                  max: { value: 90, message: 'Cannot exceed 90 days' }
                })}
                type="number"
                min="1"
                max="90"
                className="input"
              />
              {errors.backup_retention_days && (
                <p className="mt-1 text-sm text-red-600">{errors.backup_retention_days.message}</p>
              )}
            </div>
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
  )
}