from tests.conftest import login, auth_headers


def test_login_success_returns_token_and_role(client, seed_data):
    resp = client.post("/api/auth/login", data={"username": "sales1", "password": "Sales123!"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "salesman"
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20


def test_login_wrong_password_returns_401(client, seed_data):
    resp = client.post("/api/auth/login", data={"username": "sales1", "password": "WrongPassword"})
    assert resp.status_code == 401
    assert "detail" in resp.json()


def test_login_unknown_user_returns_401(client, seed_data):
    resp = client.post("/api/auth/login", data={"username": "nobody", "password": "whatever"})
    assert resp.status_code == 401


def test_protected_endpoint_without_token_returns_401(client, seed_data):
    resp = client.get("/api/orders")
    assert resp.status_code == 401


def test_protected_endpoint_with_garbage_token_returns_401(client, seed_data):
    resp = client.get("/api/orders", headers=auth_headers("not-a-real-token"))
    assert resp.status_code == 401


def test_me_endpoint_returns_current_user(client, seed_data):
    token = login(client, "sales1", "Sales123!")
    resp = client.get("/api/users/me", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["username"] == "sales1"
