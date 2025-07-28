"""
Batch writer implementation for GenXData.

This is a compatibility wrapper that implements the BaseWriter interface
for use with batch processing scenarios.
"""

from typing import Any

import pandas as pd

from utils.logging import Logger

from .base_writer import BaseWriter


class BatchWriter(BaseWriter):
    """
    Writer implementation for batch processing scenarios.

    This is a wrapper that adapts the existing BatchWriter interface
    used by streaming_batch_processor to the new BaseWriter interface.
    """

    def __init__(self, config: dict[str, Any], actual_writer: BaseWriter = None):
        """
        Initialize the batch writer.

        Args:
            config: Batch writer configuration
            actual_writer: The actual writer to delegate to (FileWriter, StreamWriter, etc.)
        """
        super().__init__(config)
        self.logger = Logger.get_logger("batch_writer")
        self.actual_writer = actual_writer
        self.batches_written = 0
        self.total_rows_written = 0

        # If no actual writer provided, default to file writer
        if not self.actual_writer:
            from .file_writer import FileWriter

            self.actual_writer = FileWriter(config)

        self.logger.debug(
            f"BatchWriter initialized with {type(self.actual_writer).__name__}"
        )

    def write_batch(self, df: pd.DataFrame, batch_info: dict[str, Any]) -> None:
        """
        Write a batch (compatibility method for streaming_batch_processor).

        Args:
            df: DataFrame batch to write
            batch_info: Information about the batch
        """
        self.logger.debug(
            f"Writing batch {batch_info.get('batch_index', 'unknown')} with {len(df)} rows"
        )

        # Delegate to the actual writer
        result = self.actual_writer.write(df, batch_info)

        # Update counters
        self.batches_written += 1
        self.total_rows_written += len(df)

        self.logger.debug(f"Batch write result: {result}")

    def write(
        self, df: pd.DataFrame, metadata: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        Write DataFrame (BaseWriter interface).

        Args:
            df: DataFrame to write
            metadata: Optional metadata

        Returns:
            Dictionary with write operation results
        """
        # Convert to batch format and delegate
        batch_info = {
            "batch_index": self.batches_written,
            "batch_size": len(df),
            "timestamp": pd.Timestamp.now().isoformat(),
        }

        if metadata:
            batch_info.update(metadata)

        self.write_batch(df, batch_info)

        return {
            "status": "success",
            "rows_written": len(df),
            "batch_index": self.batches_written - 1,
            "metadata": metadata,
        }

    def finalize(self) -> dict[str, Any]:
        """
        Finalize batch writing operations.

        Returns:
            Dictionary with summary of all write operations
        """
        self.logger.info(
            f"Finalizing batch writer. Total batches: {self.batches_written}, Total rows: {self.total_rows_written}"
        )

        # Finalize the actual writer
        actual_summary = self.actual_writer.finalize()

        summary = {
            "total_rows_written": self.total_rows_written,
            "total_batches_written": self.batches_written,
            "writer_type": "batch",
            "actual_writer_type": type(self.actual_writer).__name__,
            "actual_writer_summary": actual_summary,
        }

        self.logger.debug(f"Batch writer summary: {summary}")
        return summary
