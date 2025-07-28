from core.error.error_context import ErrorContext
from exceptions.base_exception import ErrorSeverity, NetworkError


class StreamingException(NetworkError):
    """Exception raised during streaming operations or network connectivity issues."""

    severity = ErrorSeverity.ERROR
    default_error_code = "NET002"

    def __init__(
        self,
        message: str | None = None,
        *,
        error_code: str | None = None,
        context: ErrorContext | None = None,
        severity: ErrorSeverity | None = None,
    ):
        resolved_message = message or "Streaming configuration or connection error"
        super().__init__(
            message=resolved_message,
            error_code=error_code,
            context=context,
            severity=severity,
        )
