import logging
import os
import sys
from typing import Any


class Logger:
    """
    Enhanced logging utility for GenXData.

    This class provides a centralized, configurable logging system
    with support for console and file outputs, custom formatting,
    and log level management.
    """

    # Valid log levels
    VALID_LOG_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARN": logging.WARNING,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    # Store logger instances
    _loggers: dict[str, logging.Logger] = {}

    @classmethod
    def get_logger(
        cls,
        name: str | None = None,
        log_level: str = "INFO",
        log_file: str | None = None,
        format_detailed: bool = False,
    ) -> logging.Logger:
        """
        Get or create a logger with the specified configuration.

        Args:
            name: Logger name (defaults to calling module name)
            log_level: Log level (DEBUG, INFO, WARN, ERROR, CRITICAL)
            log_file: Optional path to log file
            format_detailed: Whether to use detailed formatting

        Returns:
            Configured logger instance
        """
        # Get logger name from calling module if not provided
        if name is None:
            frame = sys._getframe(1)
            name = frame.f_globals.get("__name__", "genxdata")

        # Create a qualified name
        logger_name = f"genxdata.{name}" if not name.startswith("genxdata") else name

        # Return existing logger if already configured
        if logger_name in cls._loggers:
            return cls._loggers[logger_name]

        # Create and configure a new logger
        logger = cls._create_logger(logger_name, log_level, log_file, format_detailed)
        cls._loggers[logger_name] = logger

        return logger

    @classmethod
    def _create_logger(
        cls, name: str, log_level: str, log_file: str | None, format_detailed: bool
    ) -> logging.Logger:
        """
        Create and configure a new logger.

        Args:
            name: Logger name
            log_level: Log level
            log_file: Optional path to log file
            format_detailed: Whether to use detailed formatting

        Returns:
            Configured logger instance
        """
        # Normalize and validate log level
        log_level = log_level.upper() if log_level else "INFO"
        if log_level not in cls.VALID_LOG_LEVELS:
            print(f"Warning: Invalid log level '{log_level}'. Using INFO instead.")
            log_level = "INFO"

        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(cls.VALID_LOG_LEVELS[log_level])

        # Clear existing handlers
        if logger.handlers:
            logger.handlers.clear()

        # Create formatter
        if format_detailed:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        else:
            formatter = logging.Formatter("%(levelname)s - %(message)s")

        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Add file handler if specified
        if log_file:
            # Ensure directory exists
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    @classmethod
    def configure_all_loggers(cls, config: dict[str, Any]) -> None:
        """
        Configure all existing loggers with new settings.

        Args:
            config: Configuration dictionary with logging settings
        """
        log_level = config.get("log_level", "INFO")
        log_file = config.get("log_file")
        format_detailed = config.get("format_detailed", False)

        # Validate log level
        if log_level.upper() not in cls.VALID_LOG_LEVELS:
            print(f"Warning: Invalid log level '{log_level}'. Using INFO instead.")
            log_level = "INFO"

        # Update all existing loggers
        for _logger_name, logger in cls._loggers.items():
            logger.setLevel(cls.VALID_LOG_LEVELS[log_level.upper()])

            # Update or add handlers
            has_file_handler = False

            # Update existing handlers
            for handler in logger.handlers[:]:
                if isinstance(handler, logging.StreamHandler) and not isinstance(
                    handler, logging.FileHandler
                ):
                    # Update console formatter
                    if format_detailed:
                        handler.setFormatter(
                            logging.Formatter(
                                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                                datefmt="%Y-%m-%d %H:%M:%S",
                            )
                        )
                    else:
                        handler.setFormatter(
                            logging.Formatter("%(levelname)s - %(message)s")
                        )

                # Check for existing file handler
                if isinstance(handler, logging.FileHandler):
                    has_file_handler = True
                    # Remove old file handler if log file changed
                    if log_file and handler.baseFilename != os.path.abspath(log_file):
                        logger.removeHandler(handler)
                        has_file_handler = False

            # Add file handler if needed
            if log_file and not has_file_handler:
                # Ensure directory exists
                log_dir = os.path.dirname(log_file)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)

                file_handler = logging.FileHandler(log_file)
                if format_detailed:
                    file_handler.setFormatter(
                        logging.Formatter(
                            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S",
                        )
                    )
                else:
                    file_handler.setFormatter(
                        logging.Formatter("%(levelname)s - %(message)s")
                    )
                logger.addHandler(file_handler)
