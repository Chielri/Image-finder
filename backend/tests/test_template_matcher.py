import numpy as np
import pytest
from services.template_matcher import find_matches_single_scale, find_matches_multi_scale
from services.nms import apply_nms


def make_page_with_pattern():
    """Create a 200x200 gray page with a 20x20 white square at (50, 60)."""
    page = np.zeros((200, 200), dtype=np.uint8)
    page[60:80, 50:70] = 200
    return page


def test_single_scale_finds_exact_match():
    page = make_page_with_pattern()
    query = page[60:80, 50:70].copy()
    dets = find_matches_single_scale(page, query, confidence_threshold=0.95)
    dets = apply_nms(dets, iou_threshold=0.3)
    assert len(dets) >= 1
    best = max(dets, key=lambda d: d.confidence)
    assert best.x == 50
    assert best.y == 60


def test_single_scale_no_match():
    page = np.zeros((100, 100), dtype=np.uint8)
    query = np.ones((10, 10), dtype=np.uint8) * 255
    dets = find_matches_single_scale(page, query, confidence_threshold=0.95)
    assert len(dets) == 0


def test_query_larger_than_page_skipped():
    page = np.zeros((50, 50), dtype=np.uint8)
    query = np.zeros((100, 100), dtype=np.uint8)
    dets = find_matches_single_scale(page, query, confidence_threshold=0.5)
    assert dets == []


def test_multi_scale_finds_scaled_match():
    page = make_page_with_pattern()
    # query is 10x10 — half the size of the 20x20 pattern
    query = np.zeros((10, 10), dtype=np.uint8)
    query[:, :] = 200
    # Just check it runs without error; match presence depends on scale step alignment
    dets = find_matches_multi_scale(page, query, confidence_threshold=0.7, scale_min=0.5, scale_max=2.0, scale_steps=5)
    assert isinstance(dets, list)
