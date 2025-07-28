# Examples Directory

This directory contains example configuration files demonstrating all the available data generation strategies in the GenXData application. All examples have been validated and are aligned with the current application version.

## ✅ Validated Example Files

All example files in this directory have been checked and updated to work with the current application. They use the correct:
- Strategy names and parameters
- File writer configurations (`output_path` instead of deprecated `path_or_buf`)
- Current syntax for all strategies

## 📋 Strategy Examples

### Basic Strategies

#### **1. Series Strategy**
- **File**: `series_strategy_with_relation.yaml`
- **Description**: Demonstrates series generation for sequential IDs
- **Features**: Multiple related columns with distributed strategies

#### **2. Random Number Range Strategy**
- **Files**:
  - `simple_random_number_example.yaml` - Basic usage
  - `random_number_range_example.yaml` - Comprehensive examples
  - `random_number_with_masking_example.yaml` - Conditional generation with masking
- **Description**: Generate random numbers within specified ranges
- **Features**: Different precisions, steps, ranges, and conditional masking

#### **3. Pattern Strategy**
- **File**: `pattern_strategy.yaml`
- **Description**: Generate data matching regex patterns
- **Examples**: Product codes, phone numbers

#### **4. Random Name Strategy**
- **File**: `random_name_strategy.yaml`
- **Description**: Generate realistic first/last names
- **Features**: Combined with concat strategy for emails

### Distributed Strategies

#### **5. Distributed Number Range Strategy**
- **File**: `distributed_number_range_strategy.yaml`
- **Description**: Generate numbers from weighted ranges
- **Use Cases**: Age distributions, salary ranges

#### **6. Distributed Choice Strategy**
- **Files**: Multiple files include this strategy
- **Description**: Choose values with specified probability weights
- **Examples**: Departments, performance ratings, categories

#### **7. Distributed Time Range Strategy** ⭐ *New*
- **File**: `distributed_time_range_strategy.yaml`
- **Description**: Generate times from multiple weighted time ranges
- **Use Cases**: Work shifts, business hours, activity periods
- **Features**: Overnight ranges, multiple time formats

#### **8. Distributed Date Range Strategy** ⭐ *New*
- **File**: `distributed_date_range_strategy.yaml`
- **Description**: Generate dates from multiple weighted date ranges
- **Use Cases**: Historical events, generational data, business cycles
- **Features**: Different date formats, historical periods

### Date and Time Strategies

#### **9. Date Generator Strategy**
- **File**: `date_generator.yaml`
- **Description**: Generate dates within a single range
- **Features**: Custom date formats

#### **10. Time Range Strategy**
- **File**: `time_range_strategy.yaml`
- **Description**: Generate times within a single range
- **Features**: Business hours, custom time formats

### Utility Strategies

#### **11. Concatenation Strategy**
- **Files**:
  - `concate_strategy.yaml` - Basic concatenation
  - Multiple other files use this for email generation
- **Description**: Combine column values with separators
- **Features**: Prefixes, suffixes, custom separators
- **Fixed**: Now uses `lhs_col` and `rhs_col` (singular) parameters

#### **12. Replacement Strategy**
- **File**: `replacement_strategy.yaml`
- **Description**: Replace specific values in columns
- **Use Cases**: Data cleaning, value substitution

#### **13. Delete Strategy**
- **File**: `delete.yaml`
- **Description**: Delete rows based on conditions
- **Features**: Conditional row removal with masking

### Advanced Examples

#### **14. All Strategies Combined**
- **File**: `all_example.yaml`
- **Description**: Comprehensive example using multiple strategies
- **Features**: Employee data with departments, salaries, dates

#### **15. Batch Processing**
- **Files**:
  - `batch_config_csv.yaml` - CSV batch output
  - `large_streaming_test.yaml` - Large dataset processing
  - `masking_streaming_test.yaml` - Streaming with conditions
  - `artemis_streaming_test.yaml` - Message queue integration
- **Description**: Examples for processing large datasets in batches
- **Features**: Memory-efficient processing, multiple output formats

#### **16. Streaming Configuration**
- **File**: `streaming_config_example.yaml`
- **Description**: AMQP queue integration settings
- **Features**: Queue configuration, retry settings

## 🛠️ Recent Fixes Applied

The following issues were identified and fixed across all example files:

### 1. File Writer Parameters
- **Issue**: Examples using deprecated `path_or_buf` parameter
- **Fix**: Updated to use `output_path` parameter
- **Files Fixed**:
  - `all_example.yaml`
  - `random_number_range_example.yaml`
  - `pattern_strategy.yaml`
  - `random_number_with_masking_example.yaml`

### 2. Concat Strategy Parameters
- **Issue**: Examples using incorrect plural parameter names
- **Fix**: Changed `lhs_cols`/`rhs_cols` to `lhs_col`/`rhs_col`
- **Files Fixed**:
  - `concate_strategy.yaml`
  - `random_name_strategy.yaml`
  - `delete.yaml`

### 3. Missing Parameters
- **Issue**: Some strategies missing required `params: {}`
- **Fix**: Added empty params objects where needed
- **Files Fixed**: Various strategy configurations

## 🎯 Usage Instructions

### Running Examples

```bash
# Basic example
python main.py examples/simple_random_number_example.yaml

# Comprehensive example
python main.py examples/all_example.yaml

# Distributed strategies
python main.py examples/distributed_date_range_strategy.yaml
python main.py examples/distributed_time_range_strategy.yaml

# Batch processing
python main.py examples/batch_config_csv.yaml --batch examples/batch_config_csv.yaml
```

### Debug Mode
```bash
python main.py examples/any_example.yaml --debug
```

### Performance Monitoring
```bash
python main.py examples/any_example.yaml --perf
```

## 📊 Strategy Compatibility Matrix

| Strategy | Single Range | Multiple Ranges | Weights | Masking | Formats |
|----------|-------------|-----------------|---------|---------|---------|
| NUMBER_RANGE | ✅ | ❌ | ❌ | ✅ | ❌ |
| DISTRIBUTED_NUMBER | ❌ | ✅ | ✅ | ✅ | ❌ |
| DATE_GENERATOR | ✅ | ❌ | ❌ | ✅ | ✅ |
| DISTRIBUTED_DATE | ❌ | ✅ | ✅ | ✅ | ✅ |
| TIME_RANGE | ✅ | ❌ | ❌ | ✅ | ✅ |
| DISTRIBUTED_TIME | ❌ | ✅ | ✅ | ✅ | ✅ |
| PATTERN | ❌ | ❌ | ❌ | ✅ | ❌ |
| CHOICE | ❌ | ✅ | ✅ | ✅ | ❌ |
| SERIES | ❌ | ❌ | ❌ | ✅ | ❌ |
| CONCAT | ❌ | ❌ | ❌ | ✅ | ❌ |
| REPLACEMENT | ❌ | ❌ | ❌ | ✅ | ❌ |
| RANDOM_NAME | ❌ | ❌ | ❌ | ✅ | ❌ |
| DELETE | ❌ | ❌ | ❌ | ✅ | ❌ |

## 🔄 Validation Status

**Last Updated**: May 31, 2025
**Validation Status**: ✅ All examples validated and working
**Application Version**: Latest (with distributed date/time strategies)

All example files have been tested and confirmed to work with the current application version. The examples demonstrate realistic use cases and best practices for each strategy type.
