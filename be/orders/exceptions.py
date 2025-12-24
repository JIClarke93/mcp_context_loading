"""Custom exceptions for order operations.

This module defines domain-specific exceptions for the orders business area.
"""

from uuid import UUID


class OrderException(Exception):
    """Base exception for all order-related errors.

    This base class allows catching all order exceptions with a single except block.
    """

    pass


class OrderNotFoundError(OrderException):
    """Raised when an order cannot be found.

    Attributes:
        order_id: The UUID of the order that was not found.
    """

    def __init__(self, order_id: UUID) -> None:
        """Initialize OrderNotFoundError.

        Args:
            order_id: The UUID of the order that was not found.
        """
        self.order_id = order_id
        super().__init__(f"Order with id {order_id} not found")


class UserNotFoundForOrderError(OrderException):
    """Raised when attempting to create an order for a non-existent user.

    Attributes:
        user_id: The UUID of the user that was not found.
    """

    def __init__(self, user_id: UUID) -> None:
        """Initialize UserNotFoundForOrderError.

        Args:
            user_id: The UUID of the user that was not found.
        """
        self.user_id = user_id
        super().__init__(f"User with id {user_id} not found")
