"""OpenCV-based image preprocessing pipeline (Phase 5).

Public entry point: :func:`preprocess`. Composable steps live in
:mod:`app.services.preprocessing.steps`; the orchestrator is
:class:`Pipeline` in :mod:`app.services.preprocessing.pipeline`.
"""

from app.services.preprocessing.context import (
    PreprocessContext,
    PreprocessOptions,
    PreprocessResult,
    StepTiming,
)
from app.services.preprocessing.pipeline import (
    DEFAULT_STEPS,
    ImageInput,
    Pipeline,
    load_image,
    preprocess,
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
