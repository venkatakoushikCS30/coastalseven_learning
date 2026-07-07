"""Thin HTTP client the Gradio UI uses to talk to the FastAPI backend.

Why not ``requests``?  The portal already has ``httpx`` as a test dep
and ``urllib`` in the stdlib; pulling in a third HTTP client is
unnecessary. This module is intentionally small and easy to mock.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.logging import get_logger

logger = get_logger(__name__)


class APIError(RuntimeError):
    """Raised when the FastAPI backend returns a non-success response."""

    def __init__(self, message: str, *, status_code: int | None = None, code: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code


class APIClient:
    """Synchronous HTTP client for the FastAPI portal backend."""

    def __init__(self, base_url: str, *, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # --- public API ------------------------------------------------------

    def health(self) -> dict[str, Any]:
        """Hit ``GET /health`` and return the parsed JSON body."""
        return self._get_json("/health")

    def upload_document(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str,
        document_type: str,
        employee_id: str | None = None,
    ) -> dict[str, Any]:
        """Multipart upload to ``POST /api/v1/documents/upload``."""
        boundary = "----gradio-portal-boundary-7c4f"
        body = self._build_multipart(
            boundary=boundary,
            fields={"document_type": document_type, "employee_id": employee_id},
            file_field="file",
            filename=filename,
            content=content,
            content_type=content_type,
        )
        req = Request(
            url=f"{self.base_url}/api/v1/documents/upload",
            data=body,
            method="POST",
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        return self._request_json(req)

    def get_document(self, document_id: str) -> dict[str, Any]:
        """Hit ``GET /api/v1/documents/{id}`` and return the parsed JSON body."""
        return self._get_json(f"/api/v1/documents/{document_id}")

    def process_document(self, document_id: str) -> dict[str, Any]:
        """Hit ``POST /api/v1/documents/{id}/process``."""
        req = Request(
            url=f"{self.base_url}/api/v1/documents/{document_id}/process",
            method="POST",
            headers={"Content-Length": "0"}
        )
        return self._request_json(req)

    def list_employees(self, search: str | None = None) -> dict[str, Any]:
        """Hit ``GET /api/v1/employees``."""
        params = {}
        if search:
            params["search"] = search
        return self._get_json("/api/v1/employees", params=params)

    def list_documents(self, search: str | None = None) -> dict[str, Any]:
        """Hit ``GET /api/v1/documents``."""
        params = {}
        if search:
            params["search"] = search
        return self._get_json("/api/v1/documents", params=params)

    # --- internals -------------------------------------------------------

    def _get_json(self, path: str, params: Mapping[str, str] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        if params:
            url = f"{url}?{urlencode(params)}"
        return self._request_json(Request(url=url, method="GET"))

    def _request_json(self, req: Request) -> dict[str, Any]:
        try:
            with urlopen(req, timeout=self.timeout) as resp:  # noqa: S310 - URL is config-controlled
                payload = resp.read()
        except HTTPError as exc:
            # The FastAPI error envelope is JSON: {"error": {"code","message"}}
            try:
                body = exc.read().decode("utf-8", errors="replace")
                parsed = json.loads(body)
                code = (parsed.get("error") or {}).get("code") or "http_error"
                message = (parsed.get("error") or {}).get("message") or body or exc.reason
            except (ValueError, AttributeError):
                code, message = "http_error", str(exc.reason)
            logger.info("api error status=%s code=%s", exc.code, code)
            raise APIError(message, status_code=exc.code, code=code) from exc
        except URLError as exc:
            raise APIError(f"Cannot reach backend: {exc.reason}", code="connection_error") from exc

        try:
            return json.loads(payload.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise APIError("Backend returned a non-JSON response.", code="invalid_response") from exc

    @staticmethod
    def _build_multipart(
        *,
        boundary: str,
        fields: Mapping[str, str | None],
        file_field: str,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> bytes:
        """Construct a multipart/form-data body manually (no external deps)."""
        chunks: list[bytes] = []
        for name, value in fields.items():
            if value is None or value == "":
                continue
            chunks.extend(
                [
                    f"--{boundary}\r\n".encode("utf-8"),
                    f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"),
                    f"{value}\r\n".encode("utf-8"),
                ]
            )
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'.encode("utf-8"),
                f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"),
                content,
                b"\r\n",
                f"--{boundary}--\r\n".encode("utf-8"),
            ]
        )
        return b"".join(chunks)
