"""Smoke tests for the Gradio Blocks interface.

The UI talks to the FastAPI backend through ``APIClient``. We mock the
client to keep these tests self-contained.
"""

from __future__ import annotations

from typing import Any

from gradio_app.app import _check_backend, _handle_upload, build_interface
from gradio_app.client import APIError


class _StubClient:
    def __init__(self, *, health: dict[str, Any] | None = None, upload: dict[str, Any] | None = None) -> None:
        self.health_payload = health or {"status": "ok", "version": "9.9.9", "env": "test"}
        self.upload_payload = upload or {
            "document_id": "doc-1",
            "document_type": "aadhaar",
            "employee_id": "e-1",
            "stored_path": "/tmp/x",
            "original_filename": "aadhaar.png",
            "content_type": "image/png",
            "size_bytes": 12,
            "sha256": "z" * 64,
            "uploaded_at": "2026-01-01T00:00:00Z",
            "status": "received",
        }
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def health(self) -> dict[str, Any]:
        return self.health_payload

    def upload_document(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("upload", kwargs))
        return self.upload_payload

    def get_document(self, document_id: str) -> dict[str, Any]:
        self.calls.append(("get", {"id": document_id}))
        return {**self.upload_payload, "document_id": document_id, "has_ocr": False}

    def process_document(self, document_id: str) -> dict[str, Any]:
        self.calls.append(("process", {"id": document_id}))
        return {**self.upload_payload, "document_id": document_id, "has_ocr": True}

    def list_employees(self, search: str | None = None) -> dict[str, Any]:
        self.calls.append(("list_employees", {"search": search}))
        return {"items": [], "total": 0}

    def list_documents(self, search: str | None = None) -> dict[str, Any]:
        self.calls.append(("list_documents", {"search": search}))
        return {"items": [], "total": 0}


def _factory(client: _StubClient):
    def factory() -> _StubClient:
        return client
    return factory


def test_build_interface_returns_blocks() -> None:
    demo = build_interface(client_factory=_factory(_StubClient()))
    # Gradio's Blocks has a ``blocks`` dict of registered components.
    assert demo.blocks
    classes = {c.__class__.__name__ for c in demo.blocks.values()}
    assert "File" in classes
    assert "Dropdown" in classes
    assert "Textbox" in classes
    assert "Button" in classes
    assert "Image" in classes
    assert "Code" in classes


def test_check_backend_happy() -> None:
    client = _StubClient(health={"status": "ok", "version": "1.2.3", "env": "test"})
    msg = _check_backend(client)
    assert "OK" in msg
    assert "1.2.3" in msg


def test_check_backend_error() -> None:
    class _Broken:
        def health(self) -> dict[str, Any]:
            raise APIError("nope", code="connection_error")

    msg = _check_backend(_Broken())
    assert "unreachable" in msg.lower()


def test_handle_upload_returns_three_strings(tmp_path) -> None:
    # Create a real temp file so the upload handler can read it.
    p = tmp_path / "aadhaar.png"
    p.write_bytes(b"\x89PNG\r\n\x1a\nfaketestbytes")

    client = _StubClient()
    gen = _handle_upload(
        str(p), "aadhaar", "e-1", client_factory=_factory(client)
    )
    results = list(gen)
    
    assert len(results) == 2
    # Check the final yielded value
    status, body, doc_id = results[-1]
    
    assert "Processed doc-1" in status
    assert "doc-1" in doc_id
    # Body is a pretty-printed JSON string of the detail response.
    assert "has_ocr" in body
    assert client.calls[0][0] == "upload"
    assert client.calls[1][0] == "process"


def test_handle_upload_no_file() -> None:
    gen = _handle_upload(None, "aadhaar", None, client_factory=_factory(_StubClient()))
    results = list(gen)
    status, body, doc_id = results[-1]
    assert "No file" in status
    assert body == ""
    assert doc_id == ""


def test_handle_upload_backend_error(tmp_path) -> None:
    p = tmp_path / "x.png"
    p.write_bytes(b"x")

    class _Boom:
        def upload_document(self, **_kwargs: Any) -> dict[str, Any]:
            raise APIError("bad image", status_code=400, code="invalid_image")

        def process_document(self, _id: str) -> dict[str, Any]:
            raise AssertionError("should not be called")

    gen = _handle_upload(str(p), "aadhaar", None, client_factory=_factory(_Boom()))
    results = list(gen)
    status, body, _doc = results[-1]
    assert "Upload failed" in status
    assert "invalid_image" in body
