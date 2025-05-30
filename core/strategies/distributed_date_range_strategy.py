"""
Distributed date range strategy for generating date values from multiple weighted date ranges.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

from core.base_strategy import BaseStrategy
from core.strategy_config import DateRangeItem
from exceptions.param_exceptions import InvalidConfigParamException

class DistributedDateRangeStrategy(BaseStrategy):
    """
    Strategy for generating random date values from multiple weighted date ranges.
    """
    
    def _validate_params(self):
        """Validate strategy parameters"""
        if 'ranges' not in self.params:
            raise InvalidConfigParamException("Missing required parameter: ranges")
            
        ranges = self.params['ranges']
        if not isinstance(ranges, list) or not ranges:
            raise InvalidConfigParamException("Ranges must be a non-empty list")
            
        total_distribution = 0
        
        # Validate each range
        for i, range_item in enumerate(ranges):
            
            if not isinstance(range_item, DateRangeItem):
                raise InvalidConfigParamException(f"Range at index {i} {type(range_item)} must be a DateRangeItem")
                
            # Check required fields
            for field in ['start_date', 'end_date', 'format', 'distribution']:
                if not hasattr(range_item, field):
                    raise InvalidConfigParamException(f"Range at index {i} is missing required field: {field}")
            
            # Validate date format
            try:
                datetime.strptime(range_item.start_date, range_item.format)
                datetime.strptime(range_item.end_date, range_item.format)
            except ValueError as e:
                raise InvalidConfigParamException(f"Invalid date format for range at index {i}: {str(e)}")
                
            # Validate distribution
            if not isinstance(range_item.distribution, (int, float)) or range_item.distribution <= 0:
                raise InvalidConfigParamException(f"Distribution for range at index {i} must be positive, got {range_item.distribution}")
                
            total_distribution += range_item.distribution
            
        # Check that distributions sum to 100
        if abs(total_distribution - 100) > 0.01:  # Allow for small floating point error
            raise InvalidConfigParamException(f"Distribution weights must sum to 100, got {total_distribution}")
    
    def _generate_random_date_in_range(self, range_item: DateRangeItem) -> str:
        """Generate a single random date within the specified range"""
        start_date = datetime.strptime(range_item.start_date, range_item.format)
        end_date = datetime.strptime(range_item.end_date, range_item.format)
        
        # Calculate the total number of days between start and end
        total_days = (end_date - start_date).days
        
        # Generate a random number of days to add to start_date
        random_days = random.randint(0, total_days)
        
        # Calculate the random date
        random_date = start_date + timedelta(days=random_days)
        
        # Format the date according to output_format
        return random_date.strftime(range_item.output_format)
    
    def generate_data(self, count: int) -> pd.Series:
        """
        Generate random date values from multiple weighted date ranges.
        
        Args:
            count: Number of values to generate
            
        Returns:
            Series of random date values
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
            f"Generating {count} date values from {len(ranges)} ranges with distribution: {distributions}"
        )
        
        # Generate values for each range
        all_values = []
        for i, range_item in enumerate(ranges):
            range_count = range_counts[i]
            if range_count == 0:
                continue
                
            # Generate date values for this range
            for _ in range(range_count):
                date_value = self._generate_random_date_in_range(range_item)
                all_values.append(date_value)
            

        return pd.Series(all_values) 