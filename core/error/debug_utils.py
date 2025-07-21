"""
Debug utilities for error analysis and troubleshooting.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from core.error.error_context import ErrorContext
from utils.logging import Logger

# Initialize debug logger
logger = Logger.get_logger("debug")


class DebugFormatter:
    """
    Formats error information for debugging output.
    """

    @staticmethod
    def format_error_context(error: ErrorContext) -> str:
        """Format error context for display"""
        lines = []
        lines.append("🔍 ERROR DEBUG INFORMATION")
        lines.append(f"{'=' * 50}")
        lines.append(f"Error Type: {error.error_type}")
        lines.append(f"Message: {error.message}")
        lines.append(f"Severity: {error.severity.name}")
        lines.append(f"Timestamp: {error.timestamp}")
        lines.append(f"Component: {error.component}")

        if error.strategy_name:
            lines.append(f"Strategy: {error.strategy_name}")

        if error.column_name:
            lines.append(f"Column: {error.column_name}")

        if error.config_path:
            lines.append(f"Config Path: {error.config_path}")

        if error.additional_context:
            lines.append("\nAdditional Context:")
            for key, value in error.additional_context.items():
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)

    @staticmethod
    def format_stack_trace(error: ErrorContext, include_locals: bool = False) -> str:
        """Format stack trace with optional local variables"""
        lines = []
        lines.append("📍 STACK TRACE")
        lines.append(f"{'=' * 50}")

        if error.stack_trace:
            lines.append(error.stack_trace)

        if include_locals and error.local_variables:
            lines.append("\n🔧 LOCAL VARIABLES")
            lines.append(f"{'=' * 50}")
            for var_name, var_value in error.local_variables.items():
                try:
                    # Safely format the variable value
                    if isinstance(var_value, (str, int, float, bool, type(None))):
                        formatted_value = repr(var_value)
                    elif isinstance(var_value, (list, dict, tuple)):
                        formatted_value = (
                            str(var_value)[:200] + "..."
                            if len(str(var_value)) > 200
                            else str(var_value)
                        )
                    else:
                        formatted_value = f"<{type(var_value).__name__} object>"

                    lines.append(f"  {var_name}: {formatted_value}")
                except Exception:
                    lines.append(f"  {var_name}: <unable to format>")

        return "\n".join(lines)

    @staticmethod
    def format_suggestions(suggestions: List[str]) -> str:
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
    def analyze_error_pattern(error: ErrorContext) -> Dict[str, Any]:
        """Analyze error patterns and provide suggestions"""
        suggestions = []

        # Strategy-specific suggestions
        if error.strategy_name:
            suggestions.extend(DebugAnalyzer._get_strategy_suggestions(error))

        # Configuration-specific suggestions
        if error.config_path:
            suggestions.extend(DebugAnalyzer._get_config_suggestions(error))

        # General suggestions based on error type
        if "param" in error.error_type.lower():
            suggestions.extend(
                [
                    "Check parameter names and types in your configuration",
                    "Verify required parameters are provided",
                    "Check parameter value ranges and constraints",
                ]
            )

        if "validation" in error.error_type.lower():
            suggestions.extend(
                [
                    "Review configuration file format and structure",
                    "Check for missing required fields",
                    "Validate data types match expected formats",
                ]
            )

        if "file" in error.error_type.lower() or "path" in error.error_type.lower():
            suggestions.extend(
                [
                    "Verify file paths exist and are accessible",
                    "Check file permissions",
                    "Ensure file formats are supported",
                ]
            )

        # Add severity-based suggestions
        if hasattr(error, "severity") and error.severity:
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
            "error_pattern": error.error_type,
            "confidence": 0.8,  # Placeholder confidence score
        }

    @staticmethod
    def _get_strategy_suggestions(error: ErrorContext) -> List[str]:
        """Get strategy-specific debugging suggestions"""
        suggestions = []

        strategy_name = error.strategy_name.lower()

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
    def _get_config_suggestions(error: ErrorContext) -> List[str]:
        """Get configuration-specific debugging suggestions"""
        suggestions = []

        if error.config_path:
            config_path = error.config_path.lower()

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
    def export_debug_report(error: ErrorContext, output_dir: str = "output") -> str:
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


def debug_error(error: ErrorContext, export_report: bool = True) -> None:
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
