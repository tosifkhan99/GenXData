"""
Pattern strategy for generating random strings matching a regex or pattern.
"""

import pandas as pd
import rstr
import re
import numpy as np
from core.base_strategy import BaseStrategy
from exceptions.param_exceptions import InvalidConfigParamException


class PatternStrategy(BaseStrategy):
    """
    Strategy for generating random strings matching a regex or pattern.
    """

    def _validate_params(self):
        """Validate strategy parameters"""
        if "regex" not in self.params:
            raise InvalidConfigParamException("Missing required parameter: regex")

        # Validate that the regex pattern is valid
        try:
            re.compile(self.params["regex"])
        except re.error as e:
            raise InvalidConfigParamException(f"Invalid regex pattern: {str(e)}")

    def generate_data(self, count: int) -> pd.Series:
        """
        Generate random strings matching the regex pattern.

        Args:
            count: Number of strings to generate

        Returns:
            pd.Series: Generated strings
        """

        # Get regex pattern
        pattern = self.params["regex"]
        max_attempts = (
            count * 3
        )  # tries 3 times more than the count, to come up with unique strings
        attempts = 0

        if self.unique:
            result = set()
            while len(result) < count and attempts < max_attempts:
                attempts += 1
                value = rstr.xeger(pattern)

                # Check if it matches the pattern
                if value not in result:
                    result.add(value)

            if len(result) < count:
                remaining = count - len(result)

                result = list(result)
                result.extend(
                    [np.random.choice(list(result)) for _ in range(remaining)]
                )
        else:
            result = [rstr.xeger(pattern) for _ in range(count)]
        return pd.Series(result)
