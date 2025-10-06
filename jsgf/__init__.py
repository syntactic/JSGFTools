"""
JSGF Tools - Modern Python library for parsing and generating from JSGF grammars.

This package provides a clean, object-oriented API for working with JSGF grammars.
"""

from .grammar import Grammar
from .generators import DeterministicGenerator, ProbabilisticGenerator
from .exceptions import JSGFError, ParseError, GenerationError

__version__ = "2.0.0"
__all__ = [
    "Grammar",
    "DeterministicGenerator",
    "ProbabilisticGenerator",
    "JSGFError",
    "ParseError",
    "GenerationError"
]