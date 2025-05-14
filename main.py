import pandas as pd
import sys
import logging
import argparse
import os
from pathlib import Path

from utils.json_loader import read_json
from utils.yaml_loader import read_yaml
from utils.intermediate_column import filter_intermediate_columns
from utils.performance_timer import measure_time, get_performance_report

from core.strategy_factory import StrategyFactory

def setup_logging(debug_mode=False):
    """Set up logging configuration based on debug mode"""
    log_level = logging.DEBUG if debug_mode else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("data_generator")

def load_config(config_path):
    """
    Load configuration from either JSON or YAML format based on file extension.
    
    Args:
        config_path (str): Path to the configuration file
        
    Returns:
        dict: Configuration data
    """
    file_extension = os.path.splitext(config_path)[1].lower()
    
    if file_extension in ['.yaml', '.yml']:
        return read_yaml(config_path)
    elif file_extension in ['.json']:
        return read_json(config_path)
    else:
        raise ValueError(f"Unsupported configuration format: {file_extension}. Use .json, .yaml, or .yml")

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
        for ext in ['.json', '.yaml', '.yml']:
            config_files.extend(list(path.glob(f'*{ext}')))
        return [str(f) for f in config_files]
    else:
        raise ValueError(f"Invalid config path: {config_path}")

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
    if writer_type.endswith('_WRITER'):
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

def load_writers_and_mappings():
    """
    Load writer definitions and mappings.
    
    Returns:
        tuple: (writers, mappings) dictionaries
    """
    logger = logging.getLogger("data_generator")    

    writers = read_yaml("configs/WRITERS_IMPLEMENTATIONS.yaml")
    logger.info("Loaded writers from YAML config")
    
    mappings = read_yaml("configs/WRITERS_MAPPING.yaml")
    logger.info("Loaded writer mappings from YAML config")

    return writers, mappings

