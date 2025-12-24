"""Pydantic models for product API validation.

This module defines request and response models for product-related endpoints.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    """Base product model with common attributes.

    Attributes:
        name: Name of the product.
        description: Optional detailed description.
        price: Product price.
        category_id: UUID of the product's category.
        stock_quantity: Current stock level.
        sku: Stock keeping unit identifier.
        is_available: Whether the product is available for purchase.
    """

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    category_id: UUID
    stock_quantity: int = Field(default=0, ge=0)
    sku: str = Field(..., min_length=1, max_length=50)
    is_available: bool = True


class ProductCreate(ProductBase):
    """Model for creating a new product.

    Inherits all fields from ProductBase.
    """

    pass


class ProductUpdate(BaseModel):
    """Model for updating an existing product.

    All fields are optional to support partial updates.

    Attributes:
        name: Updated product name.
        description: Updated description.
        price: Updated price.
        category_id: Updated category.
        stock_quantity: Updated stock level.
        sku: Updated SKU.
        is_available: Updated availability status.
    """

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    category_id: Optional[UUID] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    is_available: Optional[bool] = None


class ProductResponse(ProductBase):
    """Model for product responses.

    Includes all ProductBase fields plus database-generated fields.

    Attributes:
        id: Product's unique identifier (UUID).
        created_at: Timestamp when the product was created.
    """

    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
