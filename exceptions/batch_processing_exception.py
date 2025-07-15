from exceptions.error_messages import ERROR_MESSAGES
from exceptions.base_exception import ProcessingError, ErrorSeverity
from core.error.error_context import ErrorContext
from typing import Optional

class BatchProcessingException(ProcessingError):
    """Exception raised during batch processing operations."""
    
    severity = ErrorSeverity.ERROR
    default_error_code = "PRC002"

    def __init__(self, message: Optional[str] = None, *, error_code: Optional[str] = None, context: Optional[ErrorContext] = None, severity: Optional[ErrorSeverity] = None):
        resolved_message = message or "Batch processing configuration or operation error"
        super().__init__(
            message=resolved_message, 
            error_code=error_code, 
            context=context, 
            severity=severity
        ) 