"""Tests for Phase 7: TrOCR integration.

We mock the NotebookRunner to avoid downloading actual HuggingFace
models during unit tests, ensuring the test suite remains fast.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np
import pytest

from app.core.config import settings
from app.services.notebook_runner import NotebookExecutionError, NotebookRunner
from app.services.trocr import TrOCRAvailabilityError, TrOCRService
from app.services.paddleocr.result import OCRResult
from app.services.preprocessing.pipeline import PreprocessResult


class MockNotebookRunner(NotebookRunner):
    """A runner that fakes the notebook execution for TrOCR."""

    def __init__(self, should_fail: bool = False, missing_keys: bool = False) -> None:
        super().__init__()
        self.should_fail = should_fail
        self.missing_keys = missing_keys
        self.last_parameters: dict[str, Any] | None = None

    def run(self, notebook_path: str | Path, *, parameters=None, fresh=False) -> dict[str, Any]:
        if self.should_fail:
            raise NotebookExecutionError("Mocked failure")
        
        self.last_parameters = parameters
        
        if self.missing_keys:
            return {}
            
        def mock_recognize(image, *, engine=None):
            # In TrOCR we just return the full bounding box
            h, w = image.shape[:2] if isinstance(image, np.ndarray) else (100, 200)
            return {
                "boxes": [
                    [
                        [(0.0, 0.0), (float(w), 0.0), (float(w), float(h)), (0.0, float(h))],
                        "Handwritten Text",
                        0.95,
                    ],
                    [
                        [(0.0, 30.0), (100.0, 30.0), (100.0, 50.0), (0.0, 50.0)],
                        "Low Confidence",
                        0.40,
                    ]
                ],
                "elapsed_ms": 105.0,
                "engine": "mock_trocr",
            }
            
        return {
            "engine": "mock_engine",
            "recognize": mock_recognize,
            "parameters": parameters,
        }


def _make_dummy_image(width: int = 200, height: int = 100) -> np.ndarray:
    return np.zeros((height, width, 3), dtype=np.uint8)


def test_service_is_available() -> None:
    runner = MockNotebookRunner()
    service = TrOCRService(runner=runner, preprocess=False)
    assert service.is_available is True


def test_service_is_unavailable_on_notebook_error() -> None:
    runner = MockNotebookRunner(should_fail=True)
    service = TrOCRService(runner=runner, preprocess=False)
    assert service.is_available is False


def test_service_is_unavailable_on_missing_keys() -> None:
    runner = MockNotebookRunner(missing_keys=True)
    service = TrOCRService(runner=runner, preprocess=False)
    assert service.is_available is False


def test_recognize_filters_by_confidence() -> None:
    runner = MockNotebookRunner()
    # threshold 0.6 should drop the "Low Confidence" (0.40) box
    service = TrOCRService(runner=runner, confidence_threshold=0.6, preprocess=False)
    
    img = _make_dummy_image()
    result = service.recognize(img)
    
    assert result.elapsed_ms == 105.0
    assert result.confidence_threshold == 0.6
    assert len(result.boxes) == 1
    
    box = result.boxes[0]
    assert box.text == "Handwritten Text"
    assert box.confidence == 0.95
    assert box.region_index == 0
    assert box.source == "handwritten"
    
    assert result.full_text == "Handwritten Text"


def test_recognize_handles_raw_bytes() -> None:
    runner = MockNotebookRunner()
    service = TrOCRService(runner=runner, preprocess=False)
    
    img = _make_dummy_image()
    _, buf = cv2.imencode(".png", img)
    raw_bytes = bytes(buf)
    
    result = service.recognize(raw_bytes)
    assert len(result.boxes) == 1
    assert result.boxes[0].text == "Handwritten Text"


def test_recognize_handles_preprocess_result_passthrough() -> None:
    class DummyPreprocessResult:
        def __init__(self, img):
            self.image = img
            self.width_in = img.shape[1]
            self.height_in = img.shape[0]

        def to_dict(self):
            return {"original_size": [self.width_in, self.height_in]}
            
    runner = MockNotebookRunner()
    service = TrOCRService(runner=runner, preprocess=False)
    
    img = _make_dummy_image()
    dummy_pre = DummyPreprocessResult(img)
    
    result = service.recognize(dummy_pre)  # type: ignore
    assert len(result.boxes) == 1


def test_recognize_runs_preprocessing() -> None:
    runner = MockNotebookRunner()
    service = TrOCRService(runner=runner)
    
    img = _make_dummy_image()
    result = service.recognize(img)
    assert len(result.boxes) == 1
    assert result.boxes[0].text == "Handwritten Text"


def test_recognize_graceful_fallback() -> None:
    runner = MockNotebookRunner(should_fail=True)
    service = TrOCRService(runner=runner, preprocess=False)
    
    img = _make_dummy_image()
    result = service.recognize(img)
    
    assert result.stub_reason is not None
    assert "mocked failure" in result.stub_reason.lower()
    assert len(result.boxes) == 0
    assert result.full_text == ""


def test_draw_boxes() -> None:
    runner = MockNotebookRunner()
    service = TrOCRService(runner=runner, preprocess=False)
    
    img = _make_dummy_image()
    result = service.recognize(img)
    
    canvas = TrOCRService.draw_boxes(img, result)
    assert id(canvas) != id(img)
    assert canvas.shape == img.shape
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    canvas_gray = TrOCRService.draw_boxes(gray, result)
    assert canvas_gray.ndim == 3
    assert canvas_gray.shape[2] == 3
