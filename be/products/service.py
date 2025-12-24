"""Business logic and database operations for products.

This module contains the async service layer that implements business rules
and database operations.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import Product
from .exceptions import ProductNotFoundError, SKUAlreadyExistsError
from .model import ProductCreate, ProductResponse, ProductUpdate


async def get_product(db: AsyncSession, product_id: UUID) -> Optional[Product]:
    """Retrieve a product by ID from database.

    Args:
        db: Async database session.
        product_id: Product's unique identifier.

    Returns:
        Product object if found, None otherwise.
    """
    result = await db.execute(select(Product).filter(Product.id == product_id))
    return result.scalar_one_or_none()


async def get_product_by_sku(db: AsyncSession, sku: str) -> Optional[Product]:
    """Retrieve a product by SKU from database.

    Args:
        db: Async database session.
        sku: Product's SKU.

    Returns:
        Product object if found, None otherwise.
    """
    result = await db.execute(select(Product).filter(Product.sku == sku))
    return result.scalar_one_or_none()


async def list_products(
    db: AsyncSession, skip: int = 0, limit: int = 100, category_id: Optional[UUID] = None
) -> list[ProductResponse]:
    """List products with pagination and optional category filter.

    Args:
        db: Async database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        category_id: Optional category filter.

    Returns:
        List of ProductResponse objects.
    """
    query = select(Product)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    products = result.scalars().all()
    return [ProductResponse.model_validate(product) for product in products]


async def get_product_by_id(db: AsyncSession, product_id: UUID) -> ProductResponse:
    """Get a product by ID with validation.

    Args:
        db: Async database session.
        product_id: Product's unique identifier.

    Returns:
        ProductResponse object.

    Raises:
        ProductNotFoundError: If product is not found.
    """
    product = await get_product(db, product_id)
    if product is None:
        raise ProductNotFoundError(product_id)
    return ProductResponse.model_validate(product)


async def create_new_product(db: AsyncSession, product: ProductCreate) -> ProductResponse:
    """Create a new product with validation.

    Args:
        db: Async database session.
        product: Product creation data.

    Returns:
        ProductResponse object for the created product.

    Raises:
        SKUAlreadyExistsError: If SKU already exists.
    """
    existing_product = await get_product_by_sku(db, product.sku)
    if existing_product:
        raise SKUAlreadyExistsError(product.sku)

    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        category_id=product.category_id,
        stock_quantity=product.stock_quantity,
        sku=product.sku,
        is_available=product.is_available,
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    return ProductResponse.model_validate(db_product)


async def update_existing_product(
    db: AsyncSession, product_id: UUID, product: ProductUpdate
) -> ProductResponse:
    """Update an existing product with validation.

    Args:
        db: Async database session.
        product_id: Product's unique identifier.
        product: Product update data.

    Returns:
        ProductResponse object for the updated product.

    Raises:
        ProductNotFoundError: If product not found.
        SKUAlreadyExistsError: If SKU already exists.
    """
    db_product = await get_product(db, product_id)
    if db_product is None:
        raise ProductNotFoundError(product_id)

    if product.sku is not None:
        sku_product = await get_product_by_sku(db, product.sku)
        if sku_product and sku_product.id != product_id:
            raise SKUAlreadyExistsError(product.sku)

    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)

    await db.commit()
    await db.refresh(db_product)

    return ProductResponse.model_validate(db_product)


async def delete_existing_product(db: AsyncSession, product_id: UUID) -> None:
    """Delete a product.

    Args:
        db: Async database session.
        product_id: Product's unique identifier.

    Raises:
        ProductNotFoundError: If product is not found.
    """
    db_product = await get_product(db, product_id)
    if db_product is None:
        raise ProductNotFoundError(product_id)

    await db.delete(db_product)
    await db.commit()
