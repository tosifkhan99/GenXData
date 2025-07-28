"""
Abstract base writer for GenXData output operations.
"""

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class BaseWriter(ABC):
    """
    Abstract base class for all writers in GenXData.

    Writers are responsible for taking DataFrames and outputting them
    in various formats and destinations.
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize the writer with configuration.

        Args:
            config: Writer configuration dictionary
        """
        self.config = config

    @abstractmethod
    def write(
        self, df: pd.DataFrame, metadata: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        Write a DataFrame to the output destination.

        Args:
            df: DataFrame to write
            metadata: Optional metadata about the data

        Returns:
            Dictionary with write operation results
        """
        pass

    @abstractmethod
    def finalize(self) -> dict[str, Any]:
        """
        Finalize the writing process and cleanup resources.

        Returns:
            Dictionary with finalization results and summary
        """
        pass

    def validate_config(self) -> bool:
        """
        Validate the writer configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        if not isinstance(self.config, dict):
            raise ValueError("Writer config must be a dictionary")
        return True
