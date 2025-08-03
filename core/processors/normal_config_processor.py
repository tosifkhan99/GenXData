"""
Normal config processor for GenXData.

Handles traditional data generation where all data is generated at once
and then written to output. This replaces the functionality from process_config.py.
"""

from typing import Any

from utils.performance_timer import get_performance_report, measure_time

from .base_config_processor import BaseConfigProcessor


class NormalConfigProcessor(BaseConfigProcessor):
    """
    Processor for normal (non-streaming) data generation.

    Generates all data at once, applies transformations, and writes the complete
    dataset to the output destination.
    """

    def __init__(
        self, config: dict[str, Any], writer, perf_report: bool = False
    ):
        """
        Initialize the normal config processor.

        Args:
            config: Configuration dictionary
            writer: Writer instance for output
            perf_report: Whether to generate performance report
        """
        super().__init__(config, writer)
        self.perf_report = perf_report

        self.logger.info(f"NormalConfigProcessor initialized for {self.rows} rows")

    def process(self) -> dict[str, Any]:
        """
        Process the configuration using normal (all-at-once) generation.

        Returns:
            Dictionary with processing results including the generated DataFrame
        """
        self.logger.info("Starting normal config processing")

        try:
            # Validate configuration
            self.validate_config()

            # Create base DataFrame
            df = self.create_base_dataframe()

            # Process all column strategies
            df = self.process_column_strategies(df)

            # Apply shuffle if enabled
            df = self.apply_shuffle(df)

            # Filter out intermediate columns
            df = self.filter_intermediate_columns(df)

            # Write output using the writer
            self.logger.info("Writing output using configured writer")
            with measure_time("file_writing", rows_processed=len(df)):
                write_result = self.writer.write(df)
                self.logger.info(f"Write result: {write_result}")

            # Finalize writer
            writer_summary = self.writer.finalize()

            # Generate performance report if requested
            perf_summary = None
            if self.perf_report:
                self.logger.debug("Generating performance report")
                perf_summary = get_performance_report()
                self.logger.info("Performance report generated")

            self.logger.info(
                f"Normal config processing completed. Generated {len(df)} rows "
                f"with {len(df.columns)} columns."
            )

            return {
                "status": "success",
                "processor_type": "normal",
                "rows_generated": len(df),
                "columns_generated": len(df.columns),
                "column_names": list(df.columns),
                "df": df,
                "writer_summary": writer_summary,
                "performance_report": perf_summary,
                "config_name": self.config.get("metadata", {}).get("name", "unknown"),
            }

        except Exception as e:
            self.logger.error(f"Error during normal config processing: {e}")
            return {
                "status": "error",
                "processor_type": "normal",
                "error": str(e),
                "config_name": self.config.get("metadata", {}).get("name", "unknown"),
            }
