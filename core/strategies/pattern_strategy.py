"""
Pattern strategy for generating random strings matching a regex or pattern.
"""

import pandas as pd
import rstr
from typing import List, Any
import re
import random
import string
import numpy as np
from core.base_strategy import BaseStrategy

class PatternStrategy(BaseStrategy):
    """
    Strategy for generating random strings matching a regex or pattern.
    """
    
    def _validate_params(self):
        """Validate strategy parameters"""
        if 'regex' not in self.params:
            raise ValueError("Missing required parameter: regex")
            
        # Validate that the regex pattern is valid
        try:
            re.compile(self.params['regex'])
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {str(e)}")
    
    def generate_data(self, count: int) -> pd.Series:
        """
        Generate random strings matching the regex pattern.
        
        Args:
            count: Number of strings to generate
            
        Returns:
            pd.Series: Generated strings
        """
        self.logger.debug(f"Generating {count} random strings matching pattern: {self.params['regex']}")
        
        # Get regex pattern
        pattern = self.params['regex']
        max_attempts = count * 3  # tries 3 times more than the count, to come up with unique strings
        attempts = 0

        if self.unique:
            self.logger.warning("unique is not recommended for pattern strategy, it may take a long time to generate unique strings, use with caution.")
            result = set()
            while len(result) < count and attempts < max_attempts:
                attempts += 1
                value = rstr.xeger(pattern)
                
                # Check if it matches the pattern
                if value not in result:
                    result.add(value)
        
            if len(result) < count:
                remaining = count - len(result)
                self.logger.warning(f"Could not generate {remaining} strings matching pattern: {pattern}, generated {len(result)} strings instead, repeating the same strings {remaining} times")
                
                result = list(result)
                result.extend([np.random.choice(list(result)) for _ in range(remaining)])
        else:
            result = [rstr.xeger(pattern) for _ in range(count)]
        return pd.Series(result) 