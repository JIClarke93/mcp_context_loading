"""Dispatch system for accessing business area service functions.

This module provides a centralized dispatch system that maps business areas
to their service layer functions. This enables context loading by providing
a single interface to access all data retrieval operations.
"""

from dataclasses import dataclass, field
from typing import Callable

from be.categories import service as category_service
from be.orders import service as order_service
from be.products import service as product_service
from be.reviews import service as review_service
from be.users import service as user_service


@dataclass(frozen=True)
class UserDispatch:
    """Dispatch implementation for user operations.

    Attributes:
        list_users: Function to list users with pagination.
        get_user_by_id: Function to get a specific user by ID.
    """

    list_users: Callable = field(default=user_service.list_users)
    get_user_by_id: Callable = field(default=user_service.get_user_by_id)


@dataclass(frozen=True)
class ProductDispatch:
    """Dispatch implementation for product operations.

    Attributes:
        list_products: Function to list products with pagination and optional filters.
        get_product_by_id: Function to get a specific product by ID.
    """

    list_products: Callable = field(default=product_service.list_products)
    get_product_by_id: Callable = field(default=product_service.get_product_by_id)


@dataclass(frozen=True)
class CategoryDispatch:
    """Dispatch implementation for category operations.

    Attributes:
        list_categories: Function to list categories with pagination and optional filters.
        get_category_by_id: Function to get a specific category by ID.
    """

    list_categories: Callable = field(default=category_service.list_categories)
    get_category_by_id: Callable = field(default=category_service.get_category_by_id)


@dataclass(frozen=True)
class OrderDispatch:
    """Dispatch implementation for order operations.

    Attributes:
        list_orders: Function to list orders with pagination and optional filters.
        get_order_by_id: Function to get a specific order by ID.
    """

    list_orders: Callable = field(default=order_service.list_orders)
    get_order_by_id: Callable = field(default=order_service.get_order_by_id)


@dataclass(frozen=True)
class ReviewDispatch:
    """Dispatch implementation for review operations.

    Attributes:
        list_reviews: Function to list reviews with pagination and optional filters.
        get_review_by_id: Function to get a specific review by ID.
    """

    list_reviews: Callable = field(default=review_service.list_reviews)
    get_review_by_id: Callable = field(default=review_service.get_review_by_id)


@dataclass(frozen=True)
class Dispatch:
    """Central dispatch container for all business area operations.

    Attributes:
        users: User service operations.
        products: Product service operations.
        categories: Category service operations.
        orders: Order service operations.
        reviews: Review service operations.
    """

    users: UserDispatch = field(default_factory=UserDispatch)
    products: ProductDispatch = field(default_factory=ProductDispatch)
    categories: CategoryDispatch = field(default_factory=CategoryDispatch)
    orders: OrderDispatch = field(default_factory=OrderDispatch)
    reviews: ReviewDispatch = field(default_factory=ReviewDispatch)


DISPATCH = Dispatch()
"""Central dispatch instance for accessing all business area service operations.

This provides a unified interface for accessing all business area service functions.
Access operations using dot notation: DISPATCH.users.list_users(), etc.

Example:
    ```python
    from be.context.dispatch import DISPATCH
    from be.dependencies import get_db

    async with get_db() as db:
        # Access user service functions
        users = await DISPATCH.users.list_users(db, skip=0, limit=10)

        # Access product service functions
        products = await DISPATCH.products.list_products(db, skip=0, limit=10)

        # Access specific entities
        user = await DISPATCH.users.get_user_by_id(db, user_id)
    ```
"""
