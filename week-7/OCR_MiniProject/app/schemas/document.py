"""Pydantic schemas for the documents API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field

from app.schemas.common import APIModel


class DocumentType(str, Enum):
    """Supported document categories. Values match the ORM enum."""

    AADHAAR = "aadhaar"
    PAN = "pan"
    PASSPORT = "passport"
    DEGREE = "degree"
    UNKNOWN = "unknown"


# Allowed MIME prefixes for uploaded files.
ACCEPTED_MIME_TYPES: tuple[str, ...] = (
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
    "image/tiff",
)


class DocumentUploadResponse(APIModel):
    """Returned from ``POST /api/v1/documents/upload``."""

    document_id: str = Field(description="Server-generated document identifier (UUID).")
    document_type: DocumentType
    employee_id: str = Field(description="Employee the document is bound to.")
    stored_path: str
    original_filename: str
    content_type: str
    size_bytes: int = Field(ge=0)
    sha256: str
    uploaded_at: datetime
    status: str = Field(description="Processing status. ``received`` in Phase 3.")


class DocumentSummary(APIModel):
    """Lightweight description used by list endpoints."""

    document_id: str
    employee_id: str | None
    document_type: DocumentType
    status: str
    original_filename: str
    size_bytes: int
    uploaded_at: datetime


class DocumentDetail(APIModel):
    """Detailed document payload returned by ``GET /{id}``."""

    document_id: str
    employee_id: str | None
    document_type: DocumentType
    status: str
    original_filename: str
    content_type: str
    size_bytes: int
    sha256: str
    stored_path: str
    uploaded_at: datetime
    updated_at: datetime
    error_message: str | None = None
    has_ocr: bool = Field(description="True once an OCR result has been stored.")
    has_verification: bool = Field(description="True once verification has run.")
    ocr_result: dict | None = Field(default=None, description="The raw OCR results.")
    verification_result: dict | None = Field(default=None, description="The parsed and verified fields.")


class DocumentListResponse(APIModel):
    items: list[DocumentSummary] = Field(default_factory=list)
    total: int = Field(ge=0)
