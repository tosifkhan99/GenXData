"""
Utility for loading YAML configuration files.
This will eventually replace the JSON configuration.
"""

import yaml


def read_yaml(file_path):
    """
    Read a YAML file and return its contents as a Python dictionary.

    Args:
        file_path (str): Path to the YAML file to read

    Returns:
        dict: Contents of the YAML file as a Python dictionary

    Raises:
        FileNotFoundError: If the file does not exist
        yaml.YAMLError: If the file is not valid YAML
    """
    try:
        with open(file_path) as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise
    except yaml.YAMLError:
        raise
    except Exception:
        raise
