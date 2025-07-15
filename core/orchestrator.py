"""
Main orchestrator for GenXData processing.
"""
import pandas as pd

import configs.GENERATOR_SETTINGS as SETTINGS
from exceptions.config_exception import ConfigException
from exceptions.invalid_running_mode_exception import InvalidRunningModeException
from exceptions.param_exceptions import InvalidConfigParamException
from exceptions.strategy_exceptions import UnsupportedStrategyException
from utils.config_utils import load_config, get_config_files
from core.streaming import process_streaming_config, process_batch_config
from core.error.error_context import ErrorContextBuilder
from utils.logging import Logger
from core.error.error import ErrorHandler
import configs.GENERATOR_SETTINGS as SETTINGS
from utils.intermediate_column import filter_intermediate_columns
from utils.performance_timer import measure_time, get_performance_report
from utils.file_utils import write_output_files
from core.strategy_factory import StrategyFactory
from utils.generator_utils import validate_generator_config
from exceptions.base_exception import ErrorSeverity


class DataOrchestrator:
    """
    Orchestrator class for data generation processing.
    """
    def __init__(self, config, perf_report=SETTINGS.PERF_REPORT, stream=None, batch=None, log_level=None):
        """
        Initialize the DataOrchestrator.
        
        Args:
            config (dict): Configuration dictionary
            perf_report (bool): Whether to generate performance report
            stream (str): Path to streaming config file
            batch (str): Path to batch config file
        """
        self.config = config
        self.perf_report = perf_report
        self.stream = stream
        self.batch = batch
        self.log_level = log_level
        self.logger = Logger.get_logger(__name__, log_level)
        self.error_handler = ErrorHandler(self.logger)

    def run(self):
        """
        Run the data generation process.
        
        Returns:
            dict: Processing results
        """
        self.logger.info(f"Starting data generation with config")
        self.logger.info('''
  _____           __   _______        _        
 / ____|          \ \ / /  __ \      | |       
| |  __  ___ _ __  \ V /| |  | | __ _| |_ __ _ 
| | |_ |/ _ \ '_ \  > < | |  | |/ _` | __/ _` |
| |__| |  __/ | | |/ . \| |__| | (_| | || (_| |
 \_____|\___|_| |_/_/ \_\_____/ \__,_|\__\__,_|
                                               
''')

        self.logger.debug(f"Config: {self.config}")
        self.logger.debug(f"Perf report: {self.perf_report}")
        self.logger.debug(f"Stream: {self.stream}")
        self.logger.debug(f"Batch: {self.batch}")
        self.logger.debug(f"Log level: {self.log_level}")
        
        try:
            if self.stream and self.batch:
                raise InvalidRunningModeException(context=ErrorContextBuilder().with_config(self.config).with_stream(self.stream).with_batch(self.batch).build())

            # todo: do we need this ?
            if isinstance(self.config, str):
                config_files = get_config_files(self.config)
            else:
                config_files = [self.config]
    
            if self.stream:
                self.logger.info("Processing streaming config")
                stream_config = load_config(self.stream)
                return process_streaming_config(self.config, stream_config, self.perf_report)
            elif self.batch:
                self.logger.info("Processing batch config")
                batch_config = load_config(self.batch)
                return process_batch_config(self.config, batch_config, self.perf_report)
            else:
                self.logger.info("Processing config")
                df = self.process_config()
                return {'df': df.to_dict(orient='records')}
                
        except Exception as e:
            self.error_handler.add_error(e)

        finally:
            # Centralized error reporting with severity-based formatting
            if self.error_handler.has_errors():
                self.error_handler.generate_error_report()
            
            # Only fail if there are critical errors
            if self.error_handler.has_critical_errors():
                self.logger.critical("Critical errors detected. Process cannot continue.")
                return None
            elif self.error_handler.has_errors():
                self.logger.warning(f"Process completed with {len(self.error_handler.get_errors())} non-critical errors.")
            else:
                self.logger.info("Process completed successfully with no errors.")
                
        return df


    def process_config(self):
        """
        Process a single configuration file.
        
        Args:
            config_file (dict): Configuration data
            perf_report (bool): Whether to generate a performance report
            
        Returns:
            pd.DataFrame: Generated data
        """
        
        column_name = self.config['column_name']
        file_writer = self.config['file_writer']
        rows = self.config['num_of_rows']
        write_output = self.config.get('write_output', SETTINGS.WRITE_OUTPUT)

        if rows < SETTINGS.MINIMUM_ROWS_ALLOWED: 
            rows = SETTINGS.MINIMUM_ROWS_ALLOWED

        configs = self.config['configs']
        shuffle_data = self.config.get('shuffle', SETTINGS.SHUFFLE)
        

        self.logger.debug(f"Column name: {column_name}")
        self.logger.debug(f"File writer: {file_writer}")
        self.logger.debug(f"Rows: {rows}")
        self.logger.debug(f"Write output: {write_output}")
        self.logger.debug(f"Shuffle data: {shuffle_data}")
        

        

        # Create DataFrame with the correct number of rows
        df = pd.DataFrame(index=range(rows), columns=column_name)
        
        # Initialize the strategy factory
        strategy_factory = StrategyFactory(self.logger)
        
        # Validate the full generator configuration
        try:
            validate_generator_config(self.config)
        except InvalidConfigParamException as e:
            self.error_handler.add_error(e)
        
        with measure_time("data_generation", rows_processed=rows):
                
            for cur_config in configs:
                self.logger.debug(f"Processing config: {cur_config}")

                for col_name in cur_config['names']:
                    self.logger.debug(f"Processing column: {col_name}")
                    
                    if cur_config.get('disabled', False) is True:
                        self.logger.debug(f"Column {col_name} is disabled")
                        continue

                    # Check if this is an intermediate column (not in final output)
                    is_intermediate = cur_config.get('intermediate', False)
                    self.logger.debug(f"Is intermediate: {is_intermediate}")
                    
                    strategy_name = cur_config['strategy']['name']
                    self.logger.debug(f"Strategy name: {strategy_name}")
                    
                    try:
                        with measure_time(f"strategy.{strategy_name}.{col_name}", rows_processed=rows):
                            # Prepare parameters for the strategy - define strategy_params first
                            strategy_params = cur_config.get('strategy').get('params', {})
                            self.logger.debug(f"Strategy params: {strategy_params}")
                            
                            # Add mask to strategy params if it exists at the top level
                            if 'mask' in cur_config:
                                strategy_params['mask'] = cur_config['mask']

                            params = {
                                'df': df,
                                'col_name': col_name, 
                                'rows': rows,
                                'intermediate': is_intermediate,
                                'params': strategy_params,
                                'unique': cur_config.get('strategy').get('unique', False)
                            }

                            # Create and execute the strategy
                            try:
                                strategy = strategy_factory.create_strategy(strategy_name, **params)
                                self.logger.debug(f"Strategy Created: {strategy}")

                                df = strategy_factory.execute_strategy(strategy)
                                self.logger.debug(f"DF: {df.head(10)}")

                            except UnsupportedStrategyException as e:
                                self.error_handler.add_error(e)

                    except ConfigException as e:
                        self.error_handler.add_error(e)
                        raise

                    except Exception as e:
                        self.error_handler.add_error(e)
                        raise
        
        # Apply shuffle if enabled
        if shuffle_data:
            self.logger.debug("Shuffling data")
            with measure_time("shuffle_data", rows_processed=rows):
                df = df.sample(frac=1).reset_index(drop=True)
        
        # Filter out intermediate columns before writing
        self.logger.debug("Filtering intermediate columns")
        with measure_time("filter_intermediate_columns"):
            df = filter_intermediate_columns(df)
        
        # Write output files
        if write_output:
            self.logger.debug("Writing output files")
            with measure_time("file_writing", rows_processed=rows):
                write_output_files(df, file_writer)
        
        # Output performance report if requested
        if self.perf_report:
            self.logger.debug("Generating performance report")
            report = get_performance_report()
                
        return df 
