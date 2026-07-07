"""Lightweight repository layer for SQLAlchemy models.

Keeps query logic out of the API/service code and makes the data access
patterns easy to mock in tests. Each function takes a :class:`Session`
explicitly (no global state) so callers can use FastAPI's ``get_db``
dependency.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import TypeVar

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.employee import Employee
from app.models.enums import DocumentStatus, DocumentType

T = TypeVar("T")


# --- Employees -------------------------------------------------------------


def create_employee(
    db: Session,
    *,
    employee_id: str,
    full_name: str,
    email: str | None = None,
    employee_code: str | None = None,
    department: str | None = None,
) -> Employee:
    """Insert a new employee row. Caller commits."""
    emp = Employee(
        id=employee_id,
        full_name=full_name,
        email=email,
        employee_code=employee_code,
        department=department,
    )
    db.add(emp)
    db.flush()
    return emp


def get_employee(db: Session, employee_id: str) -> Employee | None:
    """Return an employee by id or ``None``."""
    return db.get(Employee, employee_id)


def list_employees(
    db: Session, *, search: str | None = None, limit: int = 50, offset: int = 0
) -> tuple[Sequence[Employee], int]:
    """Return ``(items, total)`` for pagination, optionally filtered by search."""
    stmt = select(Employee).order_by(Employee.created_at.desc())
    count_stmt = select(Employee.id)
    
    if search:
        search_filter = or_(
            Employee.full_name.ilike(f"%{search}%"),
            Employee.email.ilike(f"%{search}%"),
            Employee.employee_code.ilike(f"%{search}%"),
        )
        stmt = stmt.where(search_filter)
        count_stmt = count_stmt.where(search_filter)
        
    items = list(db.execute(stmt.limit(limit).offset(offset)).scalars().all())
    total = len(db.execute(count_stmt).all())
    return items, total


def delete_employee(db: Session, employee_id: str) -> bool:
    """Delete an employee by id. Returns True if a row was removed."""
    emp = db.get(Employee, employee_id)
    if emp is None:
        return False
    db.delete(emp)
    db.flush()
    return True


# --- Documents -------------------------------------------------------------


def create_document(
    db: Session,
    *,
    document_id: str,
    employee_id: str | None,
    document_type: DocumentType,
    original_filename: str,
    content_type: str,
    size_bytes: int,
    sha256: str,
    stored_path: str,
    status: DocumentStatus = DocumentStatus.RECEIVED,
) -> Document:
    """Insert a new document row. Caller commits."""
    doc = Document(
        id=document_id,
        employee_id=employee_id,
        document_type=document_type,
        original_filename=original_filename,
        content_type=content_type,
        size_bytes=size_bytes,
        sha256=sha256,
        stored_path=stored_path,
        status=status,
    )
    db.add(doc)
    db.flush()
    return doc


def get_document(db: Session, document_id: str) -> Document | None:
    """Return a document by id or ``None``."""
    return db.get(Document, document_id)


def get_document_by_sha256(db: Session, sha256: str) -> Document | None:
    """Return a document by its exact SHA-256 hash or ``None``."""
    stmt = select(Document).where(Document.sha256 == sha256)
    return db.execute(stmt).scalars().first()


def list_documents(
    db: Session,
    *,
    search: str | None = None,
    document_type: DocumentType | None = None,
    employee_id: str | None = None,
    status: DocumentStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[Sequence[Document], int]:
    """Return ``(items, total)`` filtered and paginated."""
    stmt = select(Document).order_by(Document.created_at.desc())
    count_stmt = select(Document.id)

    if search:
        search_filter = Document.original_filename.ilike(f"%{search}%")
        stmt = stmt.where(search_filter)
        count_stmt = count_stmt.where(search_filter)
        
    if document_type is not None:
        stmt = stmt.where(Document.document_type == document_type)
        count_stmt = count_stmt.where(Document.document_type == document_type)
    if employee_id is not None:
        stmt = stmt.where(Document.employee_id == employee_id)
        count_stmt = count_stmt.where(Document.employee_id == employee_id)
    if status is not None:
        stmt = stmt.where(Document.status == status)
        count_stmt = count_stmt.where(Document.status == status)

    items = list(db.execute(stmt.limit(limit).offset(offset)).scalars().all())
    total = len(db.execute(count_stmt).all())
    return items, total


def delete_document(db: Session, document_id: str) -> tuple[bool, str | None]:
    """Delete a document by id. Returns ``(removed, stored_path)``.

    The caller is responsible for unlinking the file from disk.
    """
    doc = db.get(Document, document_id)
    if doc is None:
        return False, None
    path = doc.stored_path
    db.delete(doc)
    db.flush()
    return True, path


def update_document_status(
    db: Session,
    document_id: str,
    *,
    status: DocumentStatus,
    error_message: str | None = None,
) -> Document | None:
    """Update the lifecycle status (and optional error message)."""
    doc = db.get(Document, document_id)
    if doc is None:
        return None
    doc.status = status
    if error_message is not None:
        doc.error_message = error_message
    db.flush()
    return doc
