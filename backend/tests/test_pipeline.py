import os
import tempfile

import numpy as np
import pytest
from PIL import Image

from config import settings
from models.requests import SearchParams


def _create_test_image_with_logo(tmp_dir: str):
    """Create a 300x300 RGB document image with a 40x40 pattern at (100, 120)."""
    doc = np.ones((300, 300, 3), dtype=np.uint8) * 240

    # Use a checkerboard-like pattern with high contrast so the template
    # matcher has non-zero variance after grayscale conversion.
    pattern = np.zeros((40, 40, 3), dtype=np.uint8)
    for i in range(40):
        for j in range(40):
            if (i // 4 + j // 4) % 2 == 0:
                pattern[i, j] = [20, 20, 180]
            else:
                pattern[i, j] = [200, 60, 30]
    doc[120:160, 100:140] = pattern

    doc_path = os.path.join(tmp_dir, "doc.png")
    Image.fromarray(doc).save(doc_path)

    query = doc[120:160, 100:140].copy()
    query_path = os.path.join(tmp_dir, "query.png")
    Image.fromarray(query).save(query_path)
    return doc_path, query_path


def test_pipeline_finds_single_match(tmp_path):
    settings.upload_dir = str(tmp_path / "uploads")
    doc_path, query_path = _create_test_image_with_logo(str(tmp_path))

    from services.search_pipeline import run_search
    params = SearchParams(confidence=0.8, method="multi_scale")
    result = run_search(doc_path, query_path, params)

    assert result.total_pages == 1
    assert result.total_matches >= 1


def test_pipeline_no_matches(tmp_path):
    settings.upload_dir = str(tmp_path / "uploads")

    doc = np.ones((200, 200, 3), dtype=np.uint8) * 200
    doc_path = os.path.join(str(tmp_path), "doc.png")
    Image.fromarray(doc).save(doc_path)

    # Uniform query will be rejected by zero-variance guard
    query = np.zeros((20, 20, 3), dtype=np.uint8)
    query_path = os.path.join(str(tmp_path), "query.png")
    Image.fromarray(query).save(query_path)

    from services.search_pipeline import run_search
    params = SearchParams(confidence=0.95, method="template")
    result = run_search(doc_path, query_path, params)

    assert result.total_pages == 1
    assert result.total_matches == 0
