"""
Time range strategy for generating random time values within a range.
"""

import pandas as pd
from typing import List, Any
from datetime import datetime, time
import random

from core.base_strategy import BaseStrategy
from utils.time_generator import timeGenerator
from exceptions.param_exceptions import InvalidConfigParamException
class TimeRangeStrategy(BaseStrategy):
    """
    Strategy for generating random time values within a specified range.
    """
    
    def _validate_params(self):
        """Validate strategy parameters"""
        if 'start_time' not in self.params:
            raise InvalidConfigParamException("Missing required parameter: start_time")
        if 'end_time' not in self.params:
            raise InvalidConfigParamException("Missing required parameter: end_time")
            
        # Validate time formats if provided
        if 'input_format' in self.params:
            try:
                datetime.strptime(self.params['start_time'], self.params['input_format'])
                datetime.strptime(self.params['end_time'], self.params['input_format'])
            except ValueError as e:
                raise InvalidConfigParamException(f"Invalid time format: {str(e)}")
    
    def generate_data(self, count: int) -> pd.Series:
        """
        Generate random time values within the specified range.
        
        Args:
            count: Number of time values to generate
            
        Returns:
            pd.Series: Generated time values
        """
        
        # Get time generation parameters
        params = {
            'start_time': self.params['start_time'],
            'end_time': self.params['end_time']
        }
        
        if 'input_format' in self.params:
            params['input_format'] = self.params['input_format']
        if 'output_format' in self.params:
            params['output_format'] = self.params['output_format']
            
        # Generate the time values
        times = []
        for _ in range(count):
            # Parse start and end times
            if 'input_format' in params:
                start = datetime.strptime(params['start_time'], params['input_format']).time()
                end = datetime.strptime(params['end_time'], params['input_format']).time()
            else:
                start = datetime.strptime(params['start_time'], '%H:%M:%S').time()
                end = datetime.strptime(params['end_time'], '%H:%M:%S').time()
            
            # Generate random time between start and end
            start_seconds = start.hour * 3600 + start.minute * 60 + start.second
            end_seconds = end.hour * 3600 + end.minute * 60 + end.second
            
            if end_seconds < start_seconds:
                end_seconds += 24 * 3600  # Add 24 hours if end time is on next day
                
            random_seconds = random.randint(start_seconds, end_seconds)
            hours = random_seconds // 3600
            minutes = (random_seconds % 3600) // 60
            seconds = random_seconds % 60
            
            random_time = time(hours % 24, minutes, seconds)
            
            # Format the time
            if 'output_format' in params:
                time_str = random_time.strftime(params['output_format'])
            else:
                time_str = random_time.strftime('%H:%M:%S')
                
            times.append(time_str)
            
        return pd.Series(times) 