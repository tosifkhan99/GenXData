"""
Configuration classes for strategy parameters.

Each strategy has its own configuration class that defines and validates
the parameters required for that strategy.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, fields, field

@dataclass(kw_only=True)
class BaseConfig(ABC):
    """Base configuration class for all strategies"""
    mask: Any = True
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'BaseConfig':
        """
        Create a configuration instance from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration parameters
            
        Returns:
            An instance of the configuration class
        """
        field_names = [f.name for f in fields(cls)]
        filtered_dict = {k: v for k, v in config_dict.items() if k in field_names}
        return cls(**filtered_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to a dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {f.name: getattr(self, f.name) for f in fields(self)}
    
    def validate(self) -> None:
        """
        Validate the configuration parameters.
        Raises ValueError if validation fails.
        """
        pass

@dataclass
class NumberRangeConfig(BaseConfig):
    """Configuration for number range strategy."""
    min_value: float
    max_value: float
    step: float = 1.0
    precision: int = 0
    unique: bool = False
    
    def validate(self) -> None:
        """Validate number range parameters"""
        if self.min_value >= self.max_value:
            raise ValueError(f"Lower bound ({self.min_value}) must be less than upper bound ({self.max_value})")
        if not isinstance(self.min_value, (int, float)) or not isinstance(self.max_value, (int, float)):
            raise ValueError("Bounds must be numeric values")

@dataclass
class RangeItem:
    """Single range definition with distribution weight"""
    lowerbound: int
    upperbound: int
    distribution: int
    
    def validate(self) -> None:
        """Validate range item"""
        if self.lowerbound >= self.upperbound:
            raise ValueError(f"Lower bound ({self.lowerbound}) must be less than upper bound ({self.upperbound})")
        if self.distribution <= 0 or self.distribution > 100:
            raise ValueError(f"Distribution weight ({self.distribution}) must be between 1 and 100")

@dataclass
class DistributedNumberRangeConfig(BaseConfig):
    """Configuration for distributed number range strategy"""
    ranges: List[RangeItem] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DistributedNumberRangeConfig':
        """Create from dictionary with special handling for ranges"""
        config = cls()
        if 'ranges' in config_dict:
            for range_dict in config_dict['ranges']:
                config.ranges.append(RangeItem(**range_dict))
        return config
    
    def validate(self) -> None:
        """Validate distributed number range parameters"""
        if not self.ranges:
            raise ValueError("At least one range must be specified")
            
        # Validate each range
        for i, range_item in enumerate(self.ranges):
            try:
                range_item.validate()
            except ValueError as e:
                raise ValueError(f"Invalid range at index {i}: {str(e)}")
                
        # Check that weights sum to 100
        total_distribution = sum(r.distribution for r in self.ranges)
        if total_distribution != 100:
            raise ValueError(f"Distribution weights must sum to 100, got {total_distribution}")

@dataclass
class DateRangeConfig(BaseConfig):
    """Configuration for date generator strategy"""
    start_date: str
    end_date: str
    format: str = "%Y-%m-%d"
    output_format: str = "%Y-%m-%d"
    
    def validate(self) -> None:
        """Validate date range parameters"""
        from datetime import datetime
        
        try:
            if isinstance(self.start_date, str):
                start = datetime.strptime(self.start_date, self.format)
            else:
                start = self.start_date
            
            if isinstance(self.end_date, str):
                end = datetime.strptime(self.end_date, self.format)
            else:
                end = self.end_date
            
            if start >= end:
                raise ValueError(f"Start date ({self.start_date}) must be before end date ({self.end_date})")
        except ValueError as e:
            if "unconverted data remains" in str(e) or "does not match format" in str(e):
                raise ValueError(f"Invalid date format. Expected {self.format}")
            raise e

@dataclass
class PatternConfig(BaseConfig):
    """Configuration for pattern strategy"""
    regex: str
    
    def validate(self) -> None:
        """Validate pattern parameters"""
        import re
        
        try:
            re.compile(self.regex)
        except re.error:
            raise ValueError(f"Invalid regular expression: {self.regex}")

@dataclass
class SeriesConfig(BaseConfig):
    """Configuration for series strategy"""
    start: int = 1
    step: int = 1
    
    def validate(self) -> None:
        """Validate series parameters"""
        if not isinstance(self.start, (int, float)) or not isinstance(self.step, (int, float)):
            raise ValueError("Start and step must be numeric values")

@dataclass
class ChoiceItem:
    """Choice with weight"""
    value: Any
    weight: int

@dataclass
class DistributedChoiceConfig(BaseConfig):
    """Configuration for distributed choice strategy"""
    choices: Dict[str, int] = field(default_factory=dict)
    
    def validate(self) -> None:
        """Validate distributed choice parameters"""
        if not self.choices:
            raise ValueError("At least one choice must be specified")
            
        # Validate weights
        for choice, weight in self.choices.items():
            if weight <= 0:
                raise ValueError(f"Weight for choice '{choice}' must be positive, got {weight}")

@dataclass
class TimeRangeConfig(BaseConfig):
    """Configuration for time range strategy"""
    start_time: str
    end_time: str
    format: str = "%H:%M:%S"
    
    def validate(self) -> None:
        """Validate time range parameters"""
        from datetime import datetime
        
        try:
            start = datetime.strptime(self.start_time, self.format)
            end = datetime.strptime(self.end_time, self.format)
            
            if start >= end:
                raise ValueError(f"Start time ({self.start_time}) must be before end time ({self.end_time})")
        except ValueError as e:
            if "unconverted data remains" in str(e) or "does not match format" in str(e):
                raise ValueError(f"Invalid time format. Expected {self.format}")
            raise e

@dataclass
class ReplacementConfig(BaseConfig):
    """Configuration for replacement strategy"""
    from_value: Any
    to_value: Any
    
    def validate(self) -> None:
        """Validate replacement parameters"""
        # No specific validation needed
        pass

@dataclass
class ConcatConfig(BaseConfig):
    """Configuration for concatenation strategy"""
    lhs_cols: List[str] = field(default_factory=list)
    rhs_cols: List[str] = field(default_factory=list)
    separator: str = ""
    suffix: str = ""
    prefix: str = ""
    
    def validate(self) -> None:
        """Validate concatenation parameters"""
        if not self.lhs_cols and not self.rhs_cols:
            raise ValueError("At least one column must be specified for concatenation")

@dataclass
class DeleteConfig(BaseConfig):
    def validate(self) -> None:
        pass

# Config factory to create the appropriate config class based on strategy name
def create_config(strategy_name: str, params: Dict[str, Any]) -> BaseConfig:
    """
    Factory function to create a configuration object for the specified strategy.
    
    Args:
        strategy_name: Name of the strategy
        params: Dictionary of parameters for the strategy
        
    Returns:
        Configuration object for the strategy
        
    Raises:
        ValueError: If the strategy is not supported
    """
    strategy_config_map = {
        "RANDOM_NUMBER_RANGE_STRATEGY": lambda p: NumberRangeConfig.from_dict(p.get('range', {})),
        "DISTRIBUTED_NUMBER_RANGE_STRATEGY": lambda p: DistributedNumberRangeConfig.from_dict(p),
        "DATE_GENERATOR_STRATEGY": lambda p: DateRangeConfig.from_dict(p),
        "PATTERN_STRATEGY": lambda p: PatternConfig.from_dict(p),
        "SERIES_STRATEGY": lambda p: SeriesConfig.from_dict(p),
        "DISTRIBUTED_CHOICE_STRATEGY": lambda p: DistributedChoiceConfig.from_dict(p),
        "TIME_RANGE_STRATEGY": lambda p: TimeRangeConfig.from_dict(p),
        "REPLACEMENT_STRATEGY": lambda p: ReplacementConfig.from_dict(p),
        "CONCAT_STRATEGY": lambda p: ConcatConfig.from_dict(p),
        "DELETE_STRATEGY": lambda p: DeleteConfig.from_dict(p),
    }
    
    if strategy_name not in strategy_config_map:
        raise ValueError(f"Unsupported strategy: {strategy_name}")
    
    config = strategy_config_map[strategy_name](params)
    config.validate()
    return config 