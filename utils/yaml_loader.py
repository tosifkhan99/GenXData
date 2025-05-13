"""
Utility for loading YAML configuration files.
This will eventually replace the JSON configuration.
"""

import yaml
import logging

logger = logging.getLogger("data_generator.yaml_loader")

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
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"YAML file not found: {file_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file {file_path}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading YAML file {file_path}: {str(e)}")
        raise 