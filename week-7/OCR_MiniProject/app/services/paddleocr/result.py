"""Typed outputs for the OCR services.

The shape is engine-agnostic so the same dataclass can be produced by
PaddleOCR (Phase 6) and TrOCR (Phase 7) and consumed by the parsers
in Phase 8.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    import numpy as np


@dataclass
class OCRBox:
    """A single detected text region.

    ``polygon`` is the 4-point box in (x, y) order, matching the format
    PaddleOCR returns. For TrOCR the polygon is the bounding box of the
    cropped region.
    """

    polygon: list[tuple[float, float]]
    text: str
    confidence: float
    region_index: int = 0
    source: str = "printed"  # "printed" | "handwritten" | "unknown"

    def to_dict(self) -> dict[str, Any]:
        return {
            "polygon": [[float(x), float(y)] for x, y in self.polygon],
            "text": self.text,
            "confidence": round(float(self.confidence), 4),
            "region_index": int(self.region_index),
            "source": self.source,
        }


@dataclass
class OCRResult:
    """A complete OCR run over one image."""

    language: str
    boxes: list[OCRBox] = field(default_factory=list)
    full_text: str = ""
    elapsed_ms: float = 0.0
    confidence_threshold: float | None = None
    stub_reason: str | None = None  # set when the engine is a fallback

    def to_dict(self) -> dict[str, Any]:
        return {
            "language": self.language,
            "full_text": self.full_text,
            "elapsed_ms": round(self.elapsed_ms, 3),
            "confidence_threshold": self.confidence_threshold,
            "stub_reason": self.stub_reason,
            "boxes": [b.to_dict() for b in self.boxes],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
