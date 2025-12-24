"""SQLAlchemy database model for products table.

This module defines the Product database schema.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Numeric, String, Uuid, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rdb.models import Base


class Product(Base):
    """Product database model.

    Represents items available for purchase in the e-commerce system.

    Attributes:
        id: Primary key identifier (UUID).
        name: Name of the product.
        description: Optional detailed description of the product.
        price: Product price with 2 decimal precision.
        category_id: Foreign key to the product's category.
        stock_quantity: Current stock level.
        sku: Unique stock keeping unit identifier.
        is_available: Whether the product is available for purchase.
        created_at: Timestamp when the product was created.
        category: Relationship to the product's category.
        order_items: Relationship to order items containing this product.
        reviews: Relationship to reviews for this product.
    """

    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    category_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("categories.id"), nullable=False, index=True
    )
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="product"
    )
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="product")
