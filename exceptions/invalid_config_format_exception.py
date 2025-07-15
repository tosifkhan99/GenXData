from exceptions.error_messages import ERROR_MESSAGES
from exceptions.base_exception import ConfigurationError, ErrorSeverity
from core.error.error_context import ErrorContext
from typing import Optional

class InvalidConfigFormatException(ConfigurationError):
    """Exception raised when configuration file format is invalid or unsupported."""
    
    severity = ErrorSeverity.ERROR
    default_error_code = "CFG003"

    def __init__(self, message: Optional[str] = None, *, error_code: Optional[str] = None, context: Optional[ErrorContext] = None, severity: Optional[ErrorSeverity] = None):
        resolved_message = message or "Configuration file has an unsupported or malformed format"
        super().__init__(
            message=resolved_message, 
            error_code=error_code, 
            context=context, 
            severity=severity
        )