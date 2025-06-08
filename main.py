import pandas as pd
import sys
import logging
import argparse
import os
from pathlib import Path
import copy
 
import configs.GENERATOR_SETTINGS as SETTINGS
from utils.json_loader import read_json
from utils.yaml_loader import read_yaml
from utils.intermediate_column import filter_intermediate_columns
from utils.performance_timer import measure_time, get_performance_report

from core.strategy_factory import StrategyFactory

STATE_DEPENDENT_STRATEGIES = {
    'SERIES_STRATEGY': ['start'],
    'INCREMENTAL_STRATEGY': ['start'],
    'TIME_RANGE_STRATEGY': ['start_time', 'end_time'],
    'DATE_RANGE_STRATEGY': ['start_date', 'end_date'],
    'TIME_INCREMENT_STRATEGY': ['start_time', 'end_time'],
    'DATE_INCREMENT_STRATEGY': ['start_date', 'end_date'],
    'TIME_INCREMENT_STRATEGY': ['start_time', 'end_time'],
}

def setup_logging(debug_mode=False, logging_enabled=True):
    """Set up logging configuration based on debug mode and enabled status"""
    logger = logging.getLogger("data_generator")

    if not logging_enabled:
        # If logging is disabled, add a NullHandler to this specific logger
        # and prevent it from propagating messages to higher-level loggers.
        logger.handlers = [logging.NullHandler()] # Clear existing and add NullHandler
        logger.propagate = False
    else:
        # If logging is enabled, configure basicConfig.
        # debug_mode controls the log level (DEBUG or INFO).
        log_level = logging.DEBUG if debug_mode else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            # Consider adding force=True if Python >= 3.8 and basicConfig might be called multiple times
            # or if the root logger has already been configured.
        )
    return logger

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
    
def get_batches(batch_size, rows):
    full_batches = rows // batch_size
    remainder = rows % batch_size
    batches = [batch_size] * full_batches

    if remainder:
        if remainder <= 100 and batches:
            batches[-1] += remainder
        else:
            batches.append(remainder)
    
    return batches

