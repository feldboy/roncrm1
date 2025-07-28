import { useState } from 'react'
import { Dialog } from '@headlessui/react'
import { api } from '@/services/api'
import toast from 'react-hot-toast'
import { XMarkIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline'

interface ReportExportProps {
  filters: any
  data: any
}

export function ReportExport({ filters, data }: ReportExportProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [exportFormat, setExportFormat] = useState('pdf')
  const [includeCharts, setIncludeCharts] = useState(true)
  const [isExporting, setIsExporting] = useState(false)

  const handleExport = async () => {
    setIsExporting(true)
    try {
      const response = await api.post('/reports/export', {
        filters,
        format: exportFormat,
        include_charts: includeCharts,
      }, {
        responseType: 'blob',
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      
      const timestamp = new Date().toISOString().split('T')[0]
      const filename = `ai-crm-report-${timestamp}.${exportFormat}`
      
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)

      toast.success('Report exported successfully')
      setIsOpen(false)
    } catch (error) {
      console.error('Export failed:', error)
      toast.error('Export failed. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  const exportOptions = [
    { value: 'pdf', label: 'PDF Document', description: 'Complete report with charts and tables' },
    { value: 'excel', label: 'Excel Spreadsheet', description: 'Data tables for further analysis' },
    { value: 'csv', label: 'CSV File', description: 'Raw data in comma-separated format' },
  ]

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="btn-secondary flex items-center space-x-2"
      >
        <ArrowDownTrayIcon className="h-5 w-5" />
        <span>Export Report</span>
      </button>

      <Dialog open={isOpen} onClose={() => setIsOpen(false)} className="relative z-50">
        <div className="fixed inset-0 bg-black bg-opacity-25" />
        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Dialog.Panel className="mx-auto max-w-md w-full bg-white rounded-lg shadow-lg">
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                <Dialog.Title className="text-lg font-medium">
                  Export Report
                </Dialog.Title>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>

              <div className="p-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Export Format
                  </label>
                  <div className="space-y-3">
                    {exportOptions.map((option) => (
                      <label key={option.value} className="flex items-start">
                        <input
                          type="radio"
                          name="format"
                          value={option.value}
                          checked={exportFormat === option.value}
                          onChange={(e) => setExportFormat(e.target.value)}
                          className="mt-1 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                        />
                        <div className="ml-3">
                          <div className="text-sm font-medium text-gray-900">
                            {option.label}
                          </div>
                          <div className="text-sm text-gray-500">
                            {option.description}
                          </div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {exportFormat === 'pdf' && (
                  <div>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={includeCharts}
                        onChange={(e) => setIncludeCharts(e.target.checked)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        Include charts and visualizations
                      </span>
                    </label>
                  </div>
                )}

                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">
                    Report Summary
                  </h4>
                  <dl className="space-y-1 text-sm text-gray-600">
                    <div className="flex justify-between">
                      <dt>Date Range:</dt>
                      <dd>{filters.date_range} days</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt>Total Cases:</dt>
                      <dd>{data?.total_cases?.toLocaleString() || 'N/A'}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt>Success Rate:</dt>
                      <dd>{data?.success_rate?.toFixed(1) || 'N/A'}%</dd>
                    </div>
                  </dl>
                </div>
              </div>

              <div className="flex justify-end space-x-3 p-6 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={handleExport}
                  disabled={isExporting}
                  className="btn-primary"
                >
                  {isExporting ? 'Exporting...' : 'Export'}
                </button>
              </div>
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>
    </>
  )
}