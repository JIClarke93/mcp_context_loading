"""Database models for the e-commerce schema.

This module defines SQLAlchemy ORM models for a moderately complex e-commerce
database with six interrelated tables: users, categories, products, orders,
order items, and reviews.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .enums import OrderStatus


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class User(Base):
    """User account model.

    Represents registered users who can place orders and write reviews.

    Attributes:
        id: Primary key identifier.
        email: Unique email address for the user.
        username: Unique username for the user.
        full_name: Optional full name of the user.
        is_active: Whether the user account is active.
        created_at: Timestamp when the user was created.
        orders: Relationship to the user's orders.
        reviews: Relationship to the user's product reviews.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="user")


class Category(Base):
    """Product category model.

    Hierarchical categorization system for products with self-referential
    parent-child relationships.

    Attributes:
        id: Primary key identifier.
        name: Unique name of the category.
        description: Optional description of the category.
        parent_id: Foreign key to parent category for hierarchical structure.
        created_at: Timestamp when the category was created.
        parent: Relationship to parent category.
        children: Relationship to child categories.
        products: Relationship to products in this category.
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.id"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    parent: Mapped[Optional["Category"]] = relationship(
        "Category", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["Category"]] = relationship(
        "Category", back_populates="parent"
    )
    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")


class Product(Base):
    """Product model.

    Represents items available for purchase in the e-commerce system.

    Attributes:
        id: Primary key identifier.
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=False, index=True
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


class Order(Base):
    """Order model.

    Represents a customer order with status tracking and timestamps.

    Attributes:
        id: Primary key identifier.
        user_id: Foreign key to the user who placed the order.
        total_amount: Total order amount with 2 decimal precision.
        status: Current order status from OrderStatus enum.
        created_at: Timestamp when the order was created.
        shipped_at: Optional timestamp when the order was shipped.
        delivered_at: Optional timestamp when the order was delivered.
        user: Relationship to the user who placed the order.
        order_items: Relationship to items in this order.
    """

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    shipped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship("User", back_populates="orders")
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    """Order item model.

    Represents individual line items within an order, linking products to orders
    with quantity and pricing information.

    Attributes:
        id: Primary key identifier.
        order_id: Foreign key to the order.
        product_id: Foreign key to the product.
        quantity: Number of units ordered.
        unit_price: Price per unit at time of order.
        order: Relationship to the parent order.
        product: Relationship to the ordered product.
    """

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="order_items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")


class Review(Base):
    """Product review model.

    Represents customer reviews and ratings for products.

    Attributes:
        id: Primary key identifier.
        product_id: Foreign key to the reviewed product.
        user_id: Foreign key to the user who wrote the review.
        rating: Numeric rating value.
        comment: Optional text review comment.
        is_verified_purchase: Whether the review is from a verified purchase.
        created_at: Timestamp when the review was created.
        product: Relationship to the reviewed product.
        user: Relationship to the user who wrote the review.
    """

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    is_verified_purchase: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    product: Mapped["Product"] = relationship("Product", back_populates="reviews")
    user: Mapped["User"] = relationship("User", back_populates="reviews")
