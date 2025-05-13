"""
Date generator strategy for generating random dates within a range.
"""

import pandas as pd
from typing import List, Any
from datetime import datetime

from core.base_strategy import BaseStrategy
from utils.date_generator import generate_random_date

class DateGeneratorStrategy(BaseStrategy):
    """
    Strategy for generating random dates within a specified range.
    """
    
    def _validate_params(self):
        """Validate strategy parameters"""
        if 'start_date' not in self.params:
            raise ValueError("Missing required parameter: start_date")
        if 'end_date' not in self.params:
            raise ValueError("Missing required parameter: end_date")
            
        # Validate date formats if provided
        if 'input_format' in self.params:
            try:
                datetime.strptime(self.params['start_date'], self.params['input_format'])
                datetime.strptime(self.params['end_date'], self.params['input_format'])
            except ValueError as e:
                raise ValueError(f"Invalid date format: {str(e)}")
    
    def generate_data(self, count: int) -> pd.Series:
        """
        Generate random dates within the specified range.
        
        Args:
            count: Number of dates to generate
            
        Returns:
            pd.Series: Generated dates
        """
        self.logger.debug(f"Generating {count} random dates")
        
        # Get date generation parameters
        
        if isinstance(self.params['start_date'], str):
            start_date = datetime.strptime(self.params['start_date'], self.params['format'])
        else:
            start_date = self.params['start_date']
        if isinstance(self.params['end_date'], str):
            end_date = datetime.strptime(self.params['end_date'], self.params['format'])
        else:
            end_date = self.params['end_date']

        params = {
            'start_date': start_date,
            'end_date': end_date,
        }
        
        if 'output_format' in self.params:
            params['output_format'] = self.params['output_format']
        else:
            params['output_format'] = '%Y-%m-%d'
            
        # Generate the dates
        dates = [generate_random_date(**params) for _ in range(count)]
        return pd.Series(dates) 