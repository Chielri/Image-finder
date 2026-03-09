import logging
import sys
from pathlib import Path

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def _get_poppler_path() -> str | None:
    """Return the path to bundled poppler binaries on Windows, or None."""
    if sys.platform != "win32":
        return None
    # When running from a PyInstaller bundle, poppler binaries are in _MEIPASS/poppler
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir:
        candidate = Path(bundle_dir) / "poppler"
        if candidate.is_dir():
            return str(candidate)
    # When running from a PyInstaller --onedir collect folder
    exe_dir = Path(sys.executable).parent
    candidate = exe_dir / "poppler"
    if candidate.is_dir():
        return str(candidate)
    return None


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

    poppler_path = _get_poppler_path()
    logger.info("Converting PDF %s at %d DPI (poppler_path=%s)", file_path, dpi, poppler_path)
    pil_images = convert_from_path(file_path, dpi=dpi, poppler_path=poppler_path)
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
