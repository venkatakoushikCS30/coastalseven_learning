"""Application configuration loaded from environment / .env.

A single :class:`Settings` instance is exported as ``settings`` and
imported wherever configuration is needed. This keeps the rest of the
codebase free of ``os.getenv`` calls and gives us typed settings via
pydantic.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings.

    All values are overridable via environment variables or a ``.env``
    file at the project root. Paths are resolved to absolute paths so
    the rest of the code can treat them as canonical.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Runtime ---------------------------------------------------------
    app_env: Literal["development", "staging", "production", "test"] = "development"
    app_name: str = "Employee Document Verification Portal"
    app_version: str = "0.1.0"

    # --- Database --------------------------------------------------------
    database_url: str = Field(default="sqlite:///./data/portal.db")

    # --- Logging ---------------------------------------------------------
    log_level: str = Field(default="INFO")
    log_file: Path = Field(default=Path("./logs/app.log"))

    # --- Uploads ---------------------------------------------------------
    upload_dir: Path = Field(default=Path("./data/uploads"))
    max_upload_mb: int = Field(default=10, ge=1, le=100)

    # --- OCR -------------------------------------------------------------
    ocr_confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    trocr_model: str = Field(default="microsoft/trocr-base-handwritten")
    trocr_notebook: Path = Field(default=Path("./notebooks/trocr_engine.ipynb"))

    # --- Verification ----------------------------------------------------
    verification_min_confidence: float = Field(default=0.6, ge=0.0, le=1.0)

    # --- Gradio UI -------------------------------------------------------
    gradio_api_url: str = Field(default="http://127.0.0.1:8000")
    gradio_host: str = Field(default="127.0.0.1")
    gradio_port: int = Field(default=7860, ge=1, le=65535)
    gradio_share: bool = Field(default=False)

    # --- Preprocessing ---------------------------------------------------
    preprocess_max_dim: int = Field(default=1600, ge=256, le=4096)
    preprocess_deskew: bool = Field(default=True)
    preprocess_binarize: bool = Field(default=False)

    # --- PaddleOCR -------------------------------------------------------
    paddleocr_lang: str = Field(default="en")
    paddleocr_use_angle_cls: bool = Field(default=True)
    paddleocr_notebook: Path = Field(default=Path("./notebooks/paddleocr_engine.ipynb"))

    # --- Derived helpers -------------------------------------------------
    @property
    def upload_dir_abs(self) -> Path:
        """Absolute, resolved upload directory path."""
        return self.upload_dir.expanduser().resolve()

    @property
    def log_file_abs(self) -> Path:
        """Absolute, resolved log file path."""
        return self.log_file.expanduser().resolve()

    @property
    def paddleocr_notebook_abs(self) -> Path:
        """Absolute path to the PaddleOCR engine notebook.

        If ``paddleocr_notebook`` is relative, it is resolved against the
        project root (the parent of the ``app/`` package) so the app can
        be launched from any working directory.
        """
        path = Path(self.paddleocr_notebook).expanduser()
        if path.is_absolute():
            return path.resolve()
        project_root = Path(__file__).resolve().parents[2]
        return (project_root / path).resolve()

    @property
    def trocr_notebook_abs(self) -> Path:
        """Absolute path to the TrOCR engine notebook."""
        path = Path(self.trocr_notebook).expanduser()
        if path.is_absolute():
            return path.resolve()
        project_root = Path(__file__).resolve().parents[2]
        return (project_root / path).resolve()

    def ensure_runtime_dirs(self) -> None:
        """Create directories the app writes to (uploads, logs, db)."""
        self.upload_dir_abs.mkdir(parents=True, exist_ok=True)
        self.log_file_abs.parent.mkdir(parents=True, exist_ok=True)
        # Ensure SQLite parent dir exists (sqlite:///./data/portal.db -> ./data).
        if self.database_url.startswith("sqlite:///"):
            db_path = Path(self.database_url.replace("sqlite:///", "", 1))
            db_path.parent.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""
    settings = Settings()
    settings.ensure_runtime_dirs()
    return settings


settings: Settings = get_settings()
