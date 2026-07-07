"""Reusable SQLAlchemy enums for the portal."""

from __future__ import annotations

import enum


class DocumentType(str, enum.Enum):
    """Document category.

    Matches :class:`app.schemas.document.DocumentType` values.
    """

    AADHAAR = "aadhaar"
    PAN = "pan"
    PASSPORT = "passport"
    DEGREE = "degree"
    UNKNOWN = "unknown"


class DocumentStatus(str, enum.Enum):
    """Document processing lifecycle."""

    RECEIVED = "received"
    PROCESSING = "processing"
    VERIFIED = "verified"
    FAILED = "failed"
