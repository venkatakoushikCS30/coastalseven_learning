"""Generic Pydantic schemas shared across routers."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIModel(BaseModel):
    """Base model with ORM-friendly configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        populate_by_name=True,
    )


class HealthResponse(APIModel):
    """Response payload for ``GET /health``."""

    status: str = Field(default="ok", description="Liveness status, always ``ok``.")
    version: str = Field(description="Application version.")
    env: str = Field(description="Active runtime environment.")


class ErrorResponse(APIModel):
    """Standard error envelope."""

    code: str = Field(description="Machine-readable error code.")
    message: str = Field(description="Human-readable error message.")
    details: list[dict] | None = Field(default=None, description="Optional structured details.")


class Envelope(APIModel, Generic[T]):
    """Generic response envelope.

    Keeps room for a top-level ``data`` field once real payloads exist.
    """

    data: T | None = None
    meta: dict[str, str] | None = None
