"""
Configuration loading utilities for GenXData.
"""

import os
from pathlib import Path


from exceptions.invalid_config_format_exception import InvalidConfigFormatException
from exceptions.invalid_config_path_exception import InvalidConfigPathException
from utils.json_loader import read_json
from utils.yaml_loader import read_yaml


def load_config(config_path):
    """
    Load configuration from either JSON or YAML format based on file extension.

    Args:
        config_path (str): Path to the configuration file

    Returns:
        dict: Configuration data
    """
    file_extension = os.path.splitext(config_path)[1].lower()

    if file_extension in [".yaml", ".yml"]:
        return read_yaml(config_path)
    elif file_extension in [".json"]:
        return read_json(config_path)
    else:
        raise InvalidConfigFormatException(
            f"Unsupported configuration format: {file_extension}. Use .json, .yaml, or .yml"
        )


def get_config_files(config_path):
    """
    Get list of configuration files to process.
    If config_path is a directory, returns all .json, .yaml, and .yml files in it.
    If config_path is a file, returns a list with just that file.

    Args:
        config_path (str): Path to config file or directory

    Returns:
        list: List of configuration file paths
    """
    path = Path(config_path)

    if path.is_file():
        return [str(path)]
    elif path.is_dir():
        config_files = []
        for ext in [".json", ".yaml", ".yml"]:
            config_files.extend(list(path.glob(f"*{ext}")))
        return [str(f) for f in config_files]
    else:
        raise InvalidConfigPathException(
            f"Invalid config path: {config_path}"
        )


def load_writers_and_mappings():
    """
    Load writer definitions and mappings.

    Returns:
        tuple: (writers, mappings) dictionaries
    """

    writers = read_yaml("configs/WRITERS_IMPLEMENTATIONS.yaml")

    mappings = read_yaml("configs/WRITERS_MAPPING.yaml")

    return writers, mappings
