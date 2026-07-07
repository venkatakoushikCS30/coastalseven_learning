"""Liveness / readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthResponse

router = APIRouter(tags=["meta"])


@router.get("/health", response_model=HealthResponse, summary="Liveness check")
def health() -> HealthResponse:
    """Return the application health, version, and active environment."""
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        env=settings.app_env,
    )
