#!/usr/bin/env python3
"""
Batch Writer - Writes data generation output to multiple batch files
This writer splits large datasets into multiple files for easier processing
"""

import json
import os
from datetime import datetime

import pandas as pd


class BatchWriter:
    """
    Writer that splits data into multiple batch files
    Useful for processing large datasets in chunks
    """

    def __init__(
        self, output_dir="batch_output", file_prefix="batch", file_format="json"
    ):
        self.output_dir = output_dir
        self.file_prefix = file_prefix
        self.file_format = file_format.lower()
        self.batch_count = 0

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

    def write_batch(self, df, batch_info=None):
        """
        Write a DataFrame batch to a file

        Args:
            df (pd.DataFrame): DataFrame to write
            batch_info (dict): Optional metadata about the batch
        """
        try:
            filename = f"{self.file_prefix}_{self.batch_count:04d}.{self.file_format}"
            filepath = os.path.join(self.output_dir, filename)

            if self.file_format == "json":
                # JSON format with metadata
                data = {
                    "batch_info": batch_info or {},
                    "data": df.to_dict(orient="records"),
                    "metadata": {
                        "rows": len(df),
                        "columns": list(df.columns),
                        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                        "timestamp": datetime.now().isoformat(),
                    },
                }

                with open(filepath, "w") as f:
                    json.dump(data, f, indent=2, default=str)

            elif self.file_format == "csv":
                # CSV format
                df.to_csv(filepath, index=False)

                # Write metadata to separate file if batch_info provided
                if batch_info:
                    meta_filename = (
                        f"{self.file_prefix}_{self.batch_count:04d}_meta.json"
                    )
                    meta_filepath = os.path.join(self.output_dir, meta_filename)
                    with open(meta_filepath, "w") as f:
                        json.dump(
                            {
                                "batch_info": batch_info,
                                "metadata": {
                                    "rows": len(df),
                                    "columns": list(df.columns),
                                    "dtypes": {
                                        col: str(dtype)
                                        for col, dtype in df.dtypes.items()
                                    },
                                    "timestamp": datetime.now().isoformat(),
                                },
                            },
                            f,
                            indent=2,
                            default=str,
                        )

            elif self.file_format == "parquet":
                # Parquet format
                df.to_parquet(filepath, index=False)

                # Write metadata to separate file if batch_info provided
                if batch_info:
                    meta_filename = (
                        f"{self.file_prefix}_{self.batch_count:04d}_meta.json"
                    )
                    meta_filepath = os.path.join(self.output_dir, meta_filename)
                    with open(meta_filepath, "w") as f:
                        json.dump(
                            {
                                "batch_info": batch_info,
                                "metadata": {
                                    "rows": len(df),
                                    "columns": list(df.columns),
                                    "dtypes": {
                                        col: str(dtype)
                                        for col, dtype in df.dtypes.items()
                                    },
                                    "timestamp": datetime.now().isoformat(),
                                },
                            },
                            f,
                            indent=2,
                            default=str,
                        )
            else:
                raise ValueError(f"Unsupported file format: {self.file_format}")

            self.batch_count += 1

        except Exception:
            raise

    def get_summary(self):
        """Get a summary of batches written"""
        return {
            "total_batches": self.batch_count,
            "output_directory": self.output_dir,
            "file_format": self.file_format,
            "file_prefix": self.file_prefix,
        }


def read_batch_file(filepath):
    """
    Read and parse a batch file

    Args:
        filepath (str): Path to the batch file

    Returns:
        tuple: (DataFrame, batch_info, metadata) for JSON format
        DataFrame: for CSV/Parquet format
    """
    file_ext = os.path.splitext(filepath)[1].lower()

    if file_ext == ".json":
        with open(filepath) as f:
            data = json.load(f)

        # Extract components
        batch_info = data.get("batch_info", {})
        records = data.get("data", [])
        metadata = data.get("metadata", {})

        # Convert back to DataFrame
        df = pd.DataFrame(records)

        return df, batch_info, metadata

    elif file_ext == ".csv":
        df = pd.read_csv(filepath)

        # Try to read metadata file
        meta_filepath = filepath.replace(".csv", "_meta.json")
        batch_info, metadata = {}, {}
        if os.path.exists(meta_filepath):
            with open(meta_filepath) as f:
                meta_data = json.load(f)
                batch_info = meta_data.get("batch_info", {})
                metadata = meta_data.get("metadata", {})

        return df, batch_info, metadata

    elif file_ext == ".parquet":
        df = pd.read_parquet(filepath)

        # Try to read metadata file
        meta_filepath = filepath.replace(".parquet", "_meta.json")
        batch_info, metadata = {}, {}
        if os.path.exists(meta_filepath):
            with open(meta_filepath) as f:
                meta_data = json.load(f)
                batch_info = meta_data.get("batch_info", {})
                metadata = meta_data.get("metadata", {})

        return df, batch_info, metadata
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")


if __name__ == "__main__":
    # Example usage
    print("Testing BatchWriter...")

    # Create test data
    test_data = {
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "department": ["Engineering", "HR", "Sales", "Marketing", "Engineering"],
        "salary": [75000, 65000, 80000, 70000, 85000],
    }
    df = pd.DataFrame(test_data)

    # Test JSON format
    writer = BatchWriter(output_dir="test_batch_output", file_format="json")

    batch_info = {
        "batch_index": 0,
        "batch_size": 5,
        "total_batches": 1,
        "config_name": "Test Config",
    }

    writer.write_batch(df, batch_info)

    # Test CSV format
    csv_writer = BatchWriter(output_dir="test_batch_output", file_format="csv")
    csv_writer.write_batch(df, batch_info)

    # Print summary
    summary = writer.get_summary()
    print(f"Summary: {summary}")

    # Test reading the file back
    json_file = os.path.join(writer.output_dir, "batch_0000.json")
    if os.path.exists(json_file):
        df_read, batch_info_read, metadata_read = read_batch_file(json_file)
        print(f"Read back DataFrame with {len(df_read)} rows")
        print(f"Batch info: {batch_info_read}")
        print("✓ JSON round-trip test successful!")

    print(f"Check output files in: {writer.output_dir}")
