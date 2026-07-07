"""Employees API: list, create, get, update, delete."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database import repository as repo
from app.database.db import get_db
from app.models.employee import Employee
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeResponse,
    EmployeeUpdate,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/employees", tags=["employees"])


def _to_response(emp: Employee) -> EmployeeResponse:
    return EmployeeResponse(
        id=emp.id,
        full_name=emp.full_name,
        email=emp.email,
        employee_code=emp.employee_code,
        department=emp.department,
        created_at=emp.created_at,
        updated_at=emp.updated_at,
        document_count=len(emp.documents or []),
    )


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an employee",
)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
) -> EmployeeResponse:
    """Create a new employee row."""
    emp_id = str(uuid.uuid4())
    emp = repo.create_employee(
        db,
        employee_id=emp_id,
        full_name=payload.full_name,
        email=str(payload.email) if payload.email else None,
        employee_code=payload.employee_code,
        department=payload.department,
    )
    db.commit()
    db.refresh(emp)
    logger.info("employee created id=%s name=%s", emp.id, emp.full_name)
    return _to_response(emp)


@router.get(
    "",
    response_model=EmployeeListResponse,
    summary="List employees",
)
def list_employees(
    search: str | None = Query(default=None, description="Search by name, email, or code."),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> EmployeeListResponse:
    """Return paginated employees, newest first, optionally filtered by search."""
    items, total = repo.list_employees(db, search=search, limit=limit, offset=offset)
    return EmployeeListResponse(items=[_to_response(e) for e in items], total=total)


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Get an employee by id",
)
def get_employee(
    employee_id: Annotated[str, Path(description="Employee UUID.")],
    db: Session = Depends(get_db),
) -> EmployeeResponse:
    emp = repo.get_employee(db, employee_id)
    if emp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found.",
        )
    return _to_response(emp)


@router.patch(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Update an employee",
)
def update_employee(
    employee_id: Annotated[str, Path(description="Employee UUID.")],
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
) -> EmployeeResponse:
    """Apply a partial update to an employee."""
    emp = repo.get_employee(db, employee_id)
    if emp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found.",
        )

    if payload.full_name is not None:
        emp.full_name = payload.full_name
    if payload.email is not None:
        emp.email = str(payload.email)
    if payload.employee_code is not None:
        emp.employee_code = payload.employee_code
    if payload.department is not None:
        emp.department = payload.department

    db.commit()
    db.refresh(emp)
    logger.info("employee updated id=%s", emp.id)
    return _to_response(emp)


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    response_class=Response,
    summary="Delete an employee (cascades to their documents)",
)
def delete_employee(
    employee_id: Annotated[str, Path(description="Employee UUID.")],
    db: Session = Depends(get_db),
) -> None:
    removed = repo.delete_employee(db, employee_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found.",
        )
    db.commit()
    logger.info("employee deleted id=%s", employee_id)
    return None
