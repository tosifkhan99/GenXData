"""
Batch file processing functionality for GenXData.
Updated to use StreamingBatchProcessor with stateful strategies.
"""

import pandas as pd

import configs.GENERATOR_SETTINGS as SETTINGS
from core.error.error_context import ErrorContextBuilder
from core.streaming.streaming_batch_processor import (
    BatchWriter,
    StreamingBatchProcessor,
)
from exceptions.batch_processing_exception import BatchProcessingException
from utils.logging import Logger

# Initialize logger for batch file processor
logger = Logger.get_logger("batch_processing")


class FileBatchWriter(BatchWriter):
    """
    Adapter for the existing BatchWriter to work with StreamingBatchProcessor
    """

    def __init__(
        self, output_dir: str, file_prefix: str = "batch", file_format: str = "json"
    ):
        """Initialize the file batch writer"""
        from writers.batch_writer import BatchWriter as LegacyBatchWriter

        self.writer = LegacyBatchWriter(
            output_dir=output_dir, file_prefix=file_prefix, file_format=file_format
        )
        logger.debug(
            f"FileBatchWriter initialized: dir={output_dir}, format={file_format}"
        )

    def write_batch(self, df: pd.DataFrame, batch_info: dict) -> None:
        """Write a batch using the legacy batch writer"""
        logger.debug(
            f"Writing batch {batch_info.get('batch_index', 'unknown')} with {len(df)} rows"
        )
        self.writer.write_batch(df, batch_info)

    def finalize(self) -> dict:
        """Get summary from the legacy batch writer"""
        summary = self.writer.get_summary()
        logger.info(f"Batch writing finalized: {summary}")
        return summary


def process_batch_config(config_file, batch_config, error_handler, perf_report=False):
    """
    Process configuration in batch file mode using StreamingBatchProcessor.

    This implementation uses stateful strategies to eliminate the need for
    manual config parameter adjustments and provides better memory efficiency.

    Args:
        config_file (dict): Configuration data
        batch_config (dict): Batch configuration
        error_handler: Error handler instance for collecting errors
        perf_report (bool): Whether to generate a performance report

    Returns:
        dict: Results with processing summary
    """

    logger.info(
        "Starting batch file configuration processing with StreamingBatchProcessor"
    )
    logger.debug(f"Batch config: {batch_config}")
    logger.debug(f"Total rows to process: {config_file.get('num_of_rows', 'unknown')}")

    # Validate batch configuration
    if "batch_writer" not in batch_config:
        error_msg = (
            "Batch config must contain 'batch_writer' section with writer settings"
        )
        logger.error(error_msg)
        raise BatchProcessingException(
            error_msg, context=ErrorContextBuilder().with_config(batch_config).build()
        )

    writer_config = batch_config["batch_writer"]
    logger.debug(f"Batch writer configuration: {writer_config}")

    # Required batch writer settings
    if "output_dir" not in writer_config:
        error_msg = "Batch writer config must contain 'output_dir' setting"
        logger.error(error_msg)
        raise BatchProcessingException(
            error_msg, context=ErrorContextBuilder().with_config(batch_config).build()
        )

    output_dir = writer_config["output_dir"]
    file_prefix = writer_config.get("file_prefix", "batch")
    file_format = writer_config.get("file_format", "json")
    batch_size = writer_config.get("batch_size", SETTINGS.STREAM_BATCH_SIZE)
    chunk_size = writer_config.get(
        "chunk_size", 1000
    )  # New parameter for chunk generation

    logger.info(f"Batch files will be written to: {output_dir}")
    logger.info(f"File prefix: {file_prefix}, format: {file_format}")
    logger.info(f"Batch size: {batch_size}, chunk size: {chunk_size}")

    # Initialize batch writer
    try:
        logger.debug("Initializing FileBatchWriter")
        batch_writer = FileBatchWriter(
            output_dir=output_dir, file_prefix=file_prefix, file_format=file_format
        )
        logger.info("FileBatchWriter initialized successfully")

    except Exception as e:
        error_msg = f"Failed to initialize batch writer: {e}"
        logger.error(error_msg)
        raise BatchProcessingException(
            error_msg, context=ErrorContextBuilder().with_config(batch_config).build()
        )

    # Initialize and run StreamingBatchProcessor
    try:
        logger.debug("Initializing StreamingBatchProcessor")
        processor = StreamingBatchProcessor(
            config=config_file,
            batch_size=batch_size,
            batch_writer=batch_writer,
            chunk_size=chunk_size,
        )
        logger.info("StreamingBatchProcessor initialized successfully")

        # Log initial strategy states for debugging
        if logger.isEnabledFor(10):  # DEBUG level
            initial_states = processor.get_strategy_states()
            logger.debug(f"Initial strategy states: {initial_states}")

        # Process the data
        logger.info("Starting data processing with StreamingBatchProcessor")
        result = processor.process()

        # Log final strategy states for debugging
        if logger.isEnabledFor(10):  # DEBUG level
            final_states = processor.get_strategy_states()
            logger.debug(f"Final strategy states: {final_states}")

        logger.info("StreamingBatchProcessor completed successfully")
        return result

    except Exception as e:
        error_msg = f"Failed during streaming batch processing: {e}"
        logger.error(error_msg, exc_info=True)
        error_handler.add_error(e)
        raise BatchProcessingException(
            error_msg, context=ErrorContextBuilder().with_config(batch_config).build()
        )
