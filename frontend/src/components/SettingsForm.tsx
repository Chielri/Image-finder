import { SearchParams } from '../types'

interface Props {
  params: SearchParams
  onChange: (params: SearchParams) => void
}

export function SettingsForm({ params, onChange }: Props) {
  const update = <K extends keyof SearchParams>(key: K, value: SearchParams[K]) => {
    onChange({ ...params, [key]: value })
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Match Method
        </label>
        <select
          value={params.method}
          onChange={(e) => update('method', e.target.value as SearchParams['method'])}
          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="multi_scale">Multi-Scale Template (recommended)</option>
          <option value="template">Single-Scale Template (fast)</option>
          <option value="feature">Feature-Based / ORB (rotation-invariant)</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Confidence Threshold: {(params.confidence * 100).toFixed(0)}%
        </label>
        <input
          type="range"
          min={0}
          max={1}
          step={0.01}
          value={params.confidence}
          onChange={(e) => update('confidence', parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>0% (many matches)</span>
          <span>100% (exact only)</span>
        </div>
      </div>

      {params.method !== 'feature' && (
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Scale Min
            </label>
            <input
              type="number"
              min={0.1}
              max={1.0}
              step={0.1}
              value={params.scale_min}
              onChange={(e) => update('scale_min', parseFloat(e.target.value))}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Scale Max
            </label>
            <input
              type="number"
              min={1.0}
              max={5.0}
              step={0.1}
              value={params.scale_max}
              onChange={(e) => update('scale_max', parseFloat(e.target.value))}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      )}
    </div>
  )
}
