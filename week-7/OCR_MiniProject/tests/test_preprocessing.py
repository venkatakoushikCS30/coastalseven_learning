"""Tests for the preprocessing pipeline.

Uses small synthetic images so the test suite stays fast and hermetic.
"""

from __future__ import annotations

import io
from pathlib import Path

import cv2
import numpy as np
import pytest

from app.core.config import settings
from app.services.preprocessing import (
    BinarizeStep,
    ContrastStep,
    DEFAULT_STEPS,
    DeskewStep,
    DenoiseStep,
    GrayscaleStep,
    Pipeline,
    PreprocessOptions,
    ResizeStep,
    load_image,
    preprocess,
)


# --- Fixtures --------------------------------------------------------------


@pytest.fixture(autouse=True)
def _set_preprocess_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pin settings for deterministic tests."""
    monkeypatch.setattr(settings, "preprocess_max_dim", 800, raising=False)
    monkeypatch.setattr(settings, "preprocess_deskew", True, raising=False)
    monkeypatch.setattr(settings, "preprocess_binarize", False, raising=False)


def _make_synthetic_doc(width: int = 600, height: int = 400) -> np.ndarray:
    """Generate a 'document' with text-like dark strokes on a light background.

    Not a real document — just enough structure to exercise the steps.
    """
    rng = np.random.default_rng(seed=42)
    # Light-gray paper with a soft gradient.
    base = np.full((height, width, 3), 230, dtype=np.uint8)
    for y in range(height):
        base[y, :, :] = np.clip(230 - y // 8, 180, 240)
    # Random dark 'text' strokes.
    for _ in range(80):
        x0 = int(rng.integers(0, width - 80))
        y0 = int(rng.integers(0, height - 20))
        cv2.rectangle(base, (x0, y0), (x0 + 60, y0 + 12), (20, 20, 20), thickness=-1)
    # Light noise to give the denoiser something to do.
    noise = rng.integers(-15, 15, size=base.shape, dtype=np.int16)
    base = np.clip(base.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return base


def _write_png(image: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", image)
    assert ok
    return bytes(buf)


# --- load_image -----------------------------------------------------------


def test_load_image_from_path(tmp_path: Path) -> None:
    img = _make_synthetic_doc()
    p = tmp_path / "doc.png"
    p.write_bytes(_write_png(img))
    loaded = load_image(p)
    assert loaded.shape == img.shape
    assert loaded.dtype == np.uint8


def test_load_image_from_bytes() -> None:
    img = _make_synthetic_doc()
    loaded = load_image(_write_png(img))
    assert loaded.shape == img.shape


def test_load_image_from_ndarray_passthrough() -> None:
    img = _make_synthetic_doc()
    loaded = load_image(img)
    assert loaded is img


def test_load_image_rejects_garbage_bytes() -> None:
    with pytest.raises(ValueError):
        load_image(b"not an image")


def test_load_image_rejects_missing_path(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        load_image(tmp_path / "nope.png")


# --- Default pipeline ------------------------------------------------------


def test_default_pipeline_runs_all_steps() -> None:
    img = _make_synthetic_doc(1200, 800)
    result = preprocess(img)
    # Final image is grayscale (1 channel) because the default pipeline includes GrayscaleStep.
    assert result.image.ndim == 2
    assert result.original_size == (1200, 800)
    # All default step names are recorded.
    names = [s.name for s in result.step_log]
    for expected in ("load", "resize", "grayscale", "denoise", "contrast", "deskew", "binarize"):
        assert expected in names


def test_resize_step_caps_longest_side() -> None:
    img = _make_synthetic_doc(2000, 1000)
    result = preprocess(img, options=PreprocessOptions(max_dim=800, deskew=False, binarize=False))
    longest = max(result.final_size)
    assert longest == 800


def test_resize_step_preserves_aspect() -> None:
    img = _make_synthetic_doc(2000, 1000)
    result = preprocess(img, options=PreprocessOptions(max_dim=800, deskew=False, binarize=False))
    w, h = result.final_size
    assert abs(w / h - 2.0) < 0.05


def test_resize_step_is_noop_when_smaller() -> None:
    img = _make_synthetic_doc(400, 200)
    result = preprocess(img, options=PreprocessOptions(max_dim=800, deskew=False, binarize=False))
    assert result.final_size == (400, 200)


def test_binarize_off_by_default() -> None:
    img = _make_synthetic_doc()
    result = preprocess(img, options=PreprocessOptions(binarize=False, deskew=False))
    # Step is recorded as skipped.
    binarize = next(s for s in result.step_log if s.name == "binarize")
    assert binarize.skipped is True
    # Output is still grayscale (uint8, 1 channel).
    assert result.image.ndim == 2


def test_binarize_when_enabled_produces_binary_image() -> None:
    img = _make_synthetic_doc()
    result = preprocess(img, options=PreprocessOptions(binarize=True, deskew=False))
    binarize = next(s for s in result.step_log if s.name == "binarize")
    assert binarize.skipped is False
    # Adaptive threshold yields only 0 and 255.
    unique = np.unique(result.image)
    assert set(unique.tolist()).issubset({0, 255})


# --- Individual steps ------------------------------------------------------


def test_grayscale_step_keeps_already_gray_unchanged() -> None:
    img = _make_synthetic_doc()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    step = GrayscaleStep()
    out = step.apply(gray, _ctx_for(gray))
    assert out is gray


def test_denoise_step_grayscale() -> None:
    img = _make_synthetic_doc()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    out = DenoiseStep().apply(gray, _ctx_for(gray))
    assert out.shape == gray.shape


def test_contrast_step_changes_histogram() -> None:
    img = _make_synthetic_doc()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    out = ContrastStep().apply(gray, _ctx_for(gray))
    # The output should have a different histogram distribution from the input.
    in_hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    out_hist = cv2.calcHist([out], [0], None, [256], [0, 256]).flatten()
    assert not np.array_equal(in_hist, out_hist)


def test_deskew_corrects_rotation() -> None:
    """A clearly rotated synthetic image should come back close to upright."""
    img = _make_synthetic_doc(800, 600)
    rotated = _rotate(img, angle=7.0)
    result = preprocess(
        rotated, options=PreprocessOptions(max_dim=1600, deskew=True, binarize=False)
    )
    angle = _estimate_skew(result.image)
    # Allow some tolerance (deskew uses a min-area-rect heuristic).
    assert abs(angle) < 3.0


def test_deskew_disabled_leaves_image_alone() -> None:
    img = _make_synthetic_doc(800, 600)
    rotated = _rotate(img, angle=10.0)
    result = preprocess(
        rotated, options=PreprocessOptions(max_dim=1600, deskew=False, binarize=False)
    )
    angle = _estimate_skew(result.image)
    assert abs(angle) > 5.0  # still tilted


# --- Custom pipeline -------------------------------------------------------


def test_custom_pipeline_omits_steps() -> None:
    img = _make_synthetic_doc()
    pipe = Pipeline([GrayscaleStep(), ContrastStep()])
    result = pipe.run(img, options=PreprocessOptions())
    names = [s.name for s in result.step_log]
    assert names == ["grayscale", "contrast"]
    # No resize happened: final size matches the input.
    assert result.final_size == (img.shape[1], img.shape[0])


def test_pipeline_records_timings() -> None:
    img = _make_synthetic_doc()
    result = preprocess(img)
    for step in result.step_log:
        assert step.elapsed_ms >= 0.0
        assert step.width_in > 0 and step.height_in > 0
        assert step.width_out > 0 and step.height_out > 0


def test_pipeline_input_via_bytes() -> None:
    img = _make_synthetic_doc()
    result = preprocess(_write_png(img), options=PreprocessOptions(deskew=False, binarize=False))
    assert result.image.ndim == 2


# --- helpers ---------------------------------------------------------------


def _ctx_for(image: np.ndarray):
    from app.services.preprocessing.context import PreprocessContext

    return PreprocessContext(
        image=image,
        original_size=(image.shape[1], image.shape[0]),
        options=PreprocessOptions(max_dim=800, deskew=False, binarize=False),
    )


def _rotate(image: np.ndarray, angle: float) -> np.ndarray:
    h, w = image.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), borderValue=(255, 255, 255))


def _estimate_skew(image: np.ndarray) -> float:
    """Coarse skew estimate via minAreaRect on the binarized image.

    Returns the *minimum* of the two equivalent normalizations
    (minAreaRect is ambiguous modulo 90 degrees).
    """
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    inv = cv2.bitwise_not(gray)
    _, thresh = cv2.threshold(inv, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    coords = cv2.findNonZero(thresh)
    if coords is None:
        return 0.0
    rect = cv2.minAreaRect(coords)
    angle = rect[-1]
    if angle < -45:
        angle = 90 + angle
    return min(abs(angle), abs(angle - 90))
