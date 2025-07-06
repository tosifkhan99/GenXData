"""
Core data processing functionality for GenXData.
"""
import pandas as pd
import configs.GENERATOR_SETTINGS as SETTINGS
from utils.intermediate_column import filter_intermediate_columns
from utils.performance_timer import measure_time, get_performance_report
from utils.file_utils import write_output_files
from core.strategy_factory import StrategyFactory


def process_config(config_file, debug_mode=False, perf_report=False):
    """
    Process a single configuration file.
    
    Args:
        config_file (dict): Configuration data
        debug_mode (bool): Whether to run in debug mode
        perf_report (bool): Whether to generate a performance report
        
    Returns:
        pd.DataFrame: Generated data
    """
    
    column_name = config_file['column_name']
    file_writer = config_file['file_writer']
    rows = config_file['num_of_rows']
    write_output = config_file.get('write_output', SETTINGS.WRITE_OUTPUT)

    if rows < SETTINGS.MINIMUM_ROWS_ALLOWED: 
        rows = SETTINGS.MINIMUM_ROWS_ALLOWED

    configs = config_file['configs']
    shuffle_data = config_file.get('shuffle', SETTINGS.SHUFFLE)
    
    # Create DataFrame with the correct number of rows
    
    # Initialize the strategy factory
    strategy_factory = StrategyFactory()
    
    df = pd.DataFrame(index=range(rows), columns=column_name)
    
    with measure_time("data_generation", rows_processed=rows):
        for cur_config in configs:
            for col_name in cur_config['names']:
                
                if cur_config.get('disabled', False) is True:
                    continue
                    
                # Check if this is an intermediate column (not in final output)
                is_intermediate = cur_config.get('intermediate', False)
                
                if 'strategy' in cur_config.keys() and len(cur_config['strategy']) != 0:
                    strategy_name = cur_config['strategy']['name']
                    
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
                        
                    except Exception as e:
                        raise
    
    # Apply shuffle if enabled
    if shuffle_data:
        with measure_time("shuffle_data", rows_processed=rows):
            df = df.sample(frac=1).reset_index(drop=True)
    
    # Filter out intermediate columns before writing
    with measure_time("filter_intermediate_columns"):
        df = filter_intermediate_columns(df)
    
    # Write output files
    if write_output:
        with measure_time("file_writing", rows_processed=rows):
            write_output_files(df, file_writer, debug_mode)
    
    # Output performance report if requested
    if perf_report:
        report = get_performance_report()
            
    return df 