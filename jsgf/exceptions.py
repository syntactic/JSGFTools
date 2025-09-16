"""
Custom exceptions for JSGF Tools.
"""

from typing import Optional


class JSGFError(Exception):
    """Base exception for all JSGF-related errors."""
    pass


class ParseError(JSGFError):
    """Raised when grammar parsing fails."""

    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        self.line = line
        self.column = column

        if line is not None:
            message = f"Line {line}: {message}"
        if column is not None:
            message = f"{message} (column {column})"

        super().__init__(message)


class GenerationError(JSGFError):
    """Raised when string generation fails."""
    pass


class ValidationError(JSGFError):
    """Raised when grammar validation fails."""
    pass


class RecursionError(GenerationError):
    """Raised when infinite recursion is detected during generation."""
    pass