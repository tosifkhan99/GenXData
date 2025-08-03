from abc import ABC
from enum import Enum

from core.error.error_context import ErrorContext


class ErrorSeverity(Enum):
    """Error severity levels for better error classification and handling."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ErrorCategory(Enum):
    """Error categories for better organization and handling."""

    CONFIGURATION = "Configuration"
    VALIDATION = "Validation"
    STRATEGY = "Strategy"
    PROCESSING = "Processing"
    IO = "Input/Output"
    SYSTEM = "System"
    NETWORK = "Network"


class GenXDataError(Exception, ABC):
    """
    Abstract base exception for all GenXData errors.
    """

    category: ErrorCategory = ErrorCategory.SYSTEM
    severity: ErrorSeverity = ErrorSeverity.ERROR
    default_error_code: str = "GEN001"

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        context: ErrorContext | None = None,
        severity: ErrorSeverity | None = None,
    ):
        """
        Initialize GenXDataError.

        Args:
            message: Human-readable error message
            error_code: Unique error code string (uses default if not provided)
            context: Optional structured context dictionary
            severity: Error severity level (uses class default if not provided)
        """
        super().__init__(message)

        self.message: str = message
        self.error_code: str = error_code or self.default_error_code
        self.context: ErrorContext = context or {}
        self.severity: ErrorSeverity = severity or self.severity

        if isinstance(self.context, dict):
            self.context.update(
                {
                    "error_category": self.category.value,
                    "error_severity": self.severity.value,
                }
            )

    def __str__(self) -> str:
        """Return a formatted string representation of the error."""
        return f"[{self.severity.value}] {self.category.value} Error [{self.error_code}]: {self.message}"

    def __repr__(self) -> str:
        """Return a detailed string representation for debugging."""
        return (
            f"{self.__class__.__name__}(message='{self.message}', "
            f"error_code='{self.error_code}', severity='{self.severity.value}', "
            f"category='{self.category.value}')"
        )

    def is_critical(self) -> bool:
        """Check if this error is critical."""
        return self.severity == ErrorSeverity.CRITICAL

    def is_recoverable(self) -> bool:
        """
        Check if this error is potentially recoverable.
        By default, INFO and WARNING are recoverable, ERROR and CRITICAL are not.
        Subclasses can override this logic.
        """
        return self.severity in [ErrorSeverity.INFO, ErrorSeverity.WARNING]

    def get_context_summary(self) -> str:
        """Get a summary of the error context for logging."""
        if not self.context:
            return "No context available"

        key_items = []
        for key in ["strategy_name", "column", "config_path", "generator"]:
            if key in self.context and self.context[key]:
                key_items.append(f"{key}={self.context[key]}")

        return ", ".join(key_items) if key_items else "No specific context"


class ConfigurationError(GenXDataError):
    """Base class for configuration-related errors."""

    category = ErrorCategory.CONFIGURATION
    severity = ErrorSeverity.ERROR
    default_error_code = "CFG001"


class ValidationError(GenXDataError):
    """Base class for validation-related errors."""

    category = ErrorCategory.VALIDATION
    severity = ErrorSeverity.ERROR
    default_error_code = "VAL001"


class StrategyError(GenXDataError):
    """Base class for strategy-related errors."""

    category = ErrorCategory.STRATEGY
    severity = ErrorSeverity.ERROR
    default_error_code = "STR001"


class ProcessingError(GenXDataError):
    """Base class for data processing errors."""

    category = ErrorCategory.PROCESSING
    severity = ErrorSeverity.ERROR
    default_error_code = "PRC001"


class IOError(GenXDataError):
    """Base class for input/output related errors."""

    category = ErrorCategory.IO
    severity = ErrorSeverity.ERROR
    default_error_code = "IO001"


class SystemError(GenXDataError):
    """Base class for system-level errors."""

    category = ErrorCategory.SYSTEM
    severity = ErrorSeverity.CRITICAL
    default_error_code = "SYS001"


class NetworkError(GenXDataError):
    """Base class for network-related errors."""

    category = ErrorCategory.NETWORK
    severity = ErrorSeverity.ERROR
    default_error_code = "NET001"
