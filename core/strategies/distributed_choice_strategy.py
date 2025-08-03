"""
Distributed choice strategy for generating values based on weighted choices.
"""

import numpy as np
import pandas as pd

from core.base_strategy import BaseStrategy

from exceptions.param_exceptions import InvalidConfigParamException


class DistributedChoiceStrategy(BaseStrategy):
    """
    Strategy for generating values based on weighted choices.
    """

    def _validate_params(self):
        """Validate strategy parameters"""
        if "choices" not in self.params:
            raise InvalidConfigParamException("Missing required parameter: choices")

        choices = self.params["choices"]
        if not isinstance(choices, dict) or not choices:
            raise InvalidConfigParamException("Choices must be a non-empty dictionary")

        # Validate that weights are positive
        for choice, weight in choices.items():
            if not isinstance(weight, int | float) or weight <= 0:
                raise InvalidConfigParamException(
                    f"Weight for choice '{choice}' must be positive, got {weight}"
                )

        # Validate seed if provided
        if "seed" in self.params:
            try:
                int(self.params["seed"])
            except ValueError as e:
                raise InvalidConfigParamException(
                    "Seed must be an integer"
                ) from e

        total_weight = sum(choices.values())
        if total_weight != 100:
            raise InvalidConfigParamException("Total weight must be 100")

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
        self.logger.debug(f"DistributedChoiceStrategy initialized with seed={seed}")

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
        Generate random values based on weighted choices.

        Args:
            count: Number of values to generate

        Returns:
            Series of chosen values
        """
        choices_dict = self.params["choices"]

        # Extract choices and weights
        choices = list(choices_dict.keys())
        weights = list(choices_dict.values())

        # Generate random choices based on weights
        values = []

        # Calculate total weight
        total_weight = sum(weights)

        # Generate values proportionally based on weights
        for choice, weight in choices_dict.items():
            # Calculate how many values this choice should get
            proportion = weight / total_weight
            num_values = int(proportion * count)

            # Add the values for this choice
            for _ in range(num_values):
                values.append(choice)

        # Handle any remaining values due to rounding
        while len(values) < count:
            # Add random choice based on weights
            choice = np.random.choice(choices, p=[w / total_weight for w in weights])
            values.append(choice)

        return pd.Series(values)

    def reset_state(self):
        """Reset the internal state to initial values"""
        self.logger.debug("Resetting DistributedChoiceStrategy state")
        self._initialize_state()

    def get_current_state(self) -> dict:
        """Get current state information for debugging"""
        return {
            "strategy": "DistributedChoiceStrategy",
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
        self._validate_params()
        self.logger.debug(
            f"Generating {count} values using unified chunk-based approach"
        )
        # For non-batch mode, reset state to ensure consistent behavior
        self.reset_state()
        # Generate the chunk
        result = self.generate_chunk(count)
        return result
