"""
Base strategy for all data generation strategies.
"""

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from pandas.errors import IndexingError

from utils.logging import Logger


class BaseStrategy(ABC):
    """
    Base class for all data generation strategies.
    All strategies must implement the stateful generation pattern.
    """

    def __init__(self, logger=None, **kwargs):
        """Initialize the strategy with configuration parameters"""
        self.df = kwargs.get("df")
        self.col_name = kwargs.get("col_name")
        self.rows = kwargs.get("rows", 100)
        self.is_intermediate = kwargs.get("intermediate", False)
        self.params = kwargs.get("params", {})
        self.debug = kwargs.get("debug", False)
        self.unique = kwargs.get("unique", False)
        self.shuffle = kwargs.get("shuffle", False)

        # Create strategy-specific logger
        if logger is None:
            strategy_name = self.__class__.__name__.lower().replace("strategy", "")
            logger_name = f"strategies.{strategy_name}"
            self.logger = Logger.get_logger(logger_name)
        else:
            self.logger = logger

        # Log strategy initialization
        self.logger.debug(
            f"Initializing {self.__class__.__name__} for column '{self.col_name}'"
        )

        # Validate required parameters
        self._validate_params()

    @abstractmethod
    def _validate_params(self):
        """
        Validate the parameters required by this strategy.
        Raises InvalidConfigParamException if required parameters are missing or invalid.
        """
        pass

    @abstractmethod
    def generate_data(self, count: int) -> pd.Series:
        """
        Generate the data based on strategy configuration.
        This method should call generate_chunk() for consistent behavior.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Generated values
        """
        pass

    @abstractmethod
    def generate_chunk(self, count: int) -> pd.Series:
        """
        Generate a chunk of data maintaining internal state.
        All strategies must implement this method for stateful generation.

        Args:
            count: Number of values to generate

        Returns:
            pd.Series: Generated values
        """
        pass

    @abstractmethod
    def reset_state(self):
        """
        Reset the internal state to initial values.
        All strategies must implement this method.
        """
        pass

    @abstractmethod
    def get_current_state(self) -> dict:
        """
        Get current state information for debugging.
        All strategies must implement this method.

        Returns:
            dict: Current state information
        """
        pass

    def is_stateful(self) -> bool:
        """
        Check if this strategy supports stateful generation.
        All strategies are now stateful by design.

        Returns:
            bool: Always True since all strategies implement stateful methods
        """
        return True

    def apply_to_dataframe(
        self, df: pd.DataFrame, column_name: str, mask: str | None = None
    ) -> pd.DataFrame:
        """
        Apply strategy to dataframe with optional mask filtering.

        Args:
            df: Target dataframe
            column_name: Column to populate
            mask: Optional pandas query string for filtering rows

        Returns:
            Updated dataframe
        """
        self.logger.debug(
            f"Applying {self.__class__.__name__} to column '{column_name}' with {len(df)} rows"
        )

        # todo: check if this is needed. #optimizations.
        df_copy = df.copy()

        # Initialize column with NaN if it doesn't exist
        if column_name not in df_copy.columns:
            df_copy[column_name] = np.nan

        if mask and mask.strip():
            self.logger.debug(f"Applying mask to column '{column_name}': {mask}")
            try:
                filtered_df = df_copy.query(mask)
                if len(filtered_df) > 0:
                    self.logger.debug(
                        f"Mask filtered {len(filtered_df)} rows out of {len(df_copy)} total rows"
                    )
                    # Generate data only for filtered rows
                    values = self.generate_data(len(filtered_df))

                    # Ensure column has compatible dtype before assignment
                    if (
                        df_copy[column_name].dtype == "float64"
                        and values.dtype == "object"
                    ):
                        df_copy[column_name] = df_copy[column_name].astype("object")

                    df_copy.loc[filtered_df.index, column_name] = values.values
                else:
                    self.logger.warning(
                        f"Mask '{mask}' matched no rows for column '{column_name}'"
                    )

            except IndexingError as e:
                self.logger.warning(
                    f"IndexError applying mask to column '{column_name}': {e}. Applying to all rows as fallback."
                )
                # Fallback: apply to all rows
                values = self.generate_data(len(df_copy))

                # Ensure column has compatible dtype before assignment
                if df_copy[column_name].dtype == "float64" and values.dtype == "object":
                    df_copy[column_name] = df_copy[column_name].astype("object")

                df_copy[column_name] = values.values
            except Exception as e:
                self.logger.error(f"Error applying mask to column '{column_name}': {e}")
                raise e
        else:
            # No mask: apply to all rows
            self.logger.debug(f"No mask specified, applying to all {len(df_copy)} rows")
            values = self.generate_data(len(df_copy))

            # Ensure column has compatible dtype before assignment
            if df_copy[column_name].dtype == "float64" and values.dtype == "object":
                df_copy[column_name] = df_copy[column_name].astype("object")

            df_copy[column_name] = values.values

        self.logger.debug(
            f"Successfully applied {self.__class__.__name__} to column '{column_name}'"
        )
        return df_copy

    def validate_mask(self, df: pd.DataFrame, mask: str) -> tuple[bool, str]:
        """
        Validate if a mask can be executed against the dataframe.

        Args:
            df: Dataframe to test against
            mask: Mask expression to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not mask or not mask.strip():
            return True, ""

        try:
            # Test the query on a small sample
            test_df = df.head(1) if len(df) > 0 else df
            test_df.query(mask)
            self.logger.debug(f"Mask validation successful: {mask}")
            return True, ""
        except Exception as e:
            self.logger.debug(f"Mask validation failed: {mask} - {str(e)}")
            return False, str(e)

    def preview_mask_results(self, df: pd.DataFrame, mask: str) -> dict:
        """
        Preview how many rows would be affected by a mask.

        Args:
            df: Dataframe to test against
            mask: Mask expression

        Returns:
            Dictionary with preview information
        """
        if not mask or not mask.strip():
            return {
                "total_rows": len(df),
                "affected_rows": len(df),
                "percentage": 100.0,
                "mask_valid": True,
            }

        try:
            filtered_df = df.query(mask)
            affected_rows = len(filtered_df)
            total_rows = len(df)
            percentage = (affected_rows / total_rows * 100) if total_rows > 0 else 0

            self.logger.debug(
                f"Mask preview: {affected_rows}/{total_rows} rows ({percentage:.2f}%) would be affected"
            )

            return {
                "total_rows": total_rows,
                "affected_rows": affected_rows,
                "percentage": round(percentage, 2),
                "mask_valid": True,
                "sample_affected_rows": (
                    filtered_df.head(3).to_dict("records") if affected_rows > 0 else []
                ),
            }
        except Exception as e:
            self.logger.debug(f"Mask preview failed: {str(e)}")
            return {
                "total_rows": len(df),
                "affected_rows": 0,
                "percentage": 0.0,
                "mask_valid": False,
                "error": str(e),
            }
