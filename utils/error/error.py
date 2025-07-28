# Handles error states and stores them

from datetime import datetime
from logging import Logger
from typing import Any

from exceptions.base_exception import GenXDataError


class ErrorHandler:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.errors: list[dict[str, Any]] = []

    def add_error(self, error: GenXDataError | Exception):
        """
        Add an error to the error handler.
        Handles both GenXDataError and built-in Python exceptions.
        """
        tb = error.__traceback__
        file_name = tb.tb_frame.f_code.co_filename if tb else None
        line_no = tb.tb_lineno if tb else None
        func_name = tb.tb_frame.f_code.co_name if tb else None

        # Check if this is a GenXDataError or a built-in exception
        if isinstance(error, GenXDataError):
            # Handle GenXDataError with full context
            self.errors.append(
                {
                    "error": error,
                    "error_code": error.error_code,
                    "message": error.message,
                    "timestamp": datetime.now(),
                    "file": file_name,
                    "line": line_no,
                    "function": func_name,
                    "type": type(error).__name__,
                    "traceback": tb,
                    # Context fields
                    "generator": error.context.get("generator"),
                    "strategy_name": error.context.get("strategy_name"),
                    "strategy_params": error.context.get("strategy_params"),
                    "config": error.context.get("config"),
                    "batch": error.context.get("batch"),
                    "stream": error.context.get("stream"),
                    "perf_report": error.context.get("perf_report"),
                    "log_level": error.context.get("log_level"),
                    "column": error.context.get("column"),
                    "row": error.context.get("row"),
                    "value": error.context.get("value"),
                    "config_path": error.context.get("config_path"),
                }
            )
        else:
            # Handle built-in Python exceptions
            self.errors.append(
                {
                    "error": error,
                    "error_code": f"BUILTIN_{type(error).__name__.upper()}",
                    "message": str(error),
                    "timestamp": datetime.now(),
                    "file": file_name,
                    "line": line_no,
                    "function": func_name,
                    "type": type(error).__name__,
                    "traceback": tb,
                    # Default context fields for built-in exceptions
                    "generator": None,
                    "strategy_name": None,
                    "strategy_params": None,
                    "config": None,
                    "batch": None,
                    "stream": None,
                    "perf_report": None,
                    "log_level": None,
                    "column": None,
                    "row": None,
                    "value": None,
                    "config_path": None,
                }
            )

        # Log the error appropriately
        if isinstance(error, GenXDataError):
            self.logger.error(f"GenXData Error [{error.error_code}]: {error.message}")
        else:
            self.logger.error(f"System Error [{type(error).__name__}]: {str(error)}")

    def get_errors(self):
        return self.errors

    def clear_errors(self):
        self.errors = []
