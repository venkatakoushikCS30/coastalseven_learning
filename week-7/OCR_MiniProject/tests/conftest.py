"""Shared pytest fixtures.

Ensures the project root is importable and pins runtime paths to a
temporary directory so tests do not write into the repo's ``data/``
folder. The SQLite database is recreated before every test so tests
remain isolated even though the FastAPI ``TestClient`` is session-
scoped.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Importing the app causes ``app.core.config.settings`` to be created.
# We then mutate that single instance in place so the rest of the app
# (which captured a reference to it) sees the overrides.
from app.core import config as config_module  # noqa: E402
from app.core.config import settings as app_settings  # noqa: E402
from app.database.db import Base, engine  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _isolated_runtime_dirs(tmp_path_factory: pytest.TempPathFactory) -> None:
    """Redirect uploads + logs to a temp dir for the entire test session."""
    base = tmp_path_factory.mktemp("ocr_mini_runtime")
    (base / "logs").mkdir(parents=True, exist_ok=True)
    (base / "uploads").mkdir(parents=True, exist_ok=True)
    (base / "data").mkdir(parents=True, exist_ok=True)

    app_settings.upload_dir = base / "uploads"
    app_settings.log_file = base / "logs" / "app.log"
    app_settings.database_url = f"sqlite:///{base / 'data' / 'portal.db'}"
    app_settings.log_level = "WARNING"
    app_settings.max_upload_mb = 2
    app_settings.ensure_runtime_dirs()

    config_module.get_settings.cache_clear()  # type: ignore[attr-defined]


@pytest.fixture(autouse=True)
def _reset_db() -> None:
    """Drop and recreate all tables before each test for full isolation."""
    # Importing the models package registers them on Base.metadata.
    from app import models  # noqa: F401
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Return a session-scoped TestClient bound to a fresh app instance."""
    from app.main import create_app  # imported here so env overrides stick

    app = create_app()
    with TestClient(app) as c:
        yield c
