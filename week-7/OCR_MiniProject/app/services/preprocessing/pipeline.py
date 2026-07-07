"""Preprocessing pipeline orchestrator + public :func:`preprocess` API.

The default pipeline is:

    load -> resize -> grayscale -> denoise -> contrast -> deskew

Binarize is registered but disabled unless :class:`PreprocessOptions.binarize`
is set, because adaptive thresholding helps printed forms and hurts photos.
"""

from __future__ import annotations

import time
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Union

import cv2
import numpy as np

from app.core.config import settings
from app.core.logging import get_logger
from app.services.preprocessing.context import (
    PreprocessContext,
    PreprocessOptions,
    PreprocessResult,
)
from app.services.preprocessing.steps import (
    BinarizeStep,
    ContrastStep,
    DeskewStep,
    DenoiseStep,
    GrayscaleStep,
    LoadImageStep,
    PreprocessStep,
    ResizeStep,
)

logger = get_logger(__name__)

ImageInput = Union[str, Path, bytes, np.ndarray]


def load_image(source: ImageInput) -> np.ndarray:
    """Decode an image from a path, raw bytes, or pass through a numpy array."""
    if isinstance(source, np.ndarray):
        return source
    if isinstance(source, (str, Path)):
        path = Path(source)
        try:
            buf = np.fromfile(str(path), dtype=np.uint8)
        except OSError as exc:
            raise ValueError(f"Could not read image at {path}: {exc}") from exc
        if buf.size == 0:
            raise ValueError(f"Could not read image at {path} (file is empty).")
        img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Could not decode image at {path}")
        return img
    if isinstance(source, (bytes, bytearray, memoryview)):
        arr = np.frombuffer(bytes(source), dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Could not decode image from bytes.")
        return img
    raise TypeError(f"Unsupported image input type: {type(source)!r}")


class Pipeline:
    """A configurable sequence of :class:`PreprocessStep` instances."""

    def __init__(self, steps: Sequence[PreprocessStep] | None = None) -> None:
        self._steps: list[PreprocessStep] = list(steps) if steps is not None else list(DEFAULT_STEPS)

    @property
    def steps(self) -> tuple[PreprocessStep, ...]:
        return tuple(self._steps)

    def run(self, image: np.ndarray, *, options: PreprocessOptions | None = None) -> PreprocessResult:
        """Execute the pipeline against ``image``."""
        opts = options or _options_from_settings()
        ctx = PreprocessContext(
            image=image,
            original_size=(int(image.shape[1]), int(image.shape[0])),
            options=opts,
        )
        start = time.perf_counter()
        for step in self._steps:
            ctx = step(ctx)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return PreprocessResult(
            image=ctx.image,
            original_size=ctx.original_size,
            final_size=(int(ctx.image.shape[1]), int(ctx.image.shape[0])),
            steps_applied=[s.name for s in self._steps],
            elapsed_ms=elapsed_ms,
            step_log=ctx.step_log,
        )

    def with_steps(self, steps: Iterable[PreprocessStep]) -> "Pipeline":
        """Return a new :class:`Pipeline` with the given steps."""
        return Pipeline(steps=list(steps))


# Public default pipeline (steps run in this order).
DEFAULT_STEPS: list[PreprocessStep] = [
    LoadImageStep(),
    ResizeStep(),
    GrayscaleStep(),
    DenoiseStep(),
    ContrastStep(),
    DeskewStep(),
    BinarizeStep(),  # off by default; opt-in via PreprocessOptions.binarize
]


def _options_from_settings() -> PreprocessOptions:
    return PreprocessOptions(
        max_dim=settings.preprocess_max_dim,
        deskew=settings.preprocess_deskew,
        binarize=settings.preprocess_binarize,
    )


def preprocess(
    source: ImageInput,
    *,
    options: PreprocessOptions | None = None,
    pipeline: Pipeline | None = None,
) -> PreprocessResult:
    """Run the default (or custom) preprocessing pipeline on ``source``.

    Accepts a file path, raw image bytes, or a BGR numpy array. Returns
    a :class:`PreprocessResult` with the cleaned image and a step log.
    """
    image = load_image(source)
    pipe = pipeline or Pipeline(DEFAULT_STEPS)
    return pipe.run(image, options=options or _options_from_settings())


__all__ = [
    "BinarizeStep",
    "ContrastStep",
    "DEFAULT_STEPS",
    "DeskewStep",
    "DenoiseStep",
    "GrayscaleStep",
    "ImageInput",
    "LoadImageStep",
    "Pipeline",
    "PreprocessContext",
    "PreprocessOptions",
    "PreprocessResult",
    "PreprocessStep",
    "ResizeStep",
    "StepTiming",
    "load_image",
    "preprocess",
]
