"""Document ORM model."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.models.enums import DocumentStatus, DocumentType

if TYPE_CHECKING:  # pragma: no cover
    from app.models.employee import Employee


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Document(Base):
    """An uploaded employee document.

    The binary lives on disk (path stored in ``stored_path``). The
    database row holds metadata, processing status, and a SHA-256
    fingerprint. OCR / verification JSON is added in later phases.
    """

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Nullable so we can record an orphan upload first and bind it later.
    employee_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    document_type: Mapped[DocumentType] = mapped_column(
        SAEnum(DocumentType, name="document_type", native_enum=False, length=32),
        default=DocumentType.UNKNOWN,
        nullable=False,
        index=True,
    )

    status: Mapped[DocumentStatus] = mapped_column(
        SAEnum(DocumentStatus, name="document_status", native_enum=False, length=32),
        default=DocumentStatus.RECEIVED,
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    content_type: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    stored_path: Mapped[str] = mapped_column(String(1024), nullable=False)

    # Reserved for later phases. Keep them nullable to avoid empty-string bugs.
    ocr_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    employee: Mapped["Employee | None"] = relationship(
        "Employee", back_populates="documents", passive_deletes=True
    )

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"<Document id={self.id!r} type={self.document_type.value!r} status={self.status.value!r}>"
