"""Pydantic models for order API validation.

This module defines request and response models for order-related endpoints.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from rdb.enums import OrderStatus


class OrderBase(BaseModel):
    """Base order model with common attributes.

    Attributes:
        user_id: UUID of the user who placed the order.
        total_price: Total price of the order.
        status: Current status of the order.
    """

    user_id: UUID
    total_price: Decimal = Field(..., ge=0, decimal_places=2)
    status: OrderStatus = OrderStatus.PENDING


class OrderCreate(BaseModel):
    """Model for creating a new order.

    Attributes:
        user_id: UUID of the user placing the order.
    """

    user_id: UUID


class OrderUpdate(BaseModel):
    """Model for updating an existing order.

    All fields are optional to support partial updates.

    Attributes:
        total_price: Updated total price.
        status: Updated order status.
    """

    total_price: Decimal | None = Field(None, ge=0, decimal_places=2)
    status: OrderStatus | None = None


class OrderResponse(OrderBase):
    """Model for order responses.

    Includes all OrderBase fields plus database-generated fields.

    Attributes:
        id: Order's unique identifier (UUID).
        created_at: Timestamp when the order was created.
        updated_at: Timestamp when the order was last updated.
    """

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
