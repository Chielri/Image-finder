import pytest
from services.nms import Detection, apply_nms, compute_iou


def make_det(x, y, w, h, conf=0.9, scale=1.0):
    return Detection(x=x, y=y, width=w, height=h, confidence=conf, scale=scale)


def test_compute_iou_identical():
    a = make_det(0, 0, 10, 10)
    assert compute_iou(a, a) == pytest.approx(1.0)


def test_compute_iou_no_overlap():
    a = make_det(0, 0, 10, 10)
    b = make_det(20, 20, 10, 10)
    assert compute_iou(a, b) == pytest.approx(0.0)


def test_compute_iou_partial_overlap():
    a = make_det(0, 0, 10, 10)
    b = make_det(5, 5, 10, 10)
    iou = compute_iou(a, b)
    assert 0 < iou < 1


def test_nms_removes_duplicates():
    dets = [
        make_det(0, 0, 10, 10, conf=0.9),
        make_det(1, 1, 10, 10, conf=0.8),  # heavily overlapping
        make_det(50, 50, 10, 10, conf=0.7),  # separate
    ]
    result = apply_nms(dets, iou_threshold=0.3)
    assert len(result) == 2
    assert result[0].confidence == 0.9


def test_nms_empty_input():
    assert apply_nms([]) == []


def test_nms_single_detection():
    dets = [make_det(0, 0, 10, 10)]
    result = apply_nms(dets)
    assert len(result) == 1
