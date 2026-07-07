"""Base parser interface for document extraction (Phase 8)."""

from abc import ABC, abstractmethod

from pydantic import BaseModel

from app.services.paddleocr.result import OCRResult


class BaseParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def parse(self, result: OCRResult) -> BaseModel:
        """Extract structured data from the OCR result."""
        pass
