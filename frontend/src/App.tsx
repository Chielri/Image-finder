import { useSearch } from './hooks/useSearch'
import { ResultsPanel } from './components/ResultsPanel'
import { UploadPanel } from './components/UploadPanel'

export default function App() {
  const { state, result, error, search, reset } = useSearch()

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
            IS
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900 leading-none">
              Document Image Search
            </h1>
            <p className="text-xs text-gray-500 mt-0.5">Find images inside documents</p>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8 space-y-6">
        {state !== 'success' && (
          <UploadPanel onSearch={search} isLoading={state === 'loading'} />
        )}

        {state === 'loading' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-10 text-center">
            <div className="text-gray-500">Processing document...</div>
            <div className="mt-4 h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500 rounded-full animate-pulse w-3/4" />
            </div>
          </div>
        )}

        {state === 'error' && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-5">
            <div className="font-medium text-red-700">Search failed</div>
            <div className="text-sm text-red-600 mt-1">{error}</div>
            <button
              onClick={reset}
              className="mt-3 text-sm underline text-red-700 hover:text-red-900"
            >
              Try again
            </button>
          </div>
        )}

        {state === 'success' && result && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <ResultsPanel result={result} onReset={reset} />
          </div>
        )}
      </main>
    </div>
  )
}
