import os

# Point the app at a dedicated test database BEFORE importing app modules.
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/sales_test_db",
)
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.auth import hash_password
from app.models import User, UserRole, Customer, Product

engine = create_engine(os.environ["DATABASE_URL"])
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Fresh schema for every test function -- keeps tests independent."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def seed_data(db_session):
    """Create one admin, two salesmen, a customer, and a product."""
    admin = User(
        username="admin", email="admin@test.com", full_name="Admin User",
        role=UserRole.admin, hashed_password=hash_password("Admin123!"),
    )
    salesman1 = User(
        username="sales1", email="sales1@test.com", full_name="Sales One",
        role=UserRole.salesman, hashed_password=hash_password("Sales123!"),
    )
    salesman2 = User(
        username="sales2", email="sales2@test.com", full_name="Sales Two",
        role=UserRole.salesman, hashed_password=hash_password("Sales123!"),
    )
    customer = Customer(name="Test Customer", email="cust@test.com", phone="555-1234")
    product1 = Product(sku="SKU-1", name="Product One", price=10.00, stock_quantity=100)
    product2 = Product(sku="SKU-2", name="Product Two", price=25.50, stock_quantity=5)

    db_session.add_all([admin, salesman1, salesman2, customer, product1, product2])
    db_session.commit()
    for obj in (admin, salesman1, salesman2, customer, product1, product2):
        db_session.refresh(obj)

    return {
        "admin": admin,
        "salesman1": salesman1,
        "salesman2": salesman2,
        "customer": customer,
        "product1": product1,
        "product2": product2,
    }


def login(client, username, password):
    resp = client.post("/api/auth/login", data={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}
