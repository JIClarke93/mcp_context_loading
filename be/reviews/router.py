"""FastAPI routes for review operations.

This module defines the HTTP endpoints for review CRUD operations.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from be.dependencies import get_db

from .exceptions import ProductNotFoundForReviewError, ReviewNotFoundError, UserNotFoundForReviewError
from .model import ReviewCreate, ReviewResponse, ReviewUpdate
from .service import (
    create_new_review,
    delete_existing_review,
    get_review_by_id,
    list_reviews,
    update_existing_review,
)

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/", response_model=list[ReviewResponse])
async def get_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    product_id: Optional[UUID] = Query(None, description="Filter by product ID"),
    db: AsyncSession = Depends(get_db),
) -> list[ReviewResponse]:
    """List reviews with pagination and optional filters.

    Args:
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
        user_id: Optional user filter.
        product_id: Optional product filter.
        db: Database session dependency.

    Returns:
        List of ReviewResponse objects.
    """
    return await list_reviews(
        db, skip=skip, limit=limit, user_id=user_id, product_id=product_id
    )


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    """Get a review by ID.

    Args:
        review_id: Review's unique identifier.
        db: Database session dependency.

    Returns:
        ReviewResponse object.

    Raises:
        HTTPException: 404 if review not found.
    """
    try:
        return await get_review_by_id(db, review_id)
    except ReviewNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    """Create a new review.

    Args:
        review: Review creation data.
        db: Database session dependency.

    Returns:
        Created ReviewResponse object.

    Raises:
        HTTPException: 400 if user or product not found.
    """
    try:
        return await create_new_review(db, review)
    except UserNotFoundForReviewError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ProductNotFoundForReviewError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: UUID,
    review: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    """Update an existing review.

    Args:
        review_id: Review's unique identifier.
        review: Review update data.
        db: Database session dependency.

    Returns:
        Updated ReviewResponse object.

    Raises:
        HTTPException: 404 if review not found.
    """
    try:
        return await update_existing_review(db, review_id, review)
    except ReviewNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a review.

    Args:
        review_id: Review's unique identifier.
        db: Database session dependency.

    Raises:
        HTTPException: 404 if review not found.
    """
    try:
        await delete_existing_review(db, review_id)
    except ReviewNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
