"""
Number range strategy for generating random numbers within a range.
"""

import pandas as pd
import numpy as np

from core.base_strategy import BaseStrategy
from exceptions.param_exceptions import InvalidConfigParamException


class NumberRangeStrategy(BaseStrategy):
    """
    Strategy for generating random numbers within a specified range.
    """

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

    def generate_data(self, count: int) -> pd.Series:
        """
        Generate random numbers within the specified range.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Generated values
        """

        # Get parameters
        lower = float(self.params["start"])
        upper = float(self.params["end"])

        # Generate random numbers
        values = np.random.uniform(lower, upper, count)

        # Convert to integers if both bounds are integers
        if isinstance(self.params["start"], int) and isinstance(
            self.params["end"], int
        ):
            values = values.astype(int)

        return pd.Series(values)
