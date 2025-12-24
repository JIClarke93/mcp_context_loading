"""Seed the database with test data.

This script populates the database with sample e-commerce data for testing
and benchmarking purposes.
"""

import asyncio
import sys
from decimal import Decimal
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from be.dependencies import AsyncSessionLocal
from rdb.enums import OrderStatus
from rdb.models import Category, Order, Product, Review, User


async def clear_database(db: AsyncSession):
    """Clear all existing data from the database.

    Args:
        db: Async database session.
    """
    print("Clearing existing data...")

    # Delete in correct order due to foreign key constraints
    await db.execute(text("DELETE FROM reviews"))
    await db.execute(text("DELETE FROM order_items"))
    await db.execute(text("DELETE FROM orders"))
    await db.execute(text("DELETE FROM products"))
    await db.execute(text("DELETE FROM categories"))
    await db.execute(text("DELETE FROM users"))

    await db.commit()
    print("  Database cleared")


async def seed_users(db: AsyncSession, count: int = 100) -> list[User]:
    """Create sample users.

    Args:
        db: Async database session.
        count: Number of users to create.

    Returns:
        List of created User objects.
    """
    print(f"Creating {count} users...")

    users = []
    for i in range(count):
        user = User(
            email=f"user{i}@example.com",
            username=f"user{i}",
            full_name=f"User Number {i}",
            is_active=True,
        )
        db.add(user)
        users.append(user)

    await db.commit()

    # Refresh to get IDs
    for user in users:
        await db.refresh(user)

    print(f"  Created {len(users)} users")
    return users


async def seed_categories(db: AsyncSession, count: int = 100) -> list[Category]:
    """Create sample categories with hierarchy.

    Args:
        db: Async database session.
        count: Number of categories to create.

    Returns:
        List of created Category objects.
    """
    print(f"Creating {count} categories...")

    categories = []

    # Create root categories (first 20)
    for i in range(min(20, count)):
        category = Category(
            name=f"Category {i}",
            description=f"Description for category {i}",
            parent_id=None,
        )
        db.add(category)
        categories.append(category)

    await db.commit()

    # Refresh to get IDs
    for category in categories:
        await db.refresh(category)

    # Create child categories
    for i in range(20, count):
        parent = categories[i % 20]  # Cycle through root categories
        category = Category(
            name=f"Category {i}",
            description=f"Description for category {i}",
            parent_id=parent.id,
        )
        db.add(category)
        categories.append(category)

    await db.commit()

    # Refresh child categories
    for category in categories[20:]:
        await db.refresh(category)

    print(f"  Created {len(categories)} categories")
    return categories


async def seed_products(
    db: AsyncSession, categories: list[Category], count: int = 100
) -> list[Product]:
    """Create sample products.

    Args:
        db: Async database session.
        categories: List of categories to assign products to.
        count: Number of products to create.

    Returns:
        List of created Product objects.
    """
    print(f"Creating {count} products...")

    products = []
    for i in range(count):
        category = categories[i % len(categories)]
        product = Product(
            name=f"Product {i}",
            description=f"Detailed description for product {i}. This is a great product with many features.",
            price=Decimal("29.99") + Decimal(i % 100),
            category_id=category.id,
            stock_quantity=100,
            sku=f"SKU{i:06d}",
            is_available=True,
        )
        db.add(product)
        products.append(product)

    await db.commit()

    # Refresh to get IDs
    for product in products:
        await db.refresh(product)

    print(f"  Created {len(products)} products")
    return products


async def seed_orders(db: AsyncSession, users: list[User], count: int = 100) -> list[Order]:
    """Create sample orders.

    Args:
        db: Async database session.
        users: List of users to create orders for.
        count: Number of orders to create.

    Returns:
        List of created Order objects.
    """
    print(f"Creating {count} orders...")

    orders = []
    statuses = list(OrderStatus)

    for i in range(count):
        user = users[i % len(users)]
        order = Order(
            user_id=user.id,
            total_amount=Decimal("149.95") + Decimal(i % 500),
            status=statuses[i % len(statuses)],
        )
        db.add(order)
        orders.append(order)

    await db.commit()

    # Refresh to get IDs
    for order in orders:
        await db.refresh(order)

    print(f"  Created {len(orders)} orders")
    return orders


async def seed_reviews(
    db: AsyncSession, users: list[User], products: list[Product], count: int = 100
) -> list[Review]:
    """Create sample reviews.

    Args:
        db: Async database session.
        users: List of users to create reviews for.
        products: List of products to review.
        count: Number of reviews to create.

    Returns:
        List of created Review objects.
    """
    print(f"Creating {count} reviews...")

    reviews = []
    for i in range(count):
        user = users[i % len(users)]
        product = products[i % len(products)]
        review = Review(
            user_id=user.id,
            product_id=product.id,
            rating=(i % 5) + 1,
            comment=f"This is my review for product {i}. Great quality and fast shipping!",
            is_verified_purchase=(i % 3 == 0),
        )
        db.add(review)
        reviews.append(review)

    await db.commit()

    # Refresh to get IDs
    for review in reviews:
        await db.refresh(review)

    print(f"  Created {len(reviews)} reviews")
    return reviews


async def seed_database(
    clear_first: bool = True,
    num_users: int = 100,
    num_categories: int = 100,
    num_products: int = 100,
    num_orders: int = 100,
    num_reviews: int = 100,
):
    """Seed the database with test data.

    Args:
        clear_first: Whether to clear existing data first.
        num_users: Number of users to create.
        num_categories: Number of categories to create.
        num_products: Number of products to create.
        num_orders: Number of orders to create.
        num_reviews: Number of reviews to create.
    """
    print("=" * 60)
    print("Database Seeding")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        if clear_first:
            await clear_database(db)

        users = await seed_users(db, num_users)
        categories = await seed_categories(db, num_categories)
        products = await seed_products(db, categories, num_products)
        orders = await seed_orders(db, users, num_orders)
        reviews = await seed_reviews(db, users, products, num_reviews)

    print("\n" + "=" * 60)
    print("Seeding Complete!")
    print("=" * 60)
    print(f"Created {len(users)} users")
    print(f"Created {len(categories)} categories")
    print(f"Created {len(products)} products")
    print(f"Created {len(orders)} orders")
    print(f"Created {len(reviews)} reviews")
    print(f"Total: {len(users) + len(categories) + len(products) + len(orders) + len(reviews)} entities")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_database())
