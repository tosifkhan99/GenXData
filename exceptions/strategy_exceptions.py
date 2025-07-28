from core.error.error_context import ErrorContext
from exceptions.base_exception import ErrorSeverity, StrategyError
from exceptions.error_messages import ERROR_MESSAGES


class UnsupportedStrategyException(StrategyError):
    """Raised when a requested strategy is not supported by the system."""

    severity = ErrorSeverity.ERROR
    default_error_code = "STR002"

    def __init__(
        self,
        message: str | None = None,
        *,
        error_code: str | None = None,
        context: ErrorContext | None = None,
        severity: ErrorSeverity | None = None,
    ):
        # Use provided message or fall back to error messages lookup
        resolved_message = message
        if not resolved_message and error_code and error_code in ERROR_MESSAGES:
            resolved_message = ERROR_MESSAGES[error_code]
        elif not resolved_message:
            resolved_message = "Requested strategy is not supported by the system"

        super().__init__(
            message=resolved_message,
            error_code=error_code,
            context=context,
            severity=severity,
        )
