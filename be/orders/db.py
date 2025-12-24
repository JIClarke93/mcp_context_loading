"""SQLAlchemy database model for orders table.

This module defines the Order database schema.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rdb.enums import OrderStatus
from rdb.models import Base


class Order(Base):
    """Order database model.

    Represents customer orders with status tracking and line items.

    Attributes:
        id: Primary key identifier (UUID).
        user_id: Foreign key to the user who placed the order.
        total_price: Total price of the order (calculated from order items).
        status: Current status of the order.
        created_at: Timestamp when the order was created.
        updated_at: Timestamp when the order was last updated.
        user: Relationship to the user who placed the order.
        items: Relationship to order line items.
    """

    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=0
    )
    status: Mapped[OrderStatus] = mapped_column(
        nullable=False, default=OrderStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
