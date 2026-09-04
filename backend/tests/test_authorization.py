from tests.conftest import login, auth_headers


def _create_order(client, token, customer_id, product_id, qty=1):
    payload = {"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": qty}]}
    resp = client.post("/api/orders", json=payload, headers=auth_headers(token))
    assert resp.status_code == 201
    return resp.json()["id"]


def test_salesman_cannot_view_another_salesmans_order(client, seed_data):
    token1 = login(client, "sales1", "Sales123!")
    token2 = login(client, "sales2", "Sales123!")
    order_id = _create_order(client, token1, seed_data["customer"].id, seed_data["product1"].id)

    resp = client.get(f"/api/orders/{order_id}", headers=auth_headers(token2))
    assert resp.status_code == 403


def test_salesman_order_list_only_shows_own_orders(client, seed_data):
    token1 = login(client, "sales1", "Sales123!")
    token2 = login(client, "sales2", "Sales123!")
    _create_order(client, token1, seed_data["customer"].id, seed_data["product1"].id)

    resp = client.get("/api/orders", headers=auth_headers(token2))
    assert resp.status_code == 200
    assert resp.json() == []

    resp1 = client.get("/api/orders", headers=auth_headers(token1))
    assert len(resp1.json()) == 1


def test_admin_sees_all_orders_across_salesmen(client, seed_data):
    token1 = login(client, "sales1", "Sales123!")
    token2 = login(client, "sales2", "Sales123!")
    admin_token = login(client, "admin", "Admin123!")

    _create_order(client, token1, seed_data["customer"].id, seed_data["product1"].id)
    _create_order(client, token2, seed_data["customer"].id, seed_data["product1"].id)

    resp = client.get("/api/orders", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_salesman_cannot_access_dashboard_metrics(client, seed_data):
    token = login(client, "sales1", "Sales123!")
    resp = client.get("/api/dashboard/metrics", headers=auth_headers(token))
    assert resp.status_code == 403


def test_admin_can_access_dashboard_metrics(client, seed_data):
    admin_token = login(client, "admin", "Admin123!")
    resp = client.get("/api/dashboard/metrics", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "total_sales" in body and "total_orders" in body and "total_customers" in body


def test_salesman_cannot_create_product(client, seed_data):
    token = login(client, "sales1", "Sales123!")
    resp = client.post(
        "/api/products",
        json={"sku": "NEW-1", "name": "New Product", "price": 5.0, "stock_quantity": 10},
        headers=auth_headers(token),
    )
    assert resp.status_code == 403


def test_admin_can_create_product(client, seed_data):
    admin_token = login(client, "admin", "Admin123!")
    resp = client.post(
        "/api/products",
        json={"sku": "NEW-1", "name": "New Product", "price": 5.0, "stock_quantity": 10},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 201


def test_salesman_cannot_list_users(client, seed_data):
    token = login(client, "sales1", "Sales123!")
    resp = client.get("/api/users", headers=auth_headers(token))
    assert resp.status_code == 403


def test_only_admin_can_update_order_status(client, seed_data):
    token = login(client, "sales1", "Sales123!")
    admin_token = login(client, "admin", "Admin123!")
    order_id = _create_order(client, token, seed_data["customer"].id, seed_data["product1"].id)

    resp = client.patch(f"/api/orders/{order_id}/status", json={"status": "confirmed"}, headers=auth_headers(token))
    assert resp.status_code == 403

    resp = client.patch(f"/api/orders/{order_id}/status", json={"status": "confirmed"}, headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"
