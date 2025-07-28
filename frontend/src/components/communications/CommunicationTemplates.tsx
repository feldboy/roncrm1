import { useQuery } from 'react-query'
import { api } from '@/services/api'
import { EnvelopeIcon, DevicePhoneMobileIcon, EyeIcon } from '@heroicons/react/24/outline'

interface CommunicationTemplatesProps {
  onTemplateSelect: (template: any) => void
}

export function CommunicationTemplates({ onTemplateSelect }: CommunicationTemplatesProps) {
  const { data: templates, isLoading } = useQuery(
    'communication-templates',
    () => api.get('/communications/templates').then(res => res.data)
  )

  const getTypeIcon = (type: string) => {
    return type === 'email' ? EnvelopeIcon : DevicePhoneMobileIcon
  }

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'welcome':
        return 'bg-blue-100 text-blue-800'
      case 'follow-up':
        return 'bg-green-100 text-green-800'
      case 'reminder':
        return 'bg-yellow-100 text-yellow-800'
      case 'legal':
        return 'bg-purple-100 text-purple-800'
      case 'funding':
        return 'bg-orange-100 text-orange-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
        ))}
      </div>
    )
  }

  const templatesByCategory = templates?.reduce((acc: any, template: any) => {
    const category = template.category || 'other'
    if (!acc[category]) {
      acc[category] = []
    }
    acc[category].push(template)
    return acc
  }, {}) || {}

  return (
    <div className="space-y-6">
      {Object.entries(templatesByCategory).map(([category, categoryTemplates]: [string, any]) => (
        <div key={category}>
          <h3 className="text-lg font-medium text-gray-900 mb-4 capitalize">
            {category === 'other' ? 'General' : category} Templates
          </h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {categoryTemplates.map((template: any) => {
              const TypeIcon = getTypeIcon(template.type)
              return (
                <div
                  key={template.id}
                  className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => onTemplateSelect(template)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <TypeIcon className="h-5 w-5 text-gray-400" />
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getCategoryColor(template.category)}`}>
                        {template.category}
                      </span>
                    </div>
                    <button className="text-gray-400 hover:text-gray-600">
                      <EyeIcon className="h-4 w-4" />
                    </button>
                  </div>
                  
                  <h4 className="text-sm font-medium text-gray-900 mb-2">
                    {template.name}
                  </h4>
                  
                  {template.description && (
                    <p className="text-xs text-gray-600 mb-3 line-clamp-2">
                      {template.description}
                    </p>
                  )}
                  
                  {template.type === 'email' && template.subject && (
                    <div className="mb-2">
                      <p className="text-xs text-gray-500">Subject:</p>
                      <p className="text-xs text-gray-700 font-medium line-clamp-1">
                        {template.subject}
                      </p>
                    </div>
                  )}
                  
                  <div className="border-t border-gray-100 pt-2">
                    <p className="text-xs text-gray-700 line-clamp-3">
                      {template.content}
                    </p>
                  </div>
                  
                  <div className="mt-3 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {template.variables && template.variables.length > 0 && (
                        <span className="text-xs text-gray-500">
                          {template.variables.length} variable{template.variables.length !== 1 ? 's' : ''}
                        </span>
                      )}
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        onTemplateSelect(template)
                      }}
                      className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                    >
                      Use Template
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      ))}
      
      {(!templates || templates.length === 0) && (
        <div className="text-center py-12">
          <EnvelopeIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No templates available</h3>
          <p className="mt-1 text-sm text-gray-500">
            Templates will be automatically created by the system or can be added by administrators.
          </p>
        </div>
      )}
    </div>
  )
}