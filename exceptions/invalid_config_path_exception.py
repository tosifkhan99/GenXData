from exceptions.base_exception import ConfigurationError, ErrorSeverity
from core.error.error_context import ErrorContext
from typing import Optional


class InvalidConfigPathException(ConfigurationError):
    """Exception raised when configuration file path is invalid or inaccessible."""

    severity = ErrorSeverity.ERROR
    default_error_code = "CFG004"

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        error_code: Optional[str] = None,
        context: Optional[ErrorContext] = None,
        severity: Optional[ErrorSeverity] = None,
    ):
        resolved_message = (
            message or "Configuration file path does not exist or is inaccessible"
        )
        super().__init__(
            message=resolved_message,
            error_code=error_code,
            context=context,
            severity=severity,
        )
