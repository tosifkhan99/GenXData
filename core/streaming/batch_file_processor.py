"""
Batch file processing functionality for GenXData.
"""

import pandas as pd
import configs.GENERATOR_SETTINGS as SETTINGS
from core.batch_processing import get_batches, prepare_batch_config
from exceptions.batch_processing_exception import BatchProcessingException
from core.error.error_context import ErrorContextBuilder
from core.processor.process_config import process_config
from utils.logging import Logger

# Initialize logger for batch file processor
logger = Logger.get_logger("batch_processing")


def process_batch_config(config_file, batch_config, error_handler, perf_report=False):
    """
    Process configuration in batch file mode.

    Args:
        config_file (dict): Configuration data
        batch_config (dict): Batch configuration
        error_handler: Error handler instance for collecting errors
        perf_report (bool): Whether to generate a performance report

    Returns:
        dict: Results with last batch data
    """

    logger.info("Starting batch file configuration processing")
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

    logger.info(f"Batch files will be written to: {output_dir}")
    logger.info(f"File prefix: {file_prefix}, format: {file_format}")

    # Initialize state tracking for the entire batch session
    strategy_states = {}
    logger.debug("Initialized strategy states for batch session")

    # Get batch size from batch config or use default
    batch_size = writer_config.get("batch_size", SETTINGS.STREAM_BATCH_SIZE)
    batches = get_batches(batch_size, config_file["num_of_rows"])

    logger.info(f"Configured for batch processing with batch size: {batch_size}")
    logger.info(f"Total batches to process: {len(batches)}")

    # Initialize batch writer
    try:
        logger.debug("Initializing batch writer")
        from writers.batch_writer import BatchWriter

        batch_writer = BatchWriter(
            output_dir=output_dir, file_prefix=file_prefix, file_format=file_format
        )
        logger.info("Batch writer initialized successfully")

    except Exception as e:
        error_msg = f"Failed to initialize batch writer: {e}"
        logger.error(error_msg)
        raise BatchProcessingException(
            error_msg, context=ErrorContextBuilder().with_config(batch_config).build()
        )

    df = None
    for batch_index, batch_size in enumerate(batches):
        logger.info(
            f"Processing batch {batch_index + 1}/{len(batches)} (size: {batch_size})"
        )

        # Pre-calculate and modify config for this batch
        batch_config_item = prepare_batch_config(
            config_file, batch_size, batch_index, strategy_states
        )
        logger.debug(f"Prepared batch config for batch {batch_index}")

        try:
            df = process_config(batch_config_item, perf_report, error_handler)
            logger.debug(
                f"Batch {batch_index} processed successfully. Generated {len(df)} rows"
            )

            # Write batch to file
            batch_info = {
                "batch_index": batch_index,
                "batch_size": batch_size,
                "total_batches": len(batches),
                "config_name": config_file.get("metadata", {}).get("name", "unknown"),
                "timestamp": pd.Timestamp.now().isoformat(),
            }

            logger.debug(f"Writing batch {batch_index} to file")
            batch_writer.write_batch(df, batch_info)
            logger.info(f"Batch {batch_index} written to file successfully")

        except Exception as e:
            logger.error(f"Failed to process batch {batch_index}: {e}")
            error_handler.add_error(e)
            raise

    # Get summary
    try:
        logger.debug("Generating batch processing summary")
        summary = batch_writer.get_summary()
        logger.info(f"Batch processing summary: {summary}")

    except Exception as e:
        logger.warning(f"Failed to generate batch summary: {e}")
        summary = None

    logger.info(f"Batch file processing completed. Processed {len(batches)} batches")

    # Return the last batch as the result
    result_size = len(df) if df is not None else 0
    logger.info(f"Returning final result with {result_size} records")

    return {"df": df.to_dict(orient="records") if df is not None else []}
