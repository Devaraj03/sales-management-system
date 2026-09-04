from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models import UserRole, OrderStatus


# ---------- Auth ----------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    full_name: str
    user_id: str


class LoginRequest(BaseModel):
    username: str
    password: str


# ---------- Users ----------

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=150)
    role: UserRole = UserRole.salesman


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    is_active: bool
    created_at: datetime


# ---------- Customers ----------

class CustomerBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    address: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerOut(CustomerBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    is_active: bool
    created_at: datetime


# ---------- Products ----------

class ProductBase(BaseModel):
    sku: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = None
    price: Decimal = Field(ge=0)
    stock_quantity: int = Field(ge=0, default=0)


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    is_active: bool
    created_at: datetime


# ---------- Order Items ----------

class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(gt=0, description="Must be a positive integer")


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    product_id: str
    product_name: Optional[str] = None
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


# ---------- Orders ----------

class OrderCreate(BaseModel):
    customer_id: str
    items: List[OrderItemCreate] = Field(min_length=1)


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    customer_id: str
    customer_name: Optional[str] = None
    salesman_id: str
    salesman_name: Optional[str] = None
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    items: List[OrderItemOut] = []


class OrderListItem(BaseModel):
    """Lightweight representation for list views."""
    model_config = ConfigDict(from_attributes=True)
    id: str
    customer_id: str
    customer_name: Optional[str] = None
    salesman_id: str
    salesman_name: Optional[str] = None
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


# ---------- Dashboard ----------

class DashboardMetrics(BaseModel):
    total_sales: Decimal
    total_orders: int
    total_customers: int


class SalesOverTimePoint(BaseModel):
    date: str
    total_sales: Decimal
    order_count: int
