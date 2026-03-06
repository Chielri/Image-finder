import { useState } from 'react'
import { SearchResponse } from '../types'
import { getPageImageUrl } from '../api/searchApi'
import { MatchList } from './MatchList'
import { PageNavigator } from './PageNavigator'
import { PageViewer } from './PageViewer'
import { SummaryBar } from './SummaryBar'
import { ThresholdSlider } from './ThresholdSlider'

interface Props {
  result: SearchResponse
  onReset: () => void
}

export function ResultsPanel({ result, onReset }: Props) {
  const [selectedPage, setSelectedPage] = useState<number>(
    result.results.length > 0 ? result.results[0].page : 1,
  )
  const [minConfidence, setMinConfidence] = useState(0.0)

  const pageResult = result.results.find((r) => r.page === selectedPage)
  const matches = pageResult?.matches ?? []
  const pageImageUrl = getPageImageUrl(result.job_id, selectedPage)

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">Results</h2>
        <button
          onClick={onReset}
          className="text-sm text-gray-500 hover:text-gray-700 underline"
        >
          New search
        </button>
      </div>

      <SummaryBar result={result} />

      {result.total_matches === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <div className="text-4xl mb-3">0</div>
          <div className="font-medium">No matches found</div>
          <div className="text-sm mt-1">Try lowering the confidence threshold.</div>
        </div>
      ) : (
        <>
          <div>
            <div className="text-sm font-medium text-gray-700 mb-2">Pages</div>
            <PageNavigator
              results={result.results}
              totalPages={result.total_pages}
              selectedPage={selectedPage}
              onSelectPage={setSelectedPage}
            />
          </div>

          <ThresholdSlider value={minConfidence} onChange={setMinConfidence} />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <PageViewer
                imageUrl={pageImageUrl}
                matches={matches}
                minConfidence={minConfidence}
              />
            </div>
            <div>
              <div className="text-sm font-medium text-gray-700 mb-2">
                Matches on page {selectedPage}
              </div>
              <MatchList matches={matches} minConfidence={minConfidence} />
            </div>
          </div>
        </>
      )}
    </div>
  )
}
