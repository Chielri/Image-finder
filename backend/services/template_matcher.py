import logging

import cv2
import numpy as np

from services.nms import Detection

logger = logging.getLogger(__name__)

MATCH_METHOD = cv2.TM_CCOEFF_NORMED


def find_matches_single_scale(
    page_gray: np.ndarray,
    query_gray: np.ndarray,
    confidence_threshold: float,
    scale: float = 1.0,
) -> list[Detection]:
    """Run template matching at a single scale."""
    ph, pw = page_gray.shape[:2]
    qh, qw = query_gray.shape[:2]

    if qh > ph or qw > pw:
        logger.debug("Query larger than page at scale %.2f, skipping", scale)
        return []

    result = cv2.matchTemplate(page_gray, query_gray, MATCH_METHOD)
    locations = np.where(result >= confidence_threshold)

    detections = []
    for y, x in zip(locations[0], locations[1]):
        conf = float(result[y, x])
        detections.append(Detection(
            x=int(x),
            y=int(y),
            width=int(qw),
            height=int(qh),
            confidence=conf,
            scale=scale,
        ))
    return detections


def find_matches_multi_scale(
    page_gray: np.ndarray,
    query_gray: np.ndarray,
    confidence_threshold: float,
    scale_min: float = 0.5,
    scale_max: float = 1.5,
    scale_steps: int = 20,
) -> list[Detection]:
    """Run template matching at multiple scales and aggregate results."""
    all_detections: list[Detection] = []
    original_qh, original_qw = query_gray.shape[:2]

    scales = np.linspace(scale_min, scale_max, scale_steps)
    for scale in scales:
        new_w = max(1, int(original_qw * scale))
        new_h = max(1, int(original_qh * scale))
        resized_query = cv2.resize(query_gray, (new_w, new_h), interpolation=cv2.INTER_AREA)

        dets = find_matches_single_scale(page_gray, resized_query, confidence_threshold, scale=float(scale))
        # Map coords back to original page space (they already are — resize was on query)
        all_detections.extend(dets)

    logger.debug("Multi-scale template matching found %d raw detections", len(all_detections))
    return all_detections
