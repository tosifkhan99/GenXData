"""
Main orchestrator for GenXData processing.
"""

import configs.GENERATOR_SETTINGS as SETTINGS
from core.error.error import ErrorHandler
from core.error.error_context import ErrorContextBuilder
from core.processors import NormalConfigProcessor, StreamingConfigProcessor
from core.writers import BaseWriter, FileWriter, StreamWriter
from exceptions.invalid_running_mode_exception import InvalidRunningModeException
from utils.config_utils import load_config
from utils.logging import Logger


class DataOrchestrator:
    """
    Orchestrator class for data generation processing.
    """

    def __init__(
        self,
        config,
        perf_report=SETTINGS.PERF_REPORT,
        stream=None,
        batch=None,
        log_level=None,
    ):
        """
        Initialize the DataOrchestrator.

        Args:
            config (dict): Configuration dictionary
            perf_report (bool): Whether to generate performance report
            stream (str): Path to streaming config file
            batch (str): Path to batch config file
        """
        self.config = config
        self.perf_report = perf_report
        self.stream = stream
        self.batch = batch
        self.log_level = log_level
        self.logger = Logger.get_logger(__name__, log_level)
        self.error_handler = ErrorHandler(self.logger)

    def _create_writer(self, config: dict, stream_config: dict = None) -> "BaseWriter":
        """
        Create appropriate writer based on configuration.

        Args:
            config: Main configuration
            stream_config: Optional streaming configuration

        Returns:
            Writer instance
        """
        if stream_config:
            # Create stream writer for streaming/batch scenarios
            self.logger.debug("Creating StreamWriter for streaming/batch processing")
            return StreamWriter(stream_config)
        else:
            # Create file writer for normal processing
            self.logger.debug("Creating FileWriter for normal processing")
            return FileWriter(config)

    def run(self):
        """
        Run the data generation process using the new processor architecture.

        Returns:
            dict: Processing results
        """
        self.logger.info("Starting data generation with config")
        self.logger.info(
            r"""
  _____           __   _______        _
 / ____|          \ \ / /  __ \      | |
| |  __  ___ _ __  \ V /| |  | | __ _| |_ __ _
| | |_ |/ _ \ '_ \  > < | |  | |/ _` | __/ _` |
| |__| |  __/ | | |/ . \| |__| | (_| | || (_| |
 \_____|\___|_| |_/_/ \_\_____/ \__,_|\__\__,_|

"""
        )

        self.logger.debug(f"Config: {self.config}")
        self.logger.debug(f"Perf report: {self.perf_report}")
        self.logger.debug(f"Stream: {self.stream}")
        self.logger.debug(f"Batch: {self.batch}")
        self.logger.debug(f"Log level: {self.log_level}")

        try:
            # Validate running mode
            if self.stream and self.batch:
                raise InvalidRunningModeException(
                    context=ErrorContextBuilder()
                    .with_config(self.config)
                    .with_stream(self.stream)
                    .with_batch(self.batch)
                    .build()
                )

            # Determine processing mode and create appropriate processor
            if self.stream or self.batch:
                # Streaming/Batch processing
                stream_config_path = self.stream or self.batch
                stream_config = load_config(stream_config_path)

                self.logger.info(
                    f"Processing {'streaming' if self.stream else 'batch'} config"
                )
                self.logger.debug(f"Stream/Batch config: {stream_config}")

                # Create writer and processor
                writer = self._create_writer(self.config, stream_config)
                processor = StreamingConfigProcessor(
                    config=self.config,
                    writer=writer,
                    error_handler=self.error_handler,
                    batch_size=stream_config.get("batch_size", 1000),
                    chunk_size=stream_config.get("chunk_size", 1000),
                    perf_report=self.perf_report,
                )

                return processor.process()

            else:
                # Normal processing
                self.logger.info("Processing normal config")

                # Create writer and processor
                writer = self._create_writer(self.config)
                processor = NormalConfigProcessor(
                    config=self.config,
                    writer=writer,
                    error_handler=self.error_handler,
                    perf_report=self.perf_report,
                )

                result = processor.process()

                # For backward compatibility, convert DataFrame to records
                if "df" in result and hasattr(result["df"], "to_dict"):
                    result["df"] = result["df"].to_dict(orient="records")

                return result

        except Exception as e:
            self.error_handler.add_error(e)
            result = {"status": "error", "error": str(e), "processor_type": "unknown"}
        else:
            result = None

        # Centralized error reporting with severity-based formatting
        if self.error_handler.has_errors():
            self.logger.error(
                "========== Orchestrator completed with errors =========="
            )
            self.error_handler.generate_error_report()

        # Only fail if there are critical errors
        if self.error_handler.has_critical_errors():
            self.logger.error(
                "========== Orchestrator completed with critical errors =========="
            )
            self.logger.critical("Critical errors detected. Process cannot continue.")
            return None

        return result
