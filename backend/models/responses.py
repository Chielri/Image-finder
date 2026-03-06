from pydantic import BaseModel


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class MatchResult(BaseModel):
    bbox: BoundingBox
    confidence: float
    scale: float


class PageResult(BaseModel):
    page: int
    matches: list[MatchResult]
    page_image_url: str


class SearchResponse(BaseModel):
    job_id: str
    total_matches: int
    pages_with_matches: int
    total_pages: int
    results: list[PageResult]


class StatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float = 0.0
    message: str = ""
