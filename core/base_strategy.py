"""
Base strategy for all data generation strategies.
"""

import pandas as pd
import numpy as np
import logging
from typing import Union, Optional, Any
from abc import ABC, abstractmethod

from utils.intermediate_column import mark_as_intermediate

logger = logging.getLogger(__name__)

class BaseStrategy(ABC):
    """
    Base class for all data generation strategies.
    """
    
    def __init__(self, **kwargs):
        """Initialize the strategy with configuration parameters"""
        self.logger = logging.getLogger(f"data_generator.strategy.{self.__class__.__name__}")
        self.df = kwargs.get('df')
        self.col_name = kwargs.get('col_name')
        self.rows = kwargs.get('rows', 100)
        self.is_intermediate = kwargs.get('intermediate', False)
        self.params = kwargs.get('params', {})
        self.debug = kwargs.get('debug', False)
        self.unique = kwargs.get('unique', False)
        self.shuffle = kwargs.get('shuffle', False)
        # Validate required parameters
        self._validate_params()
        
        if self.debug:
            self.logger.debug(f"Initialized {self.__class__.__name__} with params: {self.params}")
    
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
        
        Args:
            count: Number of values to generate
            
        Returns:
            pd.Series: Generated values
        """
        pass
    
    def apply_to_dataframe(self, df: pd.DataFrame, column_name: str, mask: Optional[str] = None) -> pd.DataFrame:
        """
        Apply strategy to dataframe with optional mask filtering.
        
        Args:
            df: Target dataframe
            column_name: Column to populate
            mask: Optional pandas query string for filtering rows
            
        Returns:
            Updated dataframe
        """
        df_copy = df.copy()
        
        # Initialize column with NaN if it doesn't exist
        if column_name not in df_copy.columns:
            df_copy[column_name] = np.nan
        
        if mask and mask.strip():
            try:
                # Use pandas query to safely evaluate mask
                filtered_df = df_copy.query(mask)
                
                self.logger.debug(f"Mask '{mask}' matched {len(filtered_df)} out of {len(df_copy)} rows")
                
                if len(filtered_df) > 0:
                    # Generate data only for filtered rows
                    values = self.generate_data(len(filtered_df))
                    
                    self.logger.debug(f"Generated {len(values)} values for {len(filtered_df)} filtered rows")
                    
                    # Ensure column has compatible dtype before assignment
                    if df_copy[column_name].dtype == 'float64' and values.dtype == 'object':
                        df_copy[column_name] = df_copy[column_name].astype('object')
                    
                    df_copy.loc[filtered_df.index, column_name] = values.values
                    
                    self.logger.info(f"Applied strategy to {len(filtered_df)} rows matching mask: '{mask}'")
                    self.logger.debug(f"Values assigned to indices: {list(filtered_df.index)}")
                else:
                    self.logger.warning(f"No rows matched mask: '{mask}'. Column '{column_name}' will remain NaN.")
                    
            except Exception as e:
                self.logger.error(f"Failed to evaluate mask '{mask}': {e}")
                # Fallback: apply to all rows
                self.logger.info("Falling back to applying strategy to all rows")
                values = self.generate_data(len(df_copy))
                
                # Ensure column has compatible dtype before assignment
                if df_copy[column_name].dtype == 'float64' and values.dtype == 'object':
                    df_copy[column_name] = df_copy[column_name].astype('object')
                
                df_copy[column_name] = values.values
        else:
            # No mask: apply to all rows
            values = self.generate_data(len(df_copy))
            
            # Ensure column has compatible dtype before assignment
            if df_copy[column_name].dtype == 'float64' and values.dtype == 'object':
                df_copy[column_name] = df_copy[column_name].astype('object')
            
            df_copy[column_name] = values.values
            self.logger.info(f"Applied strategy to all {len(df_copy)} rows")
        
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
            return True, ""
        except Exception as e:
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
                "mask_valid": True
            }
        
        try:
            filtered_df = df.query(mask)
            affected_rows = len(filtered_df)
            total_rows = len(df)
            percentage = (affected_rows / total_rows * 100) if total_rows > 0 else 0
            
            return {
                "total_rows": total_rows,
                "affected_rows": affected_rows,
                "percentage": round(percentage, 2),
                "mask_valid": True,
                "sample_affected_rows": filtered_df.head(3).to_dict('records') if affected_rows > 0 else []
            }
        except Exception as e:
            return {
                "total_rows": len(df),
                "affected_rows": 0,
                "percentage": 0.0,
                "mask_valid": False,
                "error": str(e)
            }