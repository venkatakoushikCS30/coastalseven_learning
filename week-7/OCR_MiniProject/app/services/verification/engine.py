"""Verification engine for comparing parsed data against ground truth (Phase 9)."""

from difflib import SequenceMatcher

from pydantic import BaseModel

from app.core.config import settings
from app.models.employee import Employee
from app.schemas.verification import VerificationResult


def compute_similarity(a: str, b: str) -> float:
    """Compute the similarity ratio between two strings (0.0 to 1.0)."""
    return SequenceMatcher(None, a.strip().lower(), b.strip().lower()).ratio()


def verify_document(employee: Employee, extracted_data: BaseModel) -> VerificationResult:
    """Verify extracted document data against an employee record.

    Matches the employee's full name against the parsed full name or
    similar fields (like student_name).
    """
    remarks = []
    
    # Try to find a name-like field on the extracted schema.
    parsed_name = getattr(extracted_data, "full_name", None)
    if not parsed_name:
        # Fallback for schemas like DegreeData
        parsed_name = getattr(extracted_data, "student_name", None)
        
    if not parsed_name:
        return VerificationResult(
            is_verified=False,
            name_match_score=0.0,
            remarks=["No name field found in the extracted document data."],
        )

    score = compute_similarity(employee.full_name, parsed_name)
    threshold = settings.verification_min_confidence
    
    is_verified = score >= threshold
    
    if is_verified:
        remarks.append(f"Name match score ({score:.2f}) meets or exceeds threshold ({threshold:.2f}).")
    else:
        remarks.append(f"Name match score ({score:.2f}) is below threshold ({threshold:.2f}).")
        
    return VerificationResult(
        is_verified=is_verified,
        name_match_score=score,
        remarks=remarks,
    )
