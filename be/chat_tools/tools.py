"""Tool definitions for agent data access.

This module wraps service layer functions as PydanticAI tools, allowing
the agent to call them on-demand to retrieve specific data.
"""

from typing import Optional
from uuid import UUID

from pydantic_ai import RunContext

from be.context.dispatch import DISPATCH

from .deps import ToolsDeps


async def list_users_tool(
    ctx: RunContext[ToolsDeps],
    skip: int = 0,
    limit: int = 100,
) -> str:
    """List users with pagination.

    Args:
        ctx: Runtime context with database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        JSON string of user list.
    """
    users = await DISPATCH.users.list_users(ctx.deps.db, skip=skip, limit=limit)
    return f"Found {len(users)} users: {[user.model_dump() for user in users]}"


async def get_user_by_id_tool(
    ctx: RunContext[ToolsDeps],
    user_id: str,
) -> str:
    """Get a specific user by ID.

    Args:
        ctx: Runtime context with database session.
        user_id: User's UUID as string.

    Returns:
        JSON string of user data.
    """
    user = await DISPATCH.users.get_user_by_id(ctx.deps.db, UUID(user_id))
    return f"User: {user.model_dump()}"


async def list_products_tool(
    ctx: RunContext[ToolsDeps],
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[str] = None,
) -> str:
    """List products with pagination and optional category filter.

    Args:
        ctx: Runtime context with database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        category_id: Optional category UUID filter as string.

    Returns:
        JSON string of product list.
    """
    cat_uuid = UUID(category_id) if category_id else None
    products = await DISPATCH.products.list_products(
        ctx.deps.db, skip=skip, limit=limit, category_id=cat_uuid
    )
    return f"Found {len(products)} products: {[product.model_dump() for product in products]}"


async def get_product_by_id_tool(
    ctx: RunContext[ToolsDeps],
    product_id: str,
) -> str:
    """Get a specific product by ID.

    Args:
        ctx: Runtime context with database session.
        product_id: Product's UUID as string.

    Returns:
        JSON string of product data.
    """
    product = await DISPATCH.products.get_product_by_id(ctx.deps.db, UUID(product_id))
    return f"Product: {product.model_dump()}"


async def list_categories_tool(
    ctx: RunContext[ToolsDeps],
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[str] = None,
) -> str:
    """List categories with pagination and optional parent filter.

    Args:
        ctx: Runtime context with database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        parent_id: Optional parent category UUID filter as string.

    Returns:
        JSON string of category list.
    """
    par_uuid = UUID(parent_id) if parent_id else None
    categories = await DISPATCH.categories.list_categories(
        ctx.deps.db, skip=skip, limit=limit, parent_id=par_uuid
    )
    return f"Found {len(categories)} categories: {[category.model_dump() for category in categories]}"


async def get_category_by_id_tool(
    ctx: RunContext[ToolsDeps],
    category_id: str,
) -> str:
    """Get a specific category by ID.

    Args:
        ctx: Runtime context with database session.
        category_id: Category's UUID as string.

    Returns:
        JSON string of category data.
    """
    category = await DISPATCH.categories.get_category_by_id(ctx.deps.db, UUID(category_id))
    return f"Category: {category.model_dump()}"


async def list_orders_tool(
    ctx: RunContext[ToolsDeps],
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
) -> str:
    """List orders with pagination and optional user filter.

    Args:
        ctx: Runtime context with database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        user_id: Optional user UUID filter as string.

    Returns:
        JSON string of order list.
    """
    usr_uuid = UUID(user_id) if user_id else None
    orders = await DISPATCH.orders.list_orders(
        ctx.deps.db, skip=skip, limit=limit, user_id=usr_uuid
    )
    return f"Found {len(orders)} orders: {[order.model_dump() for order in orders]}"


async def get_order_by_id_tool(
    ctx: RunContext[ToolsDeps],
    order_id: str,
) -> str:
    """Get a specific order by ID.

    Args:
        ctx: Runtime context with database session.
        order_id: Order's UUID as string.

    Returns:
        JSON string of order data.
    """
    order = await DISPATCH.orders.get_order_by_id(ctx.deps.db, UUID(order_id))
    return f"Order: {order.model_dump()}"


async def list_reviews_tool(
    ctx: RunContext[ToolsDeps],
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    product_id: Optional[str] = None,
) -> str:
    """List reviews with pagination and optional filters.

    Args:
        ctx: Runtime context with database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        user_id: Optional user UUID filter as string.
        product_id: Optional product UUID filter as string.

    Returns:
        JSON string of review list.
    """
    usr_uuid = UUID(user_id) if user_id else None
    prod_uuid = UUID(product_id) if product_id else None
    reviews = await DISPATCH.reviews.list_reviews(
        ctx.deps.db, skip=skip, limit=limit, user_id=usr_uuid, product_id=prod_uuid
    )
    return f"Found {len(reviews)} reviews: {[review.model_dump() for review in reviews]}"


async def get_review_by_id_tool(
    ctx: RunContext[ToolsDeps],
    review_id: str,
) -> str:
    """Get a specific review by ID.

    Args:
        ctx: Runtime context with database session.
        review_id: Review's UUID as string.

    Returns:
        JSON string of review data.
    """
    review = await DISPATCH.reviews.get_review_by_id(ctx.deps.db, UUID(review_id))
    return f"Review: {review.model_dump()}"
