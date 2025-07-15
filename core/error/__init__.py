"""
Core error handling utilities for GenXData.

This package contains error context management utilities
and enhanced debugging tools that are used by the exception system.
"""

from .error_context import ErrorContext, ErrorContextBuilder
from .debug_utils import (
    DebugFormatter, 
    DebugAnalyzer, 
    DebugReporter, 
    debug_error
)

__all__ = [
    'ErrorContext',
    'ErrorContextBuilder',
    'DebugFormatter',
    'DebugAnalyzer', 
    'DebugReporter',
    'debug_error'
] 