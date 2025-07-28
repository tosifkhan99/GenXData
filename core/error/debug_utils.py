"""
Debug utilities for error analysis and troubleshooting.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from utils.logging import Logger

# Initialize debug logger
logger = Logger.get_logger("debug")


class DebugFormatter:
    """
    Formats error information for debugging output.
    """

    @staticmethod
    def format_error_context(error) -> str:
        """Format error context for display"""
        from exceptions.base_exception import GenXDataError

        lines = []
        lines.append("🔍 ERROR DEBUG INFORMATION")
        lines.append(f"{'=' * 50}")

        if isinstance(error, GenXDataError):
            lines.append(f"Error Type: {error.__class__.__name__}")
            lines.append(f"Message: {error.message}")
            lines.append(f"Error Code: {error.error_code}")
            severity_str = (
                error.severity.name if hasattr(error.severity, "name")
                else str(error.severity)
            )
            lines.append(f"Severity: {severity_str}")
            category_str = (
                error.category.value if hasattr(error.category, "value")
                else str(error.category)
            )
            lines.append(f"Category: {category_str}")

            # Add context information if available
            if hasattr(error, "context") and error.context:
                if error.context.get("strategy_name"):
                    lines.append(f"Strategy: {error.context['strategy_name']}")
                if error.context.get("column"):
                    lines.append(f"Column: {error.context['column']}")
                if error.context.get("config_path"):
                    lines.append(f"Config Path: {error.context['config_path']}")

        else:
            # Handle built-in Python exceptions
            lines.append(f"Error Type: {error.__class__.__name__}")
            lines.append(f"Message: {str(error)}")
            lines.append("Severity: ERROR")
            lines.append("Category: SYSTEM")

        return "\n".join(lines)

    @staticmethod
    def format_stack_trace(error, include_locals: bool = False) -> str:
        """Format stack trace with optional local variables"""
        import traceback

        lines = []
        lines.append("📍 STACK TRACE")
        lines.append(f"{'=' * 50}")

        # Get stack trace from the exception
        if hasattr(error, "__traceback__") and error.__traceback__:
            tb_lines = traceback.format_exception(
                type(error), error, error.__traceback__
            )
            lines.extend(tb_lines)
        else:
            lines.append("No traceback available")

        # Note: Local variables inspection is complex and not implemented here
        # as it requires more sophisticated error context tracking

        return "\n".join(lines)

    @staticmethod
    def format_suggestions(suggestions: list[str]) -> str:
        """Format debugging suggestions"""
        lines = []
        lines.append("💡 SUGGESTIONS")
        lines.append(f"{'=' * 50}")

        for i, suggestion in enumerate(suggestions, 1):
            lines.append(f"{i}. {suggestion}")

        return "\n".join(lines)


class DebugAnalyzer:
    """
    Analyzes errors to provide debugging suggestions.
    """

    @staticmethod
    def analyze_error_pattern(error) -> dict[str, Any]:
        """Analyze error patterns and provide suggestions"""
        from exceptions.base_exception import GenXDataError

        suggestions = []
        error_type = error.__class__.__name__

        # Get strategy name and config path from error context
        strategy_name = None
        config_path = None

        if (
            isinstance(error, GenXDataError)
            and hasattr(error, "context")
            and error.context
        ):
            strategy_name = error.context.get("strategy_name")
            config_path = error.context.get("config_path")

        # Strategy-specific suggestions
        if strategy_name:
            suggestions.extend(
                DebugAnalyzer._get_strategy_suggestions_by_name(strategy_name)
            )

        # Configuration-specific suggestions
        if config_path:
            suggestions.extend(
                DebugAnalyzer._get_config_suggestions_by_path(config_path)
            )

        # General suggestions based on error type
        if "param" in error_type.lower():
            suggestions.extend(
                [
                    "Check parameter names and types in your configuration",
                    "Verify required parameters are provided",
                    "Check parameter value ranges and constraints",
                ]
            )

        if "validation" in error_type.lower():
            suggestions.extend(
                [
                    "Review configuration file format and structure",
                    "Check for missing required fields",
                    "Validate data types match expected formats",
                ]
            )

        if "file" in error_type.lower() or "path" in error_type.lower():
            suggestions.extend(
                [
                    "Verify file paths exist and are accessible",
                    "Check file permissions",
                    "Ensure file formats are supported",
                ]
            )

        # Add severity-based suggestions
        if (
            isinstance(error, GenXDataError)
            and hasattr(error, "severity")
            and error.severity
        ):
            severity_name = (
                error.severity.name
                if hasattr(error.severity, "name")
                else str(error.severity)
            )
            if severity_name == "CRITICAL":
                suggestions.append(
                    "This is a critical error that requires immediate attention"
                )
            elif severity_name in ["HIGH", "ERROR"]:
                suggestions.append(
                    "This error may cause significant issues - review carefully"
                )

        return {
            "suggestions": suggestions,
            "error_pattern": error_type,
            "confidence": 0.8,  # Placeholder confidence score
        }

    @staticmethod
    def _get_strategy_suggestions_by_name(strategy_name: str) -> list[str]:
        """Get strategy-specific debugging suggestions"""
        suggestions = []

        strategy_name = strategy_name.lower()

        if "random_name" in strategy_name:
            suggestions.extend(
                [
                    "Check name_type parameter (first, last, full)",
                    "Verify gender parameter (male, female, any)",
                    "Ensure case parameter is valid (title, upper, lower)",
                ]
            )

        elif "number_range" in strategy_name:
            suggestions.extend(
                [
                    "Verify start and end parameters are numeric",
                    "Check that start < end",
                    "Ensure numeric ranges are reasonable",
                ]
            )

        elif "date" in strategy_name:
            suggestions.extend(
                [
                    "Check date format strings",
                    "Verify start_date < end_date",
                    "Ensure date ranges are valid",
                ]
            )

        elif "pattern" in strategy_name:
            suggestions.extend(
                [
                    "Validate regex pattern syntax",
                    "Test pattern with online regex tools",
                    "Check for regex special characters that need escaping",
                ]
            )

        elif "choice" in strategy_name:
            suggestions.extend(
                [
                    "Verify choices dictionary format",
                    "Check that weights are positive numbers",
                    "Ensure choices are not empty",
                ]
            )

        return suggestions

    @staticmethod
    def _get_config_suggestions_by_path(config_path: str) -> list[str]:
        """Get configuration-specific debugging suggestions"""
        suggestions = []

        if config_path:
            config_path = config_path.lower()

            if config_path.endswith(".yaml") or config_path.endswith(".yml"):
                suggestions.extend(
                    [
                        "Check YAML syntax and indentation",
                        "Verify all strings are properly quoted",
                        "Look for tab characters (use spaces instead)",
                    ]
                )

            elif config_path.endswith(".json"):
                suggestions.extend(
                    [
                        "Validate JSON syntax",
                        "Check for trailing commas",
                        "Ensure all strings are double-quoted",
                    ]
                )

        return suggestions


class DebugReporter:
    """
    Generates debug reports for error analysis.
    """

    @staticmethod
    def export_debug_report(error, output_dir: str = "output") -> str:
        """Export detailed debug report to file"""

        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"debug_report_{timestamp}.txt"
        filepath = Path(output_dir) / filename

        # Generate report content
        report_lines = []
        report_lines.append("GenXData Debug Report")
        report_lines.append(f"Generated: {datetime.now()}")
        report_lines.append(f"{'=' * 80}")
        report_lines.append("")

        # Error context
        report_lines.append(DebugFormatter.format_error_context(error))
        report_lines.append("")

        # Stack trace
        report_lines.append(
            DebugFormatter.format_stack_trace(error, include_locals=True)
        )
        report_lines.append("")

        # Analysis and suggestions
        analysis = DebugAnalyzer.analyze_error_pattern(error)
        report_lines.append(DebugFormatter.format_suggestions(analysis["suggestions"]))
        report_lines.append("")

        # System information
        report_lines.append("🖥️  SYSTEM INFORMATION")
        report_lines.append(f"{'=' * 50}")
        report_lines.append(f"Python Version: {sys.version}")
        report_lines.append(f"Platform: {sys.platform}")

        # Write report to file
        with open(filepath, "w") as f:
            f.write("\n".join(report_lines))

        return str(filepath)


def debug_error(error, export_report: bool = True) -> None:
    """
    Debug an error by displaying formatted information and suggestions.

    Args:
        error: The error to debug
        export_report: Whether to export a debug report to file
    """
    logger.error(DebugFormatter.format_error_context(error))
    logger.error("")
    logger.error(DebugFormatter.format_stack_trace(error, include_locals=True))
    logger.error("")

    analysis = DebugAnalyzer.analyze_error_pattern(error)
    logger.error("SUGGESTIONS:")
    for suggestion in analysis["suggestions"]:
        logger.error(f"  • {suggestion}")

    if export_report:
        report_path = DebugReporter.export_debug_report(error)
        logger.info(f"\nDebug report exported to: {report_path}")
