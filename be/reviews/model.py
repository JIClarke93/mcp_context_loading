"""Pydantic models for review API validation.

This module defines request and response models for review-related endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReviewBase(BaseModel):
    """Base review model with common attributes.

    Attributes:
        user_id: UUID of the user who wrote the review.
        product_id: UUID of the reviewed product.
        rating: Rating value (1-5).
        comment: Optional review comment text.
    """

    user_id: UUID
    product_id: UUID
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    """Model for creating a new review.

    Inherits all fields from ReviewBase.
    """

    pass


class ReviewUpdate(BaseModel):
    """Model for updating an existing review.

    All fields are optional to support partial updates.

    Attributes:
        rating: Updated rating value.
        comment: Updated review comment.
    """

    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(ReviewBase):
    """Model for review responses.

    Includes all ReviewBase fields plus database-generated fields.

    Attributes:
        id: Review's unique identifier (UUID).
        created_at: Timestamp when the review was created.
    """

    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
