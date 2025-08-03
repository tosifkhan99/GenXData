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

    def __init__(self, config: dict[str, Any], writer_implementation: BaseWriter = None):
        """
        Initialize the batch writer.

        Args:
            config: Batch writer configuration
            actual_writer: The actual writer to delegate to (FileWriter, StreamWriter, etc.)
        """
        super().__init__(config)
        self.logger = Logger.get_logger("batch_writer")
        self.writer_implementation = writer_implementation
        self.batches_written = 0
        self.total_rows_written = 0

        # If no actual writer provided, default to file writer
        if not self.writer_implementation:
            from .file_writer import FileWriter

            self.writer_implementation = FileWriter(config)

        self.logger.debug(
            f"BatchWriter initialized with {type(self.writer_implementation).__name__}"
        )

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
        
        # Delegate to the actual writer
        result = self.writer_implementation.write(df, batch_info)

        # Update counters
        self.batches_written += 1
        self.total_rows_written += len(df)

        self.logger.debug(f"Batch write result: {result}")

        return {
            "status": "success",
            "rows_written": len(df),
            "batch_index": self.batches_written,
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
        actual_summary = self.writer_implementation.finalize()

        summary = {
            "total_rows_written": self.total_rows_written,
            "total_batches_written": self.batches_written,
            "writer_type": "batch",
            "writer_implementation_type": type(self.writer_implementation).__name__,
            "writer_implementation_summary": actual_summary,
        }

        self.logger.debug(f"Batch writer summary: {summary}")
        return summary
