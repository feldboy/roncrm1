import { useState } from 'react'
import { useQuery, useQueryClient } from 'react-query'
import { settingsService } from '../services/settingsService'
import { SystemSettings } from '../components/settings/SystemSettings'
import { UserSettings } from '../components/settings/UserSettings'
import { AgentSettings } from '../components/settings/AgentSettings'
import { IntegrationSettings } from '../components/settings/IntegrationSettings'
import { CogIcon, UserIcon, BeakerIcon, LinkIcon, ArrowPathIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export function SettingsPage() {
  const [activeTab, setActiveTab] = useState('system')
  const [showResetConfirm, setShowResetConfirm] = useState(false)
  const queryClient = useQueryClient()

  const { data: categories, isLoading, refetch } = useQuery(
    'settings-categories',
    () => settingsService.getCategories(),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: 1, // Only retry once
      retryDelay: 1000, // Wait 1 second before retry
      onError: (error) => {
        console.log('Settings categories query failed, using fallback data:', error)
      },
      // Provide fallback data when query fails
      placeholderData: [
        {
          id: 1,
          name: "system",
          display_name: "System Settings",
          description: "Core system configuration and performance settings",
          icon: "cog",
          sort_order: 1,
          is_active: true,
          settings: []
        },
        {
          id: 2,
          name: "agents",
          display_name: "Agent Management", 
          description: "AI agent configuration and control settings",
          icon: "beaker",
          sort_order: 2,
          is_active: true,
          settings: []
        }
      ]
    }
  )

  // Generate tabs from available categories or use defaults
  const tabs = categories?.length ? categories.map(category => ({
    id: category.name,
    name: category.display_name,
    icon: getIconForCategory(category.icon || category.name),
    description: category.description
  })) : [
    { id: 'system', name: 'System', icon: CogIcon, description: 'System configuration and performance settings' },
    { id: 'user', name: 'User', icon: UserIcon, description: 'User preferences and account settings' },
    { id: 'agents', name: 'Agents', icon: BeakerIcon, description: 'AI agent configuration and management' },
    { id: 'integrations', name: 'Integrations', icon: LinkIcon, description: 'Third-party service integrations' },
  ]

  function getIconForCategory(iconName: string) {
    const iconMap: Record<string, any> = {
      'cog': CogIcon,
      'system': CogIcon,
      'user': UserIcon,
      'profile': UserIcon,
      'agents': BeakerIcon,
      'beaker': BeakerIcon,
      'integrations': LinkIcon,
      'link': LinkIcon,
    }
    return iconMap[iconName.toLowerCase()] || CogIcon
  }

  const handleSettingsUpdate = () => {
    refetch()
    queryClient.invalidateQueries(['settings-category', activeTab])
    queryClient.invalidateQueries('agent-settings')
  }

  const handleResetToDefaults = async () => {
    try {
      await settingsService.resetToDefaults(activeTab)
      toast.success(`${activeTab} settings reset to defaults`)
      handleSettingsUpdate()
      setShowResetConfirm(false)
    } catch (error: any) {
      toast.error(`Failed to reset settings: ${error.response?.data?.detail || error.message}`)
    }
  }

  const handleRefreshSettings = () => {
    queryClient.invalidateQueries('settings-categories')
    queryClient.invalidateQueries(['settings-category', activeTab])
    queryClient.invalidateQueries('agent-settings')
    toast.success('Settings refreshed')
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-sm text-gray-700">
          Configure system settings and preferences
        </p>
      </div>

      <div className="card">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-5 w-5" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {isLoading ? (
            <div className="animate-pulse space-y-6">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="space-y-3">
                  <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                  <div className="h-8 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          ) : (
            <>
              {activeTab === 'system' && (
                <SystemSettings
                  settings={categories?.find(cat => cat.name === 'system')}
                  onUpdate={handleSettingsUpdate}
                />
              )}
              {activeTab === 'user' && (
                <UserSettings
                  settings={categories?.find(cat => cat.name === 'user')}
                  onUpdate={handleSettingsUpdate}
                />
              )}
              {activeTab === 'agents' && (
                <AgentSettings
                  settings={categories?.find(cat => cat.name === 'agents')}
                  onUpdate={handleSettingsUpdate}
                />
              )}
              {activeTab === 'integrations' && (
                <IntegrationSettings
                  settings={categories?.find(cat => cat.name === 'integrations')}
                  onUpdate={handleSettingsUpdate}
                />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

// Fixed: Removed all settings references, added error handling - v2