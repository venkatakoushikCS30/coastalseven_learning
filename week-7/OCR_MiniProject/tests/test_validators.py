"""Tests for ``app.utils.validators``."""

from __future__ import annotations

import pytest

from app.core.config import settings
from app.utils.validators import (
    ImageValidationError,
    detect_image_format,
    validate_extension,
    validate_image_bytes,
    validate_size,
    validate_upload,
)

# Minimal 1x1 PNG (no PIL dependency at import time).
_PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c63000100000005000100"
    "0d0a2db40000000049454e44ae426082"
)

# Minimal 1x1 JPEG (SOI + APP0 + SOF0 + EOI fragments).
_JPEG_BYTES = bytes.fromhex(
    "ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707"
    "070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837"
    "292c30313434341f27393d38323c2e333432ffc2000b08000100010101110000ffc4001f"
    "0000010501010101010100000000000000000102030405060708090a0bffc4002b100002"
    "0103030203040000000000000000000102030004050611070821311241516107711322"
    "a181b114233f0c15252d1e1f0247282fffe1b1ffd9"
)


def test_validate_size_rejects_empty() -> None:
    with pytest.raises(ImageValidationError) as exc:
        validate_size(0)
    assert exc.value.code == "empty_upload"


def test_validate_size_rejects_oversize(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "max_upload_mb", 1, raising=False)
    with pytest.raises(ImageValidationError) as exc:
        validate_size(2 * 1024 * 1024)
    assert exc.value.code == "file_too_large"


def test_validate_extension_accepts_known() -> None:
    assert validate_extension("aadhaar.png") == ".png"


def test_validate_extension_rejects_unknown() -> None:
    with pytest.raises(ImageValidationError) as exc:
        validate_extension("doc.pdf")
    assert exc.value.code == "unsupported_extension"


def test_validate_extension_missing() -> None:
    with pytest.raises(ImageValidationError):
        validate_extension(None)


def test_validate_image_bytes_png() -> None:
    validate_image_bytes(_PNG_BYTES)  # should not raise


def test_validate_image_bytes_rejects_garbage() -> None:
    with pytest.raises(ImageValidationError) as exc:
        validate_image_bytes(b"not an image at all")
    assert exc.value.code == "invalid_image"


def test_detect_image_format() -> None:
    assert detect_image_format(_PNG_BYTES) == ".png"
    assert detect_image_format(_JPEG_BYTES) == ".jpg"
    assert detect_image_format(b"hello") == ""


def test_validate_upload_happy_path() -> None:
    ext = validate_upload("card.png", _PNG_BYTES)
    assert ext == ".png"


def test_validate_upload_extension_mismatch() -> None:
    with pytest.raises(ImageValidationError) as exc:
        validate_upload("card.jpg", _PNG_BYTES)
    assert exc.value.code == "extension_mismatch"


def test_validate_upload_jpg_jpeg_alias() -> None:
    # Declared .jpeg with JPEG bytes should pass.
    ext = validate_upload("card.jpeg", _JPEG_BYTES)
    assert ext == ".jpeg"
