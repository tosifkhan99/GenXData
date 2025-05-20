"""
Replacement strategy for replacing specific values with other values.
"""

import pandas as pd
from typing import List, Any, Union

from core.base_strategy import BaseStrategy
from exceptions.param_exceptions import InvalidConfigParamException
class ReplacementStrategy(BaseStrategy):
    """
    Strategy for replacing specific values with other values.
    """
    
    def _validate_params(self):
        """Validate strategy parameters"""
        if 'from_value' not in self.params:
            raise InvalidConfigParamException("Missing required parameter: from_value")
        if 'to_value' not in self.params:
            raise InvalidConfigParamException("Missing required parameter: to_value")
            
        # No specific type validation needed as values can be of any type
    
    def generate_data(self, count: int) -> pd.Series:
        """
        Replace specific values in a column.
        
        This strategy doesn't actually generate new data but rather
        transforms existing data by replacing values.
        
        Args:
            count: Number of values to generate
            
        Returns:
            Series of values with replacements applied
        """
        from_value = self.params['from_value']
        to_value = self.params['to_value']
        self.logger.debug(f"Replacing value '{from_value}' with '{to_value}'")
        values = self.df[self.col_name]
        return values.replace(from_value, to_value) 