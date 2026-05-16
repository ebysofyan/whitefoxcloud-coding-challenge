def test_create_book_unauthorized(client, dynamodb_table):
    response = client.post(
        "/api/books",
        json={
            "id": "/books/id1",
            "author": "/authors/id1",
            "name": "Test",
            "note": "Note",
            "serial": "S001",
        },
    )
    assert response.status_code == 401


def test_create_book_success(client, dynamodb_table, auth_token):
    response = client.post(
        "/api/books",
        json={
            "id": "/books/id1",
            "author": "/authors/id1",
            "name": "Fancy Tech",
            "note": "Awesome book",
            "serial": "C040102",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "/books/id1"


def test_create_book_missing_fields(client, dynamodb_table, auth_token):
    response = client.post(
        "/api/books",
        json={"id": "/books/id2"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 400


def test_create_book_auto_id(client, dynamodb_table, auth_token):
    response = client.post(
        "/api/books",
        json={
            "author": "/authors/id1",
            "name": "Auto ID Book",
            "note": "Note",
            "serial": "AUTO001",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert len(data["id"]) > 0


def test_list_books_unauthorized(client, dynamodb_table):
    response = client.get("/api/books")
    assert response.status_code == 401


def test_list_books_success(client, dynamodb_table, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    client.post(
        "/api/books",
        json={
            "id": "book-1",
            "author": "/authors/id1",
            "name": "Book One",
            "note": "Note 1",
            "serial": "S001",
        },
        headers=headers,
    )
    client.post(
        "/api/books",
        json={
            "id": "book-2",
            "author": "/authors/id2",
            "name": "Book Two",
            "note": "Note 2",
            "serial": "S002",
        },
        headers=headers,
    )
    response = client.get("/api/books", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 2
    assert data["items"][0]["id"] in ("book-1", "book-2")
    assert data["has_prev"] is False
    assert data["prev_cursor"] is None


def test_list_books_pagination_next_then_prev(client, dynamodb_table, auth_token):
    """Walk forward with next_cursor, then back via prev_cursor (one-step echo)."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    for i in range(3):
        client.post(
            "/api/books",
            json={
                "id": f"book-{i}",
                "author": "/authors/id1",
                "name": f"Book {i}",
                "note": "n",
                "serial": f"S{i:03d}",
            },
            headers=headers,
        )

    page1 = client.get("/api/books?limit=2", headers=headers).json()
    assert len(page1["items"]) == 2
    assert page1["has_next"] is True
    assert page1["has_prev"] is False
    assert page1["next_cursor"] is not None

    page2 = client.get(
        f"/api/books?limit=2&cursor={page1['next_cursor']}",
        headers=headers,
    ).json()
    assert len(page2["items"]) == 1
    assert page2["has_prev"] is True
    assert page2["prev_cursor"] == page1["next_cursor"]


def test_list_books_invalid_cursor(client, dynamodb_table, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/books?cursor=not-base64!!!", headers=headers)
    assert response.status_code == 400


def test_list_books_limit_validation(client, dynamodb_table, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/books?limit=0", headers=headers)
    assert response.status_code == 400


def test_get_book_unauthorized(client, dynamodb_table):
    response = client.get("/api/books/simple-id")
    assert response.status_code == 401


def test_get_book_success(client, dynamodb_table, auth_token):
    client.post(
        "/api/books",
        json={
            "id": "book-1",
            "author": "/authors/id1",
            "name": "Fancy Tech",
            "note": "Awesome book",
            "serial": "C040102",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    response = client.get(
        "/api/books/book-1", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "book-1"


def test_get_book_not_found(client, dynamodb_table, auth_token):
    response = client.get(
        "/api/books/nonexistent", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_delete_book_unauthorized(client, dynamodb_table):
    response = client.delete("/api/books/book-1")
    assert response.status_code == 401


def test_spec_example_payload_round_trips(client, dynamodb_table, auth_token):
    """Challenge spec example: POST + GET round-trip by trailing id segment."""
    payload = {
        "id": "id1",
        "author": "/authors/id1",
        "name": "Fancy Tech",
        "note": "Awesome book for beginners in Fancy.",
        "serial": "C040102",
    }
    headers = {"Authorization": f"Bearer {auth_token}"}
    create = client.post("/api/books", json=payload, headers=headers)
    assert create.status_code == 201
    # Per spec: GET /api/books/id1
    get = client.get("/api/books/id1", headers=headers)
    assert get.status_code == 200
    assert get.json() == payload


def test_delete_book_success(client, dynamodb_table, auth_token):
    client.post(
        "/api/books",
        json={
            "id": "book-to-delete",
            "author": "/authors/id1",
            "name": "Delete Me",
            "note": "Note",
            "serial": "DEL001",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    response = client.delete(
        "/api/books/book-to-delete",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 204
    get_resp = client.get(
        "/api/books/book-to-delete",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert get_resp.status_code == 404
