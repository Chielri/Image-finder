import { MatchResult } from '../types'
import { formatConfidence } from '../utils/imageHelpers'

interface Props {
  matches: MatchResult[]
  minConfidence: number
}

export function MatchList({ matches, minConfidence }: Props) {
  const visible = matches.filter((m) => m.confidence >= minConfidence)

  if (visible.length === 0) {
    return (
      <div className="text-sm text-gray-400 italic">
        No matches above {formatConfidence(minConfidence)} threshold.
      </div>
    )
  }

  return (
    <ul className="space-y-2">
      {visible.map((match, idx) => (
        <li
          key={idx}
          className="text-sm border border-gray-200 rounded-md p-2 flex justify-between items-center bg-white hover:bg-gray-50"
        >
          <div className="font-medium text-gray-800">Match {idx + 1}</div>
          <div className="text-xs text-gray-500 space-x-3">
            <span>
              ({match.bbox.x}, {match.bbox.y}) {match.bbox.width}&times;{match.bbox.height}
            </span>
            <span className="font-semibold text-green-700">
              {formatConfidence(match.confidence)}
            </span>
          </div>
        </li>
      ))}
    </ul>
  )
}
