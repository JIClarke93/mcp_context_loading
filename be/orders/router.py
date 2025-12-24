"""FastAPI routes for order operations.

This module defines the HTTP endpoints for order CRUD operations.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from be.dependencies import get_db

from .exceptions import OrderNotFoundError, UserNotFoundForOrderError
from .model import OrderCreate, OrderResponse, OrderUpdate
from .service import (
    create_new_order,
    delete_existing_order,
    get_order_by_id,
    list_orders,
    update_existing_order,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=list[OrderResponse])
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    db: AsyncSession = Depends(get_db),
) -> list[OrderResponse]:
    """List orders with pagination and optional user filter.

    Args:
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
        user_id: Optional user filter.
        db: Database session dependency.

    Returns:
        List of OrderResponse objects.
    """
    return await list_orders(db, skip=skip, limit=limit, user_id=user_id)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Get an order by ID.

    Args:
        order_id: Order's unique identifier.
        db: Database session dependency.

    Returns:
        OrderResponse object.

    Raises:
        HTTPException: 404 if order not found.
    """
    try:
        return await get_order_by_id(db, order_id)
    except OrderNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Create a new order.

    Args:
        order: Order creation data.
        db: Database session dependency.

    Returns:
        Created OrderResponse object.

    Raises:
        HTTPException: 400 if user not found.
    """
    try:
        return await create_new_order(db, order)
    except UserNotFoundForOrderError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: UUID,
    order: OrderUpdate,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Update an existing order.

    Args:
        order_id: Order's unique identifier.
        order: Order update data.
        db: Database session dependency.

    Returns:
        Updated OrderResponse object.

    Raises:
        HTTPException: 404 if order not found.
    """
    try:
        return await update_existing_order(db, order_id, order)
    except OrderNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an order.

    Args:
        order_id: Order's unique identifier.
        db: Database session dependency.

    Raises:
        HTTPException: 404 if order not found.
    """
    try:
        await delete_existing_order(db, order_id)
    except OrderNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
