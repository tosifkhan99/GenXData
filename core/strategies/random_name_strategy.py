"""
Random name strategy for generating realistic person names using the names package.
"""

import pandas as pd
from typing import List, Any, Optional

from core.base_strategy import BaseStrategy
from utils.get_names import get_name, apply_case_formatting
from exceptions.param_exceptions import InvalidConfigParamException

class RandomNameStrategy(BaseStrategy):
    """
    Strategy for generating random person names with configurable parameters.
    Supports first names, last names, full names, gender filtering, and case formatting.
    """
    
    def _validate_params(self):
        """Validate strategy parameters"""
        # Set defaults if not provided
        if 'name_type' not in self.params:
            self.params['name_type'] = 'first'
        if 'gender' not in self.params:
            self.params['gender'] = 'any'
        if 'case' not in self.params:
            self.params['case'] = 'title'
            
        # Validate name_type
        valid_name_types = ['first', 'last', 'full']
        if self.params['name_type'] not in valid_name_types:
            raise InvalidConfigParamException(f"Invalid name_type: {self.params['name_type']}. Must be one of {valid_name_types}")
            
        # Validate gender
        valid_genders = ['male', 'female', 'any']
        if self.params['gender'] not in valid_genders:
            raise InvalidConfigParamException(f"Invalid gender: {self.params['gender']}. Must be one of {valid_genders}")
            
        # Validate case
        valid_cases = ['title', 'upper', 'lower']
        if self.params['case'] not in valid_cases:
            raise InvalidConfigParamException(f"Invalid case: {self.params['case']}. Must be one of {valid_cases}")
    
    def generate_data(self, count: int) -> pd.Series:
        """
        Generate random person names based on configuration.
        
        Args:
            count: Number of names to generate
            
        Returns:
            Series of random names
        """
        name_type = self.params['name_type']
        gender = None if self.params['gender'] == 'any' else self.params['gender']
        case_format = self.params['case']
        
        self.logger.debug(f"Generating {count} random names (type: {name_type}, gender: {gender or 'any'}, case: {case_format})")
        
        result = []
        for _ in range(count):
            # Generate the name using the names package
            name = get_name(name_type=name_type, gender=gender)
            
            # Apply case formatting
            formatted_name = apply_case_formatting(name, case_format)
            
            result.append(formatted_name)
            
        self.logger.info(f"Generated {len(result)} {name_type} names")
        return pd.Series(result) 