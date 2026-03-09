import logging
import sys
from pathlib import Path

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def _get_poppler_path() -> str | None:
    """Return the path to bundled Poppler binaries on Windows, or None."""
    if sys.platform != "win32":
        return None

    # When running as a PyInstaller bundle, binaries are in sys._MEIPASS
    if getattr(sys, "frozen", False):
        candidates = [
            Path(sys._MEIPASS) / "poppler" / "bin",
            Path(sys._MEIPASS) / "poppler",
        ]
    else:
        # Running from source — check backend/poppler/bin
        candidates = [
            Path(__file__).resolve().parent.parent / "poppler" / "bin",
        ]

    for candidate in candidates:
        if candidate.is_dir() and (candidate / "pdftoppm.exe").exists():
            logger.info("Using bundled Poppler at: %s", candidate)
            return str(candidate)

    logger.debug("No bundled Poppler found; relying on system PATH")
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

    logger.info("Converting PDF %s at %d DPI", file_path, dpi)
    poppler_path = _get_poppler_path()
    kwargs: dict = {"dpi": dpi}
    if poppler_path:
        kwargs["poppler_path"] = poppler_path
    pil_images = convert_from_path(file_path, **kwargs)
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
