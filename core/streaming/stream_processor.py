"""
Streaming processing functionality for GenXData.
"""

import pandas as pd

import configs.GENERATOR_SETTINGS as SETTINGS
from core.batch_processing import get_batches, prepare_batch_config

from core.processor.process_config import process_config
from exceptions.streaming_exception import StreamingException
from utils.logging import Logger

# Initialize logger for streaming processor
logger = Logger.get_logger("streaming")


def process_streaming_config(
    config_file, stream_config, perf_report=False
):
    """
    Process configuration in streaming mode.

    Args:
        config_file (dict): Configuration data
        stream_config (dict): Streaming configuration
        perf_report (bool): Whether to generate a performance report

    Returns:
        dict: Results with last batch data
    """

    logger.info("Starting streaming configuration processing")
    logger.debug(f"Stream config: {stream_config}")
    logger.debug(f"Total rows to process: {config_file.get('num_of_rows', 'unknown')}")

    # Initialize state tracking for the entire streaming session
    strategy_states = {}
    logger.debug("Initialized strategy states for streaming session")

    # Get streaming configuration
    streaming_config = stream_config.get("streaming", {})
    logger.debug(f"Streaming configuration: {streaming_config}")

    # Get batch size from streaming config or use default
    batch_size = streaming_config.get("batch_size", SETTINGS.STREAM_BATCH_SIZE)
    batches = get_batches(batch_size, config_file["num_of_rows"])

    logger.info(f"Configured for streaming with batch size: {batch_size}")
    logger.info(f"Total batches to process: {len(batches)}")

    # Initialize queue producer using the factory
    queue_producer = None
    try:
        logger.debug("Initializing queue producer")
        from messaging.factory import QueueFactory

        queue_producer = QueueFactory.create_from_config(stream_config)
        queue_producer.connect()
        logger.info("Successfully connected to queue producer")

    except ImportError as e:
        error_msg = f"Queue library not available: {e}"
        logger.error(error_msg)
        raise StreamingException(
            error_msg, 
        ) from e
    except Exception as e:
        error_msg = f"Could not connect to queue: {e}"
        logger.error(error_msg)
        raise StreamingException(
            error_msg, 
        ) from e

    df = None
    for batch_index, batch_size in enumerate(batches):
        logger.info(
            f"Processing batch {batch_index + 1}/{len(batches)} (size: {batch_size})"
        )

        # Pre-calculate and modify config for this batch
        batch_config = prepare_batch_config(
            config_file, batch_size, batch_index, strategy_states
        )
        logger.debug(f"Prepared batch config: {batch_config}")
        logger.debug(f"Prepared batch config for batch {batch_index}")

        try:
            df = process_config(batch_config, perf_report)
            logger.debug(
                f"Batch {batch_index} processed successfully. Generated {len(df)} rows"
            )

            # Send batch to queue if producer is available
            if queue_producer:
                batch_info = {
                    "batch_index": batch_index,
                    "batch_size": batch_size,
                    "total_batches": len(batches),
                    "config_name": config_file.get("metadata", {}).get(
                        "name", "unknown"
                    ),
                    "timestamp": pd.Timestamp.now().isoformat(),
                }

                # Include additional metadata if configured
                if streaming_config.get("include_metadata", True):
                    batch_info["streaming_config"] = streaming_config
                    logger.debug(f"Including streaming metadata in batch {batch_index}")

                logger.debug(f"Sending batch {batch_index} to queue")
                queue_producer.send_dataframe(df, batch_info)
                logger.info(f"Batch {batch_index} sent to queue successfully")
            else:
                logger.warning(f"No queue producer available for batch {batch_index}")

        except Exception as e:
            logger.error(f"Failed to process batch {batch_index}: {e}")
            raise

    # Clean up queue producer
    if queue_producer:
        logger.debug("Disconnecting from queue producer")
        queue_producer.disconnect()
        logger.info("Queue producer disconnected successfully")

    logger.info(f"Streaming processing completed. Processed {len(batches)} batches")

    # Return the last batch as the result
    result_size = len(df) if df is not None else 0
    logger.info(f"Returning final result with {result_size} records")

    return {"df": df.to_dict(orient="records") if df is not None else []}
