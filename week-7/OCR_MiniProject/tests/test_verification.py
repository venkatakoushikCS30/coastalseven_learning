"""Tests for Phase 9: Verification Engine."""

from app.models.employee import Employee
from app.schemas.extraction import AadhaarData, DegreeData, UnknownData
from app.services.verification.engine import compute_similarity, verify_document


def test_compute_similarity():
    # Exact match
    assert compute_similarity("John Doe", "John Doe") == 1.0
    # Case insensitive
    assert compute_similarity("John Doe", "jOhN DoE") == 1.0
    # Small typo
    assert compute_similarity("John Doe", "Jon Doe") > 0.8
    # Totally different
    assert compute_similarity("John Doe", "Alice Smith") < 0.4


def test_verify_document_exact_match():
    emp = Employee(full_name="Jane Doe")
    data = AadhaarData(full_name="Jane Doe", aadhaar_number="1234")
    
    result = verify_document(emp, data)
    assert result.is_verified is True
    assert result.name_match_score == 1.0
    assert "meets or exceeds threshold" in result.remarks[0]


def test_verify_document_fuzzy_match():
    emp = Employee(full_name="Jane Doe")
    # Missing 'e' in Jane
    data = AadhaarData(full_name="Jan Doe", aadhaar_number="1234")
    
    result = verify_document(emp, data)
    assert result.is_verified is True
    assert result.name_match_score > 0.8  # Threshold is 0.6
    assert "meets or exceeds threshold" in result.remarks[0]


def test_verify_document_no_match():
    emp = Employee(full_name="Jane Doe")
    data = AadhaarData(full_name="Robert Smith", aadhaar_number="1234")
    
    result = verify_document(emp, data)
    assert result.is_verified is False
    assert result.name_match_score < 0.4
    assert "is below threshold" in result.remarks[0]


def test_verify_document_degree_student_name():
    emp = Employee(full_name="Bob Builder")
    data = DegreeData(student_name="Bob Builder")
    
    result = verify_document(emp, data)
    assert result.is_verified is True
    assert result.name_match_score == 1.0


def test_verify_document_no_name_field():
    emp = Employee(full_name="Jane Doe")
    data = UnknownData(raw_text="No name here.")
    
    result = verify_document(emp, data)
    assert result.is_verified is False
    assert result.name_match_score == 0.0
    assert "No name field found" in result.remarks[0]
