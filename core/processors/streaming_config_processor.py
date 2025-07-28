"""
Streaming config processor for GenXData.

Handles chunked data generation where data is generated in batches/chunks
and written incrementally. This handles both streaming and batch scenarios.
"""

from typing import Any

import pandas as pd

from core.writers.batch_writer import BatchWriter
from utils.performance_timer import get_performance_report, measure_time

from .base_config_processor import BaseConfigProcessor


class StreamingConfigProcessor(BaseConfigProcessor):
    """
    Processor for streaming/batch data generation.

    Generates data in chunks and writes incrementally, which is more memory
    efficient for large datasets and enables real-time processing.
    """

    def __init__(
        self,
        config: dict[str, Any],
        writer,
        error_handler,
        batch_size: int = 1000,
        chunk_size: int = 1000,
        perf_report: bool = False,
    ):
        """
        Initialize the streaming config processor.

        Args:
            config: Configuration dictionary
            writer: Writer instance for output
            error_handler: Error handler for collecting errors
            batch_size: Size of each batch to write
            chunk_size: Size of chunks to generate at once
            perf_report: Whether to generate performance report
        """
        super().__init__(config, writer, error_handler)
        self.batch_size = batch_size
        self.chunk_size = min(chunk_size, batch_size)  # Don't exceed batch size
        self.perf_report = perf_report

        # Ensure writer is batch-compatible
        if not isinstance(writer, BatchWriter):
            self.writer = BatchWriter(config, writer)

        self.logger.info(
            f"StreamingConfigProcessor initialized: target_rows={self.rows}, "
            f"batch_size={self.batch_size}, chunk_size={self.chunk_size}"
        )

    def _process_chunk(self, chunk_size: int) -> pd.DataFrame:
        """
        Process a single chunk following the same steps as normal processor.

        Args:
            chunk_size: Number of rows to generate in this chunk

        Returns:
            Processed DataFrame chunk ready for writing
        """
        self.logger.debug(f"Processing chunk of {chunk_size} rows")

        # Create base DataFrame (same as normal processor)
        chunk_df = self.create_base_dataframe(chunk_size)

        # Process column strategies (same as normal processor)
        chunk_df = self.process_column_strategies(chunk_df)

        # Apply shuffle if enabled (same as normal processor)
        chunk_df = self.apply_shuffle(chunk_df)

        # Filter out intermediate columns (same as normal processor)
        chunk_df = self.filter_intermediate_columns(chunk_df)

        return chunk_df

    def process(self) -> dict[str, Any]:
        """
        Process the configuration using streaming/batch generation.

        Follows the same pattern as NormalConfigProcessor but processes data in chunks.

        Returns:
            Dictionary with processing results
        """
        self.logger.info(f"Starting streaming config processing for {self.rows} rows")

        try:
            # Validate configuration (same as normal processor)
            self.validate_config()

            # Process data in chunks, following the same steps as normal processor
            total_generated = 0
            batch_count = 0

            while total_generated < self.rows:
                # Calculate chunk size
                remaining_rows = self.rows - total_generated
                chunk_size = min(self.chunk_size, remaining_rows)

                self.logger.debug(
                    f"Processing chunk {batch_count + 1}: size={chunk_size}, "
                    f"total_generated={total_generated}, "
                    f"remaining={remaining_rows}"
                )

                # Process chunk following the same steps as normal processor
                with measure_time("chunk_processing", rows_processed=chunk_size):
                    chunk_df = self._process_chunk(chunk_size)

                # Write chunk using the writer (same as normal processor)
                self.logger.debug(
                    f"Writing chunk {batch_count + 1} with {len(chunk_df)} rows"
                )
                with measure_time("chunk_writing", rows_processed=len(chunk_df)):
                    write_result = self.writer.write(chunk_df)
                    self.logger.debug(f"Chunk write result: {write_result}")

                # Update counters
                total_generated += chunk_size
                batch_count += 1

                self.logger.debug(
                    f"Chunk {batch_count} completed, total generated: {total_generated}"
                )

            # Finalize writer (same as normal processor)
            writer_summary = self.writer.finalize()

            # Generate performance report if requested (same as normal processor)
            perf_summary = None
            if self.perf_report:
                self.logger.debug("Generating performance report")
                perf_summary = get_performance_report()
                self.logger.info("Performance report generated")

            self.logger.info(
                f"Streaming config processing completed. Generated {total_generated} rows "
                f"in {batch_count} chunks."
            )

            return {
                "status": "success",
                "processor_type": "streaming",
                "rows_generated": total_generated,
                "chunks_processed": batch_count,
                "chunk_size": self.chunk_size,
                "batch_size": self.batch_size,
                "writer_summary": writer_summary,
                "performance_report": perf_summary,
                "config_name": self.config.get("metadata", {}).get("name", "unknown"),
            }

        except Exception as e:
            self.logger.error(f"Error during streaming config processing: {e}")
            return {
                "status": "error",
                "processor_type": "streaming",
                "error": str(e),
                "config_name": self.config.get("metadata", {}).get("name", "unknown"),
            }
