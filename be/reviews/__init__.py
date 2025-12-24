"""Reviews business area module.

This module handles all review-related operations following the Netflix Dispatch pattern.
"""

from .db import Review
from .exceptions import (
    ProductNotFoundForReviewError,
    ReviewException,
    ReviewNotFoundError,
    UserNotFoundForReviewError,
)
from .model import ReviewCreate, ReviewResponse, ReviewUpdate

__all__ = [
    "Review",
    "ReviewCreate",
    "ReviewUpdate",
    "ReviewResponse",
    "ReviewException",
    "ReviewNotFoundError",
    "UserNotFoundForReviewError",
    "ProductNotFoundForReviewError",
]
