from core.error.error_context import ErrorContext
from exceptions.base_exception import ConfigurationError, ErrorSeverity


class InvalidConfigFormatException(ConfigurationError):
    """Exception raised when configuration file format is invalid or unsupported."""

    severity = ErrorSeverity.ERROR
    default_error_code = "CFG003"

    def __init__(
        self,
        message: str | None = None,
        *,
        error_code: str | None = None,
        context: ErrorContext | None = None,
        severity: ErrorSeverity | None = None,
    ):
        resolved_message = (
            message or "Configuration file has an unsupported or malformed format"
        )
        super().__init__(
            message=resolved_message,
            error_code=error_code,
            context=context,
            severity=severity,
        )
