"""Custom exception types and FastAPI error handlers.

All API errors funnel through these handlers so the response shape is
predictable: ``{"error": {"code": ..., "message": ...}}``.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.utils.validators import ImageValidationError

logger = get_logger(__name__)


def _payload(code: str, message: str, **extra: Any) -> dict[str, Any]:
    body: dict[str, Any] = {"error": {"code": code, "message": message}}
    if extra:
        body["error"].update(extra)
    return body


def register_error_handlers(app: FastAPI) -> None:
    """Attach all error handlers to ``app``."""

    @app.exception_handler(ImageValidationError)
    async def _image_validation_handler(_req: Request, exc: ImageValidationError) -> JSONResponse:
        logger.info("image validation rejected code=%s", exc.code)
        # Upload too large maps to HTTP 413 (the rest stay at 400).
        status_code = 413 if exc.code == "file_too_large" else 400
        return JSONResponse(status_code=status_code, content=_payload(exc.code, str(exc)))

    @app.exception_handler(RequestValidationError)
    async def _request_validation_handler(_req: Request, exc: RequestValidationError) -> JSONResponse:
        logger.info("request validation rejected errors=%d", len(exc.errors()))
        return JSONResponse(
            status_code=422,
            content=_payload(
                "request_validation_error",
                "Request payload failed validation.",
                details=exc.errors(),
            ),
        )

    @app.exception_handler(ValueError)
    async def _value_error_handler(_req: Request, exc: ValueError) -> JSONResponse:
        logger.info("value error code=bad_request")
        return JSONResponse(status_code=400, content=_payload("bad_request", str(exc)))

    @app.exception_handler(FileNotFoundError)
    async def _not_found_handler(_req: Request, exc: FileNotFoundError) -> JSONResponse:
        logger.info("not found path=%s", getattr(exc, "filename", ""))
        return JSONResponse(status_code=404, content=_payload("not_found", str(exc) or "Not found."))

    @app.exception_handler(Exception)
    async def _unhandled_handler(_req: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled exception type=%s", exc.__class__.__name__)
        return JSONResponse(
            status_code=500,
            content=_payload("internal_error", "Internal server error.", error_type=exc.__class__.__name__),
        )
