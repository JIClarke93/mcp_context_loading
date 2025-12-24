"""Business logic and database operations for users.

This module contains the async service layer that implements business rules
and database operations.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import User
from .exceptions import EmailAlreadyExistsError, UserNotFoundError, UsernameAlreadyExistsError
from .model import UserCreate, UserResponse, UserUpdate


async def get_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Retrieve a user by ID from database.

    Args:
        db: Async database session.
        user_id: User's unique identifier.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Retrieve a user by email from database.

    Args:
        db: Async database session.
        email: User's email address.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Retrieve a user by username from database.

    Args:
        db: Async database session.
        username: User's username.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalar_one_or_none()


async def list_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[UserResponse]:
    """List users with pagination.

    Args:
        db: Async database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        List of UserResponse objects.
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return [UserResponse.model_validate(user) for user in users]


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> UserResponse:
    """Get a user by ID with validation.

    Args:
        db: Async database session.
        user_id: User's unique identifier.

    Returns:
        UserResponse object.

    Raises:
        UserNotFoundError: If user is not found.
    """
    user = await get_user(db, user_id)
    if user is None:
        raise UserNotFoundError(user_id)
    return UserResponse.model_validate(user)


async def create_new_user(db: AsyncSession, user: UserCreate) -> UserResponse:
    """Create a new user with validation.

    Args:
        db: Async database session.
        user: User creation data.

    Returns:
        UserResponse object for the created user.

    Raises:
        EmailAlreadyExistsError: If email already exists.
        UsernameAlreadyExistsError: If username already exists.
    """
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise EmailAlreadyExistsError(user.email)

    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
        raise UsernameAlreadyExistsError(user.username)

    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return UserResponse.model_validate(db_user)


async def update_existing_user(db: AsyncSession, user_id: UUID, user: UserUpdate) -> UserResponse:
    """Update an existing user with validation.

    Args:
        db: Async database session.
        user_id: User's unique identifier.
        user: User update data.

    Returns:
        UserResponse object for the updated user.

    Raises:
        UserNotFoundError: If user not found.
        EmailAlreadyExistsError: If email already exists.
        UsernameAlreadyExistsError: If username already exists.
    """
    db_user = await get_user(db, user_id)
    if db_user is None:
        raise UserNotFoundError(user_id)

    if user.email is not None:
        email_user = await get_user_by_email(db, user.email)
        if email_user and email_user.id != user_id:
            raise EmailAlreadyExistsError(user.email)

    if user.username is not None:
        username_user = await get_user_by_username(db, user.username)
        if username_user and username_user.id != user_id:
            raise UsernameAlreadyExistsError(user.username)

    update_data = user.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    await db.commit()
    await db.refresh(db_user)

    return UserResponse.model_validate(db_user)


async def delete_existing_user(db: AsyncSession, user_id: UUID) -> None:
    """Delete a user.

    Args:
        db: Async database session.
        user_id: User's unique identifier.

    Raises:
        UserNotFoundError: If user is not found.
    """
    db_user = await get_user(db, user_id)
    if db_user is None:
        raise UserNotFoundError(user_id)

    await db.delete(db_user)
    await db.commit()
