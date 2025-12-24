"""Dependencies for tool-based chat agent.

This module provides the dependency structure for the agent that uses
tool calls to access service layer functions.
"""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class ToolsDeps:
    """Dependencies for tools-based agent.

    Attributes:
        db: Database session for tool calls to access data.
    """

    db: AsyncSession


def create_tools_deps(db: AsyncSession) -> ToolsDeps:
    """Create dependencies for tools-based agent.

    Args:
        db: Async database session.

    Returns:
        ToolsDeps instance.
    """
    return ToolsDeps(db=db)
