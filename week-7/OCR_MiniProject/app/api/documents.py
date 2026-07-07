"""Documents API: upload, list, detail, delete.

Phase 3: uploads also create a database row. List/detail/delete are
DB-backed. OCR and verification are still pending.
"""

from __future__ import annotations

import hashlib
import json
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database import repository as repo
from app.database.db import get_db
from app.models.enums import DocumentStatus, DocumentType as ORMDocumentType
from app.schemas.document import (
    DocumentDetail,
    DocumentListResponse,
    DocumentSummary,
    DocumentType,
    DocumentUploadResponse,
)
from app.services import documents as doc_service
from app.services.pipeline import process_document
from app.utils import ImageValidationError, validate_upload

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


_MAX_BYTES_READ = 64 * 1024 * 1024  # 64 MiB hard cap before validation
_ALLOWED_DOC_TYPES = ", ".join(t.value for t in DocumentType)


def _coerce_document_type(value: str | DocumentType) -> DocumentType:
    """Map free-form client strings to the :class:`DocumentType` enum."""
    if isinstance(value, DocumentType):
        return value
    if value is None:
        return DocumentType.UNKNOWN
    try:
        return DocumentType(value.strip().lower())
    except (ValueError, AttributeError) as exc:
        raise ImageValidationError(
            f"Unsupported document_type '{value}'. Allowed: {_ALLOWED_DOC_TYPES}.",
            code="unsupported_document_type",
        ) from exc


def _summary_from_orm(doc) -> DocumentSummary:
    return DocumentSummary(
        document_id=doc.id,
        employee_id=doc.employee_id,
        document_type=DocumentType(doc.document_type.value),
        status=doc.status.value,
        original_filename=doc.original_filename,
        size_bytes=doc.size_bytes,
        uploaded_at=doc.created_at,
    )


def _detail_from_orm(doc) -> DocumentDetail:
    return DocumentDetail(
        document_id=doc.id,
        employee_id=doc.employee_id,
        document_type=DocumentType(doc.document_type.value),
        status=doc.status.value,
        original_filename=doc.original_filename,
        content_type=doc.content_type,
        size_bytes=doc.size_bytes,
        sha256=doc.sha256,
        stored_path=doc.stored_path,
        uploaded_at=doc.created_at,
        updated_at=doc.updated_at,
        error_message=doc.error_message,
        has_ocr=bool(doc.ocr_json),
        has_verification=bool(doc.verification_json),
        ocr_result=json.loads(doc.ocr_json) if doc.ocr_json else None,
        verification_result=json.loads(doc.verification_json) if doc.verification_json else None,
    )


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an employee document image",
    responses={
        400: {"description": "Invalid upload or unknown document_type."},
        404: {"description": "Unknown employee_id."},
    },
)
async def upload_document(
    file: Annotated[UploadFile, File(description="Image file to upload.")],
    document_type: Annotated[
        str,
        Form(description="Declared document category (e.g. aadhaar, pan, passport, degree)."),
    ] = "unknown",
    employee_id: Annotated[
        str | None,
        Form(description="Optional employee id to bind. Defaults to the 'Unassigned' bucket."),
    ] = None,
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    """Validate, hash, persist, and record an upload in the database."""
    contents = await file.read(_MAX_BYTES_READ)
    if not contents:
        raise ImageValidationError("Uploaded file is empty.", code="empty_upload")
    if len(contents) >= _MAX_BYTES_READ:
        raise ImageValidationError(
            f"Upload exceeds internal cap of {_MAX_BYTES_READ // (1024 * 1024)} MiB.",
            code="file_too_large",
        )

    doc_type_api = _coerce_document_type(document_type)

    sha256 = hashlib.sha256(contents).hexdigest()
    existing_doc = repo.get_document_by_sha256(db, sha256)
    if existing_doc:
        logger.info("duplicate upload detected sha256=%s existing_id=%s", sha256, existing_doc.id)
        return DocumentUploadResponse(
            document_id=existing_doc.id,
            document_type=DocumentType(existing_doc.document_type.value),
            employee_id=existing_doc.employee_id or "",
            stored_path=existing_doc.stored_path,
            original_filename=existing_doc.original_filename,
            content_type=existing_doc.content_type,
            size_bytes=existing_doc.size_bytes,
            sha256=existing_doc.sha256,
            uploaded_at=existing_doc.created_at,
            status=existing_doc.status.value,
        )

    extension = validate_upload(file.filename, contents)

    if employee_id is not None and repo.get_employee(db, employee_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown employee_id '{employee_id}'.",
        )

    # Persist to disk and then to the DB.
    stored = doc_service.store_upload(
        filename=file.filename,
        content_type=file.content_type,
        contents=contents,
        document_type=ORMDocumentType(doc_type_api.value),
    )
    doc = doc_service.create_document_record(
        db,
        upload=stored,
        employee_id=employee_id,
    )

    return DocumentUploadResponse(
        document_id=doc.id,
        document_type=doc_type_api,
        employee_id=doc.employee_id or "",
        stored_path=doc.stored_path,
        original_filename=doc.original_filename,
        content_type=doc.content_type,
        size_bytes=doc.size_bytes,
        sha256=doc.sha256,
        uploaded_at=doc.created_at,
        status=doc.status.value,
    )


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List uploaded documents",
)
def list_documents(
    search: str | None = Query(default=None, description="Search by original filename."),
    document_type: DocumentType | None = Query(default=None),
    employee_id: str | None = Query(default=None),
    status_filter: DocumentStatus | None = Query(
        default=None, alias="status", description="Filter by processing status."
    ),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> DocumentListResponse:
    """Return paginated documents with optional filters."""
    items, total = repo.list_documents(
        db,
        search=search,
        document_type=ORMDocumentType(document_type.value) if document_type else None,
        employee_id=employee_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    return DocumentListResponse(
        items=[_summary_from_orm(d) for d in items],
        total=total,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentDetail,
    summary="Get a single document by id",
)
def get_document(
    document_id: Annotated[str, Path(description="Document UUID.")],
    db: Session = Depends(get_db),
) -> DocumentDetail:
    """Return the full document record (metadata only — no binary)."""
    doc = repo.get_document(db, document_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )
    return _detail_from_orm(doc)


@router.post(
    "/{document_id}/process",
    response_model=DocumentDetail,
    summary="Run OCR, parsing, and verification on a document",
)
def process_document_endpoint(
    document_id: Annotated[str, Path(description="Document UUID.")],
    db: Session = Depends(get_db),
) -> DocumentDetail:
    """Run the heavy processing pipeline synchronously (Phase 10).
    
    Reads the file, runs OpenCV preprocessing, PaddleOCR, parsing logic,
    and verification. Returns the updated document.
    """
    # Just to check it exists
    doc = repo.get_document(db, document_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )
        
    process_document(db, document_id)
    
    # Reload from DB after processing
    db.refresh(doc)
    return _detail_from_orm(doc)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    response_class=Response,
    summary="Delete a document (DB row only)",
)
def delete_document(
    document_id: Annotated[str, Path(description="Document UUID.")],
    db: Session = Depends(get_db),
) -> None:
    """Delete the document row. The on-disk file is left in place for now.

    A future phase will unlink the file atomically with the delete.
    """
    removed, _path = repo.delete_document(db, document_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )
    db.commit()
    logger.info("document deleted id=%s", document_id)
    return None
