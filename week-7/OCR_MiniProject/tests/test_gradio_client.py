"""Tests for ``gradio_app.client.APIClient``.

Patches :mod:`urllib.request.urlopen` to avoid any real network I/O.
"""

from __future__ import annotations

import io
import json
from contextlib import contextmanager
from typing import Any
from unittest.mock import patch

import pytest
from urllib.error import HTTPError, URLError

from gradio_app.client import APIClient, APIError


# Minimal PNG (1x1) so the multipart builder is exercised with real bytes.
_PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c63000100000005000100"
    "0d0a2db40000000049454e44ae426082"
)


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *_exc: Any) -> None:
        return None


@contextmanager
def _mock_urlopen(side_effect: Any):
    """Patch ``urlopen`` to return ``side_effect`` for each call."""
    with patch("gradio_app.client.urlopen", side_effect=side_effect) as m:
        yield m


def test_health_returns_parsed_json() -> None:
    payload = {"status": "ok", "version": "0.1.0", "env": "test"}

    def fake_urlopen(req, timeout=0):  # noqa: ARG001
        return _FakeResponse(json.dumps(payload).encode("utf-8"))

    with _mock_urlopen(fake_urlopen):
        client = APIClient("http://api.test")
        result = client.health()
    assert result == payload


def test_upload_document_posts_multipart() -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(req, timeout=0):  # noqa: ARG001
        captured["url"] = req.full_url
        captured["method"] = req.method
        captured["headers"] = dict(req.headers)
        captured["body"] = req.data
        return _FakeResponse(json.dumps({"document_id": "abc"}).encode("utf-8"))

    with _mock_urlopen(fake_urlopen):
        APIClient("http://api.test").upload_document(
            filename="aadhaar.png",
            content=_PNG_BYTES,
            content_type="image/png",
            document_type="aadhaar",
            employee_id="e-1",
        )

    assert captured["url"] == "http://api.test/api/v1/documents/upload"
    assert captured["method"] == "POST"
    ctype = captured["headers"]["Content-type"]
    assert ctype.startswith("multipart/form-data; boundary=")
    body: bytes = captured["body"]
    assert b'name="document_type"' in body
    assert b"aadhaar" in body
    assert b'name="employee_id"' in body
    assert b"e-1" in body
    assert b'name="file"; filename="aadhaar.png"' in body
    assert _PNG_BYTES in body


def test_upload_document_omits_blank_employee_id() -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(req, timeout=0):  # noqa: ARG001
        captured["body"] = req.data
        return _FakeResponse(b"{}")

    with _mock_urlopen(fake_urlopen):
        APIClient("http://api.test").upload_document(
            filename="x.png",
            content=_PNG_BYTES,
            content_type="image/png",
            document_type="aadhaar",
            employee_id=None,
        )

    assert b'name="employee_id"' not in captured["body"]


def test_http_error_parses_envelope() -> None:
    def fake_urlopen(req, timeout=0):  # noqa: ARG001
        raise HTTPError(
            url=req.full_url,
            code=400,
            msg="Bad Request",
            hdrs=None,  # type: ignore[arg-type]
            fp=io.BytesIO(json.dumps({"error": {"code": "invalid_image", "message": "nope"}}).encode()),
        )

    with _mock_urlopen(fake_urlopen):
        client = APIClient("http://api.test")
        with pytest.raises(APIError) as exc:
            client.health()
    assert exc.value.status_code == 400
    assert exc.value.code == "invalid_image"


def test_url_error_yields_connection_error() -> None:
    def fake_urlopen(req, timeout=0):  # noqa: ARG001
        raise URLError("offline")

    with _mock_urlopen(fake_urlopen):
        client = APIClient("http://api.test")
        with pytest.raises(APIError) as exc:
            client.health()
    assert exc.value.code == "connection_error"


def test_non_json_response_raises_invalid_response() -> None:
    def fake_urlopen(req, timeout=0):  # noqa: ARG001
        return _FakeResponse(b"not json")

    with _mock_urlopen(fake_urlopen):
        client = APIClient("http://api.test")
        with pytest.raises(APIError) as exc:
            client.health()
    assert exc.value.code == "invalid_response"


def test_get_document_path() -> None:
    seen: list[str] = []

    def fake_urlopen(req, timeout=0):  # noqa: ARG001
        seen.append(req.full_url)
        return _FakeResponse(json.dumps({"document_id": "d-1"}).encode("utf-8"))

    with _mock_urlopen(fake_urlopen):
        result = APIClient("http://api.test/").get_document("d-1")
    assert seen == ["http://api.test/api/v1/documents/d-1"]
    assert result["document_id"] == "d-1"
