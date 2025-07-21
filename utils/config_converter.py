"""
Utility for converting between different configuration formats (JSON/YAML).
"""

import json
import yaml
from pathlib import Path


def json_to_yaml(json_path, yaml_path=None):
    """
    Convert a JSON configuration file to YAML format.

    Args:
        json_path (str): Path to the JSON file
        yaml_path (str, optional): Path for the output YAML file. If not specified,
                                  replaces the .json extension with .yaml

    Returns:
        str: Path to the created YAML file
    """
    try:
        # Determine the output path if not specified
        if not yaml_path:
            yaml_path = str(Path(json_path).with_suffix(".yaml"))

        # Read the JSON file
        with open(json_path, "r") as json_file:
            config_data = json.load(json_file)

        # Write as YAML
        with open(yaml_path, "w") as yaml_file:
            yaml.dump(config_data, yaml_file, default_flow_style=False, sort_keys=False)

        return yaml_path

    except Exception:
        raise


def yaml_to_json(yaml_path, json_path=None):
    """
    Convert a YAML configuration file to JSON format.

    Args:
        yaml_path (str): Path to the YAML file
        json_path (str, optional): Path for the output JSON file. If not specified,
                                  replaces the .yaml extension with .json

    Returns:
        str: Path to the created JSON file
    """
    try:
        # Determine the output path if not specified
        if not json_path:
            json_path = str(Path(yaml_path).with_suffix(".json"))

        # Read the YAML file
        with open(yaml_path, "r") as yaml_file:
            config_data = yaml.safe_load(yaml_file)

        # Write as JSON
        with open(json_path, "w") as json_file:
            json.dump(config_data, json_file, indent=2)

        return json_path

    except Exception:
        raise


def convert_configs_in_directory(directory, target_format="yaml", recursive=False):
    """
    Batch convert configurations in a directory.

    Args:
        directory (str): Directory containing configuration files
        target_format (str): Format to convert to - 'yaml' or 'json'
        recursive (bool): Whether to search directories recursively

    Returns:
        list: Paths to the created files
    """
    try:
        created_files = []
        search_pattern = "**/*.json" if recursive else "*.json"

        if target_format.lower() == "yaml":
            # Convert JSON files to YAML
            for json_file in Path(directory).glob(search_pattern):
                if json_file.is_file():
                    yaml_path = json_to_yaml(str(json_file))
                    created_files.append(yaml_path)

        elif target_format.lower() == "json":
            # Convert YAML files to JSON
            search_pattern = search_pattern.replace("json", "yaml")
            for yaml_file in Path(directory).glob(search_pattern):
                if yaml_file.is_file():
                    json_path = yaml_to_json(str(yaml_file))
                    created_files.append(json_path)
        else:
            raise ValueError(
                f"Unsupported target format: {target_format}. Use 'yaml' or 'json'."
            )

        return created_files

    except Exception:
        raise
