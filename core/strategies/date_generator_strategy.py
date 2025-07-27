"""
Date generator strategy for generating random dates within a range.
"""

from datetime import datetime

import pandas as pd

from core.base_strategy import BaseStrategy
from exceptions.param_exceptions import InvalidConfigParamException
from utils.date_generator import generate_random_date


class DateGeneratorStrategy(BaseStrategy):
    """
    Strategy for generating random dates within a specified range.
    """

    def _validate_params(self):
        """Validate strategy parameters"""
        if "start_date" not in self.params:
            raise InvalidConfigParamException("Missing required parameter: start_date")
        if "end_date" not in self.params:
            raise InvalidConfigParamException("Missing required parameter: end_date")

        # Validate date formats if provided
        if "input_format" in self.params:
            try:
                datetime.strptime(
                    self.params["start_date"], self.params["input_format"]
                )
                datetime.strptime(self.params["end_date"], self.params["input_format"])
            except ValueError as e:
                raise InvalidConfigParamException(f"Invalid date format: {str(e)}")

        # Validate seed if provided
        if "seed" in self.params:
            try:
                int(self.params["seed"])
            except ValueError:
                raise InvalidConfigParamException("Seed must be an integer")

    def __init__(self, logger=None, **kwargs):
        """Initialize the strategy with configuration parameters"""

        super().__init__(logger, **kwargs)

        # Initialize state for consistent generation

        self._initialize_state()

    def _initialize_state(self):
        """Initialize internal state for stateful generation"""

        # Initialize with seed if provided for consistent generation

        seed = self.params.get("seed", None)

        if seed is not None:
            import random

            import numpy as np

            random.seed(seed)

            np.random.seed(seed)

        self.logger.debug(f"DateGeneratorStrategy initialized with seed={seed}")

    def generate_chunk(self, count: int) -> pd.Series:
        """


        Generate a chunk of data maintaining internal state.


        This method is stateful and maintains consistent random sequence.



        Args:


            count: Number of values to generate



        Returns:


            pd.Series: Generated values


        """

        self.logger.debug(f"Generating chunk of {count} values")

        # Use the original generation logic
        """
        Generate random dates within the specified range.

        Args:
            count: Number of dates to generate

        Returns:
            pd.Series: Generated dates
        """

        # Get date generation parameters

        if isinstance(self.params["start_date"], str):
            start_date = datetime.strptime(
                self.params["start_date"], self.params["format"]
            )
        else:
            start_date = self.params["start_date"]
        if isinstance(self.params["end_date"], str):
            end_date = datetime.strptime(self.params["end_date"], self.params["format"])
        else:
            end_date = self.params["end_date"]

        params = {
            "start_date": start_date,
            "end_date": end_date,
        }

        if "output_format" in self.params:
            params["output_format"] = self.params["output_format"]
        else:
            params["output_format"] = "%Y-%m-%d"

        # Generate the dates
        dates = [generate_random_date(**params) for _ in range(count)]
        return pd.Series(dates)

    def reset_state(self):
        """Reset the internal state to initial values"""

        self.logger.debug("Resetting DateGeneratorStrategy state")

        self._initialize_state()

    def get_current_state(self) -> dict:
        """Get current state information for debugging"""

        return {
            "strategy": "DateGeneratorStrategy",
            "stateful": True,
            "column": self.col_name,
            "seed": self.params.get("seed", None),
        }

    def generate_data(self, count: int) -> pd.Series:
        """


        Generate data by calling generate_chunk.


        This ensures consistent behavior between batch and non-batch modes.



        Args:


            count: Number of values to generate



        Returns:


            pd.Series: Generated values


        """

        self.logger.debug(
            f"Generating {count} values using unified chunk-based approach"
        )

        # For non-batch mode, reset state to ensure consistent behavior

        self.reset_state()

        # Generate the chunk

        result = self.generate_chunk(count)

        return result
