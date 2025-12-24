"""Custom exceptions for review operations.

This module defines domain-specific exceptions for the reviews business area.
"""

from uuid import UUID


class ReviewException(Exception):
    """Base exception for all review-related errors.

    This base class allows catching all review exceptions with a single except block.
    """

    pass


class ReviewNotFoundError(ReviewException):
    """Raised when a review cannot be found.

    Attributes:
        review_id: The UUID of the review that was not found.
    """

    def __init__(self, review_id: UUID) -> None:
        """Initialize ReviewNotFoundError.

        Args:
            review_id: The UUID of the review that was not found.
        """
        self.review_id = review_id
        super().__init__(f"Review with id {review_id} not found")


class UserNotFoundForReviewError(ReviewException):
    """Raised when attempting to create a review for a non-existent user.

    Attributes:
        user_id: The UUID of the user that was not found.
    """

    def __init__(self, user_id: UUID) -> None:
        """Initialize UserNotFoundForReviewError.

        Args:
            user_id: The UUID of the user that was not found.
        """
        self.user_id = user_id
        super().__init__(f"User with id {user_id} not found")


class ProductNotFoundForReviewError(ReviewException):
    """Raised when attempting to create a review for a non-existent product.

    Attributes:
        product_id: The UUID of the product that was not found.
    """

    def __init__(self, product_id: UUID) -> None:
        """Initialize ProductNotFoundForReviewError.

        Args:
            product_id: The UUID of the product that was not found.
        """
        self.product_id = product_id
        super().__init__(f"Product with id {product_id} not found")
