"""
Utility for converting between different configuration formats (JSON/YAML).
"""

import json
import yaml
import logging
import os
from pathlib import Path

logger = logging.getLogger("data_generator.config_converter")

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
            yaml_path = str(Path(json_path).with_suffix('.yaml'))
            
        logger.info(f"Converting JSON config {json_path} to YAML format {yaml_path}")
        
        # Read the JSON file
        with open(json_path, 'r') as json_file:
            config_data = json.load(json_file)
            
        # Write as YAML
        with open(yaml_path, 'w') as yaml_file:
            yaml.dump(config_data, yaml_file, default_flow_style=False, sort_keys=False)
            
        logger.info(f"Successfully converted JSON to YAML: {yaml_path}")
        return yaml_path
        
    except Exception as e:
        logger.error(f"Error converting JSON to YAML: {str(e)}")
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
            json_path = str(Path(yaml_path).with_suffix('.json'))
            
        logger.info(f"Converting YAML config {yaml_path} to JSON format {json_path}")
        
        # Read the YAML file
        with open(yaml_path, 'r') as yaml_file:
            config_data = yaml.safe_load(yaml_file)
            
        # Write as JSON
        with open(json_path, 'w') as json_file:
            json.dump(config_data, json_file, indent=2)
            
        logger.info(f"Successfully converted YAML to JSON: {json_path}")
        return json_path
        
    except Exception as e:
        logger.error(f"Error converting YAML to JSON: {str(e)}")
        raise

def convert_configs_in_directory(directory, target_format='yaml', recursive=False):
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
        logger.info(f"Batch converting configs in {directory} to {target_format} format")
        
        created_files = []
        search_pattern = '**/*.json' if recursive else '*.json'
        
        if target_format.lower() == 'yaml':
            # Convert JSON files to YAML
            for json_file in Path(directory).glob(search_pattern):
                if json_file.is_file():
                    yaml_path = json_to_yaml(str(json_file))
                    created_files.append(yaml_path)
                    
        elif target_format.lower() == 'json':
            # Convert YAML files to JSON
            search_pattern = search_pattern.replace('json', 'yaml')
            for yaml_file in Path(directory).glob(search_pattern):
                if yaml_file.is_file():
                    json_path = yaml_to_json(str(yaml_file))
                    created_files.append(json_path)
        else:
            raise ValueError(f"Unsupported target format: {target_format}. Use 'yaml' or 'json'.")
            
        logger.info(f"Converted {len(created_files)} files to {target_format} format")
        return created_files
        
    except Exception as e:
        logger.error(f"Error in batch conversion: {str(e)}")
        raise 