"""Pydantic models for user API validation.

This module defines request and response models for user-related endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user model with common attributes.

    Attributes:
        email: User's email address.
        username: Unique username.
        full_name: Optional full name of the user.
    """

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """Model for creating a new user.

    Inherits all fields from UserBase.
    """

    pass


class UserUpdate(BaseModel):
    """Model for updating an existing user.

    All fields are optional to support partial updates.

    Attributes:
        email: Updated email address.
        username: Updated username.
        full_name: Updated full name.
        is_active: Updated active status.
    """

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Model for user responses.

    Includes all UserBase fields plus database-generated fields.

    Attributes:
        id: User's unique identifier (UUID).
        is_active: Whether the user account is active.
        created_at: Timestamp when the user was created.
    """

    id: UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
