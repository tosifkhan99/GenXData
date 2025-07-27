"""
Package for custom exceptions.

This package provides a comprehensive exception hierarchy for GenXData with:
- Severity levels (INFO, WARNING, ERROR, CRITICAL)
- Categories (Configuration, Validation, Strategy, Processing, IO, System, Network)
- Rich context information for debugging
- Consistent error formatting
"""

# Base exception classes and enums
from .base_exception import (
    ConfigurationError,
    ErrorCategory,
    ErrorSeverity,
    GenXDataError,
    IOError,
    NetworkError,
    ProcessingError,
    StrategyError,
    SystemError,
    ValidationError,
)
from .batch_processing_exception import BatchProcessingException

# Specific exception implementations
from .config_exception import ConfigException
from .invalid_config_format_exception import InvalidConfigFormatException
from .invalid_config_path_exception import InvalidConfigPathException
from .invalid_running_mode_exception import InvalidRunningModeException
from .param_exceptions import InvalidConfigParamException
from .strategy_exceptions import UnsupportedStrategyException
from .streaming_exception import StreamingException

__all__ = [
    # Base classes and enums
    "GenXDataError",
    "ErrorSeverity",
    "ErrorCategory",
    "ConfigurationError",
    "ValidationError",
    "StrategyError",
    "ProcessingError",
    "IOError",
    "SystemError",
    "NetworkError",
    # Specific exceptions
    "ConfigException",
    "InvalidConfigParamException",
    "UnsupportedStrategyException",
    "InvalidConfigFormatException",
    "InvalidConfigPathException",
    "InvalidRunningModeException",
    "BatchProcessingException",
    "StreamingException",
]
