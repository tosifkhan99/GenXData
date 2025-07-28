"""
Series strategy for generating sequential numeric values.
"""

import numpy as np
import pandas as pd

from core.base_strategy import BaseStrategy
from exceptions.param_exceptions import InvalidConfigParamException


class SeriesStrategy(BaseStrategy):
    """
    Strategy for generating sequential numeric values.
    Supports both traditional batch generation and stateful chunked generation.
    """

    def __init__(self, logger=None, **kwargs):
        """Initialize the strategy with configuration parameters"""
        super().__init__(logger, **kwargs)

        # Initialize state for chunked generation
        self._initialize_state()

    def _initialize_state(self):
        """Initialize internal state for stateful generation"""
        # Determine if we're working with floats or integers
        start_value = self.params["start"]
        step_value = self.params.get("step", 1 if isinstance(start_value, int) else 0.1)

        if isinstance(start_value, float) or isinstance(step_value, float):
            # Use Decimal for floating point precision
            from decimal import Decimal, getcontext

            getcontext().prec = 10  # Increased precision

            self._current_value = Decimal(str(start_value))
            self._step = Decimal(str(step_value))
            self._is_float = True
        else:
            self._current_value = int(start_value)
            self._step = int(step_value)
            self._is_float = False

        self.logger.debug(
            f"SeriesStrategy initialized with start={self._current_value}, "
            f"step={self._step}, is_float={self._is_float}"
        )

    def _validate_params(self):
        """Validate strategy parameters"""
        if "start" not in self.params:
            raise InvalidConfigParamException("Missing required parameter: start")

        # Validate that start is numeric
        if not isinstance(self.params["start"], (int, float)):
            raise InvalidConfigParamException("Start value must be numeric")

        # Validate step if provided
        if "step" in self.params:
            try:
                float(self.params["step"])
            except ValueError as e:
                raise InvalidConfigParamException("Step value must be numeric") from e

    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of sequential values maintaining internal state.
        This method is stateful and continues from where the last chunk ended.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Generated values starting from current state
        """
        self.logger.debug(
            f"Generating chunk of {count} values starting from {self._current_value}"
        )

        if self._is_float:
            # Generate float values using Decimal for precision
            values = []
            current = self._current_value
            for _ in range(count):
                values.append(float(current))
                current += self._step
            self._current_value = current

            return pd.Series(values, dtype=float)
        else:
            # Generate integer values
            start = self._current_value
            end = start + (count * self._step)
            values = np.arange(start, end, self._step, dtype=int)

            # Update current value for next chunk
            self._current_value = end

            return pd.Series(values, dtype=int)

    def reset_state(self):
        """Reset the internal state to initial values"""
        self.logger.debug("Resetting SeriesStrategy state")
        self._initialize_state()

    def get_current_state(self) -> dict:
        """Get current state information for debugging"""
        return {
            "current_value": (
                float(self._current_value)
                if self._is_float
                else int(self._current_value)
            ),
            "step": float(self._step) if self._is_float else int(self._step),
            "is_float": self._is_float,
        }

    def generate_data(self, count: int) -> pd.Series:
        """
        Generate sequential numeric values by calling generate_chunk.
        This ensures consistent behavior between batch and non-batch modes.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Generated values
        """
        self.logger.debug(
            f"Generating {count} values using unified chunk-based approach"
        )

        # For non-batch mode, we want to start from the configured start value
        # So we reset state first to ensure consistent behavior
        original_state = self.get_current_state()
        self.reset_state()

        # Generate the chunk
        result = self.generate_chunk(count)

        self.logger.debug(
            f"Generated {len(result)} values from {original_state['current_value']} "
            f"to {self.get_current_state()['current_value'] - (1 if not self._is_float else self._step)}"
        )

        return result
