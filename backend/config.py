import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    upload_dir: str = os.getenv("UPLOAD_DIR", "/tmp/doc-image-search")
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    max_pages: int = int(os.getenv("MAX_PAGES", "200"))
    default_dpi: int = int(os.getenv("DEFAULT_DPI", "300"))
    default_confidence: float = float(os.getenv("DEFAULT_CONFIDENCE", "0.8"))
    cleanup_ttl_minutes: int = int(os.getenv("CLEANUP_TTL_MINUTES", "30"))
    cors_origins: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173"
    ).split(",")

    class Config:
        env_file = ".env"


settings = Settings()
