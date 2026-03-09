"""Download and extract Poppler binaries for Windows bundling.

This script downloads a pre-built Poppler release for Windows from
https://github.com/oschwartz10612/poppler-windows and extracts the
binaries into ``backend/poppler/`` so they can be bundled with
PyInstaller.

Usage:
    python scripts/download_poppler_windows.py
"""

import io
import logging
import os
import shutil
import sys
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Poppler release from https://github.com/oschwartz10612/poppler-windows
POPPLER_VERSION = "24.08.0-0"
POPPLER_URL = (
    f"https://github.com/oschwartz10612/poppler-windows/releases/download/"
    f"v{POPPLER_VERSION}/Release-{POPPLER_VERSION}.zip"
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEST_DIR = PROJECT_ROOT / "backend" / "poppler"


def download_poppler() -> None:
    """Download and extract Poppler Windows binaries."""
    if DEST_DIR.exists():
        logger.info("Poppler directory already exists at %s — removing for fresh download", DEST_DIR)
        shutil.rmtree(DEST_DIR)

    logger.info("Downloading Poppler %s for Windows...", POPPLER_VERSION)
    logger.info("URL: %s", POPPLER_URL)

    req = Request(POPPLER_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=120) as resp:
        data = resp.read()

    logger.info("Downloaded %.1f MB", len(data) / (1024 * 1024))

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        # The zip contains a top-level directory like "poppler-24.08.0/"
        # We want to extract just the Library/bin contents to backend/poppler/bin/
        members = zf.namelist()

        # Find the prefix — typically "poppler-XX.YY.Z/"
        top_dirs = {m.split("/")[0] for m in members if "/" in m}
        if len(top_dirs) == 1:
            prefix = top_dirs.pop()
        else:
            prefix = ""

        bin_prefix = f"{prefix}/Library/bin/" if prefix else "Library/bin/"
        bin_members = [m for m in members if m.startswith(bin_prefix) and not m.endswith("/")]

        if not bin_members:
            logger.error("Could not find Library/bin/ in the zip. Contents: %s", members[:20])
            sys.exit(1)

        dest_bin = DEST_DIR / "bin"
        dest_bin.mkdir(parents=True, exist_ok=True)

        for member in bin_members:
            filename = os.path.basename(member)
            if not filename:
                continue
            target = dest_bin / filename
            with zf.open(member) as src, open(target, "wb") as dst:
                dst.write(src.read())
            logger.debug("Extracted: %s", filename)

    extracted_files = list(dest_bin.glob("*"))
    logger.info(
        "Extracted %d files to %s",
        len(extracted_files),
        dest_bin,
    )

    # Verify key executables exist
    key_exes = ["pdftoppm.exe", "pdfinfo.exe"]
    for exe in key_exes:
        if not (dest_bin / exe).exists():
            logger.warning("Expected %s not found in extracted binaries!", exe)
        else:
            logger.info("Verified: %s", exe)

    logger.info("Poppler Windows binaries are ready at: %s", DEST_DIR)


if __name__ == "__main__":
    download_poppler()
