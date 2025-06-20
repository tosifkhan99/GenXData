"""
Series strategy for generating sequential numeric values.
"""

import pandas as pd
import numpy as np
from typing import List, Any

from core.base_strategy import BaseStrategy
from exceptions.param_exceptions import InvalidConfigParamException

class SeriesStrategy(BaseStrategy):
    """
    Strategy for generating sequential numeric values.
    """
    
    def _validate_params(self):
        """Validate strategy parameters"""
        if 'start' not in self.params:
            raise InvalidConfigParamException("Missing required parameter: start")
            
        # Validate that start is numeric
        if not isinstance(self.params['start'], (int, float)):
            raise InvalidConfigParamException("Start value must be numeric")
        
        # Validate step if provided
        if 'step' in self.params:
            try:
                float(self.params['step'])
            except ValueError:
                raise InvalidConfigParamException("Step value must be numeric")
    
    def generate_data(self, count: int) -> pd.Series:
        """
        Generate sequential numeric values.
        
        Args:
            count: Number of values to generate
            
        Returns:
            pd.Series: Generated values
        """
        self.logger.debug(f"Generating {count} sequential values")
        
        # Get parameters
        if isinstance(self.params['start'], float):
            # Set precision for floating point numbers
            from decimal import Decimal, getcontext
            getcontext().prec = 2

            self.logger.debug(f"Setting precision to {getcontext().prec}")
            self.logger.warning(f"Generation with floating point numbers and a step might leads to slower generation as it requires more precision calculations")

            start = Decimal(self.params['start'])
            step = Decimal(self.params.get('step', 0.1))
        else:
            start = int(self.params['start'])
            step = int(self.params.get('step', 1))
            
        
        # Generate the sequence
        values = np.arange(start, start + (count * step), step)
        return pd.Series(values) 