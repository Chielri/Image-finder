import { useState } from 'react'
import { runSearch } from '../api/searchApi'
import { SearchParams, SearchResponse } from '../types'

type SearchState = 'idle' | 'loading' | 'success' | 'error'

interface UseSearchReturn {
  state: SearchState
  result: SearchResponse | null
  error: string | null
  search: (document: File, queryImage: File, params: SearchParams) => Promise<void>
  reset: () => void
}

export function useSearch(): UseSearchReturn {
  const [state, setState] = useState<SearchState>('idle')
  const [result, setResult] = useState<SearchResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const search = async (document: File, queryImage: File, params: SearchParams) => {
    setState('loading')
    setError(null)
    setResult(null)
    try {
      const data = await runSearch(document, queryImage, params)
      setResult(data)
      setState('success')
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : 'An unexpected error occurred.'
      setError(message)
      setState('error')
    }
  }

  const reset = () => {
    setState('idle')
    setResult(null)
    setError(null)
  }

  return { state, result, error, search, reset }
}
