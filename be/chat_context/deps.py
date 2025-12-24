"""Dependencies for context-loading chat agent.

This module provides the dependency structure that holds pre-loaded context
from all business areas.
"""

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from be.context.loader import load_full_context


@dataclass
class ContextDeps:
    """Dependencies for context-loading agent.

    Attributes:
        context: Pre-loaded context from all business areas.
        db: Database session for any additional queries.
    """

    context: dict[str, Any] = field(default_factory=dict)
    db: AsyncSession | None = None


async def create_context_deps(db: AsyncSession, limit_per_entity: int = 100) -> ContextDeps:
    """Create dependencies with pre-loaded context.

    Args:
        db: Async database session.
        limit_per_entity: Maximum number of records per entity type to load.

    Returns:
        ContextDeps with cached full context.
    """
    context = await load_full_context(db, limit_per_entity=limit_per_entity)
    return ContextDeps(context=context, db=db)
