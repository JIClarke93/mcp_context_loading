"""SQLAlchemy database model for reviews table.

This module defines the Review database schema.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from be.base import Base


class Review(Base):
    """Product review database model.

    Represents customer reviews and ratings for products.

    Attributes:
        id: Primary key identifier (UUID).
        user_id: Foreign key to the user who wrote the review.
        product_id: Foreign key to the reviewed product.
        rating: Rating value (1-5).
        comment: Optional review comment text.
        created_at: Timestamp when the review was created.
        user: Relationship to the user who wrote the review.
        product: Relationship to the reviewed product.
    """

    __tablename__ = "reviews"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    product_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="reviews")
    product: Mapped["Product"] = relationship("Product", back_populates="reviews")
