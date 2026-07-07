"""Pydantic schemas for the verification engine (Phase 9)."""

from pydantic import BaseModel, Field


class VerificationResult(BaseModel):
    """Result of verifying an extracted document against an employee record."""

    is_verified: bool = Field(description="True if the document belongs to the employee.")
    name_match_score: float = Field(description="Similarity score between 0.0 and 1.0.")
    remarks: list[str] = Field(default_factory=list, description="Reasoning or notes about the verification.")
