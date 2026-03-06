import logging
from pathlib import Path

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def convert_document_to_images(file_path: str, dpi: int = 300) -> list[np.ndarray]:
    """Convert a document (PDF or image) to a list of numpy arrays (one per page)."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _convert_pdf(file_path, dpi)
    elif suffix in {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}:
        return _load_image(file_path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def _convert_pdf(file_path: str, dpi: int) -> list[np.ndarray]:
    try:
        from pdf2image import convert_from_path
    except ImportError:
        raise RuntimeError("pdf2image is required for PDF support. Install it with: pip install pdf2image")

    logger.info("Converting PDF %s at %d DPI", file_path, dpi)
    pil_images = convert_from_path(file_path, dpi=dpi)
    pages = []
    for i, pil_img in enumerate(pil_images):
        arr = np.array(pil_img.convert("RGB"))
        pages.append(arr)
        logger.debug("Converted page %d: %s", i + 1, arr.shape)
    return pages


def _load_image(file_path: str) -> list[np.ndarray]:
    pil_img = Image.open(file_path).convert("RGB")
    arr = np.array(pil_img)
    logger.info("Loaded image %s: %s", file_path, arr.shape)
    return [arr]
