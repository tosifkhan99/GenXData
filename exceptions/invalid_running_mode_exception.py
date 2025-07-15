from exceptions.error_messages import ERROR_MESSAGES
from exceptions.base_exception import ConfigurationError, ErrorSeverity
from core.error.error_context import ErrorContext
from typing import Optional

class InvalidRunningModeException(ConfigurationError):
    """Exception raised when invalid running mode configuration is detected."""
    
    severity = ErrorSeverity.ERROR
    default_error_code = "CFG005"

    def __init__(self, message: Optional[str] = None, *, error_code: Optional[str] = None, context: Optional[ErrorContext] = None, severity: Optional[ErrorSeverity] = None):
        resolved_message = message or "Streaming and batch modes cannot be enabled simultaneously"
        super().__init__(
            message=resolved_message, 
            error_code=error_code, 
            context=context, 
            severity=severity
        )