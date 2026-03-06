interface Props {
  value: number
  onChange: (value: number) => void
}

export function ThresholdSlider({ value, onChange }: Props) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm font-medium text-gray-700 whitespace-nowrap">
        Filter: {(value * 100).toFixed(0)}%
      </span>
      <input
        type="range"
        min={0}
        max={1}
        step={0.01}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="flex-1"
      />
    </div>
  )
}
