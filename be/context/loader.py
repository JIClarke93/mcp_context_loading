"""Context loading utilities for pre-fetching database information.

This module provides functions to load data from multiple business areas
and format it for injection into an AI agent's context window.
"""

from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .dispatch import DISPATCH


async def load_user_context(
    db: AsyncSession,
    user_id: Optional[UUID] = None,
    include_orders: bool = False,
    include_reviews: bool = False,
) -> dict[str, Any]:
    """Load user context with optional related data.

    Args:
        db: Async database session.
        user_id: Optional specific user ID to load.
        include_orders: Include user's orders in context.
        include_reviews: Include user's reviews in context.

    Returns:
        Dictionary containing user data and optionally related entities.
    """
    context: dict[str, Any] = {}

    if user_id:
        user = await DISPATCH.users.get_user_by_id(db, user_id)
        context["user"] = user.model_dump()

        if include_orders:
            orders = await DISPATCH.orders.list_orders(db, user_id=user_id)
            context["orders"] = [order.model_dump() for order in orders]

        if include_reviews:
            reviews = await DISPATCH.reviews.list_reviews(db, user_id=user_id)
            context["reviews"] = [review.model_dump() for review in reviews]
    else:
        users = await DISPATCH.users.list_users(db)
        context["users"] = [user.model_dump() for user in users]

    return context


async def load_product_context(
    db: AsyncSession,
    product_id: Optional[UUID] = None,
    category_id: Optional[UUID] = None,
    include_reviews: bool = False,
) -> dict[str, Any]:
    """Load product context with optional filters and related data.

    Args:
        db: Async database session.
        product_id: Optional specific product ID to load.
        category_id: Optional category filter for products.
        include_reviews: Include product reviews in context.

    Returns:
        Dictionary containing product data and optionally related entities.
    """
    context: dict[str, Any] = {}

    if product_id:
        product = await DISPATCH.products.get_product_by_id(db, product_id)
        context["product"] = product.model_dump()

        if include_reviews:
            reviews = await DISPATCH.reviews.list_reviews(db, product_id=product_id)
            context["reviews"] = [review.model_dump() for review in reviews]
    else:
        products = await DISPATCH.products.list_products(db, category_id=category_id)
        context["products"] = [product.model_dump() for product in products]

    return context


async def load_category_context(
    db: AsyncSession,
    category_id: Optional[UUID] = None,
    parent_id: Optional[UUID] = None,
    include_products: bool = False,
) -> dict[str, Any]:
    """Load category context with optional hierarchy filtering.

    Args:
        db: Async database session.
        category_id: Optional specific category ID to load.
        parent_id: Optional parent category filter.
        include_products: Include products in the category.

    Returns:
        Dictionary containing category data and optionally related entities.
    """
    context: dict[str, Any] = {}

    if category_id:
        category = await DISPATCH.categories.get_category_by_id(db, category_id)
        context["category"] = category.model_dump()

        if include_products:
            products = await DISPATCH.products.list_products(db, category_id=category_id)
            context["products"] = [product.model_dump() for product in products]
    else:
        categories = await DISPATCH.categories.list_categories(db, parent_id=parent_id)
        context["categories"] = [category.model_dump() for category in categories]

    return context


async def load_order_context(
    db: AsyncSession,
    order_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
) -> dict[str, Any]:
    """Load order context with optional user filtering.

    Args:
        db: Async database session.
        order_id: Optional specific order ID to load.
        user_id: Optional user filter for orders.

    Returns:
        Dictionary containing order data.
    """
    context: dict[str, Any] = {}

    if order_id:
        order = await DISPATCH.orders.get_order_by_id(db, order_id)
        context["order"] = order.model_dump()
    else:
        orders = await DISPATCH.orders.list_orders(db, user_id=user_id)
        context["orders"] = [order.model_dump() for order in orders]

    return context


async def load_full_context(
    db: AsyncSession,
    limit_per_entity: int = 100,
) -> dict[str, Any]:
    """Load complete context from all business areas.

    Warning: This can be very large and consume significant tokens.
    Use with caution and appropriate limits.

    Args:
        db: Async database session.
        limit_per_entity: Maximum number of records per entity type.

    Returns:
        Dictionary containing data from all business areas.
    """
    context: dict[str, Any] = {}

    users = await DISPATCH.users.list_users(db, limit=limit_per_entity)
    context["users"] = [user.model_dump() for user in users]

    products = await DISPATCH.products.list_products(db, limit=limit_per_entity)
    context["products"] = [product.model_dump() for product in products]

    categories = await DISPATCH.categories.list_categories(db, limit=limit_per_entity)
    context["categories"] = [category.model_dump() for category in categories]

    orders = await DISPATCH.orders.list_orders(db, limit=limit_per_entity)
    context["orders"] = [order.model_dump() for order in orders]

    reviews = await DISPATCH.reviews.list_reviews(db, limit=limit_per_entity)
    context["reviews"] = [review.model_dump() for review in reviews]

    return context
