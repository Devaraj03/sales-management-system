from tests.conftest import login, auth_headers


def test_login_missing_fields_returns_422(client, seed_data):
    resp = client.post("/api/auth/login", data={"username": "sales1"})  # no password
    assert resp.status_code == 422


def test_create_customer_invalid_email_returns_422(client, seed_data):
    token = login(client, "sales1", "Sales123!")
    resp = client.post(
        "/api/customers",
        json={"name": "Bad Email Co", "email": "not-an-email"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 422


def test_create_product_negative_price_returns_422(client, seed_data):
    admin_token = login(client, "admin", "Admin123!")
    resp = client.post(
        "/api/products",
        json={"sku": "NEG-1", "name": "Negative Price", "price": -5, "stock_quantity": 10},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 422


def test_create_product_duplicate_sku_returns_409(client, seed_data):
    admin_token = login(client, "admin", "Admin123!")
    payload = {"sku": "DUP-1", "name": "Dup A", "price": 1, "stock_quantity": 1}
    resp1 = client.post("/api/products", json=payload, headers=auth_headers(admin_token))
    assert resp1.status_code == 201

    resp2 = client.post("/api/products", json={**payload, "name": "Dup B"}, headers=auth_headers(admin_token))
    assert resp2.status_code == 409


def test_get_nonexistent_order_returns_404(client, seed_data):
    token = login(client, "sales1", "Sales123!")
    resp = client.get("/api/orders/00000000-0000-0000-0000-000000000000", headers=auth_headers(token))
    assert resp.status_code == 404


def test_create_order_with_no_items_returns_422(client, seed_data):
    token = login(client, "sales1", "Sales123!")
    resp = client.post(
        "/api/orders",
        json={"customer_id": seed_data["customer"].id, "items": []},
        headers=auth_headers(token),
    )
    assert resp.status_code == 422


def test_create_order_unknown_product_returns_404(client, seed_data):
    token = login(client, "sales1", "Sales123!")
    resp = client.post(
        "/api/orders",
        json={
            "customer_id": seed_data["customer"].id,
            "items": [{"product_id": "00000000-0000-0000-0000-000000000000", "quantity": 1}],
        },
        headers=auth_headers(token),
    )
    assert resp.status_code == 404


def test_customer_search_is_case_insensitive(client, seed_data):
    token = login(client, "sales1", "Sales123!")
    resp = client.get("/api/customers?search=test", headers=auth_headers(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    resp2 = client.get("/api/customers?search=TEST", headers=auth_headers(token))
    assert len(resp2.json()) == 1
