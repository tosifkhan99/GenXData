"""
Delete strategy for removing values from a column.
"""

import numpy as np
import pandas as pd
from typing import List, Any

from core.base_strategy import BaseStrategy
from exceptions.param_exceptions import InvalidConfigParamException
class DeleteStrategy(BaseStrategy):
    """
    Strategy for deleting/nullifying values in a column.
    """
    
    def _validate_params(self):
        """Validate strategy parameters"""
        if 'mask' not in self.params:
            raise InvalidConfigParamException("Missing required parameter: mask")
            
        # Validate that the mask is a string (condition)
        if not isinstance(self.params['mask'], str):
            raise InvalidConfigParamException("Mask must be a string condition")
    
    def generate_data(self, count: int) -> pd.Series:
        """
        Generate a Series of None values to represent deletion.
        
        Args:
            count: Number of values to generate
            
        Returns:
            Series of None values
        """
        self.logger.debug(f"Generating {count} None values for deletion")
        
        # Return None values for the masked rows
        return pd.Series([None] * count)
