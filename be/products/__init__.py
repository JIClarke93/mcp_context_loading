"""Products business area module.

This module handles all product-related operations following the Netflix Dispatch pattern.
"""

from .db import Product
from .exceptions import (
    InsufficientStockError,
    ProductException,
    ProductNotFoundError,
    SKUAlreadyExistsError,
)
from .model import ProductCreate, ProductResponse, ProductUpdate

__all__ = [
    "Product",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductException",
    "ProductNotFoundError",
    "SKUAlreadyExistsError",
    "InsufficientStockError",
]
