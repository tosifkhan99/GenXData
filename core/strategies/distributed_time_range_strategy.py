"""
Distributed time range strategy for generating time values from multiple weighted time ranges.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, time, timedelta
import random

from core.base_strategy import BaseStrategy
from core.strategy_config import TimeRangeItem
from exceptions.param_exceptions import InvalidConfigParamException

class DistributedTimeRangeStrategy(BaseStrategy):
    """
    Strategy for generating random time values from multiple weighted time ranges.
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
            
            if not isinstance(range_item, TimeRangeItem):
                raise InvalidConfigParamException(f"Range at index {i} {type(range_item)} must be a TimeRangeItem")
                
            # Check required fields
            for field in ['start', 'end', 'format', 'distribution']:
                if not hasattr(range_item, field):
                    raise InvalidConfigParamException(f"Range at index {i} is missing required field: {field}")
            
            # Validate time format
            try:
                datetime.strptime(range_item.start, range_item.format)
                datetime.strptime(range_item.end, range_item.format)
            except ValueError as e:
                raise InvalidConfigParamException(f"Invalid time format for range at index {i}: {str(e)}")
                
            # Validate distribution
            if not isinstance(range_item.distribution, (int, float)) or range_item.distribution <= 0:
                raise InvalidConfigParamException(f"Distribution for range at index {i} must be positive, got {range_item.distribution}")
                
            total_distribution += range_item.distribution
            
        # Check that distributions sum to 100
        if abs(total_distribution - 100) > 0.01:  # Allow for small floating point error
            raise InvalidConfigParamException(f"Distribution weights must sum to 100, got {total_distribution}")
    
    def _time_to_seconds(self, time_str: str, format_str: str) -> int:
        """Convert time string to seconds since midnight"""
        time_obj = datetime.strptime(time_str, format_str).time()
        return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
    
    def _seconds_to_time_str(self, seconds: int, format_str: str) -> str:
        """Convert seconds since midnight to time string"""
        # Handle overflow (next day)
        seconds = seconds % (24 * 3600)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        time_obj = time(hours, minutes, secs)
        return time_obj.strftime(format_str)
    
    def _generate_random_time_in_range(self, range_item: TimeRangeItem) -> str:
        """Generate a single random time within the specified range"""
        start_seconds = self._time_to_seconds(range_item.start, range_item.format)
        end_seconds = self._time_to_seconds(range_item.end, range_item.format)
        
        # Handle overnight ranges (e.g., 22:00:00 to 06:00:00)
        if end_seconds <= start_seconds:
            # This is an overnight range
            # Pick either before midnight or after midnight
            if random.choice([True, False]):
                # Before midnight: start_seconds to 24*3600
                random_seconds = random.randint(start_seconds, 24 * 3600 - 1)
            else:
                # After midnight: 0 to end_seconds
                random_seconds = random.randint(0, end_seconds)
        else:
            # Normal range within the same day
            random_seconds = random.randint(start_seconds, end_seconds)
        
        return self._seconds_to_time_str(random_seconds, range_item.format)
    
    def generate_data(self, count: int) -> pd.Series:
        """
        Generate random time values from multiple weighted time ranges.
        
        Args:
            count: Number of values to generate
            
        Returns:
            Series of random time values
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
            f"Generating {count} time values from {len(ranges)} ranges with distribution: {distributions}"
        )
        
        # Generate values for each range
        all_values = []
        for i, range_item in enumerate(ranges):
            range_count = range_counts[i]
            if range_count == 0:
                continue
                
            # Generate time values for this range
            for _ in range(range_count):
                time_value = self._generate_random_time_in_range(range_item)
                all_values.append(time_value)
            
        
        return pd.Series(all_values) 