"""
File operation utilities for GenXData.
"""

import os


def normalize_writer_type(writer_type):
    """
    Normalize writer type to match the configuration.
    Converts uppercase types like CSV_WRITER to lowercase csv.

    Args:
        writer_type (str): Original writer type

    Returns:
        str: Normalized writer type
    """
    # Remove _WRITER suffix and convert to lowercase
    if writer_type.endswith("_WRITER"):
        writer_type = writer_type[:-7]
    return writer_type.lower()


def ensure_output_dir(output_path):
    """
    Ensure the output directory exists.

    Args:
        output_path (str): Path to the output file
    """
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)


def write_output_files(df, file_writers, debug_mode=False):
    """
    Write output files using the configured writers.

    Args:
        df: DataFrame to write
        file_writers: List of file writer configurations
        debug_mode: Whether to run in debug mode
    """
    from utils.config_utils import load_writers_and_mappings
    from utils.strategy_module import load_strategy_module

    WRITERS, WRITERS_MAPPING = load_writers_and_mappings()

    if len(file_writers) != 0:
        for i in file_writers:
            writer_type = normalize_writer_type(i["type"])

            try:
                # Use the strategy_module util to load the writer module
                writer_module = load_strategy_module(WRITERS[writer_type])
                writer = getattr(writer_module, WRITERS_MAPPING[writer_type])

                # Ensure output directory exists
                if "output_path" in i.get("params", {}):
                    ensure_output_dir(i["params"]["output_path"])

                writer(df, i.get("params", {}))
            except KeyError:
                if debug_mode:
                    raise
            except Exception:
                if debug_mode:
                    raise
