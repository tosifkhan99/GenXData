"""
Distributed number range strategy for generating numeric values from multiple
weighted ranges.
"""

import numpy as np
import pandas as pd

from core.base_strategy import BaseStrategy
from core.strategy_config import RangeItem
from exceptions.param_exceptions import InvalidConfigParamException


class DistributedNumberRangeStrategy(BaseStrategy):
    """
    Strategy for generating random numbers from multiple weighted ranges.
    """

    def _validate_params(self):
        """Validate strategy parameters"""
        if "ranges" not in self.params:
            raise InvalidConfigParamException("Missing required parameter: ranges")

        ranges = self.params["ranges"]
        if not isinstance(ranges, list) or not ranges:
            raise InvalidConfigParamException("Ranges must be a non-empty list")

        total_distribution = 0

        # Validate each range
        for i, range_item in enumerate(ranges):
            if not isinstance(range_item, RangeItem):
                raise InvalidConfigParamException(
                    f"Range at index {i} {type(range_item)} must be a dictionary"
                )

            # Check required fields
            for field in ["start", "end", "distribution"]:
                if not hasattr(range_item, field):
                    raise InvalidConfigParamException(
                        f"Range at index {i} is missing required field: {field}"
                    )

            # Validate bounds
            lb = range_item.start
            ub = range_item.end
            dist = range_item.distribution

            if not isinstance(lb, int | float) or not isinstance(ub, int | float):
                raise InvalidConfigParamException(
                    f"Bounds for range at index {i} must be numeric"
                )

            if lb >= ub:
                raise InvalidConfigParamException(
                    f"start ({lb}) must be less than end ({ub}) for range at index {i}"
                )

            # Validate distribution
            if not isinstance(dist, int | float) or dist <= 0:
                raise InvalidConfigParamException(
                    f"Distribution for range at index {i} must be positive, got {dist}"
                )

            total_distribution += dist

        # Check that distributions sum to 100
        if abs(total_distribution - 100) > 0.01:  # Allow for small floating point error
            raise InvalidConfigParamException(
                f"Distribution weights must sum to 100, got {total_distribution}"
            )

        # Validate seed if provided
        if "seed" in self.params:
            try:
                int(self.params["seed"])
            except ValueError as e:
                raise InvalidConfigParamException("Seed must be an integer") from e

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

        self.logger.debug(
            f"DistributedNumberRangeStrategy initialized with seed={seed}"
        )

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
        Generate random numbers from multiple weighted ranges.

        Args:
            count: Number of values to generate

        Returns:
            Series of random numbers
        """
        ranges = self.params["ranges"]

        # Calculate the number of values to generate from each range
        distributions = [r.distribution for r in ranges]
        total_dist = sum(distributions)

        # Normalize distributions
        normalized_dist = [d / total_dist for d in distributions]

        # Calculate counts for each range
        range_counts = np.random.multinomial(count, normalized_dist)

        # Generate values for each range
        all_values = []
        for i, range_item in enumerate(ranges):
            range_count = range_counts[i]
            if range_count == 0:
                continue

            lb = range_item.start
            ub = range_item.end

            # Handle integer vs float generation
            if isinstance(lb, int) and isinstance(ub, int):
                # Generate integers
                values = np.random.randint(lb, ub + 1, size=range_count).tolist()
            else:
                # Generate floats
                values = np.random.uniform(lb, ub, size=range_count).tolist()

            all_values.extend(values)

        # Shuffle the values to mix ranges
        np.random.shuffle(all_values)

        return pd.Series(all_values)

    def reset_state(self):
        """Reset the internal state to initial values"""

        self.logger.debug("Resetting DistributedNumberRangeStrategy state")

        self._initialize_state()

    def get_current_state(self) -> dict:
        """Get current state information for debugging"""

        return {
            "strategy": "DistributedNumberRangeStrategy",
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
