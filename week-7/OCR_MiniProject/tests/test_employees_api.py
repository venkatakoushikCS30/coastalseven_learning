"""Tests for the employees API."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_employee_minimal(client: TestClient) -> None:
    resp = client.post("/api/v1/employees", json={"full_name": "Jane Doe"})
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["full_name"] == "Jane Doe"
    assert body["document_count"] == 0
    assert body["id"]


def test_create_employee_invalid_email(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/employees",
        json={"full_name": "Jane", "email": "not-an-email"},
    )
    assert resp.status_code == 422


def test_list_employees_empty(client: TestClient) -> None:
    resp = client.get("/api/v1/employees")
    assert resp.status_code == 200
    assert resp.json() == {"items": [], "total": 0}


def test_list_employees_filtering(client: TestClient) -> None:
    for i in range(3):
        client.post("/api/v1/employees", json={"full_name": f"Name {i}"})
        
    response = client.get("/api/v1/employees?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2

    # test search
    response = client.get("/api/v1/employees?search=Name%200")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["full_name"] == "Name 0"


def test_employee_crud_flow(client: TestClient) -> None:
    # Create
    c = client.post(
        "/api/v1/employees",
        json={"full_name": "A", "email": "a@example.com", "department": "Eng"},
    )
    assert c.status_code == 201
    emp_id = c.json()["id"]

    # Read
    g = client.get(f"/api/v1/employees/{emp_id}")
    assert g.status_code == 200
    assert g.json()["department"] == "Eng"

    # Update
    u = client.patch(
        f"/api/v1/employees/{emp_id}",
        json={"department": "Platform"},
    )
    assert u.status_code == 200
    assert u.json()["department"] == "Platform"

    # Delete
    d = client.delete(f"/api/v1/employees/{emp_id}")
    assert d.status_code == 204

    # Gone
    g2 = client.get(f"/api/v1/employees/{emp_id}")
    assert g2.status_code == 404


def test_update_unknown_employee(client: TestClient) -> None:
    resp = client.patch("/api/v1/employees/nope", json={"full_name": "X"})
    assert resp.status_code == 404


def test_delete_unknown_employee(client: TestClient) -> None:
    resp = client.delete("/api/v1/employees/nope")
    assert resp.status_code == 404
