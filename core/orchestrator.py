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
from core.processor.process_config import process_config


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
                return process_streaming_config(self.config, stream_config, self.error_handler, self.perf_report)
            elif self.batch:
                self.logger.info("Processing batch config")
                batch_config = load_config(self.batch)
                return process_batch_config(self.config, batch_config, self.error_handler, self.perf_report)
            else:
                self.logger.info("Processing config")
                df = process_config(self.config, self.perf_report, self.error_handler)
                return {'df': df.to_dict(orient='records')}
                
        except Exception as e:
            self.error_handler.add_error(e)

        finally:
            # Centralized error reporting with severity-based formatting
            if self.error_handler.has_errors():
                self.logger.error("========== Orchestrator completed with errors ==========")
                self.error_handler.generate_error_report()
            
            # Only fail if there are critical errors
            if self.error_handler.has_critical_errors():
                self.logger.error("========== Orchestrator completed with critical errors ==========")
                self.logger.critical("Critical errors detected. Process cannot continue.")
                return None
            else:
                self.logger.info("========== Orchestrator completed successfully with no errors. ==========")
                
        return df
