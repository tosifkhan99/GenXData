"""
Random name strategy for generating realistic person names.
"""

import random
import pandas as pd
from typing import List, Any

from core.base_strategy import BaseStrategy
from utils.get_names import get_name

class RandomNameStrategy(BaseStrategy):
    """
    Strategy for generating random person names.
    """
    
    def _validate_params(self):
        """Validate strategy parameters"""
        # This strategy doesn't require any specific parameters
        pass
    
    def generate_data(self, count: int) -> pd.Series:
        """
        Generate random person names.
        
        Args:
            count: Number of values to generate
            
        Returns:
            Series of random names
        """
        self.logger.debug(f"Generating {count} random names")
        
        result = []
        for _ in range(count):
            name = get_name()
            result.append(name)
            
        return pd.Series(result) 