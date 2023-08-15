"""Errors for the app docucite"""

from enum import IntEnum


class ErrorCodes(IntEnum):
    GENERIC_ERROR = 1


class AppBaseError(Exception):
    """Base class for app exceptions."""

    pass


class UserConfigurationError(AppBaseError):
    """User configuration error."""


class DatabaseError(AppBaseError):
    """Database error."""


class MissingMetadataError(AppBaseError):
    """Missing metadata error."""


class InvalidMetadataError(AppBaseError):
    """Invalid metadata error."""
