import logging
import uuid
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from config import settings
from models.requests import SearchParams
from models.responses import BoundingBox, MatchResult, PageResult, SearchResponse
from services.feature_matcher import find_matches_feature
from services.image_preprocessor import preprocess_for_matching
from services.nms import Detection, apply_nms
from services.pdf_converter import convert_document_to_images
from services.template_matcher import find_matches_multi_scale, find_matches_single_scale

logger = logging.getLogger(__name__)


def run_search(
    document_path: str,
    query_path: str,
    params: SearchParams,
) -> SearchResponse:
    job_id = str(uuid.uuid4())
    job_dir = Path(settings.upload_dir) / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Job %s: loading document %s", job_id, document_path)
    page_images = convert_document_to_images(document_path, dpi=settings.default_dpi)

    total_pages = len(page_images)
    if total_pages > settings.max_pages:
        page_images = page_images[:settings.max_pages]
        logger.warning("Job %s: truncated to %d pages", job_id, settings.max_pages)

    logger.info("Job %s: loading query image %s", job_id, query_path)
    query_rgb = _load_image_rgb(query_path)
    query_gray = preprocess_for_matching(query_rgb)

    results: list[PageResult] = []
    total_matches = 0

    for page_num, page_rgb in enumerate(page_images, start=1):
        page_gray = preprocess_for_matching(page_rgb)
        detections = _run_matcher(page_gray, query_gray, params)
        detections = apply_nms(detections, iou_threshold=0.3)

        filtered = [d for d in detections if d.confidence >= params.confidence]

        if filtered:
            annotated = _annotate_page(page_rgb, filtered)
            page_img_path = job_dir / f"page_{page_num}.jpg"
            _save_image(annotated, str(page_img_path))

            matches = [
                MatchResult(
                    bbox=BoundingBox(x=d.x, y=d.y, width=d.width, height=d.height),
                    confidence=round(d.confidence, 4),
                    scale=round(d.scale, 4),
                )
                for d in filtered
            ]
            results.append(PageResult(
                page=page_num,
                matches=matches,
                page_image_url=f"/api/pages/{job_id}/{page_num}",
            ))
            total_matches += len(filtered)
        else:
            # Save unannotated page so viewer can still display it
            page_img_path = job_dir / f"page_{page_num}.jpg"
            _save_image(page_rgb, str(page_img_path))

    logger.info("Job %s: done — %d matches across %d pages", job_id, total_matches, total_pages)
    return SearchResponse(
        job_id=job_id,
        total_matches=total_matches,
        pages_with_matches=len(results),
        total_pages=total_pages,
        results=results,
    )


def get_page_image_path(job_id: str, page_number: int) -> str | None:
    path = Path(settings.upload_dir) / job_id / f"page_{page_number}.jpg"
    if path.exists():
        return str(path)
    return None


def _run_matcher(page_gray: np.ndarray, query_gray: np.ndarray, params: SearchParams) -> list[Detection]:
    if params.method == "template":
        return find_matches_single_scale(page_gray, query_gray, params.confidence)
    elif params.method == "feature":
        return find_matches_feature(page_gray, query_gray, params.confidence)
    else:  # multi_scale
        return find_matches_multi_scale(
            page_gray,
            query_gray,
            params.confidence,
            scale_min=params.scale_min,
            scale_max=params.scale_max,
        )


def _load_image_rgb(path: str) -> np.ndarray:
    pil_img = Image.open(path).convert("RGBA")
    background = Image.new("RGB", pil_img.size, (255, 255, 255))
    background.paste(pil_img, mask=pil_img.split()[3])
    return np.array(background)


def _annotate_page(page_rgb: np.ndarray, detections: list[Detection]) -> np.ndarray:
    annotated = page_rgb.copy()
    for det in detections:
        x, y, w, h = det.x, det.y, det.width, det.height
        cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 3)
        label = f"{det.confidence:.2f}"
        cv2.putText(annotated, label, (x, max(y - 5, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    return annotated


def _save_image(image_rgb: np.ndarray, path: str) -> None:
    pil_img = Image.fromarray(image_rgb)
    pil_img.save(path, "JPEG", quality=85)
