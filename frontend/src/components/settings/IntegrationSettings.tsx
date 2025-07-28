import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { api } from '@/services/api'
import toast from 'react-hot-toast'
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'

interface IntegrationSettingsProps {
  settings: any
  onUpdate: () => void
}

export function IntegrationSettings({ settings, onUpdate }: IntegrationSettingsProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showSecrets, setShowSecrets] = useState<{ [key: string]: boolean }>({})

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm({
    defaultValues: {
      // Pipedrive
      pipedrive_api_token: settings?.pipedrive?.api_token || '',
      pipedrive_base_url: settings?.pipedrive?.base_url || 'https://api.pipedrive.com/v1',
      pipedrive_webhook_secret: settings?.pipedrive?.webhook_secret || '',
      
      // OpenAI
      openai_api_key: settings?.openai?.api_key || '',
      openai_model: settings?.openai?.model || 'gpt-3.5-turbo',
      openai_max_tokens: settings?.openai?.max_tokens || 1000,
      
      // Twilio
      twilio_account_sid: settings?.twilio?.account_sid || '',
      twilio_auth_token: settings?.twilio?.auth_token || '',
      twilio_phone_number: settings?.twilio?.phone_number || '',
      
      // Email (SMTP)
      smtp_host: settings?.smtp?.host || '',
      smtp_port: settings?.smtp?.port || 587,
      smtp_username: settings?.smtp?.username || '',
      smtp_password: settings?.smtp?.password || '',
      smtp_use_tls: settings?.smtp?.use_tls || true,
    },
  })

  const onSubmit = async (data: any) => {
    setIsSubmitting(true)
    try {
      await api.put('/settings/integrations', data)
      toast.success('Integration settings updated successfully')
      onUpdate()
    } catch (error) {
      console.error('Failed to update settings:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const toggleSecretVisibility = (field: string) => {
    setShowSecrets(prev => ({ ...prev, [field]: !prev[field] }))
  }

  const testConnection = async (integration: string) => {
    try {
      await api.post(`/integrations/${integration}/test`)
      toast.success(`${integration} connection successful`)
    } catch (error) {
      toast.error(`${integration} connection failed`)
    }
  }

  const openaiModels = [
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
    { value: 'gpt-4', label: 'GPT-4' },
    { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
  ]

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
      {/* Pipedrive Integration */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Pipedrive CRM</h3>
          <button
            type="button"
            onClick={() => testConnection('pipedrive')}
            className="btn-secondary text-sm"
          >
            Test Connection
          </button>
        </div>
        
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <label htmlFor="pipedrive_api_token" className="block text-sm font-medium text-gray-700 mb-2">
              API Token
            </label>
            <div className="relative">
              <input
                {...register('pipedrive_api_token')}
                type={showSecrets.pipedrive_api_token ? 'text' : 'password'}
                className="input pr-10"
                placeholder="Enter Pipedrive API token"
              />
              <button
                type="button"
                onClick={() => toggleSecretVisibility('pipedrive_api_token')}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                {showSecrets.pipedrive_api_token ? (
                  <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                ) : (
                  <EyeIcon className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
          </div>

          <div>
            <label htmlFor="pipedrive_base_url" className="block text-sm font-medium text-gray-700 mb-2">
              Base URL
            </label>
            <input
              {...register('pipedrive_base_url')}
              type="url"
              className="input"
              placeholder="https://api.pipedrive.com/v1"
            />
          </div>

          <div className="sm:col-span-2">
            <label htmlFor="pipedrive_webhook_secret" className="block text-sm font-medium text-gray-700 mb-2">
              Webhook Secret
            </label>
            <div className="relative">
              <input
                {...register('pipedrive_webhook_secret')}
                type={showSecrets.pipedrive_webhook_secret ? 'text' : 'password'}
                className="input pr-10"
                placeholder="Enter webhook secret"
              />
              <button
                type="button"
                onClick={() => toggleSecretVisibility('pipedrive_webhook_secret')}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                {showSecrets.pipedrive_webhook_secret ? (
                  <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                ) : (
                  <EyeIcon className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* OpenAI Integration */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">OpenAI</h3>
          <button
            type="button"
            onClick={() => testConnection('openai')}
            className="btn-secondary text-sm"
          >
            Test Connection
          </button>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <label htmlFor="openai_api_key" className="block text-sm font-medium text-gray-700 mb-2">
              API Key
            </label>
            <div className="relative">
              <input
                {...register('openai_api_key')}
                type={showSecrets.openai_api_key ? 'text' : 'password'}
                className="input pr-10"
                placeholder="Enter OpenAI API key"
              />
              <button
                type="button"
                onClick={() => toggleSecretVisibility('openai_api_key')}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                {showSecrets.openai_api_key ? (
                  <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                ) : (
                  <EyeIcon className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
          </div>

          <div>
            <label htmlFor="openai_model" className="block text-sm font-medium text-gray-700 mb-2">
              Model
            </label>
            <select
              {...register('openai_model')}
              className="input"
            >
              {openaiModels.map((model) => (
                <option key={model.value} value={model.value}>
                  {model.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="openai_max_tokens" className="block text-sm font-medium text-gray-700 mb-2">
              Max Tokens
            </label>
            <input
              {...register('openai_max_tokens', { 
                valueAsNumber: true,
                min: { value: 100, message: 'Must be at least 100' },
                max: { value: 4000, message: 'Cannot exceed 4000' }
              })}
              type="number"
              min="100"
              max="4000"
              className="input"
            />
            {errors.openai_max_tokens && (
              <p className="mt-1 text-sm text-red-600">{errors.openai_max_tokens.message}</p>
            )}
          </div>
        </div>
      </div>

      {/* Twilio Integration */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Twilio SMS</h3>
          <button
            type="button"
            onClick={() => testConnection('twilio')}
            className="btn-secondary text-sm"
          >
            Test Connection
          </button>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <label htmlFor="twilio_account_sid" className="block text-sm font-medium text-gray-700 mb-2">
              Account SID
            </label>
            <input
              {...register('twilio_account_sid')}
              className="input"
              placeholder="Enter Twilio Account SID"
            />
          </div>

          <div>
            <label htmlFor="twilio_auth_token" className="block text-sm font-medium text-gray-700 mb-2">
              Auth Token
            </label>
            <div className="relative">
              <input
                {...register('twilio_auth_token')}
                type={showSecrets.twilio_auth_token ? 'text' : 'password'}
                className="input pr-10"
                placeholder="Enter Twilio Auth Token"
              />
              <button
                type="button"
                onClick={() => toggleSecretVisibility('twilio_auth_token')}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                {showSecrets.twilio_auth_token ? (
                  <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                ) : (
                  <EyeIcon className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
          </div>

          <div className="sm:col-span-2">
            <label htmlFor="twilio_phone_number" className="block text-sm font-medium text-gray-700 mb-2">
              Phone Number
            </label>
            <input
              {...register('twilio_phone_number')}
              type="tel"
              className="input"
              placeholder="+1234567890"
            />
          </div>
        </div>
      </div>

      {/* SMTP Integration */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Email (SMTP)</h3>
          <button
            type="button"
            onClick={() => testConnection('smtp')}
            className="btn-secondary text-sm"
          >
            Test Connection
          </button>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <label htmlFor="smtp_host" className="block text-sm font-medium text-gray-700 mb-2">
              SMTP Host
            </label>
            <input
              {...register('smtp_host')}
              className="input"
              placeholder="smtp.gmail.com"
            />
          </div>

          <div>
            <label htmlFor="smtp_port" className="block text-sm font-medium text-gray-700 mb-2">
              SMTP Port
            </label>
            <input
              {...register('smtp_port', { valueAsNumber: true })}
              type="number"
              min="1"
              max="65535"
              className="input"
              placeholder="587"
            />
          </div>

          <div>
            <label htmlFor="smtp_username" className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              {...register('smtp_username')}
              className="input"
              placeholder="your-email@gmail.com"
            />
          </div>

          <div>
            <label htmlFor="smtp_password" className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <div className="relative">
              <input
                {...register('smtp_password')}
                type={showSecrets.smtp_password ? 'text' : 'password'}
                className="input pr-10"
                placeholder="Enter email password"
              />
              <button
                type="button"
                onClick={() => toggleSecretVisibility('smtp_password')}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                {showSecrets.smtp_password ? (
                  <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                ) : (
                  <EyeIcon className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
          </div>

          <div className="sm:col-span-2">
            <label className="flex items-center">
              <input
                {...register('smtp_use_tls')}
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700">Use TLS encryption</span>
            </label>
          </div>
        </div>
      </div>

      <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
        <button
          type="submit"
          disabled={!isDirty || isSubmitting}
          className="btn-primary"
        >
          {isSubmitting ? 'Saving...' : 'Save Integration Settings'}
        </button>
      </div>
    </form>
  )
}