"""
Concat strategy for concatenating values from multiple columns.
"""

import pandas as pd
from typing import List, Any

from core.base_strategy import BaseStrategy

class ConcatStrategy(BaseStrategy):
    """
    Strategy for concatenating values from multiple columns.
    """
    
    def _validate_params(self):
        """Validate strategy parameters"""
        if 'lhs_cols' not in self.params:
            raise ValueError("Missing required parameter: lhs_cols")
        if 'rhs_cols' not in self.params:
            raise ValueError("Missing required parameter: rhs_cols")
            
        # Validate that all columns exist in the dataframe
        for col in self.params['lhs_cols'] + self.params['rhs_cols']:
            if col not in self.df.columns:
                raise ValueError(f"Column '{col}' not found in dataframe")
    
    def generate_data(self, count: int) -> pd.Series:
        """
        Concatenate values from multiple columns.
        
        Args:
            count: Number of values to generate (not used in this strategy)
            
        Returns:
            Series of concatenated values
        """
        self.logger.debug("Concatenating values from multiple columns")
        
        # Get columns to concatenate
        lhs_cols = self.params['lhs_cols']
        rhs_cols = self.params['rhs_cols']
        prefix = self.params.get('prefix', '')
        suffix = self.params.get('suffix', '')
        
        # Concatenate values
        lhs_values = self.df[lhs_cols].apply(lambda x: ''.join(x.astype(str)), axis=1)
        rhs_values = self.df[rhs_cols].apply(lambda x: ''.join(x.astype(str)), axis=1)
        
        # Combine with separator if provided
        separator = self.params.get('separator', '')
        return prefix + lhs_values + separator + rhs_values + suffix 