import { PageResult } from '../types'

interface Props {
  results: PageResult[]
  totalPages: number
  selectedPage: number | null
  onSelectPage: (page: number) => void
}

export function PageNavigator({ results, totalPages, selectedPage, onSelectPage }: Props) {
  const matchMap = new Map(results.map((r) => [r.page, r.matches.length]))

  return (
    <div className="flex flex-wrap gap-2">
      {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
        const count = matchMap.get(page) ?? 0
        const isSelected = selectedPage === page
        return (
          <button
            key={page}
            onClick={() => onSelectPage(page)}
            className={`relative px-3 py-1.5 text-sm rounded-md border transition-colors ${
              isSelected
                ? 'bg-blue-600 text-white border-blue-600'
                : count > 0
                  ? 'bg-green-50 text-green-800 border-green-300 hover:bg-green-100'
                  : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
            }`}
          >
            {page}
            {count > 0 && (
              <span
                className={`absolute -top-1.5 -right-1.5 text-xs rounded-full w-4 h-4 flex items-center justify-center font-bold ${
                  isSelected ? 'bg-white text-blue-600' : 'bg-green-500 text-white'
                }`}
              >
                {count}
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}
