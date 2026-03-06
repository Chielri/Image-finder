export interface BoundingBox {
  x: number
  y: number
  width: number
  height: number
}

export interface MatchResult {
  bbox: BoundingBox
  confidence: number
  scale: number
}

export interface PageResult {
  page: number
  matches: MatchResult[]
  page_image_url: string
}

export interface SearchResponse {
  job_id: string
  total_matches: number
  pages_with_matches: number
  total_pages: number
  results: PageResult[]
}

export interface SearchParams {
  confidence: number
  method: 'template' | 'feature' | 'multi_scale'
  scale_min: number
  scale_max: number
}
