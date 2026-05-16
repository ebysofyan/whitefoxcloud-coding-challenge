from fastapi.testclient import TestClient


def test_full_auth_and_book_lifecycle(client: TestClient, dynamodb_table):
    """Integration: login → create book → get book → unauthorized access."""
    login_resp = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "password": "admin123",
        },
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    book_data = {
        "id": "int-test",
        "author": "/authors/test",
        "name": "Integration Book",
        "note": "Testing full flow.",
        "serial": "INT001",
    }
    create_resp = client.post("/api/books", json=book_data, headers=headers)
    assert create_resp.status_code == 201

    get_resp = client.get("/api/books/int-test", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == book_data["name"]

    no_auth_resp = client.get("/api/books/int-test")
    assert no_auth_resp.status_code == 401

    nf_resp = client.get("/api/books/nonexistent", headers=headers)
    assert nf_resp.status_code == 404
