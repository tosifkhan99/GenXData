"""
Factory for creating strategy instances based on strategy name.
"""

from typing import Dict, Any, Type
import pandas as pd

from core.base_strategy import BaseStrategy
from core.strategy_config import create_config, BaseConfig
from core.strategy_mapping import get_strategy_class, get_config_class
from exceptions.strategy_exceptions import UnsupportedStrategyException
from utils.intermediate_column import mark_as_intermediate


class StrategyFactory:
    """
    Factory class for creating strategy instances.
    
    This class is responsible for creating strategy instances with validated
    configuration parameters.
    """
    
    def __init__(self):
        """Initialize the factory"""
    
    def create_strategy(self, strategy_name: str, **kwargs) -> BaseStrategy:
        """
        Create a strategy instance.
        
        Args:
            strategy_name: Name of the strategy to create
            **kwargs: Parameters for the strategy
            
        Returns:
            An instance of the strategy
            
        Raises:
            UnsupportedStrategyException: If the strategy cannot be created
        """
        
        try:
            # Get the strategy class from our mapping
            strategy_class = get_strategy_class(strategy_name)
            
            # Get the config class and create a config instance
            config_class = get_config_class(strategy_name)
            
            # Extract and validate params
            params = kwargs.get('params', {})
            config = config_class.from_dict(params)

            config.validate()
            
            # Update kwargs with validated config
            kwargs['params'] = config.to_dict()
            
            # Create and return strategy instance
            return strategy_class(**kwargs)
            
        except Exception as e:
            raise UnsupportedStrategyException(f"Could not create strategy {strategy_name}: {str(e)}")
            
    def execute_strategy(self, strategy: BaseStrategy) -> pd.DataFrame:
        """
        Execute a strategy by generating data and applying it to the dataframe.
        
        Args:
            strategy: The strategy instance to execute
            
        Returns:
            The updated dataframe
        """
        
        # Get mask from params
        mask = strategy.params.get('mask')
        
        # Use the new mask evaluation from base strategy
        strategy.df = strategy.apply_to_dataframe(strategy.df, strategy.col_name, mask)
        
        # Mark as intermediate if needed
        if strategy.is_intermediate:
            strategy.df = mark_as_intermediate(strategy.df, strategy.col_name)
        
        return strategy.df 