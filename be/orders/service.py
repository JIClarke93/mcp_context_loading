"""Business logic and database operations for orders.

This module contains the async service layer that implements business rules
and database operations.
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import Order
from .exceptions import OrderNotFoundError, UserNotFoundForOrderError
from .model import OrderCreate, OrderResponse, OrderUpdate


async def get_order(db: AsyncSession, order_id: UUID) -> Optional[Order]:
    """Retrieve an order by ID from database.

    Args:
        db: Async database session.
        order_id: Order's unique identifier.

    Returns:
        Order object if found, None otherwise.
    """
    result = await db.execute(select(Order).filter(Order.id == order_id))
    return result.scalar_one_or_none()


async def verify_user_exists(db: AsyncSession, user_id: UUID) -> bool:
    """Verify that a user exists in the database.

    Args:
        db: Async database session.
        user_id: User's unique identifier.

    Returns:
        True if user exists, False otherwise.
    """
    from be.users.db import User

    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none() is not None


async def list_orders(
    db: AsyncSession, skip: int = 0, limit: int = 100, user_id: Optional[UUID] = None
) -> list[OrderResponse]:
    """List orders with pagination and optional user filter.

    Args:
        db: Async database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        user_id: Optional user filter to show only orders for a specific user.

    Returns:
        List of OrderResponse objects.
    """
    query = select(Order)
    if user_id is not None:
        query = query.filter(Order.user_id == user_id)
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    orders = result.scalars().all()
    return [OrderResponse.model_validate(order) for order in orders]


async def get_order_by_id(db: AsyncSession, order_id: UUID) -> OrderResponse:
    """Get an order by ID with validation.

    Args:
        db: Async database session.
        order_id: Order's unique identifier.

    Returns:
        OrderResponse object.

    Raises:
        OrderNotFoundError: If order is not found.
    """
    order = await get_order(db, order_id)
    if order is None:
        raise OrderNotFoundError(order_id)
    return OrderResponse.model_validate(order)


async def create_new_order(db: AsyncSession, order: OrderCreate) -> OrderResponse:
    """Create a new order with validation.

    Args:
        db: Async database session.
        order: Order creation data.

    Returns:
        OrderResponse object for the created order.

    Raises:
        UserNotFoundForOrderError: If user doesn't exist.
    """
    if not await verify_user_exists(db, order.user_id):
        raise UserNotFoundForOrderError(order.user_id)

    db_order = Order(
        user_id=order.user_id,
        total_price=Decimal("0.00"),
    )
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)

    return OrderResponse.model_validate(db_order)


async def update_existing_order(
    db: AsyncSession, order_id: UUID, order: OrderUpdate
) -> OrderResponse:
    """Update an existing order with validation.

    Args:
        db: Async database session.
        order_id: Order's unique identifier.
        order: Order update data.

    Returns:
        OrderResponse object for the updated order.

    Raises:
        OrderNotFoundError: If order not found.
    """
    db_order = await get_order(db, order_id)
    if db_order is None:
        raise OrderNotFoundError(order_id)

    update_data = order.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_order, field, value)

    await db.commit()
    await db.refresh(db_order)

    return OrderResponse.model_validate(db_order)


async def delete_existing_order(db: AsyncSession, order_id: UUID) -> None:
    """Delete an order.

    Args:
        db: Async database session.
        order_id: Order's unique identifier.

    Raises:
        OrderNotFoundError: If order is not found.
    """
    db_order = await get_order(db, order_id)
    if db_order is None:
        raise OrderNotFoundError(order_id)

    await db.delete(db_order)
    await db.commit()
