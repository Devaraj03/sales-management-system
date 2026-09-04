from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.database import get_db
from app.deps import require_admin
from app.models import Order, Customer, OrderStatus, User
from app.schemas import DashboardMetrics, SalesOverTimePoint

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
def get_metrics(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    total_sales = (
        db.query(func.coalesce(func.sum(Order.total_amount), 0))
        .filter(Order.status != OrderStatus.cancelled)
        .scalar()
    )
    total_orders = db.query(func.count(Order.id)).scalar()
    total_customers = db.query(func.count(Customer.id)).filter(Customer.is_active.is_(True)).scalar()

    return DashboardMetrics(
        total_sales=total_sales or 0,
        total_orders=total_orders or 0,
        total_customers=total_customers or 0,
    )


@router.get("/sales-over-time", response_model=list[SalesOverTimePoint])
def get_sales_over_time(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    """Daily sales totals (excluding cancelled orders) for a simple time-series chart."""
    day = func.date(Order.created_at)
    rows = (
        db.query(day.label("d"), func.coalesce(func.sum(Order.total_amount), 0), func.count(Order.id))
        .filter(Order.status != OrderStatus.cancelled)
        .group_by(day)
        .order_by(day)
        .all()
    )
    return [SalesOverTimePoint(date=str(r[0]), total_sales=r[1], order_count=r[2]) for r in rows]
