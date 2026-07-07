"""Tests for ORM models and the repository layer."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import repository as repo
from app.database.db import Base
from app.models.enums import DocumentStatus, DocumentType


@pytest.fixture()
def db_session():
    """Yield a fresh in-memory SQLite session for each test."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_create_and_get_employee(db_session) -> None:
    emp = repo.create_employee(
        db_session,
        employee_id="e-1",
        full_name="Jane Doe",
        email="jane@example.com",
        employee_code="JD-001",
        department="Engineering",
    )
    db_session.commit()
    fetched = repo.get_employee(db_session, "e-1")
    assert fetched is not None
    assert fetched.full_name == "Jane Doe"
    assert fetched.email == "jane@example.com"


def test_list_employees_paginated_and_search(db_session) -> None:
    for i in range(5):
        repo.create_employee(
            db_session, employee_id=f"e-{i}", full_name=f"User {i}", email=f"user{i}@ex.com"
        )
    # create one specific to test search
    repo.create_employee(db_session, employee_id="e-99", full_name="Alice Smith", email="alice@ex.com")
    db_session.commit()
    
    # Test pagination
    items, total = repo.list_employees(db_session, limit=2, offset=0)
    assert total == 6
    assert len(items) == 2
    
    # Test search by name
    items, total = repo.list_employees(db_session, search="Alice")
    assert total == 1
    assert items[0].full_name == "Alice Smith"
    
    # Test search by email
    items, total = repo.list_employees(db_session, search="user2@")
    assert total == 1
    assert items[0].email == "user2@ex.com"


def test_create_document_persists_fields(db_session) -> None:
    repo.create_employee(db_session, employee_id="e-1", full_name="Jane")
    db_session.commit()

    doc = repo.create_document(
        db_session,
        document_id="d-1",
        employee_id="e-1",
        document_type=DocumentType.AADHAAR,
        original_filename="aadhaar.png",
        content_type="image/png",
        size_bytes=1024,
        sha256="a" * 64,
        stored_path="/tmp/aadhaar.png",
    )
    db_session.commit()
    assert doc.id == "d-1"
    assert doc.status == DocumentStatus.RECEIVED
    assert doc.employee_id == "e-1"


def test_list_documents_filtered_by_type_and_search(db_session) -> None:
    repo.create_employee(db_session, employee_id="e-1", full_name="Jane")
    db_session.commit()
    for i, dt in enumerate([DocumentType.AADHAAR, DocumentType.PAN, DocumentType.AADHAAR]):
        repo.create_document(
            db_session,
            document_id=f"d-{i}",
            employee_id="e-1",
            document_type=dt,
            original_filename=f"file_special_{i}.png",
            content_type="image/png",
            size_bytes=10,
            sha256="b" * 64,
            stored_path=f"/tmp/{i}",
        )
    db_session.commit()
    
    items, total = repo.list_documents(
        db_session, document_type=DocumentType.AADHAAR
    )
    assert total == 2
    assert all(d.document_type == DocumentType.AADHAAR for d in items)
    
    # Test search by original_filename
    items, total = repo.list_documents(
        db_session, search="special_1"
    )
    assert total == 1
    assert items[0].original_filename == "file_special_1.png"


def test_delete_document_returns_path(db_session) -> None:
    repo.create_employee(db_session, employee_id="e-1", full_name="Jane")
    db_session.commit()
    repo.create_document(
        db_session,
        document_id="d-1",
        employee_id="e-1",
        document_type=DocumentType.PAN,
        original_filename="x.png",
        content_type="image/png",
        size_bytes=1,
        sha256="c" * 64,
        stored_path="/tmp/x",
    )
    db_session.commit()
    removed, path = repo.delete_document(db_session, "d-1")
    db_session.commit()
    assert removed is True
    assert path == "/tmp/x"
    assert repo.get_document(db_session, "d-1") is None


def test_update_document_status(db_session) -> None:
    repo.create_employee(db_session, employee_id="e-1", full_name="Jane")
    db_session.commit()
    repo.create_document(
        db_session,
        document_id="d-1",
        employee_id="e-1",
        document_type=DocumentType.PASSPORT,
        original_filename="p.png",
        content_type="image/png",
        size_bytes=1,
        sha256="d" * 64,
        stored_path="/tmp/p",
    )
    db_session.commit()
    doc = repo.update_document_status(
        db_session, "d-1", status=DocumentStatus.VERIFIED
    )
    db_session.commit()
    assert doc is not None
    assert doc.status == DocumentStatus.VERIFIED
