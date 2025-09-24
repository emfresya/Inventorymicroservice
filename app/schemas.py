from pydantic import BaseModel
from typing import Optional

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderItemResponse(BaseModel):
    order_item_id: int
    order_id: int
    product_id: int
    quantity: int
    price_at_order: float