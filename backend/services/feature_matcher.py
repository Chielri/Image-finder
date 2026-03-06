import logging

import cv2
import numpy as np

from services.nms import Detection

logger = logging.getLogger(__name__)


def find_matches_feature(
    page_gray: np.ndarray,
    query_gray: np.ndarray,
    confidence_threshold: float,
    min_good_matches: int = 10,
) -> list[Detection]:
    """Use ORB keypoints + BFMatcher + homography to find query in page."""
    orb = cv2.ORB_create(nfeatures=2000)

    kp_query, desc_query = orb.detectAndCompute(query_gray, None)
    kp_page, desc_page = orb.detectAndCompute(page_gray, None)

    if desc_query is None or desc_page is None:
        logger.debug("Feature matching: no descriptors found")
        return []

    if len(kp_query) < 4 or len(kp_page) < 4:
        logger.debug("Feature matching: not enough keypoints")
        return []

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    raw_matches = bf.knnMatch(desc_query, desc_page, k=2)

    # Lowe's ratio test
    good_matches = []
    for match_pair in raw_matches:
        if len(match_pair) == 2:
            m, n = match_pair
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

    if len(good_matches) < min_good_matches:
        logger.debug("Feature matching: only %d good matches (need %d)", len(good_matches), min_good_matches)
        return []

    src_pts = np.float32([kp_query[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp_page[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    if H is None:
        logger.debug("Feature matching: homography estimation failed")
        return []

    inlier_count = int(mask.sum()) if mask is not None else 0
    confidence = inlier_count / len(good_matches) if good_matches else 0.0

    if confidence < confidence_threshold:
        logger.debug("Feature matching: confidence %.2f below threshold %.2f", confidence, confidence_threshold)
        return []

    qh, qw = query_gray.shape[:2]
    corners = np.float32([[0, 0], [qw, 0], [qw, qh], [0, qh]]).reshape(-1, 1, 2)
    transformed = cv2.perspectiveTransform(corners, H)
    pts = transformed.reshape(-1, 2)

    x_min = int(max(0, pts[:, 0].min()))
    y_min = int(max(0, pts[:, 1].min()))
    x_max = int(min(page_gray.shape[1], pts[:, 0].max()))
    y_max = int(min(page_gray.shape[0], pts[:, 1].max()))

    w = x_max - x_min
    h = y_max - y_min
    if w <= 0 or h <= 0:
        return []

    return [Detection(x=x_min, y=y_min, width=w, height=h, confidence=confidence, scale=1.0)]
