from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, require_admin
from app.models import Order, OrderItem, Product, Customer, User, UserRole, OrderStatus
from app.schemas import OrderCreate, OrderOut, OrderListItem, OrderItemOut, OrderStatusUpdate

router = APIRouter(prefix="/api/orders", tags=["orders"])


def _to_order_out(order: Order) -> OrderOut:
    return OrderOut(
        id=order.id,
        customer_id=order.customer_id,
        customer_name=order.customer.name if order.customer else None,
        salesman_id=order.salesman_id,
        salesman_name=order.salesman.full_name if order.salesman else None,
        status=order.status,
        total_amount=order.total_amount,
        created_at=order.created_at,
        items=[
            OrderItemOut(
                id=i.id,
                product_id=i.product_id,
                product_name=i.product.name if i.product else None,
                quantity=i.quantity,
                unit_price=i.unit_price,
                subtotal=i.subtotal,
            )
            for i in order.items
        ],
    )


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create an order. Any authenticated user may create an order, attributed to
    themselves as the salesman. Prices are always taken from the current
    product catalog server-side -- the client only supplies product_id + quantity,
    so a tampered client cannot manipulate pricing or totals.
    """
    customer = db.query(Customer).filter(Customer.id == payload.customer_id, Customer.is_active.is_(True)).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    # De-duplicate product_ids while preserving quantities (sum if repeated)
    quantities: dict[str, int] = {}
    for item in payload.items:
        quantities[item.product_id] = quantities.get(item.product_id, 0) + item.quantity

    product_ids = list(quantities.keys())
    products = db.query(Product).filter(Product.id.in_(product_ids), Product.is_active.is_(True)).all()
    products_by_id = {p.id: p for p in products}

    missing = [pid for pid in product_ids if pid not in products_by_id]
    if missing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product(s) not found: {missing}")

    order = Order(customer_id=customer.id, salesman_id=current_user.id, status=OrderStatus.pending, total_amount=0)
    total = 0
    order_items = []
    for pid, qty in quantities.items():
        product = products_by_id[pid]
        if product.stock_quantity < qty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for '{product.name}'. Available: {product.stock_quantity}, requested: {qty}",
            )
        subtotal = product.price * qty
        total += subtotal
        order_items.append(OrderItem(product_id=product.id, quantity=qty, unit_price=product.price, subtotal=subtotal))
        product.stock_quantity -= qty

    order.items = order_items
    order.total_amount = total

    db.add(order)
    db.commit()
    db.refresh(order)
    order = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product), joinedload(Order.customer), joinedload(Order.salesman))
        .filter(Order.id == order.id)
        .first()
    )
    return _to_order_out(order)


@router.get("", response_model=list[OrderListItem])
def list_orders(
    search: Optional[str] = None,
    status_filter: Optional[OrderStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Salesmen only see their own orders. Admins see all orders and can search
    by customer/salesman name.
    """
    query = db.query(Order).options(joinedload(Order.customer), joinedload(Order.salesman))

    if current_user.role != UserRole.admin:
        query = query.filter(Order.salesman_id == current_user.id)

    if status_filter:
        query = query.filter(Order.status == status_filter)

    if search and current_user.role == UserRole.admin:
        like = f"%{search}%"
        query = query.join(Customer).filter(Customer.name.ilike(like))

    orders = query.order_by(Order.created_at.desc()).limit(200).all()
    return [
        OrderListItem(
            id=o.id,
            customer_id=o.customer_id,
            customer_name=o.customer.name if o.customer else None,
            salesman_id=o.salesman_id,
            salesman_name=o.salesman.full_name if o.salesman else None,
            status=o.status,
            total_amount=o.total_amount,
            created_at=o.created_at,
        )
        for o in orders
    ]


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product), joinedload(Order.customer), joinedload(Order.salesman))
        .filter(Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if current_user.role != UserRole.admin and order.salesman_id != current_user.id:
        # A salesman may not view another salesman's order.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this order")

    return _to_order_out(order)


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: str,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Admin-only: confirm or cancel an order."""
    order = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product), joinedload(Order.customer), joinedload(Order.salesman))
        .filter(Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order.status = payload.status
    db.commit()
    db.refresh(order)
    return _to_order_out(order)
