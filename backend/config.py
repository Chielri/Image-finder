from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    upload_dir: str = "/tmp/doc-image-search"
    max_file_size_mb: int = 50
    max_pages: int = 200
    default_dpi: int = 300
    default_confidence: float = 0.8
    cleanup_ttl_minutes: int = 30
    cors_origins: str = "http://localhost:5173"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, v: str | list[str]) -> str | list[str]:
        return v

    @property
    def cors_origin_list(self) -> list[str]:
        if isinstance(self.cors_origins, list):
            return self.cors_origins
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
