"""Base class for backend SQLAlchemy models.

This module provides a separate Base class for the UUID-based backend models,
distinct from the integer-based models in rdb/models.py used for migrations.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all backend database models."""

    pass
