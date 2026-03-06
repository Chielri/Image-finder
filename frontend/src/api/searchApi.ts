import axios from 'axios'
import { SearchParams, SearchResponse } from '../types'

const BASE_URL = '/api'

export async function runSearch(
  document: File,
  queryImage: File,
  params: SearchParams,
): Promise<SearchResponse> {
  const formData = new FormData()
  formData.append('document', document)
  formData.append('query_image', queryImage)
  formData.append('confidence', String(params.confidence))
  formData.append('method', params.method)
  formData.append('scale_min', String(params.scale_min))
  formData.append('scale_max', String(params.scale_max))

  const response = await axios.post<SearchResponse>(`${BASE_URL}/search`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export function getPageImageUrl(jobId: string, pageNumber: number): string {
  return `${BASE_URL}/pages/${jobId}/${pageNumber}`
}
