"""FastAPI router for product endpoints.

This module defines async RESTful API endpoints for product operations.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from be.dependencies import get_db

from .exceptions import ProductNotFoundError, SKUAlreadyExistsError
from .model import ProductCreate, ProductResponse, ProductUpdate
from .service import (
    create_new_product,
    delete_existing_product,
    get_product_by_id,
    list_products,
    update_existing_product,
)

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    db: AsyncSession = Depends(get_db),
) -> list[ProductResponse]:
    """List all products with pagination and optional category filter.

    Args:
        skip: Number of records to skip (default: 0).
        limit: Maximum number of records to return (default: 100, max: 100).
        category_id: Optional category UUID to filter products.
        db: Async database session dependency.

    Returns:
        List of products.
    """
    return await list_products(db, skip=skip, limit=min(limit, 100), category_id=category_id)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """Get a specific product by ID.

    Args:
        product_id: Product's unique identifier.
        db: Async database session dependency.

    Returns:
        Product details.

    Raises:
        HTTPException: 404 if product not found.
    """
    try:
        return await get_product_by_id(db, product_id)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """Create a new product.

    Args:
        product: Product creation data.
        db: Async database session dependency.

    Returns:
        Created product details.

    Raises:
        HTTPException: 400 if SKU already exists.
    """
    try:
        return await create_new_product(db, product)
    except SKUAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product: ProductUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """Update an existing product.

    Args:
        product_id: Product's unique identifier.
        product: Product update data (partial updates supported).
        db: Async database session dependency.

    Returns:
        Updated product details.

    Raises:
        HTTPException: 404 if product not found, 400 if SKU conflict.
    """
    try:
        return await update_existing_product(db, product_id, product)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except SKUAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a product.

    Args:
        product_id: Product's unique identifier.
        db: Async database session dependency.

    Returns:
        None (204 No Content on success).

    Raises:
        HTTPException: 404 if product not found.
    """
    try:
        await delete_existing_product(db, product_id)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
