import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from routers.search import router


def _get_frontend_dir() -> Path | None:
    """Return the path to the bundled frontend build, if it exists."""
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller bundle
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent
    candidate = base / "frontend_dist"
    return candidate if candidate.is_dir() else None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.upload_dir, exist_ok=True)
    logger.info("Upload directory: %s", settings.upload_dir)
    yield


app = FastAPI(
    title="Document Image Search",
    description="Find occurrences of a query image inside a document.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Serve the bundled frontend (when running as a packaged executable)
_frontend = _get_frontend_dir()
if _frontend is not None:
    app.mount("/", StaticFiles(directory=str(_frontend), html=True), name="frontend")
