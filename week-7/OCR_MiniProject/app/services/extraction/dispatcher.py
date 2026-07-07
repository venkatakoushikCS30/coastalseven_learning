"""Dispatcher for document extraction parsers (Phase 8)."""

from app.schemas.document import DocumentType
from app.services.extraction.base import BaseParser
from app.services.extraction.parsers import (
    AadhaarParser,
    DegreeParser,
    PanParser,
    PassportParser,
    UnknownParser,
)

_PARSERS = {
    DocumentType.AADHAAR: AadhaarParser(),
    DocumentType.PAN: PanParser(),
    DocumentType.PASSPORT: PassportParser(),
    DocumentType.DEGREE: DegreeParser(),
    DocumentType.UNKNOWN: UnknownParser(),
}


def get_parser(doc_type: DocumentType) -> BaseParser:
    """Return the appropriate parser for the given document type.
    
    Defaults to :class:`UnknownParser` if not found.
    """
    return _PARSERS.get(doc_type, UnknownParser())
