"""
Abstract base config processor for GenXData.

Contains common functionality shared across all processor implementations.
"""

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

import configs.GENERATOR_SETTINGS as SETTINGS
from core.strategy_factory import StrategyFactory
from core.writers.base_writer import BaseWriter
from exceptions.param_exceptions import InvalidConfigParamException
from utils.generator_utils import validate_generator_config
from utils.intermediate_column import filter_intermediate_columns
from utils.logging import Logger
from utils.performance_timer import measure_time


class BaseConfigProcessor(ABC):
    """
    Abstract base class for all config processors in GenXData.

    Contains common functionality for data generation, strategy management,
    and configuration validation.
    """

    def __init__(self, config: dict[str, Any], writer: BaseWriter, error_handler):
        """
        Initialize the base config processor.

        Args:
            config: Configuration dictionary
            writer: Writer instance for output
            error_handler: Error handler for collecting errors
        """
        self.config = config
        self.writer = writer
        self.error_handler = error_handler
        self.logger = Logger.get_logger(self.__class__.__name__.lower())

        # Initialize common configuration values
        self.column_names = config["column_name"]
        self.rows = config["num_of_rows"]
        self.configs = config["configs"]
        self.shuffle_data = config.get("shuffle", SETTINGS.SHUFFLE)

        # Validate minimum rows
        if self.rows < SETTINGS.MINIMUM_ROWS_ALLOWED:
            self.logger.warning(
                f"Requested rows ({self.rows}) below minimum allowed "
                f"({SETTINGS.MINIMUM_ROWS_ALLOWED}). Using minimum."
            )
            self.rows = SETTINGS.MINIMUM_ROWS_ALLOWED

        # Initialize strategy factory
        self.strategy_factory = StrategyFactory(self.logger)

        self.logger.debug(f"BaseConfigProcessor initialized with {self.rows} rows")

    def validate_config(self) -> bool:
        """
        Validate the processor configuration.

        Returns:
            True if configuration is valid

        Raises:
            InvalidConfigParamException: If configuration is invalid
        """
        try:
            validate_generator_config(self.config)
            self.logger.debug("Configuration validation passed")
            return True
        except InvalidConfigParamException as e:
            self.logger.error(f"Configuration validation failed: {e}")
            self.error_handler.add_error(e)
            raise

    def create_base_dataframe(self, size: int = None) -> pd.DataFrame:
        """
        Create the base DataFrame with correct structure.

        Args:
            size: Number of rows to create (defaults to self.rows)

        Returns:
            Empty DataFrame with proper index and columns
        """
        num_rows = size if size is not None else self.rows
        df = pd.DataFrame(index=range(num_rows), columns=self.column_names)
        self.logger.debug(
            f"Created base DataFrame with {num_rows} rows and "
            f"columns: {self.column_names}"
        )
        return df

    def process_column_strategies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process all column strategies and populate the DataFrame.

        Args:
            df: Base DataFrame to populate

        Returns:
            DataFrame with generated data
        """
        self.logger.info(f"Processing {len(self.configs)} column configurations")

        with measure_time("data_generation", rows_processed=self.rows):
            for cur_config in self.configs:
                df = self._process_single_config(df, cur_config)

        return df

    def _process_single_config(
        self, df: pd.DataFrame, cur_config: dict[str, Any]
    ) -> pd.DataFrame:
        """
        Process a single column configuration.

        Args:
            df: DataFrame to update
            cur_config: Configuration for current columns

        Returns:
            Updated DataFrame
        """
        self.logger.debug(f"Processing config: {cur_config.get('names', 'unknown')}")

        for col_name in cur_config["names"]:
            self.logger.debug(f"Processing column: {col_name}")

            if cur_config.get("disabled", False):
                self.logger.info(f"Column {col_name} is disabled, skipping")
                continue

            # Check if this is an intermediate column
            is_intermediate = cur_config.get("intermediate", False)
            self.logger.debug(f"Column {col_name} - Is intermediate: {is_intermediate}")

            strategy_name = cur_config["strategy"]["name"]
            self.logger.debug(f"Column {col_name} - Strategy: {strategy_name}")

            try:
                df = self._execute_column_strategy(
                    df, col_name, cur_config, is_intermediate
                )
            except Exception as e:
                self.logger.error(f"Column {col_name} - Error: {e}")
                self.error_handler.add_error(e)
                raise

        return df

    def _execute_column_strategy(
        self,
        df: pd.DataFrame,
        col_name: str,
        cur_config: dict[str, Any],
        is_intermediate: bool,
    ) -> pd.DataFrame:
        """
        Execute strategy for a single column.

        Args:
            df: DataFrame to update
            col_name: Name of the column to process
            cur_config: Configuration for the column
            is_intermediate: Whether this is an intermediate column

        Returns:
            Updated DataFrame
        """
        strategy_name = cur_config["strategy"]["name"]

        with measure_time(
            f"strategy.{strategy_name}.{col_name}", rows_processed=self.rows
        ):
            # Prepare strategy parameters
            strategy_params = cur_config.get("strategy", {}).get("params", {})
            self.logger.debug(f"Column {col_name} - Strategy params: {strategy_params}")

            # Add mask to strategy params if it exists
            if "mask" in cur_config:
                strategy_params["mask"] = cur_config["mask"]
                self.logger.debug(
                    f"Column {col_name} - Added mask: {cur_config['mask']}"
                )

            params = {
                "df": df,
                "col_name": col_name,
                "rows": self.rows,
                "intermediate": is_intermediate,
                "params": strategy_params,
                "unique": cur_config.get("strategy", {}).get("unique", False),
            }

            # Create and execute strategy
            strategy = self.strategy_factory.create_strategy(strategy_name, **params)
            self.logger.debug(
                f"Column {col_name} - Strategy created: {strategy.__class__.__name__}"
            )

            df = self.strategy_factory.execute_strategy(strategy)
            self.logger.debug(
                f"Column {col_name} - Strategy executed. Sample: "
                f"{df[col_name].head(3).tolist() if col_name in df.columns else 'N/A'}"
            )

        return df

    def apply_shuffle(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply shuffle to the DataFrame if configured.

        Args:
            df: DataFrame to shuffle

        Returns:
            Shuffled DataFrame (or original if shuffle disabled)
        """
        if self.shuffle_data:
            self.logger.debug("Shuffling data")
            with measure_time("shuffle_data", rows_processed=len(df)):
                df = df.sample(frac=1).reset_index(drop=True)
            self.logger.debug("Data shuffling completed")

        return df

    def filter_intermediate_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter out intermediate columns from the final DataFrame.

        Args:
            df: DataFrame to filter

        Returns:
            DataFrame with intermediate columns removed
        """
        self.logger.debug("Filtering intermediate columns")
        with measure_time("filter_intermediate_columns"):
            df = filter_intermediate_columns(df)
        self.logger.debug(
            f"Intermediate columns filtered. Final columns: {list(df.columns)}"
        )
        return df

    @abstractmethod
    def process(self) -> dict[str, Any]:
        """
        Process the configuration and generate data.

        This method must be implemented by concrete processor classes.

        Returns:
            Dictionary with processing results
        """
        pass
