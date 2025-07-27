"""
Configuration classes for strategy parameters.

Each strategy has its own configuration class that defines and validates
the parameters required for that strategy.
"""

from abc import ABC
from dataclasses import dataclass, field, fields
from typing import Any

from exceptions.param_exceptions import InvalidConfigParamException
from exceptions.strategy_exceptions import UnsupportedStrategyException


@dataclass(kw_only=True)
class BaseConfig(ABC):
    """Base configuration class for all strategies"""

    mask: str = ""

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "BaseConfig":
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

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def validate(self) -> None:
        """
        Validate the configuration parameters.
        Raises InvalidConfigParamException if validation fails.
        """
        pass


@dataclass
class NumberRangeConfig(BaseConfig):
    """Configuration for number range strategy."""

    start: float = 0
    end: float = 99
    step: float = 1
    precision: int = 0
    unique: bool = False

    def validate(self) -> None:
        """Validate number range parameters"""
        if self.start >= self.end:
            raise InvalidConfigParamException(
                f"start ({self.start}) must be less than end ({self.end})"
            )
        if not isinstance(self.start, (int, float)) or not isinstance(
            self.end, (int, float)
        ):
            raise InvalidConfigParamException("Bounds must be numeric values")


@dataclass
class RangeItem:
    """Single range definition with distribution weight"""

    start: int = 10
    end: int = 50
    distribution: int = 100

    def __init__(self, start: int, end: int, distribution: int):
        self.start = start
        self.end = end
        self.distribution = distribution

    def validate(self) -> None:
        """Validate range item"""
        if self.start >= self.end:
            raise InvalidConfigParamException(
                f"start ({self.start}) must be less than end ({self.end})"
            )
        if self.distribution <= 0 or self.distribution > 100:
            raise InvalidConfigParamException(
                f"Distribution weight ({self.distribution}) must be between 1 and 100"
            )


