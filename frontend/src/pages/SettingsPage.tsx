import { useState } from 'react'
import { useQuery } from 'react-query'
import { api } from '@/services/api'
import { SystemSettings } from '@/components/settings/SystemSettings'
import { UserSettings } from '@/components/settings/UserSettings'
import { AgentSettings } from '@/components/settings/AgentSettings'
import { IntegrationSettings } from '@/components/settings/IntegrationSettings'
import { CogIcon, UserIcon, BeakerIcon, LinkIcon } from '@heroicons/react/24/outline'

export function SettingsPage() {
  const [activeTab, setActiveTab] = useState('system')

  const { data: settings, isLoading, refetch } = useQuery(
    'settings',
    () => api.get('/settings').then(res => res.data)
  )

  const tabs = [
    { id: 'system', name: 'System', icon: CogIcon },
    { id: 'user', name: 'User', icon: UserIcon },
    { id: 'agents', name: 'Agents', icon: BeakerIcon },
    { id: 'integrations', name: 'Integrations', icon: LinkIcon },
  ]

  const handleSettingsUpdate = () => {
    refetch()
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
                  settings={settings?.system}
                  onUpdate={handleSettingsUpdate}
                />
              )}
              {activeTab === 'user' && (
                <UserSettings
                  settings={settings?.user}
                  onUpdate={handleSettingsUpdate}
                />
              )}
              {activeTab === 'agents' && (
                <AgentSettings
                  settings={settings?.agents}
                  onUpdate={handleSettingsUpdate}
                />
              )}
              {activeTab === 'integrations' && (
                <IntegrationSettings
                  settings={settings?.integrations}
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