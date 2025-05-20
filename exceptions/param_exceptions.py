class InvalidConfigParamException(Exception):
    """Exception raised for invalid config parameters."""

    def __init__(self, message, error_code=400):
        super().__init__(message)
        self.error_code = error_code

    def __str__(self):
        return f"{self.message} (Error Code: {self.error_code})"