"""Shared dependencies for FastAPI endpoints.

This module provides common dependencies used across all routers,
including async database session management.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from rdb.config import settings

# Create async SQLAlchemy engine
async_engine = create_async_engine(
    settings.async_database_url,
    echo=settings.echo_sql,
    connect_args={"check_same_thread": False},  # Needed for SQLite
)

# Create async SessionLocal class
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session dependency.

    Yields:
        Async database session that automatically closes after use.

    Example:
        ```python
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
        ```
    """
    async with AsyncSessionLocal() as session:
        yield session
