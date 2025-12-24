"""Users business area module.

This module handles all user-related operations following the Netflix Dispatch pattern.
"""

from .db import User
from .exceptions import (
    EmailAlreadyExistsError,
    UserException,
    UserNotFoundError,
    UsernameAlreadyExistsError,
)
from .model import UserCreate, UserResponse, UserUpdate

__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserException",
    "UserNotFoundError",
    "EmailAlreadyExistsError",
    "UsernameAlreadyExistsError",
]
