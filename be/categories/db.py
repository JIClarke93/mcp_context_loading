"""SQLAlchemy database model for categories table.

This module defines the Category database schema.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from be.base import Base


class Category(Base):
    """Product category database model.

    Hierarchical categorization system for products with self-referential
    parent-child relationships.

    Attributes:
        id: Primary key identifier (UUID).
        name: Unique name of the category.
        description: Optional description of the category.
        parent_id: Foreign key to parent category for hierarchical structure.
        created_at: Timestamp when the category was created.
        parent: Relationship to parent category.
        children: Relationship to child categories.
        products: Relationship to products in this category.
    """

    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("categories.id"), index=True
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
