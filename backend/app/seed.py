"""
Seed the database with demo data: one admin, two salesmen, customers,
and products. Safe to re-run (skips if data already exists).

Usage: python -m app.seed
"""
from app.auth import hash_password
from app.database import SessionLocal
from app.models import User, UserRole, Customer, Product


def run():
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Database already seeded, skipping.")
            return

        admin = User(
            username="admin",
            email="admin@example.com",
            full_name="Alex Admin",
            role=UserRole.admin,
            hashed_password=hash_password("Admin123!"),
        )
        salesman1 = User(
            username="jdoe",
            email="jdoe@example.com",
            full_name="John Doe",
            role=UserRole.salesman,
            hashed_password=hash_password("Sales123!"),
        )
        salesman2 = User(
            username="asmith",
            email="asmith@example.com",
            full_name="Amy Smith",
            role=UserRole.salesman,
            hashed_password=hash_password("Sales123!"),
        )
        db.add_all([admin, salesman1, salesman2])

        customers = [
            Customer(name="Acme Corp", email="buyer@acme.com", phone="555-0101", address="123 Main St, Springfield"),
            Customer(name="Globex Inc", email="purchasing@globex.com", phone="555-0102", address="456 Oak Ave, Metropolis"),
            Customer(name="Initech", email="orders@initech.com", phone="555-0103", address="789 Pine Rd, Gotham"),
            Customer(name="Umbrella Retail", email="hello@umbrella.com", phone="555-0104", address="12 Elm St, Star City"),
        ]
        db.add_all(customers)

        products = [
            Product(sku="WID-001", name="Standard Widget", description="Our best-selling widget.", price=9.99, stock_quantity=500),
            Product(sku="WID-002", name="Deluxe Widget", description="Premium widget with extra features.", price=19.99, stock_quantity=300),
            Product(sku="GAD-001", name="Gadget Pro", description="Professional-grade gadget.", price=49.99, stock_quantity=150),
            Product(sku="GAD-002", name="Gadget Mini", description="Compact gadget for small jobs.", price=24.99, stock_quantity=200),
            Product(sku="TOOL-001", name="Universal Tool Kit", description="All-in-one tool kit.", price=79.99, stock_quantity=75),
        ]
        db.add_all(products)

        db.commit()
        print("Seed complete.")
        print("  Admin login:    admin / Admin123!")
        print("  Salesman login: jdoe / Sales123!")
        print("  Salesman login: asmith / Sales123!")
    finally:
        db.close()


if __name__ == "__main__":
    run()
