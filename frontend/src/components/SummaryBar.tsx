import { SearchResponse } from '../types'

interface Props {
  result: SearchResponse
}

export function SummaryBar({ result }: Props) {
  return (
    <div className="grid grid-cols-3 gap-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
      <Stat label="Total Matches" value={result.total_matches} />
      <Stat label="Pages with Matches" value={result.pages_with_matches} />
      <Stat label="Total Pages" value={result.total_pages} />
    </div>
  )
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="text-center">
      <div className="text-2xl font-bold text-blue-700">{value}</div>
      <div className="text-xs text-gray-600 mt-1">{label}</div>
    </div>
  )
}
