"""
Distributed number range strategy for generating numeric values from multiple weighted ranges.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Union

from core.base_strategy import BaseStrategy
from core.strategy_config import RangeItem
class DistributedNumberRangeStrategy(BaseStrategy):
    """
    Strategy for generating random numbers from multiple weighted ranges.
    """
    
    def _validate_params(self):
        """Validate strategy parameters"""
        if 'ranges' not in self.params:
            raise ValueError("Missing required parameter: ranges")
            
        ranges = self.params['ranges']
        if not isinstance(ranges, list) or not ranges:
            raise ValueError("Ranges must be a non-empty list")
            
        total_distribution = 0
        
        # Validate each range
        for i, range_item in enumerate(ranges):
            
            if not isinstance(range_item, RangeItem):
                raise ValueError(f"Range at index {i} {type(range_item)} must be a dictionary")
                
            # Check required fields
            for field in ['start', 'end', 'distribution']:
                if not hasattr(range_item, field):
                    raise ValueError(f"Range at index {i} is missing required field: {field}")
            
            # Validate bounds
            lb = range_item.start
            ub = range_item.end
            dist = range_item.distribution
            
            if not isinstance(lb, (int, float)) or not isinstance(ub, (int, float)):
                raise ValueError(f"Bounds for range at index {i} must be numeric")
                
            if lb >= ub:
                raise ValueError(f"start ({lb}) must be less than end ({ub}) for range at index {i}")
                
            # Validate distribution
            if not isinstance(dist, (int, float)) or dist <= 0:
                raise ValueError(f"Distribution for range at index {i} must be positive, got {dist}")
                
            total_distribution += dist
            
        # Check that distributions sum to 100
        if abs(total_distribution - 100) > 0.01:  # Allow for small floating point error
            raise ValueError(f"Distribution weights must sum to 100, got {total_distribution}")
    
    def generate_data(self, count: int) -> pd.Series:
        """
        Generate random numbers from multiple weighted ranges.
        
        Args:
            count: Number of values to generate
            
        Returns:
            Series of random numbers
        """
        ranges = self.params['ranges']
        
        # Calculate the number of values to generate from each range
        distributions = [r.distribution for r in ranges]
        total_dist = sum(distributions)
        
        # Normalize distributions
        normalized_dist = [d / total_dist for d in distributions]
        
        # Calculate counts for each range
        range_counts = np.random.multinomial(count, normalized_dist)
        
        self.logger.debug(
            f"Generating {count} values from {len(ranges)} ranges with distribution: {distributions}"
        )
        
        # Generate values for each range
        all_values = []
        for i, range_item in enumerate(ranges):
            range_count = range_counts[i]
            if range_count == 0:
                continue
                
            lb = range_item.start
            ub = range_item.end
            
            # Handle integer vs float generation
            if isinstance(lb, int) and isinstance(ub, int):
                # Generate integers
                values = np.random.randint(lb, ub + 1, size=range_count).tolist()
            else:
                # Generate floats
                values = np.random.uniform(lb, ub, size=range_count).tolist()
                
            all_values.extend(values)
            
        # Shuffle the values to mix ranges
        np.random.shuffle(all_values)
        
        return pd.Series(all_values)