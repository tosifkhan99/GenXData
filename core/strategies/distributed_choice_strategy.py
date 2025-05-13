"""
Distributed choice strategy for generating values based on weighted choices.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any

from core.base_strategy import BaseStrategy

class DistributedChoiceStrategy(BaseStrategy):
    """
    Strategy for generating values based on weighted choices.
    """
    
    def _validate_params(self):
        """Validate strategy parameters"""
        if 'choices' not in self.params:
            raise ValueError("Missing required parameter: choices")
            
        choices = self.params['choices']
        if not isinstance(choices, dict) or not choices:
            raise ValueError("Choices must be a non-empty dictionary")
            
        # Validate that weights are positive
        for choice, weight in choices.items():
            if not isinstance(weight, (int, float)) or weight <= 0:
                raise ValueError(f"Weight for choice '{choice}' must be positive, got {weight}")
    
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
        
        self.logger.debug(
            f"Generating {count} choices from {len(choices)} options with weights: {weights}"
        )
        
        # Generate random choices based on weights
        values= []
        # more accurate than np.random.choice
        for k, v in choices_dict.items():
            for _ in range(int(v*(count/100))):
                values.append(k)
        
        return pd.Series(values) 