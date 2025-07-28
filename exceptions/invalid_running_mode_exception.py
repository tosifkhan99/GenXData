from core.error.error_context import ErrorContext
from exceptions.base_exception import ConfigurationError, ErrorSeverity


class InvalidRunningModeException(ConfigurationError):
    """Exception raised when invalid running mode configuration is detected."""

    severity = ErrorSeverity.ERROR
    default_error_code = "CFG005"

    def __init__(
        self,
        message: str | None = None,
        *,
        error_code: str | None = None,
        context: ErrorContext | None = None,
        severity: ErrorSeverity | None = None,
    ):
        resolved_message = (
            message or "Streaming and batch modes cannot be enabled simultaneously"
        )
        super().__init__(
            message=resolved_message,
            error_code=error_code,
            context=context,
            severity=severity,
        )
