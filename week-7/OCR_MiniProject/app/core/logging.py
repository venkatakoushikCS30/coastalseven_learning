"""Centralized logging configuration.

Call :func:`configure_logging` once at process start (the FastAPI app
factory does this). It configures the root logger with a rotating file
handler and a colored console handler. Module-level loggers obtained
via ``logging.getLogger(__name__)`` will inherit this configuration.
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Final

from app.core.config import settings

_CONFIGURED: bool = False
_LOG_FORMAT: Final[str] = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"


def _build_console_handler(level: int) -> logging.Handler:
    """Return a stdout handler. Falls back to a plain stream if ``rich`` is unavailable."""
    try:
        from rich.logging import RichHandler  # type: ignore

        handler: logging.Handler = RichHandler(
            level=level,
            rich_tracebacks=True,
            markup=False,
            show_path=False,
            show_time=False,
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
    except Exception:  # pragma: no cover - rich is optional
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    return handler


def _build_file_handler(path: Path, level: int) -> logging.Handler:
    """Return a rotating file handler writing to ``path``."""
    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(path),
        maxBytes=2 * 1024 * 1024,  # 2 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    return file_handler


def configure_logging() -> None:
    """Configure root logging. Idempotent: safe to call multiple times."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)
    # Remove any pre-existing handlers (e.g. uvicorn default) so we own the format.
    for h in list(root.handlers):
        root.removeHandler(h)

    root.addHandler(_build_console_handler(level))
    root.addHandler(_build_file_handler(settings.log_file_abs, level))

    # Tame chatty third-party loggers.
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    _CONFIGURED = True
    logging.getLogger(__name__).info(
        "logging configured level=%s file=%s", settings.log_level, settings.log_file_abs
    )


def get_logger(name: str) -> logging.Logger:
    """Return a module logger. Calls :func:`configure_logging` first."""
    configure_logging()
    return logging.getLogger(name)
