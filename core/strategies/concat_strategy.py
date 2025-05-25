"""
Concat strategy for concatenating values from multiple columns.
"""

import pandas as pd
from typing import List, Any

from core.base_strategy import BaseStrategy
from exceptions.param_exceptions import InvalidConfigParamException
class ConcatStrategy(BaseStrategy):
    """
    Strategy for concatenating values from multiple columns.
    """
    
    def _validate_params(self):
        """Validate strategy parameters"""
        if 'lhs_col' not in self.params:
            raise InvalidConfigParamException("Missing required parameter: lhs_col")
        if 'rhs_col' not in self.params:
            raise InvalidConfigParamException("Missing required parameter: rhs_col")

        # Validate that all columns exist in the dataframe
        for col in [self.params['lhs_col'], self.params['rhs_col']]:
            if col not in self.df.columns:
                raise ValueError(f"Column {col} not found in dataframe")
    
    def generate_data(self, count: int) -> pd.Series:
        """
        Concatenate values from multiple columns.
        
        Args:
            count: Number of values to generate (not used in this strategy)
            
        Returns:
            Series of concatenated values
        """
        self.logger.debug("Concatenating values from multiple columns")
        
        # Get LHS column and prepare its data as string for concatenation
        lhs_col = self.params['lhs_col']
        # Ensure data from lhs_col is string. Note: a similar step will be needed for rhs_col.
        # The actual concatenation logic should use this processed series (and a similarly processed one for RHS).
        lhs_data_as_string = self.df[lhs_col].astype(str)
        rhs_col = self.params['rhs_col']
        prefix = self.params.get('prefix', '')
        suffix = self.params.get('suffix', '')
        # Concatenate values
        lhs_values = self.df[lhs_col]
        rhs_values = self.df[rhs_col]
        
        # Combine with separator if provided
        separator = self.params.get('separator', '')
        return prefix + lhs_values + separator + rhs_values + suffix 