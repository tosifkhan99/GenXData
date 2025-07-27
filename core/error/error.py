from datetime import datetime
from logging import Logger
from typing import Any

from exceptions.base_exception import ErrorSeverity, GenXDataError


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

        if isinstance(error, GenXDataError):
            severity = error.severity
            self.errors.append(
                {
                    "error": error,
                    "error_code": error.error_code,
                    "message": error.message,
                    "severity": severity,
                    "category": error.category,
                    "timestamp": datetime.now(),
                    "file": file_name,
                    "line": line_no,
                    "function": func_name,
                    "type": type(error).__name__,
                    "traceback": tb,
                    "is_critical": error.is_critical(),
                    "is_recoverable": error.is_recoverable(),
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
            severity = ErrorSeverity.ERROR
            self.errors.append(
                {
                    "error": error,
                    "error_code": f"BUILTIN_{type(error).__name__.upper()}",
                    "message": str(error),
                    "severity": severity,
                    "category": None,
                    "timestamp": datetime.now(),
                    "file": file_name,
                    "line": line_no,
                    "function": func_name,
                    "type": type(error).__name__,
                    "traceback": tb,
                    "is_critical": severity in [ErrorSeverity.CRITICAL],
                    "is_recoverable": severity not in [ErrorSeverity.CRITICAL],
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

        self._log_error_by_severity(error, severity)

        if severity == ErrorSeverity.CRITICAL or self._is_debug_mode():
            self._generate_debug_info(error)

    def _is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.logger.level <= 10  # DEBUG level

    def _generate_debug_info(self, error: GenXDataError | Exception):
        """Generate enhanced debug information for critical errors."""
        from .debug_utils import DebugAnalyzer, DebugFormatter, DebugReporter

        context_info = DebugFormatter.format_error_context(error)
        self.logger.debug("Enhanced Error Context:")
        for line in context_info.split("\n"):
            self.logger.debug(line)

        analysis = DebugAnalyzer.analyze_error_pattern(error)
        self.logger.debug(f"Error Pattern Analysis: {analysis['error_pattern']}")
        self.logger.debug("Debugging Suggestions:")
        for suggestion in analysis["suggestions"]:
            self.logger.debug(f"  • {suggestion}")

        if isinstance(error, GenXDataError) and error.is_critical():
            try:
                report_path = DebugReporter.export_debug_report(error)
                self.logger.critical(
                    f"Critical error debug report exported to: {report_path}"
                )
            except Exception as e:
                self.logger.error(f"Failed to export debug report: {str(e)}")

    def _log_error_by_severity(
        self, error: GenXDataError | Exception, severity: ErrorSeverity
    ):
        """Log errors with appropriate log level based on severity."""
        if isinstance(error, GenXDataError):
            message = f"GenXData Error [{error.error_code}]: {error.message}"
        else:
            message = f"System Error [{type(error).__name__}]: {str(error)}"

        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(message)
        elif severity == ErrorSeverity.ERROR:
            self.logger.error(message)
        elif severity == ErrorSeverity.WARNING:
            self.logger.warning(message)
        elif severity == ErrorSeverity.INFO:
            self.logger.info(message)

    def get_errors(self) -> list[dict[str, Any]]:
        """Get all errors."""
        return self.errors

    def get_errors_by_severity(self, severity: ErrorSeverity) -> list[dict[str, Any]]:
        """Get errors filtered by severity level."""
        return [error for error in self.errors if error.get("severity") == severity]

    def get_critical_errors(self) -> list[dict[str, Any]]:
        """Get only critical errors."""
        return self.get_errors_by_severity(ErrorSeverity.CRITICAL)

    def get_recoverable_errors(self) -> list[dict[str, Any]]:
        """Get only recoverable errors."""
        return [error for error in self.errors if error.get("is_recoverable", True)]

    def has_critical_errors(self) -> bool:
        """Check if there are any critical errors."""
        return len(self.get_critical_errors()) > 0

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    def get_error_summary(self) -> dict[str, int]:
        """Get a summary of errors by severity."""
        summary = {severity.value: 0 for severity in ErrorSeverity}
        for error in self.errors:
            severity = error.get("severity")
            if severity:
                summary[severity.value] += 1
        return summary

    def clear_errors(self):
        """Clear all errors."""
        self.errors = []

    def should_continue_processing(self) -> bool:
        """
        Determine if processing should continue based on error severity.
        Returns False if there are critical errors, True otherwise.
        """
        return not self.has_critical_errors()

    def generate_error_report(self):
        """Generate a comprehensive error report with severity breakdown."""
        error_summary = self.get_error_summary()
        total_errors = sum(error_summary.values())

        self.logger.error("=== ERROR REPORT ===")
        self.logger.error(f"Total Errors: {total_errors}")

        # Report by severity
        for severity, count in error_summary.items():
            if count > 0:
                self.logger.error(f"{severity}: {count}")

        # List critical errors in detail
        critical_errors = self.get_critical_errors()
        if critical_errors:
            self.logger.critical("=== CRITICAL ERRORS ===")
            for error_info in critical_errors:
                self.logger.critical(
                    f"[{error_info['error_code']}] {error_info['message']}"
                )
                if error_info.get("file") and error_info.get("line"):
                    self.logger.critical(
                        f"  Location: {error_info['file']}:{error_info['line']}"
                    )

        # List other errors by severity
        for severity in [
            ErrorSeverity.ERROR,
            ErrorSeverity.WARNING,
            ErrorSeverity.INFO,
        ]:
            errors = self.get_errors_by_severity(severity)
            if errors:
                self.logger.error(f"=== {severity.value} ERRORS ===")
                for error_info in errors:
                    self.logger.error(
                        f"[{error_info['error_code']}] {error_info['message']}"
                    )
                    if error_info.get("strategy_name"):
                        self.logger.error(f"  Strategy: {error_info['strategy_name']}")
                    if error_info.get("column"):
                        self.logger.error(f"  Column: {error_info['column']}")

        self.logger.error("=== END ERROR REPORT ===")

        # Export detailed error report to file if needed
        if self.has_critical_errors() or len(self.get_errors()) > 5:
            self.export_detailed_error_report()

    def export_detailed_error_report(self):
        """Export a detailed error report to a file for debugging."""
        import json
        from datetime import datetime

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_error_summary(),
            "total_errors": len(self.get_errors()),
            "has_critical_errors": self.has_critical_errors(),
            "errors": [],
        }

        for error_info in self.get_errors():
            serializable_error = {
                "error_code": error_info.get("error_code"),
                "message": error_info.get("message"),
                "severity": (
                    error_info.get("severity").value
                    if error_info.get("severity")
                    else None
                ),
                "category": (
                    error_info.get("category").value
                    if error_info.get("category")
                    else None
                ),
                "timestamp": (
                    error_info.get("timestamp").isoformat()
                    if error_info.get("timestamp")
                    else None
                ),
                "file": error_info.get("file"),
                "line": error_info.get("line"),
                "function": error_info.get("function"),
                "type": error_info.get("type"),
                "is_critical": error_info.get("is_critical"),
                "is_recoverable": error_info.get("is_recoverable"),
                "strategy_name": error_info.get("strategy_name"),
                "column": error_info.get("column"),
                "config_path": error_info.get("config_path"),
            }
            report_data["errors"].append(serializable_error)

        error_report_path = (
            f"./output/error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        try:
            with open(error_report_path, "w") as f:
                json.dump(report_data, f, indent=2)
            self.logger.info(f"Detailed error report exported to: {error_report_path}")
        except Exception as e:
            self.logger.error(f"Failed to export error report: {str(e)}")
