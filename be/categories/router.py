"""FastAPI routes for category operations.

This module defines the HTTP endpoints for category CRUD operations.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from be.dependencies import get_db

from .exceptions import CategoryNameAlreadyExistsError, CategoryNotFoundError, CircularReferenceError
from .model import CategoryCreate, CategoryResponse, CategoryUpdate
from .service import (
    create_new_category,
    delete_existing_category,
    get_category_by_id,
    list_categories,
    update_existing_category,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryResponse])
async def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    parent_id: Optional[UUID] = Query(None, description="Filter by parent category ID"),
    db: AsyncSession = Depends(get_db),
) -> list[CategoryResponse]:
    """List categories with pagination and optional parent filter.

    Args:
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
        parent_id: Optional parent category filter.
        db: Database session dependency.

    Returns:
        List of CategoryResponse objects.
    """
    return await list_categories(db, skip=skip, limit=limit, parent_id=parent_id)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    """Get a category by ID.

    Args:
        category_id: Category's unique identifier.
        db: Database session dependency.

    Returns:
        CategoryResponse object.

    Raises:
        HTTPException: 404 if category not found.
    """
    try:
        return await get_category_by_id(db, category_id)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    """Create a new category.

    Args:
        category: Category creation data.
        db: Database session dependency.

    Returns:
        Created CategoryResponse object.

    Raises:
        HTTPException: 400 if category name already exists or parent not found.
    """
    try:
        return await create_new_category(db, category)
    except CategoryNameAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    """Update an existing category.

    Args:
        category_id: Category's unique identifier.
        category: Category update data.
        db: Database session dependency.

    Returns:
        Updated CategoryResponse object.

    Raises:
        HTTPException: 404 if category not found, 400 if name exists or circular reference.
    """
    try:
        return await update_existing_category(db, category_id, category)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CategoryNameAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except CircularReferenceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a category.

    Args:
        category_id: Category's unique identifier.
        db: Database session dependency.

    Raises:
        HTTPException: 404 if category not found.
    """
    try:
        await delete_existing_category(db, category_id)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
