"""Pydantic schemas for extracted document data (Phase 8)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AadhaarData(BaseModel):
    """Structured data extracted from an Aadhaar card."""

    aadhaar_number: str | None = Field(default=None, description="12-digit Aadhaar number.")
    full_name: str | None = Field(default=None, description="Cardholder's full name.")
    dob: str | None = Field(default=None, description="Date of birth or Year of birth.")
    gender: str | None = Field(default=None, description="Male / Female / Transgender.")


class PanData(BaseModel):
    """Structured data extracted from a PAN card."""

    pan_number: str | None = Field(default=None, description="10-character alphanumeric PAN.")
    full_name: str | None = Field(default=None, description="Cardholder's full name.")
    father_name: str | None = Field(default=None, description="Father's full name.")
    dob: str | None = Field(default=None, description="Date of birth.")


class PassportData(BaseModel):
    """Structured data extracted from a Passport."""

    passport_number: str | None = Field(default=None, description="Passport number.")
    given_name: str | None = Field(default=None, description="Given name(s).")
    surname: str | None = Field(default=None, description="Surname.")
    dob: str | None = Field(default=None, description="Date of birth.")
    expiry_date: str | None = Field(default=None, description="Date of expiry.")


class DegreeData(BaseModel):
    """Structured data extracted from a Degree certificate."""

    university_name: str | None = Field(default=None, description="Name of the university.")
    student_name: str | None = Field(default=None, description="Name of the student.")
    degree_name: str | None = Field(default=None, description="Name of the degree.")
    year_of_passing: str | None = Field(default=None, description="Year of passing.")


class UnknownData(BaseModel):
    """Fallback schema for unknown document types."""
    
    raw_text: str | None = Field(default=None, description="Raw OCR text.")
