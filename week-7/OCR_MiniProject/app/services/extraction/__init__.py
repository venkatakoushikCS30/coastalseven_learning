"""Document-type specific field extractors (Phase 8)."""

from app.services.extraction.base import BaseParser
from app.services.extraction.dispatcher import get_parser
from app.services.extraction.parsers import (
    AadhaarParser,
    DegreeParser,
    PanParser,
    PassportParser,
    UnknownParser,
)

__all__ = [
    "AadhaarParser",
    "BaseParser",
    "DegreeParser",
    "PanParser",
    "PassportParser",
    "UnknownParser",
    "get_parser",
]
