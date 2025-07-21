from exceptions.base_exception import NetworkError, ErrorSeverity
from core.error.error_context import ErrorContext
from typing import Optional


class StreamingException(NetworkError):
    """Exception raised during streaming operations or network connectivity issues."""

    severity = ErrorSeverity.ERROR
    default_error_code = "NET002"

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        error_code: Optional[str] = None,
        context: Optional[ErrorContext] = None,
        severity: Optional[ErrorSeverity] = None,
    ):
        resolved_message = message or "Streaming configuration or connection error"
        super().__init__(
            message=resolved_message,
            error_code=error_code,
            context=context,
            severity=severity,
        )
