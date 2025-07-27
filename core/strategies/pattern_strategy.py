"""
Pattern strategy for generating random strings matching a regex or pattern.
"""

import random
import re

import numpy as np
import pandas as pd
import rstr

from core.base_strategy import BaseStrategy
from exceptions.param_exceptions import InvalidConfigParamException


class PatternStrategy(BaseStrategy):
    """
    Strategy for generating random strings matching a regex or pattern.
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
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        # Store pattern for efficient access
        self._pattern = self.params["regex"]
        self._unique_values = set() if self.unique else None

        self.logger.debug(
            f"PatternStrategy initialized with pattern='{self._pattern}', "
            f"unique={self.unique}, seed={seed}"
        )

    def _validate_params(self):
        """Validate strategy parameters"""
        if "regex" not in self.params:
            raise InvalidConfigParamException("Missing required parameter: regex")

        # Validate that the regex pattern is valid
        try:
            re.compile(self.params["regex"])
        except re.error as e:
            raise InvalidConfigParamException(f"Invalid regex pattern: {str(e)}")

        # Validate seed if provided
        if "seed" in self.params:
            try:
                int(self.params["seed"])
            except ValueError:
                raise InvalidConfigParamException("Seed must be an integer")

    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of random strings matching the pattern maintaining internal state.
        This method is stateful and maintains consistent random sequence and uniqueness.

        Args:
            count: Number of strings to generate

        Returns:
            pd.Series: Generated strings
        """
        self.logger.debug(
            f"Generating chunk of {count} strings matching pattern '{self._pattern}'"
        )

        max_attempts = count * 3  # tries 3 times more than the count
        attempts = 0

        if self.unique and self._unique_values is not None:
            result = []
            while len(result) < count and attempts < max_attempts:
                attempts += 1
                value = rstr.xeger(self._pattern)

                # Check if it's unique
                if value not in self._unique_values:
                    self._unique_values.add(value)
                    result.append(value)

            # If we couldn't generate enough unique values, pad with existing ones
            if len(result) < count:
                remaining = count - len(result)
                existing_values = list(self._unique_values)
                if existing_values:
                    padding = [
                        np.random.choice(existing_values) for _ in range(remaining)
                    ]
                    result.extend(padding)
                else:
                    # Fallback: generate non-unique values
                    padding = [rstr.xeger(self._pattern) for _ in range(remaining)]
                    result.extend(padding)
        else:
            result = [rstr.xeger(self._pattern) for _ in range(count)]

        return pd.Series(result, dtype=str)

    def reset_state(self):
        """Reset the internal random state to initial values"""
        self.logger.debug("Resetting PatternStrategy state")
        self._initialize_state()

    def get_current_state(self) -> dict:
        """Get current state information for debugging"""
        return {
            "strategy": "PatternStrategy",
            "stateful": True,
            "column": self.col_name,
            "pattern": self._pattern,
            "unique": self.unique,
            "unique_count": len(self._unique_values) if self._unique_values else 0,
            "seed": self.params.get("seed", None),
        }

    def generate_data(self, count: int) -> pd.Series:
        """
        Generate random strings by calling generate_chunk.
        This ensures consistent behavior between batch and non-batch modes.

        Args:
            count: Number of strings to generate

        Returns:
            pd.Series: Generated strings
        """
        self.logger.debug(
            f"Generating {count} values using unified chunk-based approach"
        )

        # For non-batch mode, reset state to ensure consistent behavior
        self.reset_state()

        # Generate the chunk
        result = self.generate_chunk(count)

        self.logger.debug(
            f"Generated {len(result)} strings matching pattern '{self._pattern}'"
        )

        return result
