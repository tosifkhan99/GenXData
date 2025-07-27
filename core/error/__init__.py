"""
Core error handling utilities for GenXData.

This package contains error context management utilities
and enhanced debugging tools that are used by the exception system.
"""

from .debug_utils import DebugAnalyzer, DebugFormatter, DebugReporter, debug_error
from .error_context import ErrorContext, ErrorContextBuilder

__all__ = [
    "ErrorContext",
    "ErrorContextBuilder",
    "DebugFormatter",
    "DebugAnalyzer",
    "DebugReporter",
    "debug_error",
]
