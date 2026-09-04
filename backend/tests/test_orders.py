from decimal import Decimal

from tests.conftest import login, auth_headers


def test_create_order_computes_total_from_server_side_prices(client, seed_data):
    token = login(client, "sales1", "Sales123!")
    customer = seed_data["customer"]
    p1, p2 = seed_data["product1"], seed_data["product2"]

    payload = {
        "customer_id": customer.id,
        "items": [
            {"product_id": p1.id, "quantity": 3},   # 3 * 10.00 = 30.00
            {"product_id": p2.id, "quantity": 2},   # 2 * 25.50 = 51.00
        ],
    }
    resp = client.post("/api/orders", json=payload, headers=auth_headers(token))
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert Decimal(body["total_amount"]) == Decimal("81.00")
    assert body["status"] == "pending"
    assert len(body["items"]) == 2
    # unit_price on the order item must reflect the catalog price, not anything client-supplied
    prices = {item["product_id"]: item["unit_price"] for item in body["items"]}
    assert Decimal(prices[p1.id]) == Decimal("10.00")
    assert Decimal(prices[p2.id]) == Decimal("25.50")


def test_create_order_ignores_client_supplied_price_tampering(client, seed_data):
    """The API only accepts product_id + quantity; there is no price field a client could tamper with."""
    token = login(client, "sales1", "Sales123!")
    customer = seed_data["customer"]
    p1 = seed_data["product1"]

    payload = {
        "customer_id": customer.id,
        # Even if a malicious client stuffs a 'price' key in, the schema ignores unknown fields.
        "items": [{"product_id": p1.id, "quantity": 1, "price": "0.01"}],
    }
    resp = client.post("/api/orders", json=payload, headers=auth_headers(token))
    assert resp.status_code == 201
    assert Decimal(resp.json()["total_amount"]) == Decimal("10.00")


def test_create_order_rejects_zero_quantity(client, seed_data):
    token = login(client, "sales1", "Sales123!")
    payload = {
        "customer_id": seed_data["customer"].id,
        "items": [{"product_id": seed_data["product1"].id, "quantity": 0}],
    }
    resp = client.post("/api/orders", json=payload, headers=auth_headers(token))
    assert resp.status_code == 422


def test_create_order_rejects_unknown_customer(client, seed_data):
    token = login(client, "sales1", "Sales123!")
    payload = {
        "customer_id": "00000000-0000-0000-0000-000000000000",
        "items": [{"product_id": seed_data["product1"].id, "quantity": 1}],
    }
    resp = client.post("/api/orders", json=payload, headers=auth_headers(token))
    assert resp.status_code == 404


def test_create_order_rejects_insufficient_stock(client, seed_data):
    token = login(client, "sales1", "Sales123!")
    p2 = seed_data["product2"]  # stock_quantity = 5
    payload = {
        "customer_id": seed_data["customer"].id,
        "items": [{"product_id": p2.id, "quantity": 999}],
    }
    resp = client.post("/api/orders", json=payload, headers=auth_headers(token))
    assert resp.status_code == 400
    assert "Insufficient stock" in resp.json()["detail"]


def test_create_order_decrements_stock(client, seed_data):
    token = login(client, "sales1", "Sales123!")
    p1 = seed_data["product1"]  # stock = 100
    payload = {
        "customer_id": seed_data["customer"].id,
        "items": [{"product_id": p1.id, "quantity": 10}],
    }
    resp = client.post("/api/orders", json=payload, headers=auth_headers(token))
    assert resp.status_code == 201

    product_resp = client.get(f"/api/products/{p1.id}", headers=auth_headers(token))
    assert product_resp.json()["stock_quantity"] == 90


def test_order_appears_in_salesman_history(client, seed_data):
    token = login(client, "sales1", "Sales123!")
    payload = {
        "customer_id": seed_data["customer"].id,
        "items": [{"product_id": seed_data["product1"].id, "quantity": 1}],
    }
    create_resp = client.post("/api/orders", json=payload, headers=auth_headers(token))
    order_id = create_resp.json()["id"]

    list_resp = client.get("/api/orders", headers=auth_headers(token))
    assert list_resp.status_code == 200
    ids = [o["id"] for o in list_resp.json()]
    assert order_id in ids

    detail_resp = client.get(f"/api/orders/{order_id}", headers=auth_headers(token))
    assert detail_resp.status_code == 200
    assert detail_resp.json()["status"] == "pending"
