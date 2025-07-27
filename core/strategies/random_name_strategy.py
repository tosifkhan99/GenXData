"""
Random name strategy for generating realistic person names using the names package.
"""

import random

import pandas as pd

from core.base_strategy import BaseStrategy
from exceptions.param_exceptions import InvalidConfigParamException
from utils.get_names import apply_case_formatting, get_name


class RandomNameStrategy(BaseStrategy):
    """
    Strategy for generating random person names with configurable parameters.
    Supports first names, last names, full names, gender filtering, and case formatting.
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

        # Store parameters for efficient access
        self._name_type = self.params["name_type"]
        self._gender = None if self.params["gender"] == "any" else self.params["gender"]
        self._case_format = self.params["case"]

        self.logger.debug(
            f"RandomNameStrategy initialized with name_type={self._name_type}, "
            f"gender={self._gender}, case={self._case_format}, seed={seed}"
        )

    def _validate_params(self):
        """Validate strategy parameters"""
        # Set defaults if not provided
        if "name_type" not in self.params:
            self.params["name_type"] = "first"
        if "gender" not in self.params:
            self.params["gender"] = "any"
        if "case" not in self.params:
            self.params["case"] = "title"

        # Validate name_type
        valid_name_types = ["first", "last", "full"]
        if self.params["name_type"] not in valid_name_types:
            raise InvalidConfigParamException(
                f"Invalid name_type: {self.params['name_type']}. Must be one of {valid_name_types}"
            )

        # Validate gender
        valid_genders = ["male", "female", "any"]
        if self.params["gender"] not in valid_genders:
            raise InvalidConfigParamException(
                f"Invalid gender: {self.params['gender']}. Must be one of {valid_genders}"
            )

        # Validate case
        valid_cases = ["title", "upper", "lower"]
        if self.params["case"] not in valid_cases:
            raise InvalidConfigParamException(
                f"Invalid case: {self.params['case']}. Must be one of {valid_cases}"
            )

        # Validate seed if provided
        if "seed" in self.params:
            try:
                int(self.params["seed"])
            except ValueError:
                raise InvalidConfigParamException("Seed must be an integer")

    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of random names maintaining internal random state.
        This method is stateful and maintains consistent random sequence.

        Args:
            count: Number of names to generate

        Returns:
            pd.Series: Generated names
        """
        self.logger.debug(
            f"Generating chunk of {count} names (type={self._name_type}, gender={self._gender})"
        )

        result = []
        for _ in range(count):
            # Generate the name using the names package
            name = get_name(name_type=self._name_type, gender=self._gender)

            # Apply case formatting
            formatted_name = apply_case_formatting(name, self._case_format)

            result.append(formatted_name)

        return pd.Series(result, dtype=str)

    def reset_state(self):
        """Reset the internal random state to initial values"""
        self.logger.debug("Resetting RandomNameStrategy state")
        self._initialize_state()

    def get_current_state(self) -> dict:
        """Get current state information for debugging"""
        return {
            "strategy": "RandomNameStrategy",
            "stateful": True,
            "column": self.col_name,
            "name_type": self._name_type,
            "gender": self._gender,
            "case_format": self._case_format,
            "seed": self.params.get("seed", None),
        }

    def generate_data(self, count: int) -> pd.Series:
        """
        Generate random names by calling generate_chunk.
        This ensures consistent behavior between batch and non-batch modes.

        Args:
            count: Number of names to generate

        Returns:
            pd.Series: Generated names
        """
        self.logger.debug(
            f"Generating {count} values using unified chunk-based approach"
        )

        # For non-batch mode, reset state to ensure consistent behavior
        self.reset_state()

        # Generate the chunk
        result = self.generate_chunk(count)

        self.logger.debug(f"Generated {len(result)} names (type={self._name_type})")

        return result
