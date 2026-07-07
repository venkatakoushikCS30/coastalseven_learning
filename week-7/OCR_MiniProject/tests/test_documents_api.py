"""Tests for the documents API (Phase 3: DB-backed)."""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient

# Minimal valid PNG (1x1).
_PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c63000100000005000100"
    "0d0a2db40000000049454e44ae426082"
)


def _png_file(name: str = "card.png") -> tuple[str, io.BytesIO, str]:
    from PIL import Image
    import os
    
    buf = io.BytesIO()
    # Random color to ensure unique sha256 hashes per test
    color = (ord(os.urandom(1)), ord(os.urandom(1)), ord(os.urandom(1)))
    img = Image.new("RGB", (1, 1), color=color)
    img.save(buf, format="PNG")
    return name, io.BytesIO(buf.getvalue()), "image/png"


def test_upload_creates_db_row(client: TestClient) -> None:
    name, buf, ctype = _png_file("aadhaar.png")
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": (name, buf, ctype)},
        data={"document_type": "aadhaar"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["document_type"] == "aadhaar"
    assert body["status"] == "received"
    assert body["employee_id"]  # auto-assigned
    assert body["size_bytes"] == len(_PNG_BYTES)
    assert len(body["sha256"]) == 64


def test_upload_with_explicit_employee(client: TestClient) -> None:
    # Create an employee first.
    emp_resp = client.post(
        "/api/v1/employees",
        json={"full_name": "Jane Doe", "email": "jane@example.com"},
    )
    assert emp_resp.status_code == 201, emp_resp.text
    emp_id = emp_resp.json()["id"]

    name, buf, ctype = _png_file("pan.png")
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": (name, buf, ctype)},
        data={"document_type": "pan", "employee_id": emp_id},
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["employee_id"] == emp_id


def test_upload_unknown_employee_returns_404(client: TestClient) -> None:
    name, buf, ctype = _png_file()
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": (name, buf, ctype)},
        data={"document_type": "aadhaar", "employee_id": "no-such-id"},
    )
    assert resp.status_code == 404


def test_upload_rejects_empty_file(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": ("x.png", io.BytesIO(b""), "image/png")},
        data={"document_type": "aadhaar"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "empty_upload"


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
    assert resp.json()["error"]["code"] == "unsupported_document_type"


def test_list_documents_filtering(client: TestClient) -> None:
    # We uploaded two documents in the previous tests via fixtures? 
    # Actually, tests are isolated. We need to upload first.
    client.post("/api/v1/employees", json={"full_name": "Employee"})
    
    name1, buf1, ctype1 = _png_file("file1.png")
    client.post(
        "/api/v1/documents/upload",
        data={"document_type": "aadhaar"},
        files={"file": (name1, buf1, ctype1)},
    )
    name2, buf2, ctype2 = _png_file("test_pan.png")
    client.post(
        "/api/v1/documents/upload",
        data={"document_type": "pan"},
        files={"file": (name2, buf2, ctype2)},
    )

    # list all
    r = client.get("/api/v1/documents")
    assert r.status_code == 200
    assert r.json()["total"] == 2

    # filter by type
    r_aadhaar = client.get("/api/v1/documents?document_type=aadhaar")
    assert r_aadhaar.json()["total"] == 1
    
    # filter by search
    r_search = client.get("/api/v1/documents?search=test_pan")
    assert r_search.json()["total"] == 1
    assert r_search.json()["items"][0]["original_filename"] == "test_pan.png"


def test_list_documents_returns_inserted_rows(client: TestClient) -> None:
    for dt in ("aadhaar", "pan", "passport"):
        name, buf, ctype = _png_file(f"{dt}.png")
        r = client.post(
            "/api/v1/documents/upload",
            files={"file": (name, buf, ctype)},
            data={"document_type": dt},
        )
        assert r.status_code == 201, r.text

    resp = client.get("/api/v1/documents")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 3
    assert len(body["items"]) == 3
    types_returned = {item["document_type"] for item in body["items"]}
    assert types_returned == {"aadhaar", "pan", "passport"}


def test_list_documents_filter_by_type(client: TestClient) -> None:
    for dt in ("aadhaar", "pan"):
        name, buf, ctype = _png_file(f"{dt}.png")
        client.post(
            "/api/v1/documents/upload",
            files={"file": (name, buf, ctype)},
            data={"document_type": dt},
        )

    resp = client.get("/api/v1/documents", params={"document_type": "aadhaar"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["document_type"] == "aadhaar"


def test_get_document_detail(client: TestClient) -> None:
    name, buf, ctype = _png_file("aadhaar.png")
    r = client.post(
        "/api/v1/documents/upload",
        files={"file": (name, buf, ctype)},
        data={"document_type": "aadhaar"},
    )
    doc_id = r.json()["document_id"]

    resp = client.get(f"/api/v1/documents/{doc_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["document_id"] == doc_id
    assert body["has_ocr"] is False
    assert body["has_verification"] is False


def test_get_document_404(client: TestClient) -> None:
    resp = client.get("/api/v1/documents/does-not-exist")
    assert resp.status_code == 404


def test_delete_document(client: TestClient) -> None:
    name, buf, ctype = _png_file()
    r = client.post(
        "/api/v1/documents/upload",
        files={"file": (name, buf, ctype)},
        data={"document_type": "aadhaar"},
    )
    doc_id = r.json()["document_id"]

    d = client.delete(f"/api/v1/documents/{doc_id}")
    assert d.status_code == 204

    g = client.get(f"/api/v1/documents/{doc_id}")
    assert g.status_code == 404


def test_openapi_lists_new_endpoints(client: TestClient) -> None:
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    paths = resp.json()["paths"].keys()
    assert "/api/v1/employees" in paths
    assert "/api/v1/documents/{document_id}" in paths
