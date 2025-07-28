"""
Stream writer implementation for GenXData.

Handles writing DataFrames to message queues (AMQP, Kafka, etc.).
"""

from typing import Dict, Any
import pandas as pd

from .base_writer import BaseWriter
from messaging.factory import QueueFactory
from utils.logging import Logger


class StreamWriter(BaseWriter):
    """
    Writer implementation for streaming/message queue outputs.

    Uses the messaging module to send data to various message queue systems.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the stream writer.

        Args:
            config: Stream writer configuration containing queue settings
        """
        super().__init__(config)
        self.logger = Logger.get_logger("stream_writer")
        self.queue_producer = None
        self.total_rows_written = 0
        self.total_batches_sent = 0

        # Validate configuration
        self.validate_config()

        # Initialize queue producer
        self._initialize_producer()

        self.logger.debug("StreamWriter initialized with config")

    def validate_config(self) -> bool:
        """
        Validate stream writer configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        super().validate_config()

        # Check for required streaming configuration
        required_fields = ["type", "host", "port", "queue"]
        for field in required_fields:
            if field not in self.config:
                raise ValueError(
                    f"Stream writer config missing required field: {field}"
                )

        return True

    def _initialize_producer(self):
        """Initialize the message queue producer."""
        try:
            self.logger.debug("Initializing queue producer")
            self.queue_producer = QueueFactory.create_from_config(self.config)
            self.queue_producer.connect()
            self.logger.info("Successfully connected to message queue")
        except Exception as e:
            self.logger.error(f"Failed to initialize queue producer: {e}")
            raise

    def write(
        self, df: pd.DataFrame, metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Write DataFrame to message queue.

        Args:
            df: DataFrame to write
            metadata: Optional metadata (batch info, etc.)

        Returns:
            Dictionary with write operation results
        """
        if df.empty:
            self.logger.warning("Received empty DataFrame, skipping write")
            return {"status": "skipped", "reason": "empty_dataframe"}

        if not self.queue_producer:
            self.logger.error("Queue producer not initialized")
            return {"status": "error", "error": "Queue producer not initialized"}

        self.logger.info(f"Sending DataFrame with {len(df)} rows to message queue")

        try:
            # Prepare batch information
            batch_info = {
                "rows": len(df),
                "columns": list(df.columns),
                "timestamp": pd.Timestamp.now().isoformat(),
            }

            # Add metadata if provided
            if metadata:
                batch_info.update(metadata)

            # Send DataFrame to queue
            self.queue_producer.send_dataframe(df, batch_info)

            # Update counters
            self.total_rows_written += len(df)
            self.total_batches_sent += 1

            self.logger.info(f"Successfully sent {len(df)} rows to message queue")

            return {
                "status": "success",
                "rows_written": len(df),
                "batch_info": batch_info,
                "metadata": metadata,
            }

        except Exception as e:
            self.logger.error(f"Error sending DataFrame to message queue: {e}")
            return {"status": "error", "error": str(e), "metadata": metadata}

    def finalize(self) -> Dict[str, Any]:
        """
        Finalize stream writing operations and cleanup.

        Returns:
            Dictionary with summary of all write operations
        """
        self.logger.info(
            f"Finalizing stream writer. Total rows sent: {self.total_rows_written}"
        )

        # Disconnect from queue
        if self.queue_producer:
            try:
                self.queue_producer.disconnect()
                self.logger.info("Disconnected from message queue")
            except Exception as e:
                self.logger.warning(f"Error disconnecting from queue: {e}")

        summary = {
            "total_rows_written": self.total_rows_written,
            "total_batches_sent": self.total_batches_sent,
            "queue_type": self.config.get("type", "unknown"),
            "queue_host": self.config.get("host", "unknown"),
            "queue_name": self.config.get("queue", "unknown"),
            "writer_type": "stream",
        }

        self.logger.debug(f"Stream writer summary: {summary}")
        return summary
