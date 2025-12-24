"""Pydantic models for category API validation.

This module defines request and response models for category-related endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """Base category model with common attributes.

    Attributes:
        name: Name of the category.
        description: Optional description.
        parent_id: Optional parent category UUID for hierarchical structure.
    """

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None


class CategoryCreate(CategoryBase):
    """Model for creating a new category.

    Inherits all fields from CategoryBase.
    """

    pass


class CategoryUpdate(BaseModel):
    """Model for updating an existing category.

    All fields are optional to support partial updates.

    Attributes:
        name: Updated category name.
        description: Updated description.
        parent_id: Updated parent category.
    """

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None


class CategoryResponse(CategoryBase):
    """Model for category responses.

    Includes all CategoryBase fields plus database-generated fields.

    Attributes:
        id: Category's unique identifier (UUID).
        created_at: Timestamp when the category was created.
    """

    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