def process_config(configFile, debug_mode=False, perf_report=False):
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
    logger.debug(f"Processing config file: {configFile}")
    columnName = configFile['column_name']
    fileWriter = configFile['file_writer']
    rows = configFile['num_of_rows']
    write_output = configFile.get('write_output', SETTINGS.WRITE_OUTPUT)

    if rows < SETTINGS.MINIMUM_ROWS_ALLOWED: 
        rows = SETTINGS.MINIMUM_ROWS_ALLOWED
        logger.warning(f"Row count too low, using minimum of {SETTINGS.MINIMUM_ROWS_ALLOWED} rows")
    

    configs = configFile['configs']
    shuffle_data = configFile.get('shuffle', SETTINGS.SHUFFLE)
    # Create DataFrame with the correct number of rows
    logger.info(f"Creating dataframe with {len(columnName)} columns and {rows} rows")
    
    # Initialize the strategy factory
    strategy_factory = StrategyFactory()
    
    df = pd.DataFrame(index=range(rows), columns=columnName)
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
                            strategy_params = cur_config.get('strategy').get('params', {})
                            
                            # Add mask to strategy params if it exists at the top level
                            if 'mask' in cur_config:
                                strategy_params['mask'] = cur_config['mask']
                            
                            params = {
                                'df': df,
                                'col_name': col_name, 
                                'rows': rows,
                                'debug': cur_config.get('debug', SETTINGS.DEBUG),
                                'intermediate': is_intermediate,
                                'params': strategy_params,
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
    if write_output:
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
            
    logger.info(f"Processed config file: {configFile['metadata']['name']}")
    return df

def start(config, debug_mode=SETTINGS.DEBUG, perf_report=SETTINGS.PERF_REPORT, logging_enabled=True, stream=None, batch=None):
    """
    Process one or more configuration files.
    If config is a directory, process all config files in it.
    If config is a file, process just that file.
    If config is a dict, process just that config.
    
    Args:
        config (str or dict): Path to config file/directory or a config dictionary.
        debug_mode (bool): Whether to run in debug mode (sets log level to DEBUG if logging_enabled).
        perf_report (bool): Whether to generate a performance report.
        logging_enabled (bool): Whether logging should be enabled for the application.
        stream (str): Path to streaming config file containing AMQP connection details and streaming settings.
        batch (str): Path to batch config file containing batch writing settings.
    """
    logger = setup_logging(debug_mode, logging_enabled=logging_enabled)

    # Log the initial state, this will be silent if logging_enabled is False
    logger.debug(f"Starting data generation. Config: {config}, Debug mode: {debug_mode}, Perf report: {perf_report}, Logging enabled: {logging_enabled}")
    
    if isinstance(config, str):
        # Get list of config files to process
        config_files = get_config_files(config)
        logger.info(f"Found {len(config_files)} configuration files to process")
    else:
        config_files = [config]
    
    # Process each config file
    results = {}
    if (stream or batch) and len(config_files) > 1:
        # todo: replace with proper error handling
        raise ValueError("Streaming and batch modes are not supported for multiple config files")
    
    if stream and batch:
        raise ValueError("Streaming and batch modes are not supported together")

    for config_file in config_files:
        try:
            if isinstance(config_file, str):
                configFile = load_config(config_file)
                logger.info(f"Loaded config file: {config_file}")
            else:
                configFile = config_file
                
            if stream:
                # Initialize state tracking for the entire streaming session
                strategy_states = {}
                stream_config = load_config(stream)
                
                # Validate streaming configuration
                if 'amqp' not in stream_config:
                    raise ValueError("Streaming config must contain 'amqp' section with connection details")
                
                amqp_config = stream_config['amqp']
                streaming_config = stream_config.get('streaming', {})
                
                # Required AMQP settings
                if 'url' not in amqp_config or 'queue' not in amqp_config:
                    raise ValueError("AMQP config must contain 'url' and 'queue' settings")
                
                # Get batch size from streaming config or use default
                batch_size = streaming_config.get('batch_size', SETTINGS.STREAM_BATCH_SIZE)
                batches = get_batches(batch_size, configFile['num_of_rows'])
                
                # Initialize AMQP producer (streaming mode only)
                amqp_producer = None
                try:
                    from amqp.producer import AMQPProducer
                    amqp_producer = AMQPProducer(amqp_config['url'], amqp_config['queue'])
                    logger.info(f"AMQP streaming enabled - URL: {amqp_config['url']}, Queue: {amqp_config['queue']}")
                except ImportError as e:
                    raise ValueError(f"AMQP library not available. Install python-qpid-proton: {e}")
                except ConnectionError as e:
                    raise ValueError(f"Could not connect to AMQP broker: {e}")
                
                for batch_index, batch_size in enumerate(batches):
                    logger.info(f"Processing batch {batch_index + 1}/{len(batches)} with {batch_size} rows")
                    
                    # Pre-calculate and modify config for this batch
                    batch_config = prepare_batch_config(configFile, batch_size, batch_index, strategy_states)
                    
                    df = process_config(batch_config, debug_mode, perf_report)
                    
                    # Send batch to AMQP queue if producer is available
                    if amqp_producer:
                        batch_info = {
                            'batch_index': batch_index,
                            'batch_size': batch_size,
                            'total_batches': len(batches),
                            'config_name': configFile.get('metadata', {}).get('name', 'unknown'),
                            'timestamp': pd.Timestamp.now().isoformat()
                        }
                        
                        # Include additional metadata if configured
                        if streaming_config.get('include_metadata', True):
                            batch_info['streaming_config'] = streaming_config
                        
                        amqp_producer.send_dataframe(df, batch_info)
                        logger.info(f"Sent batch {batch_index + 1} to AMQP queue")
                
                # Clean up AMQP producer
                if amqp_producer:
                    amqp_producer.close_connection()
                    logger.info("AMQP streaming completed successfully")
                
                # For streaming, return the last batch as the result
                results['df'] = df.to_dict(orient='records') if 'df' in locals() else []
            elif batch:
                # Initialize state tracking for the entire batch session
                strategy_states = {}
                batch_config = load_config(batch)
                
                # Validate batch configuration
                if 'batch_writer' not in batch_config:
                    raise ValueError("Batch config must contain 'batch_writer' section with writer settings")
                
                writer_config = batch_config['batch_writer']
                
                # Required batch writer settings
                if 'output_dir' not in writer_config:
                    raise ValueError("Batch writer config must contain 'output_dir' setting")
                
                # Get batch size from batch config or use default
                batch_size = writer_config.get('batch_size', SETTINGS.STREAM_BATCH_SIZE)
                batches = get_batches(batch_size, configFile['num_of_rows'])
                
                # Initialize batch writer
                from writers.batch_writer import BatchWriter
                batch_writer = BatchWriter(
                    output_dir=writer_config['output_dir'],
                    file_prefix=writer_config.get('file_prefix', 'batch'),
                    file_format=writer_config.get('file_format', 'json')
                )
                logger.info(f"Batch mode enabled - Output: {writer_config['output_dir']}, Format: {writer_config.get('file_format', 'json')}")
                
                for batch_index, batch_size in enumerate(batches):
                    logger.info(f"Processing batch {batch_index + 1}/{len(batches)} with {batch_size} rows")
                    
                    # Pre-calculate and modify config for this batch
                    batch_config_item = prepare_batch_config(configFile, batch_size, batch_index, strategy_states)
                    
                    df = process_config(batch_config_item, debug_mode, perf_report)
                    
                    # Write batch to file
                    batch_info = {
                        'batch_index': batch_index,
                        'batch_size': batch_size,
                        'total_batches': len(batches),
                        'config_name': configFile.get('metadata', {}).get('name', 'unknown'),
                        'timestamp': pd.Timestamp.now().isoformat()
                    }
                    
                    batch_writer.write_batch(df, batch_info)
                    logger.info(f"Wrote batch {batch_index + 1} to file")
                
                # Get summary
                summary = batch_writer.get_summary()
                logger.info(f"Batch processing completed: {summary}")
                
                # For batch mode, return the last batch as the result
                results['df'] = df.to_dict(orient='records') if 'df' in locals() else []
            else:
                df = process_config(configFile, debug_mode, perf_report)

            results['df'] = df.to_dict(orient='records')
        except Exception as e:
            logger.error(f"Error processing config file {str(e)}")
            if debug_mode:
                raise
    
    logger.info("Data generation completed")
    return results

def prepare_batch_config(original_config, batch_size, batch_index, strategy_states):
    """
    Prepare config for a specific batch, adjusting parameters for state-dependent strategies.
    """
    batch_config = copy.deepcopy(original_config)
    batch_config['num_of_rows'] = batch_size
    batch_config['write_output'] = False
    
    # Calculate cumulative rows processed so far
    cumulative_rows = sum(get_batches(SETTINGS.STREAM_BATCH_SIZE, original_config['num_of_rows'])[:batch_index])
    
    # Adjust parameters for state-dependent strategies
    for config_item in batch_config['configs']:
        strategy_name = config_item['strategy']['name']
        
        if strategy_name in STATE_DEPENDENT_STRATEGIES:
            for col_name in config_item['names']:
                adjust_strategy_params(config_item, col_name, cumulative_rows, strategy_states)
    
    return batch_config

def adjust_strategy_params(config_item, col_name, cumulative_rows, strategy_states):
    """
    Adjust strategy parameters based on previous batches.
    """
    strategy_name = config_item['strategy']['name']
    params = config_item['strategy']['params']
    
    if strategy_name == 'SERIES_STRATEGY':
        # For series strategy, adjust the start value
        original_start = params.get('start', 1)
        step = params.get('step', 1)
        
        # Calculate new start value based on cumulative rows
        new_start = original_start + (cumulative_rows * step)
        params['start'] = new_start
        
        # Store state for potential future use
        strategy_states[f"{strategy_name}_{col_name}"] = {
            'last_value': new_start + (config_item.get('batch_size', 100) * step) - step
        }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate synthetic data based on configuration.')
    parser.add_argument('config_path', help='Path to configuration file or directory containing config files (.json, .yaml, or .yml)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with verbose logging (sets log level to DEBUG if logging is enabled)')
    parser.add_argument('--perf', action='store_true', help='Generate performance report after execution')
    parser.add_argument('--convert', choices=['json', 'yaml'], help='Convert config to specified format instead of running generation')
    parser.add_argument('--disable-logging', action='store_true', help='Disable logging output from this application')
    parser.add_argument('--stream', type=str, metavar='CONFIG_FILE', help='Enable streaming mode with AMQP configuration file (YAML/JSON format)')
    parser.add_argument('--batch', type=str, metavar='CONFIG_FILE', help='Enable batch mode - write output to multiple batch files (YAML/JSON format)')
    
    args = parser.parse_args()
    
    if args.convert:
        from utils.config_converter import json_to_yaml, yaml_to_json
        
        if args.convert == 'yaml':
            json_to_yaml(args.config_path)
        elif args.convert == 'json':
            yaml_to_json(args.config_path)
    else:
        start(args.config_path, args.debug, args.perf, logging_enabled=not args.disable_logging, stream=args.stream, batch=args.batch) 