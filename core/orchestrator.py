"""
Main orchestrator for GenXData processing.
"""

import configs.GENERATOR_SETTINGS as SETTINGS
from core.processors import NormalConfigProcessor, StreamingConfigProcessor
from core.writers import BaseWriter, BatchWriter, FileWriter, StreamWriter
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
            # Check if this is batch processing (has batch_writer config)
            if "batch" in stream_config:
                self.logger.debug("Creating BatchWriter for batch processing")
                batch_config = stream_config["batch"]
                file_writer = FileWriter(config) 
                return BatchWriter(stream_config, file_writer)
            else:
                # Create stream writer for streaming scenarios
                self.logger.debug("Creating StreamWriter for streaming processing")
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
                raise InvalidRunningModeException()

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
                
                # Extract batch_size and chunk_size from the appropriate location
                if "batch" in stream_config["metadata"]["type"] or "batch" in stream_config:
                    # For batch processing, get sizes from batch_writer config
                    batch_config = stream_config["batch"]
                    batch_size = batch_config.get("batch_size", 1000)
                    chunk_size = batch_config.get("chunk_size", batch_size)
                else:
                    # For streaming processing, get sizes from root config
                    batch_size = stream_config.get("batch_size", 1000)
                    chunk_size = stream_config.get("chunk_size", 1000)
                
                processor = StreamingConfigProcessor(
                    config=self.config,
                    writer=writer,
                    batch_size=batch_size,
                    chunk_size=chunk_size,
                    perf_report=self.perf_report,
                )

            else:
                # Normal processing
                self.logger.info("Processing normal config")

                # Create writer and processor
                writer = self._create_writer(self.config)
                processor = NormalConfigProcessor(
                    config=self.config,
                    writer=writer,
                    perf_report=self.perf_report,
                )

            return processor.process()

        except Exception as e:
            self.logger.error(f"Error during processing: {str(e)}")
            return {"status": "error", "error": str(e), "processor_type": "unknown"}
