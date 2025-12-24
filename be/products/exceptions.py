"""Custom exceptions for product operations.

This module defines domain-specific exceptions for the products business area.
"""

from uuid import UUID


class ProductException(Exception):
    """Base exception for all product-related errors.

    This base class allows catching all product exceptions with a single except block.
    """

    pass


class ProductNotFoundError(ProductException):
    """Raised when a product cannot be found.

    Attributes:
        product_id: The UUID of the product that was not found.
    """

    def __init__(self, product_id: UUID) -> None:
        """Initialize ProductNotFoundError.

        Args:
            product_id: The UUID of the product that was not found.
        """
        self.product_id = product_id
        super().__init__(f"Product with id {product_id} not found")


class SKUAlreadyExistsError(ProductException):
    """Raised when attempting to create a product with an existing SKU.

    Attributes:
        sku: The SKU that already exists.
    """

    def __init__(self, sku: str) -> None:
        """Initialize SKUAlreadyExistsError.

        Args:
            sku: The SKU that already exists.
        """
        self.sku = sku
        super().__init__(f"Product with SKU {sku} already exists")


class InsufficientStockError(ProductException):
    """Raised when there is insufficient stock for an operation.

    Attributes:
        product_id: The UUID of the product with insufficient stock.
        requested: The requested quantity.
        available: The available quantity.
    """

    def __init__(self, product_id: UUID, requested: int, available: int) -> None:
        """Initialize InsufficientStockError.

        Args:
            product_id: The UUID of the product with insufficient stock.
            requested: The requested quantity.
            available: The available quantity.
        """
        self.product_id = product_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient stock for product {product_id}: requested {requested}, available {available}"
        )
