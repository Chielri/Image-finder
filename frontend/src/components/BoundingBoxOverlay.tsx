import { MatchResult } from '../types'

interface Props {
  matches: MatchResult[]
  imageWidth: number
  imageHeight: number
  displayWidth: number
  displayHeight: number
  minConfidence: number
}

export function BoundingBoxOverlay({
  matches,
  imageWidth,
  imageHeight,
  displayWidth,
  displayHeight,
  minConfidence,
}: Props) {
  const scaleX = displayWidth / imageWidth
  const scaleY = displayHeight / imageHeight

  const visible = matches.filter((m) => m.confidence >= minConfidence)

  return (
    <svg
      style={{ position: 'absolute', top: 0, left: 0, width: displayWidth, height: displayHeight }}
      viewBox={`0 0 ${displayWidth} ${displayHeight}`}
    >
      {visible.map((match, idx) => {
        const x = match.bbox.x * scaleX
        const y = match.bbox.y * scaleY
        const w = match.bbox.width * scaleX
        const h = match.bbox.height * scaleY
        return (
          <g key={idx}>
            <rect
              x={x}
              y={y}
              width={w}
              height={h}
              fill="none"
              stroke="#22c55e"
              strokeWidth={2}
            />
            <rect x={x} y={y - 16} width={44} height={16} fill="#22c55e" rx={2} />
            <text x={x + 2} y={y - 4} fontSize={10} fill="white" fontWeight="bold">
              {(match.confidence * 100).toFixed(0)}%
            </text>
          </g>
        )
      })}
    </svg>
  )
}
