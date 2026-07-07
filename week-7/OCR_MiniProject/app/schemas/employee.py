"""Pydantic schemas for the employees API."""

from __future__ import annotations

from datetime import datetime

from pydantic import EmailStr, Field

from app.schemas.common import APIModel


class EmployeeCreate(APIModel):
    """Payload for ``POST /api/v1/employees``."""

    full_name: str = Field(min_length=1, max_length=255, description="Employee full name.")
    email: EmailStr | None = Field(default=None, description="Corporate email (optional).")
    employee_code: str | None = Field(
        default=None, max_length=64, description="Internal employee code (optional)."
    )
    department: str | None = Field(default=None, max_length=128, description="Department name.")


class EmployeeUpdate(APIModel):
    """Payload for ``PATCH /api/v1/employees/{id}``."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    employee_code: str | None = Field(default=None, max_length=64)
    department: str | None = Field(default=None, max_length=128)


class EmployeeResponse(APIModel):
    """Response payload for employee endpoints."""

    id: str
    full_name: str
    email: str | None = None
    employee_code: str | None = None
    department: str | None = None
    created_at: datetime
    updated_at: datetime
    document_count: int = Field(default=0, description="Number of associated documents.")


class EmployeeListResponse(APIModel):
    items: list[EmployeeResponse] = Field(default_factory=list)
    total: int = Field(ge=0)
