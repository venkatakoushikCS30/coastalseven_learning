"""FastAPI application entry point.

Creates the app, configures logging + database, registers routers, and
exposes the full API surface. The OCR pipeline is added in later phases.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from app.api import api_router
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging, get_logger
from app.database.db import init_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> Any:
    """Application lifespan: setup on start, cleanup on stop."""
    configure_logging()
    logger.info(
        "starting %s v%s env=%s",
        settings.app_name,
        settings.app_version,
        settings.app_env,
    )
    init_db()
    yield
    logger.info("shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    """Application factory."""
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Upload employee identity documents, extract structured fields via OCR, "
            "verify them, and persist the result in SQLite.\n\n"
            "**API base path:** `/api/v1`\n\n"
            "Interactive docs: `/docs` (Swagger) and `/redoc`."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    register_error_handlers(app)
    app.include_router(api_router)

    return app


app: FastAPI = create_app()
