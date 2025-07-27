"""
Concat strategy for concatenating values from multiple columns.
"""

import pandas as pd

from core.base_strategy import BaseStrategy
from exceptions.param_exceptions import InvalidConfigParamException


class ConcatStrategy(BaseStrategy):
    """
    Strategy for concatenating values from multiple columns.
    Implements stateful interface for consistency.
    """

    def __init__(self, logger=None, **kwargs):
        """Initialize the strategy with configuration parameters"""
        super().__init__(logger, **kwargs)

        # Initialize state (simple for concat strategy)
        self._initialize_state()

    def _initialize_state(self):
        """Initialize internal state for stateful generation"""
        # Store concatenation parameters for efficient access
        self._lhs_col = self.params["lhs_col"]
        self._rhs_col = self.params["rhs_col"]
        self._prefix = self.params.get("prefix", "")
        self._suffix = self.params.get("suffix", "")
        self._separator = self.params.get("separator", "")

        self.logger.debug(
            f"ConcatStrategy initialized: {self._lhs_col} + {self._rhs_col} "
            f"with prefix='{self._prefix}', suffix='{self._suffix}', separator='{self._separator}'"
        )

    def _validate_params(self):
        """Validate strategy parameters"""
        if "lhs_col" not in self.params:
            raise InvalidConfigParamException("Missing required parameter: lhs_col")
        if "rhs_col" not in self.params:
            raise InvalidConfigParamException("Missing required parameter: rhs_col")

        # Validate that all columns exist in the dataframe
        if self.df is not None:
            for col in [self.params["lhs_col"], self.params["rhs_col"]]:
                if col not in self.df.columns:
                    raise ValueError(f"Column {col} not found in dataframe")

    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of concatenated values maintaining internal state.
        For concat strategy, this works with existing data from multiple columns.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Series of concatenated values
        """
        self.logger.debug(f"Generating chunk of {count} concatenated values")

        if self.df is None:
            self.logger.warning("No dataframe available for concatenation")
            return pd.Series([f"{self._prefix}{self._separator}{self._suffix}"] * count)

        # Get data from both columns, limited to count
        lhs_data = self.df[self._lhs_col].head(count)
        rhs_data = self.df[self._rhs_col].head(count)

        # Convert to string for concatenation
        if lhs_data.dtype != "str":
            lhs_data_as_string = lhs_data.astype(str)
        else:
            lhs_data_as_string = lhs_data

        if rhs_data.dtype != "str":
            rhs_data_as_string = rhs_data.astype(str)
        else:
            rhs_data_as_string = rhs_data

        # Perform concatenation
        result = (
            self._prefix
            + lhs_data_as_string
            + self._separator
            + rhs_data_as_string
            + self._suffix
        )

        return result

    def reset_state(self):
        """Reset the internal state to initial values"""
        self.logger.debug("Resetting ConcatStrategy state")
        self._initialize_state()

    def get_current_state(self) -> dict:
        """Get current state information for debugging"""
        return {
            "strategy": "ConcatStrategy",
            "stateful": True,
            "column": self.col_name,
            "lhs_col": self._lhs_col,
            "rhs_col": self._rhs_col,
            "prefix": self._prefix,
            "suffix": self._suffix,
            "separator": self._separator,
        }

    def generate_data(self, count: int) -> pd.Series:
        """
        Concatenate values by calling generate_chunk.
        This ensures consistent behavior between batch and non-batch modes.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Series of concatenated values
        """
        self.logger.debug(
            f"Generating {count} values using unified chunk-based approach"
        )

        # For concat strategy, state doesn't change the logic, but we maintain consistency
        result = self.generate_chunk(count)

        self.logger.debug(f"Generated {len(result)} concatenated values")

        return result
