"""Discrete preprocessing steps.

Each step subclasses :class:`PreprocessStep` and is registered by name.
Steps read :class:`PreprocessContext.options` to honor per-call toggles
(so deskew and binarize can be enabled/disabled without subclassing).
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod

import cv2
import numpy as np

from app.core.logging import get_logger
from app.services.preprocessing.context import PreprocessContext, StepTiming

logger = get_logger(__name__)


class PreprocessStep(ABC):
    """Base class for all preprocessing steps."""

    #: Identifier recorded in the step log.
    name: str = "step"

    def __call__(self, ctx: PreprocessContext) -> PreprocessContext:
        """Run the step, recording timing metadata on ``ctx``."""
        h, w = ctx.image.shape[:2]
        start = time.perf_counter()
        try:
            enabled = self.is_enabled(ctx)
            if not enabled:
                ctx.step_log.append(
                    StepTiming(
                        name=self.name,
                        width_in=w,
                        height_in=h,
                        width_out=w,
                        height_out=h,
                        elapsed_ms=0.0,
                        skipped=True,
                    )
                )
                return ctx
            ctx.image = self.apply(ctx.image, ctx)
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("preprocessing step failed name=%s err=%s", self.name, exc)
            # Re-raise so callers see a clean failure; the step log is already updated
            # with partial timing below.
            elapsed = (time.perf_counter() - start) * 1000.0
            h2, w2 = ctx.image.shape[:2]
            ctx.step_log.append(
                StepTiming(
                    name=self.name,
                    width_in=w,
                    height_in=h,
                    width_out=w2,
                    height_out=h2,
                    elapsed_ms=elapsed,
                )
            )
            raise
        elapsed = (time.perf_counter() - start) * 1000.0
        h2, w2 = ctx.image.shape[:2]
        ctx.step_log.append(
            StepTiming(
                name=self.name,
                width_in=w,
                height_in=h,
                width_out=w2,
                height_out=h2,
                elapsed_ms=elapsed,
            )
        )
        return ctx

    def is_enabled(self, ctx: PreprocessContext) -> bool:  # noqa: ARG002 - default: always on
        return True

    @abstractmethod
    def apply(self, image: np.ndarray, ctx: PreprocessContext) -> np.ndarray:
        """Return the transformed image."""


# --- Concrete steps --------------------------------------------------------


class LoadImageStep(PreprocessStep):
    """No-op placeholder so the pipeline log has an entry for the load itself."""

    name = "load"

    def apply(self, image: np.ndarray, ctx: PreprocessContext) -> np.ndarray:
        # The actual loading is done by ``preprocess()`` before the pipeline starts.
        return image


class ResizeStep(PreprocessStep):
    """Aspect-preserving resize so the longest side is at most ``max_dim``."""

    name = "resize"

    def is_enabled(self, ctx: PreprocessContext) -> bool:
        return True  # always runs; no toggle

    def apply(self, image: np.ndarray, ctx: PreprocessContext) -> np.ndarray:
        max_dim = (ctx.options.max_dim if ctx.options else 1600) if ctx else 1600
        h, w = image.shape[:2]
        longest = max(h, w)
        if longest <= max_dim:
            return image
        scale = max_dim / float(longest)
        new_w = max(1, int(round(w * scale)))
        new_h = max(1, int(round(h * scale)))
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


class GrayscaleStep(PreprocessStep):
    """BGR -> single-channel grayscale."""

    name = "grayscale"

    def apply(self, image: np.ndarray, ctx: PreprocessContext) -> np.ndarray:  # noqa: ARG002
        if image.ndim == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


class DenoiseStep(PreprocessStep):
    """Non-local means denoising. Works on grayscale or color."""

    name = "denoise"

    def apply(self, image: np.ndarray, ctx: PreprocessContext) -> np.ndarray:  # noqa: ARG002
        if image.ndim == 2:
            return cv2.fastNlMeansDenoising(image, h=10)
        return cv2.fastNlMeansDenoisingColored(image, h=10, hColor=10)


class ContrastStep(PreprocessStep):
    """CLAHE on the L channel of LAB (preserves color) or directly on grayscale."""

    name = "contrast"

    def apply(self, image: np.ndarray, ctx: PreprocessContext) -> np.ndarray:  # noqa: ARG002
        if image.ndim == 2:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            return clahe.apply(image)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        merged = cv2.merge((l, a, b))
        return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


class DeskewStep(PreprocessStep):
    """Estimate and correct rotation using a min-area-rect on a text mask."""

    name = "deskew"

    def is_enabled(self, ctx: PreprocessContext) -> bool:
        return bool(ctx.options.deskew) if ctx.options else True

    def apply(self, image: np.ndarray, ctx: PreprocessContext) -> np.ndarray:  # noqa: ARG002
        if image.ndim == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        # Invert so text becomes white (foreground) for the connected-component analysis.
        inv = cv2.bitwise_not(gray)
        _, thresh = cv2.threshold(inv, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        # Find the angle of the minimum-area bounding box of all foreground.
        coords = cv2.findNonZero(thresh)
        if coords is None:
            return image
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        # minAreaRect returns angles in (-90, 0]. Normalize to a small skew range.
        if angle < -45:
            angle = 90 + angle
        # Ignore near-zero rotations to avoid pointless work.
        if abs(angle) < 0.5:
            return image
        h, w = image.shape[:2]
        center = (w / 2.0, h / 2.0)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        return rotated


class BinarizeStep(PreprocessStep):
    """Adaptive Gaussian threshold. Bypassed unless explicitly enabled."""

    name = "binarize"

    def is_enabled(self, ctx: PreprocessContext) -> bool:
        return bool(ctx.options.binarize) if ctx.options else False

    def apply(self, image: np.ndarray, ctx: PreprocessContext) -> np.ndarray:  # noqa: ARG002
        if image.ndim == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        return cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
        )
