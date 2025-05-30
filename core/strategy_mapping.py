"""
Mapping between strategy names, strategy classes, and configuration classes.
"""

from typing import Dict, Tuple, Type, List, Any

from core.base_strategy import BaseStrategy
from core.strategy_config import (
    BaseConfig,
    NumberRangeConfig,
    DistributedNumberRangeConfig,
    DateRangeConfig,
    PatternConfig,
    SeriesConfig,
    DistributedChoiceConfig,
    TimeRangeConfig,
    DistributedTimeRangeConfig,
    ReplacementConfig,
    ConcatConfig
)

from core.strategies.number_range_strategy import NumberRangeStrategy
from core.strategies.distributed_number_range_strategy import DistributedNumberRangeStrategy
from core.strategies.date_generator_strategy import DateGeneratorStrategy
from core.strategies.pattern_strategy import PatternStrategy
from core.strategies.series_strategy import SeriesStrategy
from core.strategies.distributed_choice_strategy import DistributedChoiceStrategy
from core.strategies.time_range_strategy import TimeRangeStrategy
from core.strategies.distributed_time_range_strategy import DistributedTimeRangeStrategy
from core.strategies.replacement_strategy import ReplacementStrategy
from core.strategies.concat_strategy import ConcatStrategy
from core.strategies.random_name_strategy import RandomNameStrategy
from core.strategies.delete_strategy import DeleteStrategy
from exceptions.strategy_exceptions import UnsupportedStrategyException

# Map strategy names to classes and their config classes
STRATEGY_MAP: Dict[str, Tuple[Type[BaseStrategy], Type[BaseConfig]]] = {
    "RANDOM_NUMBER_RANGE_STRATEGY": (NumberRangeStrategy, NumberRangeConfig),
    "DISTRIBUTED_NUMBER_RANGE_STRATEGY": (DistributedNumberRangeStrategy, DistributedNumberRangeConfig),
    "DATE_GENERATOR_STRATEGY": (DateGeneratorStrategy, DateRangeConfig),
    "PATTERN_STRATEGY": (PatternStrategy, PatternConfig),
    "SERIES_STRATEGY": (SeriesStrategy, SeriesConfig),
    "DISTRIBUTED_CHOICE_STRATEGY": (DistributedChoiceStrategy, DistributedChoiceConfig),
    "TIME_RANGE_STRATEGY": (TimeRangeStrategy, TimeRangeConfig),
    "DISTRIBUTED_TIME_RANGE_STRATEGY": (DistributedTimeRangeStrategy, DistributedTimeRangeConfig),
    "REPLACEMENT_STRATEGY": (ReplacementStrategy, ReplacementConfig),
    "CONCAT_STRATEGY": (ConcatStrategy, ConcatConfig),
    "RANDOM_NAME_STRATEGY": (RandomNameStrategy, BaseConfig),  # Uses base config since no specific params
    "DELETE_STRATEGY": (DeleteStrategy, BaseConfig),  # Uses base config since no specific params
}

def get_all_strategy_names() -> List[str]:
    return list(STRATEGY_MAP.keys())

def get_all_strategy_schemas() -> List[Dict[str, Any]]:
    schemas = {}
    for strategy_name in get_all_strategy_names():
        schemas[strategy_name] = STRATEGY_MAP[strategy_name][1].__doc__
    return schemas

def get_strategy_class(strategy_name: str) -> Type[BaseStrategy]:
    """
    Get the strategy class for the given strategy name.
    
    Args:
        strategy_name: Name of the strategy
        
    Returns:
        Strategy class
        
    Raises:
        UnsupportedStrategyException: If the strategy is not supported
    """
    if strategy_name not in STRATEGY_MAP:
        raise UnsupportedStrategyException(f"Unsupported strategy: {strategy_name}")
        
    return STRATEGY_MAP[strategy_name][0]

def get_config_class(strategy_name: str) -> Type[BaseConfig]:
    """
    Get the configuration class for the given strategy name.
    
    Args:
        strategy_name: Name of the strategy
        
    Returns:
        Configuration class
        
    Raises:
        UnsupportedStrategyException: If the strategy is not supported
    """
    if strategy_name not in STRATEGY_MAP:
        raise UnsupportedStrategyException(f"Unsupported strategy: {strategy_name}")
        
    return STRATEGY_MAP[strategy_name][1] 