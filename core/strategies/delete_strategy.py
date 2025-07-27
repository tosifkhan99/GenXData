"""
Delete strategy for removing values from a column.
"""

import pandas as pd

from core.base_strategy import BaseStrategy
from exceptions.param_exceptions import InvalidConfigParamException


class DeleteStrategy(BaseStrategy):
    """
    Strategy for deleting/nullifying values in a column.
    Implements stateful interface for consistency.
    """

    def __init__(self, logger=None, **kwargs):
        """Initialize the strategy with configuration parameters"""
        super().__init__(logger, **kwargs)

        # Initialize state (simple for delete strategy)
        self._initialize_state()

    def _initialize_state(self):
        """Initialize internal state for stateful generation"""
        # Store mask for efficient access
        self._mask = self.params["mask"]

        self.logger.debug(f"DeleteStrategy initialized with mask='{self._mask}'")

    def _validate_params(self):
        """Validate strategy parameters"""
        if "mask" not in self.params:
            raise InvalidConfigParamException("Missing required parameter: mask")

        # Validate that the mask is a string (condition)
        if not isinstance(self.params["mask"], str):
            raise InvalidConfigParamException("Mask must be a string condition")

    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of None values maintaining internal state.
        For delete strategy, this is stateless but implements the interface.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Series of None values
        """
        self.logger.debug(f"Generating chunk of {count} None values for deletion")

        # Return None values for the masked rows
        return pd.Series([None] * count, dtype=object)

    def reset_state(self):
        """Reset the internal state to initial values"""
        self.logger.debug("Resetting DeleteStrategy state")
        self._initialize_state()

    def get_current_state(self) -> dict:
        """Get current state information for debugging"""
        return {
            "strategy": "DeleteStrategy",
            "stateful": True,
            "column": self.col_name,
            "mask": self._mask,
        }

    def generate_data(self, count: int) -> pd.Series:
        """
        Generate None values by calling generate_chunk.
        This ensures consistent behavior between batch and non-batch modes.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Series of None values
        """
        self.logger.debug(
            f"Generating {count} values using unified chunk-based approach"
        )

        # For delete strategy, state doesn't matter, but we maintain consistency
        result = self.generate_chunk(count)

        self.logger.debug(f"Generated {len(result)} None values for deletion")

        return result
