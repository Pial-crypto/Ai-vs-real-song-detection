"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "AI vs Real Song Detection API"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    api_prefix: str = "/api/v1"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # Database
    database_url: str = Field(
        default="sqlite:///./fakesong.db", alias="DATABASE_URL"
    )
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_echo: bool = False

    # Security
    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"
    password_min_length: int = 8
    bcrypt_rounds: int = 12

    # CORS
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"],
        alias="CORS_ORIGINS",
    )
    cors_allow_credentials: bool = True

    # File upload
    max_upload_size_mb: int = 50
    allowed_audio_extensions: list[str] = Field(
        default_factory=lambda: [".wav", ".mp3", ".flac", ".ogg", ".m4a"]
    )
    max_audio_duration_sec: int = 600

    # ML
    model_dir: str = Field(default="./models", alias="MODEL_DIR")
    device: str = "cpu"
    chunk_sec: int = 10
    sample_rate: int = 22050

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    log_file: str | None = Field(default=None, alias="LOG_FILE")

    # Backup
    backup_dir: str = Field(default="./backups", alias="BACKUP_DIR")
    backup_retention_days: int = 30
    backup_schedule_cron: str = "0 2 * * *"

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window_sec: int = 60

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    @field_validator("allowed_audio_extensions", mode="before")
    @classmethod
    def _parse_exts(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


def reset_settings_cache() -> None:
    """Clear cached settings (useful in tests)."""
    get_settings.cache_clear()
