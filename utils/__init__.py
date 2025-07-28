"""
Utilities package for GenXData.

This package contains various utility modules for configuration loading,
file operations, and generator management.
"""

# Import specific functions to avoid circular dependencies
from .generator_utils import (
    create_domain_configs_example,
    generator_to_config,
    get_generator_info,
    get_generator_stats,
    get_generators_by_strategy,
    list_available_generators,
    load_all_generators,
    save_config_as_json,
    save_config_as_yaml,
    validate_generator_config,
)

# Note: config_utils and file_utils imports are avoided here to prevent circular dependencies
# Import them directly where needed: from utils.config_utils import load_config
# Import them directly where needed: from utils.file_utils import write_output_files

__all__ = [
    # Generator utilities
    "load_all_generators",
    "list_available_generators",
    "get_generator_info",
    "get_generators_by_strategy",
    "generator_to_config",
    "save_config_as_yaml",
    "save_config_as_json",
    "create_domain_configs_example",
    "validate_generator_config",
    "get_generator_stats",
]