def process_config(config_path, debug_mode=False, perf_report=False):
    """
    Process a single configuration file.
    
    Args:
        config_path (str): Path to the configuration file
        debug_mode (bool): Whether to run in debug mode
        perf_report (bool): Whether to generate a performance report
        
    Returns:
        pd.DataFrame: Generated data
    """
    logger = logging.getLogger("data_generator")
    logger.info(f"Processing config file: {config_path}")
    
    with measure_time("config_loading"):
        configFile = load_config(config_path)
        columnName = configFile['column_name']
        fileWriter = configFile['file_writer']
        rows = configFile['num_of_rows']
        
        if rows < 100: 
            rows = 100
            logger.warning(f"Row count too low, using minimum of 100 rows")
        
        configs = configFile['configs']
        shuffle_data = configFile.get('shuffle', False)
        
        df = pd.DataFrame(columns=columnName)
        
    logger.info(f"Creating dataframe with {len(columnName)} columns and {rows} rows")
    
    # Initialize the strategy factory
    strategy_factory = StrategyFactory()
    
    with measure_time("data_generation", rows_processed=rows):
        for cur_config in configs:
            for col_name in cur_config['names']:
                
                if cur_config.get('disabled', False) is True:
                    logger.info(f"Skipping disabled column: {col_name}")
                    continue
                    
                # Check if this is an intermediate column (not in final output)
                is_intermediate = cur_config.get('intermediate', False)
                
                if 'strategy' in cur_config.keys() and len(cur_config['strategy']) != 0:
                    strategy_name = cur_config['strategy']['name']
                    logger.info(f"Applying strategy {strategy_name} to column {col_name}")
                    
                    try:
                        with measure_time(f"strategy.{strategy_name}.{col_name}", rows_processed=rows):
                        
                            # Prepare parameters for the strategy
                            params = {
                                'df': df,
                                'col_name': col_name, 
                                'rows': rows,
                                'debug': cur_config.get('debug', debug_mode),
                                'intermediate': is_intermediate,
                                'params': cur_config.get('strategy').get('params', {}),
                                'unique': cur_config.get('strategy').get('unique', False)
                            }

                            # Create and execute the strategy
                            strategy = strategy_factory.create_strategy(strategy_name, **params)
                            df = strategy_factory.execute_strategy(strategy)
                            logger.info(f"Successfully applied {strategy_name} to {col_name}")
                        
                    except Exception as e:
                        logger.error(f"Error applying strategy to {col_name}: {str(e)}")
                        raise
                else:
                    logger.warning(f'No strategy found for {col_name}')
    
    # Apply shuffle if enabled
    if shuffle_data:
        with measure_time("shuffle_data", rows_processed=rows):
            logger.info("Shuffling data")
            df = df.sample(frac=1).reset_index(drop=True)
    
    # Filter out intermediate columns before writing
    with measure_time("filter_intermediate_columns"):
        df = filter_intermediate_columns(df)
    
    # Write output files
    with measure_time("file_writing", rows_processed=rows):
        WRITERS, WRITERS_MAPPING = load_writers_and_mappings()
        
        if len(fileWriter) != 0:
            for i in fileWriter:
                writer_type = normalize_writer_type(i['type'])
                logger.info(f"Writing output using {writer_type} writer")
                
                try:
                    # Use the strategy_module util to load the writer module
                    from utils.strategy_module import load_strategy_module
                    writer_module = load_strategy_module(WRITERS[writer_type])
                    writer = getattr(writer_module, WRITERS_MAPPING[writer_type])
                    
                    # Ensure output directory exists
                    if 'output_path' in i.get('params', {}):
                        ensure_output_dir(i['params']['output_path'])
                    
                    writer(df, i.get('params', {}))
                    logger.info(f"Successfully wrote output with {writer_type} writer")
                except KeyError as e:
                    logger.error(f"Writer type '{writer_type}' not found in configuration")
                    if debug_mode:
                        raise
                except Exception as e:
                    logger.error(f"Error writing output with {writer_type} writer: {str(e)}")
                    if debug_mode:
                        raise
        else:
            logger.warning("No file writers specified in config")
    
    # Output performance report if requested
    if perf_report:
        report = get_performance_report()
        logger.info("\n" + report)
            
    logger.info(f"Successfully processed config file: {config_path}")
    return df

def start(config_path, debug_mode=False, perf_report=False):
    """
    Process one or more configuration files.
    If config_path is a directory, process all config files in it.
    If config_path is a file, process just that file.
    
    Args:
        config_path (str): Path to config file or directory
        debug_mode (bool): Whether to run in debug mode
        perf_report (bool): Whether to generate a performance report
    """
    logger = setup_logging(debug_mode)
    logger.info(f"Starting data generation with config path: {config_path}")
    
    # Get list of config files to process
    config_files = get_config_files(config_path)
    logger.info(f"Found {len(config_files)} configuration files to process")
    
    # Process each config file
    results = {}
    for config_file in config_files:
        try:
            df = process_config(config_file, debug_mode, perf_report)
            results[config_file] = df
        except Exception as e:
            logger.error(f"Error processing config file {config_file}: {str(e)}")
            if debug_mode:
                raise
    
    logger.info("Data generation completed")
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate synthetic data based on configuration.')
    parser.add_argument('config_path', help='Path to configuration file or directory containing config files (.json, .yaml, or .yml)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with verbose logging')
    parser.add_argument('--perf', action='store_true', help='Generate performance report after execution')
    parser.add_argument('--convert', choices=['json', 'yaml'], help='Convert config to specified format instead of running generation')
    args = parser.parse_args()
    
    if args.convert:
        from utils.config_converter import json_to_yaml, yaml_to_json
        
        if args.convert == 'yaml':
            json_to_yaml(args.config_path)
        elif args.convert == 'json':
            yaml_to_json(args.config_path)
    else:
        start(args.config_path, args.debug, args.perf) 