@dataclass
class DistributedNumberRangeConfig(BaseConfig):
    """Configuration for distributed number range strategy"""

    ranges: list[RangeItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "DistributedNumberRangeConfig":
        """Create from dictionary with special handling for ranges"""
        config = cls()
        if "ranges" in config_dict:
            for range_dict in config_dict["ranges"]:
                config.ranges.append(RangeItem(**range_dict))
        return config

    def validate(self) -> None:
        """Validate distributed number range parameters"""
        if not self.ranges:
            raise InvalidConfigParamException("At least one range must be specified")

        # Validate each range
        for i, range_item in enumerate(self.ranges):
            try:
                range_item.validate()
            except InvalidConfigParamException as e:
                raise InvalidConfigParamException(
                    f"Invalid range at index {i}: {str(e)}"
                )

        # Check that weights sum to 100
        total_distribution = sum(r.distribution for r in self.ranges)
        if total_distribution != 100:
            raise InvalidConfigParamException(
                f"Distribution weights must sum to 100, got {total_distribution}"
            )


@dataclass
class DateRangeConfig(BaseConfig):
    """Configuration for date generator strategy"""

    start_date: str = "2020-1-31"
    end_date: str = "2020-12-31"
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
                raise InvalidConfigParamException(
                    f"Start date ({self.start_date}) must be before end date ({self.end_date})"
                )
        except ValueError as e:
            if "unconverted data remains" in str(e) or "does not match format" in str(
                e
            ):
                raise InvalidConfigParamException(
                    f"Invalid date format. Expected {self.format}"
                )
            raise e


@dataclass
class PatternConfig(BaseConfig):
    """Configuration for pattern strategy"""

    regex: str = r"^[A-Za-z0-9]+$"

    def validate(self) -> None:
        """Validate pattern parameters"""
        import re

        try:
            re.compile(self.regex)
        except re.error:
            raise InvalidConfigParamException(
                f"Invalid regular expression: {self.regex}"
            )


@dataclass
class SeriesConfig(BaseConfig):
    """Configuration for series strategy"""

    start: int = 1
    step: int = 1

    def validate(self) -> None:
        """Validate series parameters"""
        if not isinstance(self.start, (int, float)) or not isinstance(
            self.step, (int, float)
        ):
            raise InvalidConfigParamException("Start and step must be numeric values")


@dataclass
class ChoiceItem:
    """Choice with weight"""

    value: Any
    weight: int


@dataclass
class DistributedChoiceConfig(BaseConfig):
    """Configuration for distributed choice strategy"""

    choices: dict[str, int] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate distributed choice parameters"""
        if not self.choices:
            raise InvalidConfigParamException("At least one choice must be specified")

        # Validate weights
        for choice, weight in self.choices.items():
            if weight <= 0:
                raise InvalidConfigParamException(
                    f"Weight for choice '{choice}' must be positive, got {weight}"
                )


@dataclass
class TimeRangeItem:
    """Single time range definition with distribution weight"""

    start: str = "00:00:00"
    end: str = "23:59:59"
    format: str = "%H:%M:%S"
    distribution: int = 100

    def __init__(
        self, start: str, end: str, format: str = "%H:%M:%S", distribution: int = 100
    ):
        self.start = start
        self.end = end
        self.format = format
        self.distribution = distribution

    def validate(self) -> None:
        """Validate time range item"""
        from datetime import datetime

        try:
            start_time = datetime.strptime(self.start, self.format)
            end_time = datetime.strptime(self.end, self.format)

            # Special handling for overnight time ranges (e.g., 22:00:00 to 06:00:00)
            if start_time >= end_time:
                # Check if this could be an overnight range
                if (
                    self.start > self.end
                ):  # String comparison for times like "22:00:00" > "06:00:00"
                    # This is likely an overnight range, which is valid
                    pass
                else:
                    raise InvalidConfigParamException(
                        f"Start time ({self.start}) must be before end time ({self.end})"
                    )
        except ValueError as e:
            if "unconverted data remains" in str(e) or "does not match format" in str(
                e
            ):
                raise InvalidConfigParamException(
                    f"Invalid time format. Expected {self.format}"
                )
            raise e

        if self.distribution <= 0 or self.distribution > 100:
            raise InvalidConfigParamException(
                f"Distribution weight ({self.distribution}) must be between 1 and 100"
            )


@dataclass
class DateRangeItem:
    """Single date range definition with distribution weight"""

    start_date: str = "2020-01-01"
    end_date: str = "2020-12-31"
    format: str = "%Y-%m-%d"
    output_format: str = "%Y-%m-%d"
    distribution: int = 100

    def __init__(
        self,
        start_date: str,
        end_date: str,
        format: str = "%Y-%m-%d",
        output_format: str = "%Y-%m-%d",
        distribution: int = 100,
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.format = format
        self.output_format = output_format
        self.distribution = distribution

    def validate(self) -> None:
        """Validate date range item"""
        from datetime import datetime

        try:
            start_date = datetime.strptime(self.start_date, self.format)
            end_date = datetime.strptime(self.end_date, self.format)

            if start_date >= end_date:
                raise InvalidConfigParamException(
                    f"Start date ({self.start_date}) must be before end date ({self.end_date})"
                )
        except ValueError as e:
            if "unconverted data remains" in str(e) or "does not match format" in str(
                e
            ):
                raise InvalidConfigParamException(
                    f"Invalid date format. Expected {self.format}"
                )
            raise e

        if self.distribution <= 0 or self.distribution > 100:
            raise InvalidConfigParamException(
                f"Distribution weight ({self.distribution}) must be between 1 and 100"
            )


@dataclass
class DistributedTimeRangeConfig(BaseConfig):
    """Configuration for distributed time range strategy"""

    ranges: list[TimeRangeItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "DistributedTimeRangeConfig":
        """Create from dictionary with special handling for ranges"""
        config = cls()
        if "ranges" in config_dict:
            for range_dict in config_dict["ranges"]:
                config.ranges.append(TimeRangeItem(**range_dict))
        return config

    def validate(self) -> None:
        """Validate distributed time range parameters"""
        if not self.ranges:
            raise InvalidConfigParamException(
                "At least one time range must be specified"
            )

        # Validate each range
        for i, range_item in enumerate(self.ranges):
            try:
                range_item.validate()
            except InvalidConfigParamException as e:
                raise InvalidConfigParamException(
                    f"Invalid time range at index {i}: {str(e)}"
                )

        # Check that weights sum to 100
        total_distribution = sum(r.distribution for r in self.ranges)
        if total_distribution != 100:
            raise InvalidConfigParamException(
                f"Distribution weights must sum to 100, got {total_distribution}"
            )


@dataclass
class DistributedDateRangeConfig(BaseConfig):
    """Configuration for distributed date range strategy"""

    ranges: list[DateRangeItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "DistributedDateRangeConfig":
        """Create from dictionary with special handling for ranges"""
        config = cls()
        if "ranges" in config_dict:
            for range_dict in config_dict["ranges"]:
                config.ranges.append(DateRangeItem(**range_dict))
        return config

    def validate(self) -> None:
        """Validate distributed date range parameters"""
        if not self.ranges:
            raise InvalidConfigParamException(
                "At least one date range must be specified"
            )

        # Validate each range
        for i, range_item in enumerate(self.ranges):
            try:
                range_item.validate()
            except InvalidConfigParamException as e:
                raise InvalidConfigParamException(
                    f"Invalid date range at index {i}: {str(e)}"
                )

        # Check that weights sum to 100
        total_distribution = sum(r.distribution for r in self.ranges)
        if total_distribution != 100:
            raise InvalidConfigParamException(
                f"Distribution weights must sum to 100, got {total_distribution}"
            )


@dataclass
class TimeRangeConfig(BaseConfig):
    """Configuration for time range strategy"""

    start_time: str = "00:00:00"
    end_time: str = "23:59:59"
    format: str = "%H:%M:%S"

    def validate(self) -> None:
        """Validate time range parameters"""
        from datetime import datetime

        try:
            start = datetime.strptime(self.start_time, self.format)
            end = datetime.strptime(self.end_time, self.format)

            if start >= end:
                raise InvalidConfigParamException(
                    f"Start time ({self.start_time}) must be before end time ({self.end_time})"
                )
        except ValueError as e:
            if "unconverted data remains" in str(e) or "does not match format" in str(
                e
            ):
                raise InvalidConfigParamException(
                    f"Invalid time format. Expected {self.format}"
                )
            raise e


@dataclass
class ReplacementConfig(BaseConfig):
    """Configuration for replacement strategy"""

    from_value: Any = "a"
    to_value: Any = "b"

    def validate(self) -> None:
        """Validate replacement parameters"""
        # No specific validation needed
        pass


@dataclass
class ConcatConfig(BaseConfig):
    """Configuration for concatenation strategy"""

    lhs_col: str = ""
    rhs_col: str = ""
    separator: str = ""
    suffix: str = ""
    prefix: str = ""

    def validate(self) -> None:
        """Validate concatenation parameters"""
        if not self.lhs_col and not self.rhs_col:
            raise InvalidConfigParamException(
                "At least one column must be specified for concatenation"
            )


@dataclass
class DeleteConfig(BaseConfig):
    def validate(self) -> None:
        pass


@dataclass
class RandomNameConfig(BaseConfig):
    """Configuration for random name generation strategy"""

    name_type: str = "first"  # 'first', 'last', or 'full'
    gender: str = "any"  # 'male', 'female', or 'any'
    case: str = "title"  # 'title', 'upper', or 'lower'

    def validate(self) -> None:
        """Validate random name parameters"""
        valid_name_types = ["first", "last", "full"]
        if self.name_type not in valid_name_types:
            raise InvalidConfigParamException(
                f"Invalid name_type: {self.name_type}. Must be one of {valid_name_types}"
            )

        valid_genders = ["male", "female", "any"]
        if self.gender not in valid_genders:
            raise InvalidConfigParamException(
                f"Invalid gender: {self.gender}. Must be one of {valid_genders}"
            )

        valid_cases = ["title", "upper", "lower"]
        if self.case not in valid_cases:
            raise InvalidConfigParamException(
                f"Invalid case: {self.case}. Must be one of {valid_cases}"
            )


# Config factory to create the appropriate config class based on strategy name
def create_config(strategy_name: str, params: dict[str, Any]) -> BaseConfig:
    """
    Factory function to create a configuration object for the specified strategy.

    Args:
        strategy_name: Name of the strategy
        params: Dictionary of parameters for the strategy

    Returns:
        Configuration object for the strategy

    Raises:
        UnsupportedStrategyException: If the strategy is not supported
    """
    strategy_config_map = {
        "RANDOM_NUMBER_RANGE_STRATEGY": lambda p: NumberRangeConfig.from_dict(p),
        "DISTRIBUTED_NUMBER_RANGE_STRATEGY": lambda p: DistributedNumberRangeConfig.from_dict(
            p
        ),
        "DATE_GENERATOR_STRATEGY": lambda p: DateRangeConfig.from_dict(p),
        "DISTRIBUTED_DATE_RANGE_STRATEGY": lambda p: DistributedDateRangeConfig.from_dict(
            p
        ),
        "PATTERN_STRATEGY": lambda p: PatternConfig.from_dict(p),
        "SERIES_STRATEGY": lambda p: SeriesConfig.from_dict(p),
        "DISTRIBUTED_CHOICE_STRATEGY": lambda p: DistributedChoiceConfig.from_dict(p),
        "TIME_RANGE_STRATEGY": lambda p: TimeRangeConfig.from_dict(p),
        "DISTRIBUTED_TIME_RANGE_STRATEGY": lambda p: DistributedTimeRangeConfig.from_dict(
            p
        ),
        "REPLACEMENT_STRATEGY": lambda p: ReplacementConfig.from_dict(p),
        "CONCAT_STRATEGY": lambda p: ConcatConfig.from_dict(p),
        "RANDOM_NAME_STRATEGY": lambda p: RandomNameConfig.from_dict(p),
        "DELETE_STRATEGY": lambda p: DeleteConfig.from_dict(p),
    }

    if strategy_name not in strategy_config_map:
        raise UnsupportedStrategyException(f"Unsupported strategy: {strategy_name}")

    config = strategy_config_map[strategy_name](params)
    config.validate()
    return config
