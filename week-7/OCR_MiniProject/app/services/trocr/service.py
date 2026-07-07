"""TrOCR service (Phase 7).

Runs the engine notebook in ``notebooks/trocr_engine.ipynb`` and
wraps the result in the engine-agnostic :class:`OCRResult` shape.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import cv2
import numpy as np

from app.core.config import settings
from app.core.logging import get_logger
from app.services.notebook_runner import NotebookExecutionError, NotebookRunner
from app.services.paddleocr.result import OCRBox, OCRResult

if TYPE_CHECKING:  # pragma: no cover
    from app.services.preprocessing import PreprocessResult

logger = get_logger(__name__)


class TrOCRAvailabilityError(RuntimeError):
    """Raised when the TrOCR engine cannot be loaded and no stub is acceptable."""


class TrOCRService:
    """High-level wrapper around the TrOCR notebook engine."""

    def __init__(
        self,
        *,
        notebook_path: str | Path | None = None,
        runner: NotebookRunner | None = None,
        confidence_threshold: float | None = None,
        preprocess: bool = True,
    ) -> None:
        self._notebook_path = Path(
            notebook_path or settings.trocr_notebook_abs
        ).expanduser()
        self._runner = runner or NotebookRunner()
        self._confidence_threshold = (
            confidence_threshold
            if confidence_threshold is not None
            else settings.ocr_confidence_threshold
        )
        self._preprocess = preprocess
        self._namespace: dict[str, Any] | None = None  # set lazily

    @property
    def notebook_path(self) -> Path:
        return self._notebook_path

    @property
    def is_available(self) -> bool:
        """True when the engine notebook executes without error."""
        return self._namespace is not None or self._try_load_engine() is not None

    def recognize(
        self,
        image: "str | Path | bytes | np.ndarray | PreprocessResult",
        *,
        language: str | None = None,
        confidence_threshold: float | None = None,
    ) -> OCRResult:
        """Run TrOCR over ``image`` and return a typed result."""
        bgr, pre_meta = self._materialize_image(image)

        ns = self._try_load_engine()
        stub_reason: str | None = None
        if ns is None:
            stub_reason = (
                f"trocr engine notebook failed to execute: "
                f"{self._last_load_error}"
            )
            logger.warning("trocr unavailable: %s", stub_reason)
            return self._empty_result(language, stub_reason=stub_reason)

        lang = language or "en"
        try:
            output = ns["recognize"](bgr, engine=ns.get("engine"))
        except Exception as exc:  # pragma: no cover
            logger.exception("trocr.recognize failed: %s", exc)
            return self._empty_result(lang, stub_reason=f"recognition failed: {exc}")

        threshold = (
            float(confidence_threshold)
            if confidence_threshold is not None
            else self._confidence_threshold
        )
        boxes = [
            OCRBox(
                polygon=[(float(x), float(y)) for x, y in polygon],
                text=str(text),
                confidence=float(conf),
                region_index=i,
                source="handwritten",
            )
            for i, (polygon, text, conf) in enumerate(output.get("boxes", []))
            if float(conf) >= threshold
        ]
        full_text = "\n".join(b.text for b in boxes)
        result = OCRResult(
            language=lang,
            boxes=boxes,
            full_text=full_text,
            elapsed_ms=float(output.get("elapsed_ms", 0.0)),
            confidence_threshold=threshold,
        )
        if pre_meta:
            width_in, height_in = pre_meta.get("original_size", [0, 0])
            logger.info(
                "preprocess→trocr: %dx%d → %d boxes (threshold=%.2f)",
                width_in,
                height_in,
                len(boxes),
                threshold,
            )
        return result

    @staticmethod
    def draw_boxes(image: np.ndarray, result: OCRResult) -> np.ndarray:
        """Return a copy of ``image`` with OCR polygons + labels drawn on it."""
        if image.ndim == 2:
            canvas = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            canvas = image.copy()
        for box in result.boxes:
            pts = np.array(box.polygon, dtype=np.int32)
            cv2.polylines(canvas, [pts], isClosed=True, color=(200, 0, 0), thickness=2)
            if box.text:
                x, y = int(box.polygon[0][0]), int(box.polygon[0][1])
                cv2.putText(
                    canvas,
                    box.text,
                    (x, max(0, y - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 0, 0),
                    1,
                    cv2.LINE_AA,
                )
        return canvas

    def _materialize_image(
        self, image: "str | Path | bytes | np.ndarray | PreprocessResult"
    ) -> tuple[np.ndarray, dict | None]:
        if hasattr(image, "image") and hasattr(image, "to_dict"):
            pre = image  # type: ignore[assignment]
            return np.asarray(pre.image), pre.to_dict()  # type: ignore[arg-type]

        bgr = self._decode(image)
        if not self._preprocess:
            return bgr, None
        try:
            from app.services.preprocessing import preprocess as run_preprocess
            pre = run_preprocess(bgr)
            return np.asarray(pre.image), pre.to_dict()
        except Exception as exc:  # pragma: no cover
            logger.warning("preprocessing failed, using raw image: %s", exc)
            return bgr, None

    @staticmethod
    def _decode(image: "str | Path | bytes | np.ndarray") -> np.ndarray:
        if isinstance(image, np.ndarray):
            return image
        if isinstance(image, (str, Path)):
            buf = np.fromfile(str(image), dtype=np.uint8)
            decoded = cv2.imdecode(buf, cv2.IMREAD_COLOR)
            if decoded is None:
                raise ValueError(f"Could not decode image at {image}")
            return decoded
        if isinstance(image, (bytes, bytearray, memoryview)):
            buf = np.frombuffer(bytes(image), dtype=np.uint8)
            decoded = cv2.imdecode(buf, cv2.IMREAD_COLOR)
            if decoded is None:
                raise ValueError("Could not decode image from bytes")
            return decoded
        raise TypeError(f"Unsupported image type: {type(image)!r}")

    _last_load_error: str | None = None

    def _try_load_engine(self) -> dict[str, Any] | None:
        if self._namespace is not None:
            return self._namespace
        try:
            ns = self._runner.run(
                self._notebook_path,
                parameters={
                    "model_id": settings.trocr_model,
                },
            )
        except NotebookExecutionError as exc:
            self._last_load_error = str(exc)
            return None
        if "engine" not in ns or "recognize" not in ns:
            self._last_load_error = "notebook did not define 'engine'/'recognize'"
            return None
        self._last_load_error = None
        self._namespace = ns
        return ns

    def _empty_result(
        self, language: str | None, *, stub_reason: str
    ) -> OCRResult:
        return OCRResult(
            language=language or "en",
            boxes=[],
            full_text="",
            elapsed_ms=0.0,
            confidence_threshold=self._confidence_threshold,
            stub_reason=stub_reason,
        )


__all__ = ["TrOCRAvailabilityError", "TrOCRService"]
