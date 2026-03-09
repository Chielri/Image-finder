import asyncio
import logging
import os
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from config import settings
from models.requests import SearchParams
from models.responses import SearchResponse, StatusResponse
from services.search_pipeline import get_page_image_path, run_search

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

ALLOWED_DOCUMENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/tiff",
    "image/bmp",
}

ALLOWED_QUERY_TYPES = {
    "image/png",
    "image/jpeg",
}


@router.post("/search", response_model=SearchResponse)
async def search(
    document: UploadFile = File(...),
    query_image: UploadFile = File(...),
    confidence: float = Form(default=settings.default_confidence),
    method: str = Form(default="multi_scale"),
    scale_min: float = Form(default=0.5),
    scale_max: float = Form(default=1.5),
):
    _validate_content_type(document.content_type, ALLOWED_DOCUMENT_TYPES, "document")
    _validate_content_type(query_image.content_type, ALLOWED_QUERY_TYPES, "query_image")

    max_bytes = settings.max_file_size_mb * 1024 * 1024

    with tempfile.TemporaryDirectory() as tmp_dir:
        doc_path = _save_upload(document, tmp_dir, max_bytes)
        query_path = _save_upload(query_image, tmp_dir, max_bytes)

        valid_methods = {"template", "feature", "multi_scale"}
        if method not in valid_methods:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid method '{method}'. Allowed: {sorted(valid_methods)}",
            )

        params = SearchParams(
            confidence=confidence,
            method=method,  # type: ignore[arg-type]
            scale_min=scale_min,
            scale_max=scale_max,
        )

        try:
            result = await asyncio.to_thread(
                run_search, doc_path, query_path, params
            )
        except Exception as exc:
            logger.exception("Search failed")
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return result


@router.get("/pages/{job_id}/{page_number}")
async def get_page(job_id: str, page_number: int):
    image_path = get_page_image_path(job_id, page_number)
    if image_path is None:
        raise HTTPException(status_code=404, detail="Page not found")
    return FileResponse(image_path, media_type="image/jpeg")


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    job_dir = Path(settings.upload_dir) / job_id
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")
    return StatusResponse(job_id=job_id, status="completed", progress=1.0)


@router.get("/config")
async def get_config():
    return {
        "default_confidence": settings.default_confidence,
        "default_dpi": settings.default_dpi,
        "max_file_size_mb": settings.max_file_size_mb,
        "max_pages": settings.max_pages,
    }


def _validate_content_type(content_type: str | None, allowed: set[str], field: str) -> None:
    if content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field} type '{content_type}'. Allowed: {sorted(allowed)}",
        )


def _save_upload(upload: UploadFile, directory: str, max_bytes: int) -> str:
    suffix = Path(upload.filename or "file").suffix or ".bin"
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    dest = os.path.join(directory, unique_name)
    data = upload.file.read()
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File '{upload.filename}' exceeds size limit of {max_bytes // (1024 * 1024)} MB",
        )
    with open(dest, "wb") as f:
        f.write(data)
    return dest
