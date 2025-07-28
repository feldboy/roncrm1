import { useState } from 'react'
import { useQuery } from 'react-query'
import { api } from '@/services/api'
import { CommunicationList } from '@/components/communications/CommunicationList'
import { CommunicationComposer } from '@/components/communications/CommunicationComposer'
import { CommunicationTemplates } from '@/components/communications/CommunicationTemplates'
import { PlusIcon, ChatBubbleLeftIcon } from '@heroicons/react/24/outline'

export function CommunicationsPage() {
  const [activeTab, setActiveTab] = useState('list')
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [filters, setFilters] = useState({
    type: '',
    status: '',
    search: '',
    page: 1,
    limit: 20,
  })

  const { data: communicationsData, isLoading, refetch } = useQuery(
    ['communications', filters],
    () => api.get('/communications', { params: filters }).then(res => res.data),
    { keepPreviousData: true }
  )

  const handleNewCommunication = () => {
    setSelectedTemplate(null)
    setActiveTab('compose')
  }

  const handleTemplateSelect = (template: any) => {
    setSelectedTemplate(template)
    setActiveTab('compose')
  }

  const handleCommunicationSent = () => {
    refetch()
    setActiveTab('list')
  }

  const tabs = [
    { id: 'list', name: 'Communications', icon: ChatBubbleLeftIcon },
    { id: 'compose', name: 'Compose', icon: PlusIcon },
    { id: 'templates', name: 'Templates', icon: null },
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Communications</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage email and SMS communications with automated templates
          </p>
        </div>
        <button
          onClick={handleNewCommunication}
          className="btn-primary flex items-center space-x-2"
        >
          <PlusIcon className="h-5 w-5" />
          <span>New Communication</span>
        </button>
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
                {tab.icon && <tab.icon className="h-5 w-5" />}
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'list' && (
            <CommunicationList
              communications={communicationsData?.communications || []}
              isLoading={isLoading}
              filters={filters}
              onFilterChange={setFilters}
              pagination={{
                page: filters.page,
                limit: filters.limit,
                total: communicationsData?.total || 0,
              }}
            />
          )}

          {activeTab === 'compose' && (
            <CommunicationComposer
              template={selectedTemplate}
              onSent={handleCommunicationSent}
              onCancel={() => setActiveTab('list')}
            />
          )}

          {activeTab === 'templates' && (
            <CommunicationTemplates
              onTemplateSelect={handleTemplateSelect}
            />
          )}
        </div>
      </div>
    </div>
  )
}