"""SQLAlchemy engine, session factory, and declarative Base.

Single source of truth for database access. Modules that need a session
should use the :func:`get_db` FastAPI dependency rather than creating
their own engine.
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _build_engine(url: str) -> Engine:
    """Create a SQLAlchemy engine with sensible defaults per backend."""
    connect_args: dict[str, Any] = {}
    engine_kwargs: dict[str, Any] = {"future": True}

    if url.startswith("sqlite"):
        # SQLite needs the same connection across requests in a single thread.
        connect_args["check_same_thread"] = False
        engine_kwargs["connect_args"] = connect_args

    engine = create_engine(url, **engine_kwargs)

    if url.startswith("sqlite"):
        # Enforce foreign keys on SQLite (off by default).
        @event.listens_for(engine, "connect")
        def _enable_sqlite_fk(dbapi_connection: Any, _connection_record: Any) -> None:  # noqa: ANN401
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine: Engine = _build_engine(settings.database_url)
SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a request-scoped :class:`Session`."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        logger.exception("database session error; rolling back")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Context manager for use outside of FastAPI (scripts, services)."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        logger.exception("session_scope error; rolling back")
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Create tables for all imported models. No-op until models exist."""
    # Import models so they are registered on Base.metadata before create_all.
    from app import models  # noqa: F401  (side-effect import)

    Base.metadata.create_all(bind=engine)
    logger.info("database initialized url=%s", settings.database_url)
