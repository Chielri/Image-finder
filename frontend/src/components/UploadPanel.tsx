import { useState } from 'react'
import { SearchParams } from '../types'
import { DocumentDropzone } from './DocumentDropzone'
import { SettingsForm } from './SettingsForm'

interface Props {
  onSearch: (doc: File, query: File, params: SearchParams) => void
  isLoading: boolean
}

const DEFAULT_PARAMS: SearchParams = {
  confidence: 0.8,
  method: 'multi_scale',
  scale_min: 0.5,
  scale_max: 1.5,
}

const DOCUMENT_ACCEPT = {
  'application/pdf': ['.pdf'],
  'image/png': ['.png'],
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/tiff': ['.tiff', '.tif'],
}

const QUERY_ACCEPT = {
  'image/png': ['.png'],
  'image/jpeg': ['.jpg', '.jpeg'],
}

export function UploadPanel({ onSearch, isLoading }: Props) {
  const [docFile, setDocFile] = useState<File | null>(null)
  const [queryFile, setQueryFile] = useState<File | null>(null)
  const [params, setParams] = useState<SearchParams>(DEFAULT_PARAMS)
  const [showSettings, setShowSettings] = useState(false)

  const canSearch = docFile !== null && queryFile !== null && !isLoading

  const handleSearch = () => {
    if (docFile && queryFile) {
      onSearch(docFile, queryFile, params)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-5">
      <h2 className="text-lg font-semibold text-gray-800">Upload Files</h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <div className="text-sm font-medium text-gray-700 mb-2">Document</div>
          <DocumentDropzone
            file={docFile}
            onFile={setDocFile}
            label="Drop PDF or image"
            accept={DOCUMENT_ACCEPT}
          />
        </div>
        <div>
          <div className="text-sm font-medium text-gray-700 mb-2">Query Image</div>
          <DocumentDropzone
            file={queryFile}
            onFile={setQueryFile}
            label="Drop query image"
            accept={QUERY_ACCEPT}
          />
        </div>
      </div>

      <div>
        <button
          type="button"
          onClick={() => setShowSettings((s) => !s)}
          className="text-sm text-blue-600 hover:text-blue-800 underline"
        >
          {showSettings ? 'Hide' : 'Show'} advanced settings
        </button>
        {showSettings && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <SettingsForm params={params} onChange={setParams} />
          </div>
        )}
      </div>

      <button
        onClick={handleSearch}
        disabled={!canSearch}
        className={`w-full py-3 px-6 rounded-lg font-medium text-white transition-colors ${
          canSearch
            ? 'bg-blue-600 hover:bg-blue-700 cursor-pointer'
            : 'bg-gray-300 cursor-not-allowed'
        }`}
      >
        {isLoading ? 'Searching...' : 'Search'}
      </button>
    </div>
  )
}
