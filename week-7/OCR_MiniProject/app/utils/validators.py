"""Input validation utilities for uploaded documents.

Centralizes all "is this upload acceptable?" checks so the API layer
stays thin. Each validator raises :class:`ImageValidationError` with a
machine-readable ``code`` so the API can return structured errors.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from app.core.config import settings
from app.utils.files import allowed_extensions

# --- Public errors ---------------------------------------------------------


class ImageValidationError(ValueError):
    """Raised when an upload fails any validation step.

    The ``code`` attribute is a short, machine-readable identifier
    suitable for the API response payload.
    """

    def __init__(self, message: str, code: str = "invalid_upload") -> None:
        super().__init__(message)
        self.code = code


# --- Internal helpers ------------------------------------------------------


@dataclass(frozen=True)
class _MagicSignature:
    offset: int
    signature: bytes


# Compact subset of common image magic numbers. Enough to reject obvious
# non-images without pulling in a heavy dependency.
_MAGIC_SIGNATURES: Final[tuple[_MagicSignature, ...]] = (
    _MagicSignature(0, b"\xff\xd8\xff"),  # JPEG
    _MagicSignature(0, b"\x89PNG\r\n\x1a\n"),  # PNG
    _MagicSignature(0, b"GIF87a"),  # GIF87
    _MagicSignature(0, b"GIF89a"),  # GIF89
    _MagicSignature(0, b"BM"),  # BMP
    _MagicSignature(0, b"RIFF"),  # WEBP (followed by WEBP at offset 8)
    _MagicSignature(0, b"II*\x00"),  # TIFF (little-endian)
    _MagicSignature(0, b"MM\x00*"),  # TIFF (big-endian)
)


def _matches_magic(data: bytes) -> bool:
    for sig in _MAGIC_SIGNATURES:
        end = sig.offset + len(sig.signature)
        if data[: max(end, 8)] and data[sig.offset:end] == sig.signature:
            # Extra WEBP check: "WEBP" must appear at offset 8.
            if sig.signature == b"RIFF":
                if len(data) >= 12 and data[8:12] != b"WEBP":
                    continue
            return True
    return False


def _sniff_extension(data: bytes) -> str:
    """Return the most likely file extension based on magic bytes."""
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"GIF8"):
        return ".gif"
    if data.startswith(b"BM"):
        return ".bmp"
    if data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WEBP":
        return ".webp"
    if data.startswith(b"II*\x00") or data.startswith(b"MM\x00*"):
        return ".tiff"
    return ""


# --- Public API ------------------------------------------------------------


def validate_size(num_bytes: int) -> None:
    """Reject empty or oversized uploads."""
    if num_bytes <= 0:
        raise ImageValidationError("Uploaded file is empty.", code="empty_upload")
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if num_bytes > max_bytes:
        raise ImageValidationError(
            f"File exceeds maximum size of {settings.max_upload_mb} MB.",
            code="file_too_large",
        )


def validate_extension(filename: str | None) -> str:
    """Return the normalized extension or raise :class:`ImageValidationError`."""
    if not filename:
        raise ImageValidationError("Missing filename.", code="missing_filename")
    ext = Path(filename).suffix.lower()
    if not ext:
        raise ImageValidationError("File has no extension.", code="missing_extension")
    if ext not in allowed_extensions():
        raise ImageValidationError(
            f"Unsupported file type '{ext}'. Allowed: {sorted(allowed_extensions())}.",
            code="unsupported_extension",
        )
    return ext


def validate_image_bytes(data: bytes) -> None:
    """Verify the bytes look like a real image (magic number check)."""
    if not _matches_magic(data):
        raise ImageValidationError(
            "File content does not appear to be a valid image.", code="invalid_image"
        )


def detect_image_format(data: bytes) -> str:
    """Best-effort format detection from bytes; returns empty string if unknown."""
    return _sniff_extension(data)


def validate_upload(filename: str | None, data: bytes) -> str:
    """Run the full validation chain. Returns the normalized extension on success."""
    validate_size(len(data))
    ext = validate_extension(filename)
    validate_image_bytes(data)
    # Cross-check: magic number must agree with the extension.
    sniffed = detect_image_format(data)
    if sniffed and _extension_mismatch(ext, sniffed):
        raise ImageValidationError(
            f"File extension '{ext}' does not match its actual content '{sniffed}'.",
            code="extension_mismatch",
        )
    return ext


def _extension_mismatch(declared: str, sniffed: str) -> bool:
    """Return True if the declared and sniffed extensions disagree.

    JPEG can be named ``.jpg`` or ``.jpeg``; treat those as equivalent.
    """
    if not declared or not sniffed:
        return False
    aliases: dict[str, frozenset[str]] = {
        ".jpg": frozenset({".jpg", ".jpeg"}),
        ".jpeg": frozenset({".jpg", ".jpeg"}),
    }
    allowed = aliases.get(declared, frozenset({declared}))
    return sniffed not in allowed
