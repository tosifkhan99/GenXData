import pandas as pd
import configs.GENERATOR_SETTINGS as SETTINGS
from core.strategy_factory import StrategyFactory
from exceptions.config_exception import ConfigException
from exceptions.param_exceptions import InvalidConfigParamException
from exceptions.strategy_exceptions import UnsupportedStrategyException
from utils.generator_utils import validate_generator_config
from utils.intermediate_column import filter_intermediate_columns
from utils.logging import Logger
from utils.file_utils import write_output_files
from utils.performance_timer import get_performance_report, measure_time

# Initialize logger for process_config
logger = Logger.get_logger("processor")

def process_config(config, perf_report, error_handler):
        """
        Process a single configuration file.
        
        Args:
            config_file (dict): Configuration data
            perf_report (bool): Whether to generate a performance report
            error_handler: Error handler instance for collecting errors
            
        Returns:
            pd.DataFrame: Generated data
        """
        
        column_name = config['column_name']
        file_writer = config['file_writer']
        rows = config['num_of_rows']
        write_output = config.get('write_output', SETTINGS.WRITE_OUTPUT)

        if rows < SETTINGS.MINIMUM_ROWS_ALLOWED: 
            logger.warning(f"Requested rows ({rows}) below minimum allowed ({SETTINGS.MINIMUM_ROWS_ALLOWED}). Using minimum.")
            rows = SETTINGS.MINIMUM_ROWS_ALLOWED

        configs = config['configs']
        shuffle_data = config.get('shuffle', SETTINGS.SHUFFLE)
        

        logger.debug(f"Column name: {column_name}")
        logger.debug(f"File writer: {file_writer}")
        logger.debug(f"Rows: {rows}")
        logger.debug(f"Write output: {write_output}")
        logger.debug(f"Shuffle data: {shuffle_data}")
                
        # Create DataFrame with the correct number of rows
        df = pd.DataFrame(index=range(rows), columns=column_name)
        logger.debug(f"Created DataFrame with {rows} rows and columns: {column_name}")
        
        # Initialize the strategy factory
        strategy_factory = StrategyFactory(logger)
        logger.debug("Initialized strategy factory")
        
        # Validate the full generator configuration
        try:
            validate_generator_config(config)
            logger.debug("Configuration validation passed")
        except InvalidConfigParamException as e:
            logger.error(f"Configuration validation failed: {e}")
            error_handler.add_error(e)
        
        with measure_time("data_generation", rows_processed=rows):
                
            for cur_config in configs:
                logger.debug(f"Processing config: {cur_config.get('names', 'unknown')}")

                for col_name in cur_config['names']:
                    logger.debug(f"Processing column: {col_name}")
                    
                    if cur_config.get('disabled', False) is True:
                        logger.info(f"Column {col_name} is disabled, skipping")
                        continue

                    # Check if this is an intermediate column (not in final output)
                    is_intermediate = cur_config.get('intermediate', False)
                    logger.debug(f"Column {col_name} - Is intermediate: {is_intermediate}")
                    
                    strategy_name = cur_config['strategy']['name']
                    logger.debug(f"Column {col_name} - Strategy: {strategy_name}")
                    
                    try:
                        with measure_time(f"strategy.{strategy_name}.{col_name}", rows_processed=rows):
                            # Prepare parameters for the strategy - define strategy_params first
                            strategy_params = cur_config.get('strategy').get('params', {})
                            logger.debug(f"Column {col_name} - Strategy params: {strategy_params}")
                            
                            # Add mask to strategy params if it exists at the top level
                            if 'mask' in cur_config:
                                strategy_params['mask'] = cur_config['mask']
                                logger.debug(f"Column {col_name} - Added mask: {cur_config['mask']}")

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
                                logger.debug(f"Column {col_name} - Strategy created successfully: {strategy.__class__.__name__}")

                                df = strategy_factory.execute_strategy(strategy)
                                logger.debug(f"Column {col_name} - Strategy executed successfully. Sample data: {df[col_name].head(3).tolist() if col_name in df.columns else 'N/A'}")

                            except UnsupportedStrategyException as e:
                                logger.error(f"Column {col_name} - Unsupported strategy '{strategy_name}': {e}")
                                error_handler.add_error(e)

                    except ConfigException as e:
                        logger.error(f"Column {col_name} - Configuration error: {e}")
                        error_handler.add_error(e)
                        raise

                    except Exception as e:
                        logger.error(f"Column {col_name} - Unexpected error: {e}")
                        error_handler.add_error(e)
                        raise
        
        # Apply shuffle if enabled
        if shuffle_data:
            logger.debug("Shuffling data")
            with measure_time("shuffle_data", rows_processed=rows):
                df = df.sample(frac=1).reset_index(drop=True)
            logger.debug("Data shuffling completed")
        
        # Filter out intermediate columns before writing
        logger.debug("Filtering intermediate columns")
        with measure_time("filter_intermediate_columns"):
            df = filter_intermediate_columns(df)
        logger.debug(f"Intermediate columns filtered. Final columns: {list(df.columns)}")
        
        # Write output files
        if write_output:
            logger.debug("Writing output files")
            with measure_time("file_writing", rows_processed=rows):
                write_output_files(df, file_writer)
            logger.info("Output files written successfully")
        
        # Output performance report if requested
        if perf_report:
            logger.debug("Generating performance report")
            report = get_performance_report()
            logger.info("Performance report generated")
                
        logger.info(f"Configuration processing completed. Generated {len(df)} rows with {len(df.columns)} columns.")
        return df 