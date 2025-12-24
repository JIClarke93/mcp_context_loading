"""Protocol definitions for context loading dispatch.

This module defines the interfaces for accessing each business area's data.
Protocols provide type-safe contracts for the dispatch system.
"""

from typing import Optional, Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from be.categories.model import CategoryResponse
from be.orders.model import OrderResponse
from be.products.model import ProductResponse
from be.reviews.model import ReviewResponse
from be.users.model import UserResponse


class UserProtocol(Protocol):
    """Protocol for user data access operations.

    Defines the interface for retrieving user information.
    """

    async def list_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[UserResponse]:
        """List users with pagination."""
        ...

    async def get_user_by_id(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> UserResponse:
        """Get a specific user by ID."""
        ...


class ProductProtocol(Protocol):
    """Protocol for product data access operations.

    Defines the interface for retrieving product information.
    """

    async def list_products(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[UUID] = None,
    ) -> list[ProductResponse]:
        """List products with pagination and optional category filter."""
        ...

    async def get_product_by_id(
        self,
        db: AsyncSession,
        product_id: UUID,
    ) -> ProductResponse:
        """Get a specific product by ID."""
        ...


class CategoryProtocol(Protocol):
    """Protocol for category data access operations.

    Defines the interface for retrieving category information.
    """

    async def list_categories(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        parent_id: Optional[UUID] = None,
    ) -> list[CategoryResponse]:
        """List categories with pagination and optional parent filter."""
        ...

    async def get_category_by_id(
        self,
        db: AsyncSession,
        category_id: UUID,
    ) -> CategoryResponse:
        """Get a specific category by ID."""
        ...


class OrderProtocol(Protocol):
    """Protocol for order data access operations.

    Defines the interface for retrieving order information.
    """

    async def list_orders(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[UUID] = None,
    ) -> list[OrderResponse]:
        """List orders with pagination and optional user filter."""
        ...

    async def get_order_by_id(
        self,
        db: AsyncSession,
        order_id: UUID,
    ) -> OrderResponse:
        """Get a specific order by ID."""
        ...


class ReviewProtocol(Protocol):
    """Protocol for review data access operations.

    Defines the interface for retrieving review information.
    """

    async def list_reviews(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[UUID] = None,
        product_id: Optional[UUID] = None,
    ) -> list[ReviewResponse]:
        """List reviews with pagination and optional filters."""
        ...

    async def get_review_by_id(
        self,
        db: AsyncSession,
        review_id: UUID,
    ) -> ReviewResponse:
        """Get a specific review by ID."""
        ...
