from enum import IntEnum


class ErrorCodes(IntEnum):
    GENERIC_ERROR = 1


class AppBaseError(Exception):
    """Base class for app exceptions."""


class UserConfigurationError(AppBaseError):
    """User configuration error."""


class DatabaseError(AppBaseError):
    """Database error."""


class EmbeddingError(AppBaseError):
    """Embedding error."""


class MetadataError(AppBaseError):
    """Metadata error."""


class LLMError(AppBaseError):
    """LLM error."""


class PromptError(AppBaseError):
    """Prompt error."""
