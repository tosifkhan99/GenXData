"""
Number range strategy for generating random numbers within a range.
"""

import numpy as np
import pandas as pd

from core.base_strategy import BaseStrategy
from exceptions.param_exceptions import InvalidConfigParamException


class NumberRangeStrategy(BaseStrategy):
    """
    Strategy for generating random numbers within a specified range.
    Supports stateful generation with consistent random state.
    """

    def __init__(self, logger=None, **kwargs):
        """Initialize the strategy with configuration parameters"""
        super().__init__(logger, **kwargs)

        # Initialize random state for consistent generation
        self._initialize_state()

    def _initialize_state(self):
        """Initialize internal state for stateful generation"""
        # Initialize random state with seed if provided
        seed = self.params.get("seed", None)
        self._random_state = np.random.RandomState(seed)

        # Store bounds for efficient access
        self._lower = float(self.params["start"])
        self._upper = float(self.params["end"])
        self._is_integer = isinstance(self.params["start"], int) and isinstance(
            self.params["end"], int
        )

        self.logger.debug(
            f"NumberRangeStrategy initialized with range=[{self._lower}, {self._upper}], "
            f"integer={self._is_integer}, seed={seed}"
        )

    def _validate_params(self):
        """Validate strategy parameters"""
        if "start" not in self.params:
            raise InvalidConfigParamException("Missing required parameter: start")
        if "end" not in self.params:
            raise InvalidConfigParamException("Missing required parameter: end")

        # Validate that bounds are numeric
        try:
            lower = float(self.params["start"])
            upper = float(self.params["end"])
        except ValueError:
            raise InvalidConfigParamException("Bounds must be numeric")

        # Validate that start is less than end
        if lower >= upper:
            raise InvalidConfigParamException(
                f"start ({lower}) must be less than end ({upper})"
            )

        # Validate seed if provided
        if "seed" in self.params:
            try:
                int(self.params["seed"])
            except ValueError:
                raise InvalidConfigParamException("Seed must be an integer")

    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of random numbers maintaining internal random state.
        This method is stateful and maintains consistent random sequence.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Generated values
        """
        self.logger.debug(
            f"Generating chunk of {count} random numbers in range [{self._lower}, {self._upper}]"
        )

        # Generate random numbers using internal state
        values = self._random_state.uniform(self._lower, self._upper, count)

        # Convert to integers if both bounds are integers
        if self._is_integer:
            values = values.astype(int)

        return pd.Series(values, dtype=int if self._is_integer else float)

    def reset_state(self):
        """Reset the internal random state to initial values"""
        self.logger.debug("Resetting NumberRangeStrategy state")
        self._initialize_state()

    def get_current_state(self) -> dict:
        """Get current state information for debugging"""
        return {
            "strategy": "NumberRangeStrategy",
            "stateful": True,
            "column": self.col_name,
            "range": [self._lower, self._upper],
            "is_integer": self._is_integer,
            "seed": self.params.get("seed", None),
            "random_state": str(
                self._random_state.get_state()[1][:5]
            ),  # First 5 state values
        }

    def generate_data(self, count: int) -> pd.Series:
        """
        Generate random numbers by calling generate_chunk.
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

        self.logger.debug(
            f"Generated {len(result)} random numbers in range [{self._lower}, {self._upper}]"
        )

        return result
