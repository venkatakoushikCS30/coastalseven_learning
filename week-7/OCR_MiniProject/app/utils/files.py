"""File-system helpers for uploaded documents."""

from __future__ import annotations

import secrets
from pathlib import Path
from typing import Final

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_ALLOWED_EXTS: Final[frozenset[str]] = frozenset({".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"})


def generate_stored_filename(extension: str) -> str:
    """Return a collision-resistant filename with the given extension."""
    safe_ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"
    return f"{secrets.token_hex(16)}{safe_ext}"


def save_upload(contents: bytes, suffix: str) -> Path:
    """Persist ``contents`` to :attr:`Settings.upload_dir` and return the path.

    A random filename is generated. The suffix should include the leading
    dot (e.g. ``.png``).
    """
    if not suffix.startswith("."):
        suffix = f".{suffix}"

    dest_dir = settings.upload_dir_abs
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest = dest_dir / generate_stored_filename(suffix)
    dest.write_bytes(contents)
    logger.info("saved upload path=%s bytes=%d", dest, len(contents))
    return dest


def allowed_extensions() -> frozenset[str]:
    """Return the set of accepted file extensions."""
    return _ALLOWED_EXTS
