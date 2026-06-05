from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"


class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int


class OrderItem(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: float


class OrderCreate(BaseModel):
    user_email: str
    items: List[OrderItemRequest]


class OrderRead(BaseModel):
    id: str
    user_email: str
    items: List[OrderItem]
    total: float
    status: OrderStatus
    created_at: datetime


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
