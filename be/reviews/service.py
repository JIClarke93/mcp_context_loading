"""Business logic and database operations for reviews.

This module contains the async service layer that implements business rules
and database operations.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import Review
from .exceptions import ProductNotFoundForReviewError, ReviewNotFoundError, UserNotFoundForReviewError
from .model import ReviewCreate, ReviewResponse, ReviewUpdate


async def get_review(db: AsyncSession, review_id: UUID) -> Optional[Review]:
    """Retrieve a review by ID from database.

    Args:
        db: Async database session.
        review_id: Review's unique identifier.

    Returns:
        Review object if found, None otherwise.
    """
    result = await db.execute(select(Review).filter(Review.id == review_id))
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


async def verify_product_exists(db: AsyncSession, product_id: UUID) -> bool:
    """Verify that a product exists in the database.

    Args:
        db: Async database session.
        product_id: Product's unique identifier.

    Returns:
        True if product exists, False otherwise.
    """
    from be.products.db import Product

    result = await db.execute(select(Product).filter(Product.id == product_id))
    return result.scalar_one_or_none() is not None


async def list_reviews(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[UUID] = None,
    product_id: Optional[UUID] = None,
) -> list[ReviewResponse]:
    """List reviews with pagination and optional filters.

    Args:
        db: Async database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        user_id: Optional user filter to show only reviews by a specific user.
        product_id: Optional product filter to show only reviews for a specific product.

    Returns:
        List of ReviewResponse objects.
    """
    query = select(Review)
    if user_id is not None:
        query = query.filter(Review.user_id == user_id)
    if product_id is not None:
        query = query.filter(Review.product_id == product_id)
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    reviews = result.scalars().all()
    return [ReviewResponse.model_validate(review) for review in reviews]


async def get_review_by_id(db: AsyncSession, review_id: UUID) -> ReviewResponse:
    """Get a review by ID with validation.

    Args:
        db: Async database session.
        review_id: Review's unique identifier.

    Returns:
        ReviewResponse object.

    Raises:
        ReviewNotFoundError: If review is not found.
    """
    review = await get_review(db, review_id)
    if review is None:
        raise ReviewNotFoundError(review_id)
    return ReviewResponse.model_validate(review)


async def create_new_review(db: AsyncSession, review: ReviewCreate) -> ReviewResponse:
    """Create a new review with validation.

    Args:
        db: Async database session.
        review: Review creation data.

    Returns:
        ReviewResponse object for the created review.

    Raises:
        UserNotFoundForReviewError: If user doesn't exist.
        ProductNotFoundForReviewError: If product doesn't exist.
    """
    if not await verify_user_exists(db, review.user_id):
        raise UserNotFoundForReviewError(review.user_id)

    if not await verify_product_exists(db, review.product_id):
        raise ProductNotFoundForReviewError(review.product_id)

    db_review = Review(
        user_id=review.user_id,
        product_id=review.product_id,
        rating=review.rating,
        comment=review.comment,
    )
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)

    return ReviewResponse.model_validate(db_review)


async def update_existing_review(
    db: AsyncSession, review_id: UUID, review: ReviewUpdate
) -> ReviewResponse:
    """Update an existing review with validation.

    Args:
        db: Async database session.
        review_id: Review's unique identifier.
        review: Review update data.

    Returns:
        ReviewResponse object for the updated review.

    Raises:
        ReviewNotFoundError: If review not found.
    """
    db_review = await get_review(db, review_id)
    if db_review is None:
        raise ReviewNotFoundError(review_id)

    update_data = review.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_review, field, value)

    await db.commit()
    await db.refresh(db_review)

    return ReviewResponse.model_validate(db_review)


async def delete_existing_review(db: AsyncSession, review_id: UUID) -> None:
    """Delete a review.

    Args:
        db: Async database session.
        review_id: Review's unique identifier.

    Raises:
        ReviewNotFoundError: If review is not found.
    """
    db_review = await get_review(db, review_id)
    if db_review is None:
        raise ReviewNotFoundError(review_id)

    await db.delete(db_review)
    await db.commit()
