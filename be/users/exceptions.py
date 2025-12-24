"""Custom exceptions for user operations.

This module defines domain-specific exceptions for the users business area.
"""

from uuid import UUID


class UserException(Exception):
    """Base exception for all user-related errors.

    This base class allows catching all user exceptions with a single except block.
    """

    pass


class UserNotFoundError(UserException):
    """Raised when a user cannot be found.

    Attributes:
        user_id: The UUID of the user that was not found.
    """

    def __init__(self, user_id: UUID) -> None:
        """Initialize UserNotFoundError.

        Args:
            user_id: The UUID of the user that was not found.
        """
        self.user_id = user_id
        super().__init__(f"User with id {user_id} not found")


class EmailAlreadyExistsError(UserException):
    """Raised when attempting to create a user with an existing email.

    Attributes:
        email: The email address that already exists.
    """

    def __init__(self, email: str) -> None:
        """Initialize EmailAlreadyExistsError.

        Args:
            email: The email address that already exists.
        """
        self.email = email
        super().__init__(f"Email {email} is already registered")


class UsernameAlreadyExistsError(UserException):
    """Raised when attempting to create a user with an existing username.

    Attributes:
        username: The username that already exists.
    """

    def __init__(self, username: str) -> None:
        """Initialize UsernameAlreadyExistsError.

        Args:
            username: The username that already exists.
        """
        self.username = username
        super().__init__(f"Username {username} is already taken")
