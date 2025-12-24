"""SQLAlchemy database model for users table.

This module defines the User database schema.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rdb.models import Base


class User(Base):
    """User account database model.

    Represents registered users who can place orders and write reviews.

    Attributes:
        id: Primary key identifier (UUID).
        email: Unique email address for the user.
        username: Unique username for the user.
        full_name: Optional full name of the user.
        is_active: Whether the user account is active.
        created_at: Timestamp when the user was created.
        orders: Relationship to the user's orders.
        reviews: Relationship to the user's product reviews.
    """

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="user")
