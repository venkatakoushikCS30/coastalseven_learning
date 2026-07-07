"""Employee ORM model."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base

if TYPE_CHECKING:  # pragma: no cover - import-only type hints
    from app.models.document import Document


def _utcnow() -> datetime:
    """Return a timezone-aware UTC ``now`` (SQLite stores ISO 8601)."""
    return datetime.now(timezone.utc)


class Employee(Base):
    """An employee whose documents we verify."""

    __tablename__ = "employees"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    employee_code: Mapped[str | None] = mapped_column(
        String(64), nullable=True, unique=True, index=True
    )
    department: Mapped[str | None] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="employee",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"<Employee id={self.id!r} name={self.full_name!r}>"
