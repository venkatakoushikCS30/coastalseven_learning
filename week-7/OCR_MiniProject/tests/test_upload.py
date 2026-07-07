"""Tests for the documents upload + listing endpoints."""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient

# Minimal valid PNG (1x1) — embedded as raw bytes.
_PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c63000100000005000100"
    "0d0a2db40000000049454e44ae426082"
)


def _png_file(name: str = "card.png") -> tuple[str, io.BytesIO, str]:
    return name, io.BytesIO(_PNG_BYTES), "image/png"


def test_upload_happy_path(client: TestClient) -> None:
    name, buf, ctype = _png_file("aadhaar.png")
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": (name, buf, ctype)},
        data={"document_type": "aadhaar"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["document_type"] == "aadhaar"
    assert body["original_filename"] == "aadhaar.png"
    assert body["content_type"] == "image/png"
    assert body["size_bytes"] == len(_PNG_BYTES)
    assert len(body["sha256"]) == 64
    assert body["status"] == "received"
    assert body["stored_path"].endswith(".png")


def test_upload_rejects_empty_file(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": ("x.png", io.BytesIO(b""), "image/png")},
        data={"document_type": "aadhaar"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] in {"empty_upload"}


def test_upload_rejects_bad_extension(client: TestClient) -> None:
    name, buf, ctype = _png_file("doc.pdf")
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": (name, buf, ctype)},
        data={"document_type": "aadhaar"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "unsupported_extension"


def test_upload_rejects_non_image_bytes(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": ("x.png", io.BytesIO(b"hello world"), "image/png")},
        data={"document_type": "aadhaar"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "invalid_image"


def test_upload_rejects_unknown_document_type(client: TestClient) -> None:
    name, buf, ctype = _png_file()
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": (name, buf, ctype)},
        data={"document_type": "drivers_license"},
    )
    assert resp.status_code == 400
    assert "document_type" in resp.text.lower()


def test_list_documents_returns_empty(client: TestClient) -> None:
    resp = client.get("/api/v1/documents")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"items": [], "total": 0}


def test_openapi_lists_endpoints(client: TestClient) -> None:
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    paths = resp.json()["paths"].keys()
    assert "/health" in paths
    assert "/api/v1/documents/upload" in paths
    assert "/api/v1/documents" in paths
