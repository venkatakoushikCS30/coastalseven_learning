"""PaddleOCR integration (Phase 6).

The engine itself lives in ``notebooks/paddleocr_engine.ipynb`` and
is executed by the :class:`PaddleOCRService` via
:mod:`app.services.notebook_runner`. This package exposes the typed
result dataclasses and the service class.
"""

from app.services.paddleocr.result import OCRBox, OCRResult
from app.services.paddleocr.service import (
    OCRAvailabilityError,
    PaddleOCRService,
)

__all__ = [
    "OCRAvailabilityError",
    "OCRBox",
    "OCRResult",
    "PaddleOCRService",
]
