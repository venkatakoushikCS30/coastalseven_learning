"""Preprocessing context and result dataclasses.

A :class:`PreprocessContext` is the in-flight state passed between
pipeline steps. It carries the current image (BGR numpy array), the
original dimensions, and a per-step log. A :class:`PreprocessResult` is
what :func:`preprocess` returns to the caller.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    import numpy as np


@dataclass
class PreprocessContext:
    """Mutable state passed between pipeline steps."""

    image: "np.ndarray"  # BGR or grayscale (single-channel) numpy array
    original_size: tuple[int, int]  # (width, height) of the **input** image
    step_log: list["StepTiming"] = field(default_factory=list)
    options: "PreprocessOptions | None" = None


@dataclass
class PreprocessOptions:
    """Per-call pipeline toggles. Defaults are read from :class:`Settings`."""

    max_dim: int = 1600
    deskew: bool = True
    binarize: bool = False


@dataclass
class StepTiming:
    """Per-step record: name, dimensions before/after, elapsed milliseconds."""

    name: str
    width_in: int
    height_in: int
    width_out: int
    height_out: int
    elapsed_ms: float
    skipped: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "width_in": self.width_in,
            "height_in": self.height_in,
            "width_out": self.width_out,
            "height_out": self.height_out,
            "elapsed_ms": round(self.elapsed_ms, 3),
            "skipped": self.skipped,
        }


@dataclass
class PreprocessResult:
    """The final pipeline output."""

    image: "np.ndarray"
    original_size: tuple[int, int]
    final_size: tuple[int, int]
    steps_applied: list[str]
    elapsed_ms: float
    step_log: list[StepTiming]

    def to_dict(self) -> dict:
        return {
            "original_size": list(self.original_size),
            "final_size": list(self.final_size),
            "steps_applied": list(self.steps_applied),
            "elapsed_ms": round(self.elapsed_ms, 3),
            "step_log": [s.to_dict() for s in self.step_log],
        }
