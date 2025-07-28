from core.error.error_context import ErrorContext
from exceptions.base_exception import ErrorSeverity, ProcessingError


class BatchProcessingException(ProcessingError):
    """Exception raised during batch processing operations."""

    severity = ErrorSeverity.ERROR
    default_error_code = "PRC002"

    def __init__(
        self,
        message: str | None = None,
        *,
        error_code: str | None = None,
        context: ErrorContext | None = None,
        severity: ErrorSeverity | None = None,
    ):
        resolved_message = (
            message or "Batch processing configuration or operation error"
        )
        super().__init__(
            message=resolved_message,
            error_code=error_code,
            context=context,
            severity=severity,
        )
