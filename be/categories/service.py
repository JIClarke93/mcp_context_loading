"""Business logic and database operations for categories.

This module contains the async service layer that implements business rules
and database operations.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import Category
from .exceptions import CategoryNameAlreadyExistsError, CategoryNotFoundError, CircularReferenceError
from .model import CategoryCreate, CategoryResponse, CategoryUpdate


async def get_category(db: AsyncSession, category_id: UUID) -> Optional[Category]:
    """Retrieve a category by ID from database.

    Args:
        db: Async database session.
        category_id: Category's unique identifier.

    Returns:
        Category object if found, None otherwise.
    """
    result = await db.execute(select(Category).filter(Category.id == category_id))
    return result.scalar_one_or_none()


async def get_category_by_name(db: AsyncSession, name: str) -> Optional[Category]:
    """Retrieve a category by name from database.

    Args:
        db: Async database session.
        name: Category's name.

    Returns:
        Category object if found, None otherwise.
    """
    result = await db.execute(select(Category).filter(Category.name == name))
    return result.scalar_one_or_none()


async def check_circular_reference(db: AsyncSession, category_id: UUID, parent_id: UUID) -> bool:
    """Check if setting a parent would create a circular reference.

    Args:
        db: Async database session.
        category_id: The category to update.
        parent_id: The proposed parent.

    Returns:
        True if circular reference would be created, False otherwise.
    """
    if category_id == parent_id:
        return True

    current_id = parent_id
    visited = {category_id}

    while current_id:
        if current_id in visited:
            return True
        visited.add(current_id)

        parent = await get_category(db, current_id)
        if not parent or parent.parent_id is None:
            break
        current_id = parent.parent_id

    return False


async def list_categories(
    db: AsyncSession, skip: int = 0, limit: int = 100, parent_id: Optional[UUID] = None
) -> list[CategoryResponse]:
    """List categories with pagination and optional parent filter.

    Args:
        db: Async database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        parent_id: Optional parent category filter (use 'root' for top-level categories).

    Returns:
        List of CategoryResponse objects.
    """
    query = select(Category)
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    categories = result.scalars().all()
    return [CategoryResponse.model_validate(category) for category in categories]


async def get_category_by_id(db: AsyncSession, category_id: UUID) -> CategoryResponse:
    """Get a category by ID with validation.

    Args:
        db: Async database session.
        category_id: Category's unique identifier.

    Returns:
        CategoryResponse object.

    Raises:
        CategoryNotFoundError: If category is not found.
    """
    category = await get_category(db, category_id)
    if category is None:
        raise CategoryNotFoundError(category_id)
    return CategoryResponse.model_validate(category)


async def create_new_category(db: AsyncSession, category: CategoryCreate) -> CategoryResponse:
    """Create a new category with validation.

    Args:
        db: Async database session.
        category: Category creation data.

    Returns:
        CategoryResponse object for the created category.

    Raises:
        CategoryNameAlreadyExistsError: If category name already exists.
        CategoryNotFoundError: If parent category doesn't exist.
    """
    existing_category = await get_category_by_name(db, category.name)
    if existing_category:
        raise CategoryNameAlreadyExistsError(category.name)

    if category.parent_id:
        parent = await get_category(db, category.parent_id)
        if not parent:
            raise CategoryNotFoundError(category.parent_id)

    db_category = Category(
        name=category.name,
        description=category.description,
        parent_id=category.parent_id,
    )
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)

    return CategoryResponse.model_validate(db_category)


async def update_existing_category(
    db: AsyncSession, category_id: UUID, category: CategoryUpdate
) -> CategoryResponse:
    """Update an existing category with validation.

    Args:
        db: Async database session.
        category_id: Category's unique identifier.
        category: Category update data.

    Returns:
        CategoryResponse object for the updated category.

    Raises:
        CategoryNotFoundError: If category not found.
        CategoryNameAlreadyExistsError: If category name already exists.
        CircularReferenceError: If parent update would create circular reference.
    """
    db_category = await get_category(db, category_id)
    if db_category is None:
        raise CategoryNotFoundError(category_id)

    if category.name is not None:
        name_category = await get_category_by_name(db, category.name)
        if name_category and name_category.id != category_id:
            raise CategoryNameAlreadyExistsError(category.name)

    if category.parent_id is not None:
        parent = await get_category(db, category.parent_id)
        if not parent:
            raise CategoryNotFoundError(category.parent_id)

        if await check_circular_reference(db, category_id, category.parent_id):
            raise CircularReferenceError(category_id, category.parent_id)

    update_data = category.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)

    await db.commit()
    await db.refresh(db_category)

    return CategoryResponse.model_validate(db_category)


async def delete_existing_category(db: AsyncSession, category_id: UUID) -> None:
    """Delete a category.

    Args:
        db: Async database session.
        category_id: Category's unique identifier.

    Raises:
        CategoryNotFoundError: If category is not found.
    """
    db_category = await get_category(db, category_id)
    if db_category is None:
        raise CategoryNotFoundError(category_id)

    await db.delete(db_category)
    await db.commit()
