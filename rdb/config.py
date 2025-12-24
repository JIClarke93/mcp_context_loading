"""Database configuration using Pydantic Settings.

This module provides validated configuration for database connections,
with settings loaded from environment variables or .env files.
"""

from pathlib import Path
from typing import Optional

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings.

    Validates and manages database connection parameters loaded from
    environment variables or .env files.

    Attributes:
        db_path: Path to the SQLite database file relative to rdb directory.
        echo_sql: Whether to log all SQL statements (useful for debugging).
        pool_size: Connection pool size (primarily for non-SQLite databases).
        max_overflow: Maximum overflow connections beyond pool_size.
    """

    db_path: str = Field(
        default="ecommerce.db",
        description="Path to SQLite database file"
    )
    echo_sql: bool = Field(
        default=False,
        description="Enable SQL statement logging"
    )
    pool_size: int = Field(
        default=5,
        ge=1,
        description="Database connection pool size"
    )
    max_overflow: int = Field(
        default=10,
        ge=0,
        description="Maximum overflow connections"
    )

    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @computed_field
    @property
    def database_url(self) -> str:
        """Generate SQLAlchemy database URL.

        Returns:
            Complete SQLAlchemy connection string for SQLite.
        """
        # Ensure we're using an absolute path for SQLite
        db_file = Path(__file__).parent / self.db_path
        return f"sqlite:///{db_file}"

    @computed_field
    @property
    def async_database_url(self) -> str:
        """Generate async SQLAlchemy database URL.

        Returns:
            Complete async SQLAlchemy connection string for SQLite.
        """
        db_file = Path(__file__).parent / self.db_path
        return f"sqlite+aiosqlite:///{db_file}"


# Singleton instance
settings = DatabaseSettings()
