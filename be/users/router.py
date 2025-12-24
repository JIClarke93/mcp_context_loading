"""FastAPI router for user endpoints.

This module defines async RESTful API endpoints for user operations.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from be.dependencies import get_db

from .exceptions import EmailAlreadyExistsError, UserNotFoundError, UsernameAlreadyExistsError
from .model import UserCreate, UserResponse, UserUpdate
from .service import (
    create_new_user,
    delete_existing_user,
    get_user_by_id,
    list_users,
    update_existing_user,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=list[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> list[UserResponse]:
    """List all users with pagination.

    Args:
        skip: Number of records to skip (default: 0).
        limit: Maximum number of records to return (default: 100, max: 100).
        db: Async database session dependency.

    Returns:
        List of users.
    """
    return await list_users(db, skip=skip, limit=min(limit, 100))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Get a specific user by ID.

    Args:
        user_id: User's unique identifier.
        db: Async database session dependency.

    Returns:
        User details.

    Raises:
        HTTPException: 404 if user not found.
    """
    try:
        return await get_user_by_id(db, user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Create a new user.

    Args:
        user: User creation data.
        db: Async database session dependency.

    Returns:
        Created user details.

    Raises:
        HTTPException: 400 if email or username already exists.
    """
    try:
        return await create_new_user(db, user)
    except EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except UsernameAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update an existing user.

    Args:
        user_id: User's unique identifier.
        user: User update data (partial updates supported).
        db: Async database session dependency.

    Returns:
        Updated user details.

    Raises:
        HTTPException: 404 if user not found, 400 if email/username conflict.
    """
    try:
        return await update_existing_user(db, user_id, user)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except UsernameAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a user.

    Args:
        user_id: User's unique identifier.
        db: Async database session dependency.

    Returns:
        None (204 No Content on success).

    Raises:
        HTTPException: 404 if user not found.
    """
    try:
        await delete_existing_user(db, user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
