#!/usr/bin/env python3
"""
Command-line utility for converting configuration files between JSON and YAML formats.

Usage:
    python convert_configs.py [--format yaml|json] [--recursive] [--backup] directory1 [directory2 ...]
"""

import argparse
import os
import logging
import sys

from utils.config_converter import convert_configs_in_directory

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("config_converter")

def main():
    parser = argparse.ArgumentParser(description='Convert configuration files between YAML and JSON formats')
    parser.add_argument('directories', nargs='+', help='Directories containing configuration files to convert')
    parser.add_argument('--format', choices=['yaml', 'json'], default='yaml', 
                      help='Target format for conversion (default: yaml)')
    parser.add_argument('--recursive', action='store_true', 
                      help='Recursively search directories for config files')
    parser.add_argument('--backup', action='store_true', 
                      help='Create backup of original files before conversion')
    args = parser.parse_args()
    
    logger = setup_logging()
    
    for directory in args.directories:
        if not os.path.isdir(directory):
            logger.error(f"Directory not found: {directory}")
            continue
            
        logger.info(f"Converting files in {directory} to {args.format} format")
        
        try:
            # Create backups if requested
            if args.backup:
                import shutil
                backup_dir = os.path.join(directory, "backup_configs")
                os.makedirs(backup_dir, exist_ok=True)
                
                if args.format == 'yaml':
                    files = list(os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json'))
                else:
                    files = list(os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.yaml') or f.endswith('.yml'))
                    
                for file in files:
                    if os.path.isfile(file):
                        shutil.copy2(file, os.path.join(backup_dir, os.path.basename(file)))
                        logger.info(f"Created backup of {file}")
            
            # Perform the conversion
            converted_files = convert_configs_in_directory(
                directory, 
                target_format=args.format,
                recursive=args.recursive
            )
            
            logger.info(f"Successfully converted {len(converted_files)} files in {directory}")
            
        except Exception as e:
            logger.error(f"Error converting files in {directory}: {str(e)}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 