# Completed Tasks

## Quick Wins
1. ✅ fix regex strategy: remove unused `null_mask` and `map_to_null`.
2. ✅ add ignore-case flag in string comparisons and replace print-based errors with proper exceptions.
3. ✅ replace operation names: `insertIfEmpty` → `insert_if_empty`; `insert` → `overwrite`.
4. ✅ add shuffle/random flag in config.
5. ✅ add proper logging framework to show progress.
6. ✅ add debug mode.
7. ✅ test `insert` and `insert_if_empty` behaviors under null-mask scenarios.
8. ✅ re-write README with updated instructions.

## Medium Tasks
10. ✅ migrate JSON-based config to YAML for readability.
11. ✅ implement intermediate columns (used internally, not output).
12. ✅ implement write-adapters to support multiple output formats.
13. ✅ write a simple performance timer script to measure time per column/strategy.

## Heavy Refactors & Features (Most changes)
21. ✅ restructure codebase into a robust OOP architecture with clear interfaces.
23. ✅ create config classes for each of the strategy, do not pass every params, as kwargs.

## Implementation Details

### 1. Regex Strategy Fix
- Removed unused `null_mask` and `map_to_null` import
- Updated the implementation to directly use DataFrame operations

### 2-3. Error Handling and Operation Names
- Replaced print-based errors with proper exceptions
- Added case-insensitive comparisons for operations
- Standardized operation names: `insert` → `overwrite` and `insertIfEmpty` → `insert_if_empty`
- Updated all strategy files to use the new operation names consistently

### 4. Shuffle Feature
- Added a `shuffle` flag to the config
- Implemented shuffling with `df.sample(frac=1).reset_index(drop=True)`
- Added performance measurement for shuffling operation

### 5-6. Logging and Debug Mode
- Implemented comprehensive logging framework using Python's `logging` module
- Added different log levels based on debug mode
- Created a command-line flag for debug mode: `--debug`
- Added file-specific loggers for better traceability

### 7. Null-mask Handling
- Fixed the behavior of `insert_if_empty` to only fill null values
- Improved handling of masks in relations
- Added proper error handling for column existence

### 8. README Updates
- Completely rewrote the README with clear instructions
- Added documentation for all new features
- Created better examples and explanations
- Added progress tracking section

### 10. YAML Configuration Support
- Added YAML loader utility for reading YAML configuration files
- Created fallback mechanism to support both YAML and JSON formats
- Added configuration converter utilities for JSON to YAML and vice versa
- Created a command-line utility script for batch converting configuration files
- Updated the data generator to support YAML configurations for both user configs and internal configs
- Created YAML versions of all standard configuration files
- Updated README with documentation and examples for YAML configuration

### 11. Intermediate Columns
- Implemented a system to mark columns as "intermediate"
- Created utility functions for tracking and filtering intermediate columns
- Added the ability to exclude intermediate columns from the final output
- Updated the README with examples

### 12. Write Adapters
- Implemented seven different file writers: CSV, JSON, Excel, Parquet, SQLite, HTML, and Feather
- Added proper error handling and logging to all file writers
- Created a consistent API for all writers
- Updated configuration files to support the new writers
- Added parameter validation and documentation
- Created an example configuration with all output formats

### 13. Performance Timing
- Created a performance tracking system to measure execution time
- Added a command-line flag for generating performance reports: `--perf`
- Implemented detailed metrics collection: count, total time, min/max, rows/sec
- Added context managers for easy timing of code blocks 

### 21. OOP Architecture Refactoring
- Created a BaseStrategy abstract class defining the interface for all strategies
- Implemented a generic strategy execution flow in the base class
- Moved common functionality (like operation handling) to the base class
- Created a StrategyFactory for instantiating strategies
- Implemented modular and extensible validation system
- Created strategy classes that inherit from the base class
- Added comprehensive error handling and logging
- Created a unified interface for all strategies

### 23. Strategy Configuration Classes
- Created config classes for each strategy type
- Added validation logic specific to each strategy's parameters
- Implemented a config factory for creating the appropriate config class
- Added proper type checking and parameter validation
- Created conversion methods between config objects and dictionaries
- Integrated config validation into the strategy factory
- Updated strategy classes to use validated parameters 