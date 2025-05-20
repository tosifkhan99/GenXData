"""
Base strategy class defining the interface for all data generation strategies.
"""

import pandas as pd
import logging
from abc import ABC, abstractmethod

from utils.intermediate_column import mark_as_intermediate

class BaseStrategy(ABC):
    """
    Abstract base class for all data generation strategies.
    
    This class defines the interface that all strategies must implement,
    providing a consistent way to generate data and manage strategy parameters.
    """
    mask: bool
    
    def __init__(self, **kwargs):
        """Initialize the strategy with configuration parameters"""
        self.logger = logging.getLogger(f"data_generator.strategy.{self.__class__.__name__}")
        self.df = kwargs.get('df')
        self.col_name = kwargs.get('col_name')
        self.rows = kwargs.get('rows', 100)
        self.is_intermediate = kwargs.get('intermediate', False)
        self.params = kwargs.get('params', {})
        self.debug = kwargs.get('debug', False)
        self.unique = kwargs.get('unique', False)
        self.shuffle = kwargs.get('shuffle', False)
        # Validate required parameters
        self._validate_params()
        
        if self.debug:
            self.logger.debug(f"Initialized {self.__class__.__name__} with params: {self.params}")
    
    @abstractmethod
    def _validate_params(self):
        """
        Validate the parameters required by this strategy.
        Raises InvalidConfigParamException if required parameters are missing or invalid.
        """
        pass
    
    @abstractmethod
    def generate_data(self, count: int) -> pd.Series:
        """
        Generate the data based on strategy configuration.
        
        Args:
            count: Number of values to generate
            
        Returns:
            pd.Series: Generated values
        """
        pass