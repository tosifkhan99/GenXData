"""
File writer implementation for GenXData.

Handles writing DataFrames to various file formats (CSV, JSON, Excel, etc.).
"""

from typing import Dict, Any
import pandas as pd

from .base_writer import BaseWriter
from utils.file_utils import write_output_files
from utils.logging import Logger


class FileWriter(BaseWriter):
    """
    Writer implementation for file-based outputs.

    Supports various file formats through the existing file_utils module.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the file writer.

        Args:
            config: File writer configuration containing file_writer settings
        """
        super().__init__(config)
        self.logger = Logger.get_logger("file_writer")
        self.files_written = []
        self.total_rows_written = 0

        # Validate configuration
        self.validate_config()

        self.logger.debug(f"FileWriter initialized with config: {config}")

    def validate_config(self) -> bool:
        """
        Validate file writer configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        super().validate_config()

        if "file_writer" not in self.config:
            raise ValueError("file_writer configuration is required")

        file_writer_config = self.config["file_writer"]
        if not isinstance(file_writer_config, list) or len(file_writer_config) == 0:
            raise ValueError("file_writer must be a non-empty list")

        # Validate each file writer configuration
        for writer_config in file_writer_config:
            if "type" not in writer_config:
                raise ValueError("Each file writer must have a 'type' field")

            if "params" not in writer_config:
                raise ValueError("Each file writer must have a 'params' field")

        return True

    def write(
        self, df: pd.DataFrame, metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Write DataFrame to file(s) based on configuration.

        Args:
            df: DataFrame to write
            metadata: Optional metadata (batch info, etc.)

        Returns:
            Dictionary with write operation results
        """
        if df.empty:
            self.logger.warning("Received empty DataFrame, skipping write")
            return {"status": "skipped", "reason": "empty_dataframe"}

        self.logger.info(
            f"Writing DataFrame with {len(df)} rows and {len(df.columns)} columns"
        )

        try:
            # Use existing file_utils functionality
            write_result = write_output_files(df, self.config["file_writer"])

            # Track written files and rows
            self.total_rows_written += len(df)

            # Extract file information from the result if available
            if isinstance(write_result, dict) and "files" in write_result:
                self.files_written.extend(write_result["files"])
            else:
                # Fallback: try to determine files from config
                for writer_config in self.config["file_writer"]:
                    if (
                        "params" in writer_config
                        and "output_path" in writer_config["params"]
                    ):
                        self.files_written.append(
                            writer_config["params"]["output_path"]
                        )

            self.logger.info(f"Successfully wrote {len(df)} rows to file(s)")

            return {
                "status": "success",
                "rows_written": len(df),
                "files_written": len(self.files_written),
                "metadata": metadata,
            }

        except Exception as e:
            self.logger.error(f"Error writing DataFrame to file: {e}")
            return {"status": "error", "error": str(e), "metadata": metadata}

    def finalize(self) -> Dict[str, Any]:
        """
        Finalize file writing operations.

        Returns:
            Dictionary with summary of all write operations
        """
        self.logger.info(
            f"Finalizing file writer. Total rows written: {self.total_rows_written}"
        )

        summary = {
            "total_rows_written": self.total_rows_written,
            "total_files_written": len(set(self.files_written)),  # Unique files
            "files": list(set(self.files_written)),
            "writer_type": "file",
        }

        self.logger.debug(f"File writer summary: {summary}")
        return summary
