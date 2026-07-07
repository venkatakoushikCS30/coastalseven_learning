"""SQLAlchemy ORM models.

Importing this package registers all models on :class:`Base.metadata`,
which is what :func:`app.database.db.init_db` relies on.
"""

from app.models.document import Document
from app.models.employee import Employee
from app.models.enums import DocumentStatus, DocumentType

__all__ = ["Document", "DocumentStatus", "DocumentType", "Employee"]
