"""Tests for Phase 10: End-to-end processing pipeline."""

import json
from unittest.mock import patch

import cv2
import numpy as np
import pytest

from app.models.enums import DocumentStatus
from app.schemas.document import DocumentType
from app.services.paddleocr.result import OCRResult
from app.services.pipeline import process_document

@pytest.fixture()
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database.db import Base
    
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()



def _create_test_image(path: str):
    """Write a small dummy image to disk."""
    img = np.zeros((100, 200, 3), dtype=np.uint8)
    cv2.imwrite(path, img)


def test_process_document_success(db_session, tmp_path):
    # Create employee
    from app.models.employee import Employee
    emp = Employee(id="emp-1", full_name="Jane Doe", email="jane@ex.com", department="IT")
    db_session.add(emp)
    
    # Create document
    from app.models.document import Document
    img_path = str(tmp_path / "test_doc.png")
    _create_test_image(img_path)
    
    doc = Document(
        id="doc-1",
        employee_id="emp-1",
        document_type=DocumentType.AADHAAR,
        original_filename="aadhaar.png",
        stored_path=img_path,
        sha256="dummy",
        status=DocumentStatus.RECEIVED,
    )
    db_session.add(doc)
    db_session.commit()

    # Mock OCR
    mock_ocr_result = OCRResult(
        language="en",
        full_text="Government of India\nJane Doe\nDOB: 15/08/1990\nFemale\n1234 5678 9012\nSome extra text",
    )
    
    with patch("app.services.pipeline._get_ocr_service") as mock_get_ocr, patch("app.services.pipeline.preprocess") as mock_pre:
        mock_pre.return_value = np.zeros((10, 10), dtype=np.uint8)
        mock_get_ocr.return_value.recognize.return_value = mock_ocr_result
        success = process_document(db_session, "doc-1")
        
    if not success:
        db_session.refresh(doc)
        print("Error:", doc.error_message)
    assert success is True
    
    # Verify DB updates
    db_session.refresh(doc)
    assert doc.status == DocumentStatus.VERIFIED
    
    ocr_json = json.loads(doc.ocr_json)
    assert ocr_json["full_text"] == mock_ocr_result.full_text
    
    ver_json = json.loads(doc.verification_json)
    assert "parsed_fields" in ver_json
    assert ver_json["parsed_fields"]["aadhaar_number"] == "1234 5678 9012"
    assert "verification" in ver_json
    assert ver_json["verification"]["is_verified"] is True
    assert ver_json["verification"]["name_match_score"] == 1.0


def test_process_document_verification_fails(db_session, tmp_path):
    from app.models.employee import Employee
    emp = Employee(id="emp-2", full_name="Jane Doe", email="jane@ex.com", department="IT")
    db_session.add(emp)
    
    from app.models.document import Document
    img_path = str(tmp_path / "test_doc2.png")
    _create_test_image(img_path)
    
    doc = Document(
        id="doc-2",
        employee_id="emp-2",
        document_type=DocumentType.AADHAAR,
        original_filename="aadhaar.png",
        stored_path=img_path,
        sha256="dummy",
        status=DocumentStatus.RECEIVED,
    )
    db_session.add(doc)
    db_session.commit()

    mock_ocr_result = OCRResult(
        language="en",
        full_text="Government of India\nDOB: 15/08/1990\nRobert Smith\nMale\n1234 5678 9012",
    )
    
    with patch("app.services.pipeline._get_ocr_service") as mock_get_ocr, patch("app.services.pipeline.preprocess") as mock_pre:
        mock_pre.return_value = np.zeros((10, 10), dtype=np.uint8)
        mock_get_ocr.return_value.recognize.return_value = mock_ocr_result
        success = process_document(db_session, "doc-2")
        
    assert success is False
    db_session.refresh(doc)
    assert doc.status == DocumentStatus.FAILED
    
    ver_json = json.loads(doc.verification_json)
    assert ver_json["verification"]["is_verified"] is False
    assert ver_json["verification"]["name_match_score"] < 0.5


def test_process_document_no_employee(db_session, tmp_path):
    from app.models.document import Document
    img_path = str(tmp_path / "test_doc3.png")
    _create_test_image(img_path)
    
    doc = Document(
        id="doc-3",
        employee_id=None,
        document_type=DocumentType.PAN,
        original_filename="pan.png",
        stored_path=img_path,
        sha256="dummy",
        status=DocumentStatus.RECEIVED,
    )
    db_session.add(doc)
    db_session.commit()

    mock_ocr_result = OCRResult(
        language="en",
        full_text="INCOME TAX DEPARTMENT\nName\nJohn Doe\nFather\nRichard Doe\n12/04/1985\nABCDE1234F",
    )
    
    with patch("app.services.pipeline._get_ocr_service") as mock_get_ocr, patch("app.services.pipeline.preprocess") as mock_pre:
        mock_pre.return_value = np.zeros((10, 10), dtype=np.uint8)
        mock_get_ocr.return_value.recognize.return_value = mock_ocr_result
        success = process_document(db_session, "doc-3")
        
    assert success is True
    db_session.refresh(doc)
    assert doc.status == DocumentStatus.VERIFIED
    assert doc.employee_id is not None  # Auto-created employee

    ver_json = json.loads(doc.verification_json)
    assert "verification" in ver_json  # Verification happens with auto-created employee
    assert ver_json["parsed_fields"]["pan_number"] == "ABCDE1234F"


def test_process_document_exception_handling(db_session, tmp_path):
    from app.models.document import Document
    img_path = str(tmp_path / "test_doc4.png")
    _create_test_image(img_path)
    
    doc = Document(
        id="doc-4",
        employee_id=None,
        document_type=DocumentType.PAN,
        original_filename="pan.png",
        stored_path=img_path,
        sha256="dummy",
        status=DocumentStatus.RECEIVED,
    )
    db_session.add(doc)
    db_session.commit()

    with patch("app.services.pipeline._get_ocr_service"), patch("app.services.pipeline.preprocess", side_effect=ValueError("Simulated Error")):
        success = process_document(db_session, "doc-4")
        
    assert success is False
    db_session.refresh(doc)
    assert doc.status == DocumentStatus.FAILED
    assert doc.error_message == "Simulated Error"
