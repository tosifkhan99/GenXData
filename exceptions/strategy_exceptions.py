class UnsupportedStrategyException(Exception):
    """Exception raised for unsupported strategies."""

    def __init__(self, message, error_code=400):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self):
        return f"{self.message} (Error Code: {self.error_code})"