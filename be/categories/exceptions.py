"""Custom exceptions for category operations.

This module defines domain-specific exceptions for the categories business area.
"""

from uuid import UUID


class CategoryException(Exception):
    """Base exception for all category-related errors.

    This base class allows catching all category exceptions with a single except block.
    """

    pass


class CategoryNotFoundError(CategoryException):
    """Raised when a category cannot be found.

    Attributes:
        category_id: The UUID of the category that was not found.
    """

    def __init__(self, category_id: UUID) -> None:
        """Initialize CategoryNotFoundError.

        Args:
            category_id: The UUID of the category that was not found.
        """
        self.category_id = category_id
        super().__init__(f"Category with id {category_id} not found")


class CategoryNameAlreadyExistsError(CategoryException):
    """Raised when attempting to create a category with an existing name.

    Attributes:
        name: The category name that already exists.
    """

    def __init__(self, name: str) -> None:
        """Initialize CategoryNameAlreadyExistsError.

        Args:
            name: The category name that already exists.
        """
        self.name = name
        super().__init__(f"Category with name '{name}' already exists")


class CircularReferenceError(CategoryException):
    """Raised when a category update would create a circular reference.

    Attributes:
        category_id: The category that would create a circular reference.
        parent_id: The proposed parent that would cause the circular reference.
    """

    def __init__(self, category_id: UUID, parent_id: UUID) -> None:
        """Initialize CircularReferenceError.

        Args:
            category_id: The category that would create a circular reference.
            parent_id: The proposed parent that would cause the circular reference.
        """
        self.category_id = category_id
        self.parent_id = parent_id
        super().__init__(
            f"Setting parent {parent_id} for category {category_id} would create a circular reference"
        )
