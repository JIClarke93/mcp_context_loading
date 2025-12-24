"""Categories business area module.

This module handles all category-related operations following the Netflix Dispatch pattern.
"""

from .db import Category
from .exceptions import (
    CategoryException,
    CategoryNameAlreadyExistsError,
    CategoryNotFoundError,
    CircularReferenceError,
)
from .model import CategoryCreate, CategoryResponse, CategoryUpdate

__all__ = [
    "Category",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryException",
    "CategoryNotFoundError",
    "CategoryNameAlreadyExistsError",
    "CircularReferenceError",
]
