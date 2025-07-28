import { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { api } from '@/services/api'
import toast from 'react-hot-toast'
import { DocumentIcon, XMarkIcon } from '@heroicons/react/24/outline'

interface DocumentUploadProps {
  onUploadSuccess: () => void
}

export function DocumentUpload({ onUploadSuccess }: DocumentUploadProps) {
  const [files, setFiles] = useState<File[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [caseId, setCaseId] = useState('')

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    onDrop: (acceptedFiles) => {
      setFiles(prev => [...prev, ...acceptedFiles])
    },
  })

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleUpload = async () => {
    if (files.length === 0) {
      toast.error('Please select files to upload')
      return
    }

    setIsUploading(true)
    try {
      for (const file of files) {
        const formData = new FormData()
        formData.append('file', file)
        if (caseId) {
          formData.append('case_id', caseId)
        }

        await api.post('/documents/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
      }

      toast.success(`${files.length} document(s) uploaded successfully`)
      setFiles([])
      setCaseId('')
      onUploadSuccess()
    } catch (error) {
      console.error('Upload failed:', error)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="case_id" className="block text-sm font-medium text-gray-700 mb-2">
          Case ID (Optional)
        </label>
        <input
          type="text"
          id="case_id"
          value={caseId}
          onChange={(e) => setCaseId(e.target.value)}
          placeholder="Associate with specific case"
          className="input"
        />
      </div>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-primary-400 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <DocumentIcon className="mx-auto h-12 w-12 text-gray-400" />
        <p className="mt-2 text-sm text-gray-600">
          {isDragActive
            ? 'Drop the files here...'
            : 'Drag & drop files here, or click to select files'}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Supports PDF, DOC, DOCX, PNG, JPG, JPEG
        </p>
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-700">Selected Files</h3>
          <div className="space-y-1">
            {files.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div className="flex items-center space-x-2">
                  <DocumentIcon className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-900">{file.name}</span>
                  <span className="text-xs text-gray-500">
                    ({(file.size / 1024 / 1024).toFixed(2)} MB)
                  </span>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="text-red-500 hover:text-red-700"
                >
                  <XMarkIcon className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {files.length > 0 && (
        <button
          onClick={handleUpload}
          disabled={isUploading}
          className="btn-primary w-full"
        >
          {isUploading ? 'Uploading...' : `Upload ${files.length} file(s)`}
        </button>
      )}
    </div>
  )
}