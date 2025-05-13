"""
Number range strategy for generating random numbers within a range.
"""

import pandas as pd
import numpy as np
from typing import List, Any

from core.base_strategy import BaseStrategy

class NumberRangeStrategy(BaseStrategy):
    """
    Strategy for generating random numbers within a specified range.
    """
    
    def _validate_params(self):
        """Validate strategy parameters"""
        if 'lowerbound' not in self.params:
            raise ValueError("Missing required parameter: lowerbound")
        if 'upperbound' not in self.params:
            raise ValueError("Missing required parameter: upperbound")
            
        # Validate that bounds are numeric
        try:
            lower = float(self.params['lowerbound'])
            upper = float(self.params['upperbound'])
        except ValueError:
            raise ValueError("Bounds must be numeric")
            
        # Validate that lower bound is less than upper bound
        if lower >= upper:
            raise ValueError(f"Lower bound ({lower}) must be less than upper bound ({upper})")
    
    def generate_data(self, count: int) -> pd.Series:
        """
        Generate random numbers within the specified range.
        
        Args:
            count: Number of values to generate
            
        Returns:
            pd.Series: Generated values
        """
        self.logger.debug(f"Generating {count} random numbers")
        
        # Get parameters
        lower = float(self.params['lowerbound'])
        upper = float(self.params['upperbound'])
        
        # Generate random numbers
        values = np.random.uniform(lower, upper, count)
        
        # Convert to integers if both bounds are integers
        if isinstance(self.params['lowerbound'], int) and isinstance(self.params['upperbound'], int):
            values = values.astype(int)
            
        return pd.Series(values) 