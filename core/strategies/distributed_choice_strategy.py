"""
Distributed choice strategy for generating values based on weighted choices.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any

from core.base_strategy import BaseStrategy
from exceptions.param_exceptions import InvalidConfigParamException 
class DistributedChoiceStrategy(BaseStrategy):
    """
    Strategy for generating values based on weighted choices.
    """
    
    def _validate_params(self):
        """Validate strategy parameters"""
        if 'choices' not in self.params:
            raise InvalidConfigParamException("Missing required parameter: choices")
            
        choices = self.params['choices']
        if not isinstance(choices, dict) or not choices:
            raise InvalidConfigParamException("Choices must be a non-empty dictionary")
            
        # Validate that weights are positive
        for choice, weight in choices.items():
            if not isinstance(weight, (int, float)) or weight <= 0:
                raise InvalidConfigParamException(f"Weight for choice '{choice}' must be positive, got {weight}")
    
    def generate_data(self, count: int) -> pd.Series:
        """
        Generate random values based on weighted choices.
        
        Args:
            count: Number of values to generate
            
        Returns:
            Series of chosen values
        """
        choices_dict = self.params['choices']
        
        # Extract choices and weights
        choices = list(choices_dict.keys())
        weights = list(choices_dict.values())
        
        
        # Generate random choices based on weights
        values = []
        
        # Calculate total weight
        total_weight = sum(weights)
        
        
        # Generate values proportionally based on weights
        for choice, weight in choices_dict.items():
            # Calculate how many values this choice should get
            proportion = weight / total_weight
            num_values = int(proportion * count)
            
            
            # Add the values for this choice
            for _ in range(num_values):
                values.append(choice)
        
        
        # Handle any remaining values due to rounding
        while len(values) < count:
            # Add random choice based on weights
            choice = np.random.choice(choices, p=[w/total_weight for w in weights])
            values.append(choice)
        

        
        return pd.Series(values) 