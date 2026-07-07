"""Document service: orchestrates upload, persistence, and lifecycle.

Centralizing this here keeps the API routers thin and makes the flow
easy to test in isolation.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import BinaryIO

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database import repository as repo
from app.models.document import Document
from app.models.enums import DocumentStatus, DocumentType
from app.utils import save_upload, validate_upload

logger = get_logger(__name__)

_UNASSIGNED_EMPLOYEE_NAME = "Unassigned"


@dataclass(frozen=True)
class StoredUpload:
    """Result of a successful upload (before DB persistence)."""

    filename: str
    content_type: str
    size_bytes: int
    sha256: str
    stored_path: str
    document_type: DocumentType


def _read_stream(stream: BinaryIO, chunk: int = 64 * 1024) -> bytes:
    """Read ``stream`` to bytes. Caller is responsible for seek(0)."""
    data = stream.read()
    if isinstance(data, str):  # defensive
        data = data.encode("utf-8")
    return data


def store_upload(
    *,
    filename: str | None,
    content_type: str | None,
    contents: bytes,
    document_type: DocumentType,
) -> StoredUpload:
    """Validate, hash, and persist an upload to disk.

    Raises :class:`app.utils.validators.ImageValidationError` on bad input.
    """
    extension = validate_upload(filename, contents)
    stored_path = save_upload(contents, suffix=extension)
    sha256 = hashlib.sha256(contents).hexdigest()
    logger.info(
        "store_upload filename=%s type=%s bytes=%d sha256=%s path=%s",
        filename,
        document_type.value,
        len(contents),
        sha256[:12],
        stored_path,
    )
    return StoredUpload(
        filename=filename or "",
        content_type=content_type or "application/octet-stream",
        size_bytes=len(contents),
        sha256=sha256,
        stored_path=str(stored_path),
        document_type=document_type,
    )


def get_or_create_unassigned_employee(db: Session) -> str:
    """Return the id of the singleton 'Unassigned' employee, creating it if needed.

    Used when an upload is submitted without an explicit employee binding
    so we can still keep a clean foreign-key relationship.
    """
    from app.models.employee import Employee

    existing = (
        db.query(Employee)
        .filter(Employee.full_name == _UNASSIGNED_EMPLOYEE_NAME)
        .order_by(Employee.created_at.asc())
        .first()
    )
    if existing is not None:
        return existing.id

    new_id = str(uuid.uuid4())
    emp = repo.create_employee(
        db,
        employee_id=new_id,
        full_name=_UNASSIGNED_EMPLOYEE_NAME,
    )
    db.commit()
    logger.info("created unassigned employee id=%s", new_id)
    return emp.id


def create_document_record(
    db: Session,
    *,
    upload: StoredUpload,
    employee_id: str | None,
) -> Document:
    """Create the DB row for a stored upload and commit."""
    if not employee_id:
        employee_id = get_or_create_unassigned_employee(db)

    doc_id = str(uuid.uuid4())
    doc = repo.create_document(
        db,
        document_id=doc_id,
        employee_id=employee_id,
        document_type=upload.document_type,
        original_filename=upload.filename,
        content_type=upload.content_type,
        size_bytes=upload.size_bytes,
        sha256=upload.sha256,
        stored_path=upload.stored_path,
        status=DocumentStatus.RECEIVED,
    )
    db.commit()
    db.refresh(doc)
    logger.info("document row created id=%s employee_id=%s", doc.id, doc.employee_id)
    return doc


def utcnow() -> datetime:
    """Test-friendly time hook."""
    return datetime.now(timezone.utc)
