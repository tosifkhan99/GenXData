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
        
        # Get LHS column and prepare its data as string for concatenation
        if self.df[self.params['lhs_col']].dtype != 'str':
            lhs_data_as_string = self.df[self.params['lhs_col']].astype(str)
        else:
            lhs_data_as_string = self.df[self.params['lhs_col']]
        
        if self.df[self.params['rhs_col']].dtype != 'str':
            rhs_data_as_string = self.df[self.params['rhs_col']].astype(str)
        else:
            rhs_data_as_string = self.df[self.params['rhs_col']]
        

        prefix = self.params.get('prefix', '')
        suffix = self.params.get('suffix', '')
        separator = self.params.get('separator', '')
        
        return prefix + lhs_data_as_string + separator + rhs_data_as_string + suffix 