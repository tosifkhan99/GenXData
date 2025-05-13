# Data Generator
Data generator or data-gen, is a tool focused towards generating data, either based on a relation with some other column, or using a strategy.

## Getting Started
**Step 1**: Install dependencies
```bash
pip install -r requirements.txt
```

**Step 2**: Create a configuration file. You can copy `examples/config.json.example` to `examples/config.json`, or create your own config (refer to examples folder for more info).

**Step 3**: Run the script with your configuration:
```bash
python data_generator.py ./examples/config.json
```

For verbose output and debugging information, use the debug flag:
```bash
python data_generator.py ./examples/config.json --debug
```

## Key Concepts

### Relations (`relation_type`)
> relation_type : optional : list

Relations establish a set of dependencies on one or more columns which are already present, then generate the specified column based on the dependencies.

### Strategies (`strategy`)
> strategy : required : dict

A strategy defines how the data is going to be generated for a column.

### Operations
Data-gen supports two primary operations:
- `overwrite`: Always overwrites the value for the column (previously called "insert")
- `insert_if_empty`: Only fills null values in the column (previously called "insertIfEmpty")

### Shuffle Option
You can add a `"shuffle": true` option to your config to randomly shuffle the generated data.

### Intermediate Columns
You can mark columns as "intermediate" by setting `"intermediate": true` in their config. These columns will be used during data generation but excluded from the final output. This is useful for:
- Creating temporary calculation columns
- Generating data that's only needed to derive other columns
- Keeping your output clean while using complex data generation logic

Example:
```json
{
  "names": ["TEMP_CALCULATION"],
  "intermediate": true,
  "strategy": {
    "name": "RANDOM_NUMBER_RANGE_STRATEGY",
    "params": {
      "range": {
        "upperbound": 100,
        "lowerbound": 1
      }
    }
  }
}
```

## About the tool

The `data_generator.py` reads a config file in `json` format and applies data generation strategies based on the config file to the columns. The script uses various data generation strategies such as regular expression, series, random names, and distribution-based data generation. It is capable of generating data independently or based on some other column, i.e. using `relation`.

## Config Examples
Config examples can be found in the examples/config folder, which includes examples for generating data based on each type of strategy and relation.

## Config Explanation
```json
{
  "column_name": [ "ALL_COLUMNS" ],
  "file_writer": [{ 
      "type": "FILE_FORMAT",
      "params": {
          "path_or_buf": "FILENAME.FILE_FORMAT"
      }
  }],
  "shuffle": true,
  "num_of_rows": "NUMBER_OF_ROWS",
  "configs": [
    {
      "names": [ "INDEPENDENT_COLUMN" ],
      "strategy": {
        "is_unique": "False", 
        "name": "STRATEGY_NAME",
        "params": {
          "STRATEGY_SPECIFIC_PARAMS": "VALUES"
        }
      },
      "debug": false
    },
    {
      "names": [ "DEPENDENT_COLUMN" ],
      "relation_type": [
        {
          "filter": {
            "lhs": [ "COLUMNS_TO_BE_COMPARED" ],
            "rhs": [ "VALUE_TO_COMPARE" ],
            "boolean": [ "BOOLEAN_OPERATORS" ]
          },
          "strategy": {
            "RELATIONAL_STRATEGY": "VALUES"
          }
        }
      ]
    }
  ]
}
```

### Placeholder Definitions
- **ALL_COLUMNS**: List of all the columns that will be in the final output (column will be empty if no generation definition is supplied)
- **FILE_FORMAT**: Type of format the output should be in (e.g., "csv")
- **FILENAME.FILE_FORMAT**: Name of file with its format (e.g., "output.csv")
- **NUMBER_OF_ROWS**: Number of rows in output (defaults to 100 and cannot be smaller than 100)
- **INDEPENDENT_COLUMN**: Column that can be generated without dependency on another column
- **STRATEGY_NAME**: Name of the strategy to use (see STRATEGIES.json)
- **STRATEGY_SPECIFIC_PARAMS**: Parameters required to run a particular strategy
- **OPERATION_MODE**: Mode of insertion, either "overwrite" or "insert_if_empty"
- **DEPENDENT_COLUMN**: Column generated via a relation to other columns
- **COLUMNS_TO_BE_COMPARED**: Column names to use in the comparison
- **VALUE_TO_COMPARE**: Values to compare against
- **RELATIONAL_OPERATOR**: Comparison operator (e.g., ">", "<", "==")
- **BOOLEAN_OPERATORS**: Boolean operators for multiple conditions (e.g., "AND", "OR")
- **RELATIONAL_STRATEGY**: Strategy definition for the relation

## Available Strategies

The following strategies are available:

1. **DATE_GENERATOR_STRATEGY**: Generate date values within a range
2. **DELETE_STRATEGY**: Delete values from a column
3. **DISTRIBUTED_NUMBER_RANGE_STRATEGY**: Generate numbers with custom distributions
4. **DISTRIBUTED_CHOICE_STRATEGY**: Generate categorical data with custom distributions
5. **RANDOM_NUMBER_RANGE_STRATEGY**: Generate random numbers within a range
6. **RANDOM_NAME_STRATEGY**: Generate random names
7. **PATTERN_STRATEGY**: Generate data matching a regex or pattern
8. **TIME_RANGE_STRATEGY**: Generate time values within a range
9. **REPLACEMENT_STRATEGY**: Replace specific values
10. **SERIES_STRATEGY**: Generate a series of values
11. **DISTRIBUTED_DATE_STRATEGY**: Generate dates with custom distributions
12. **CONCAT_STRATEGY**: Concatenate values from other columns

### Performance Monitoring
You can generate a performance report for your data generation by using the `--perf` flag:

```bash
python data_generator.py ./examples/config.json --perf
```

This will show detailed timing information for each operation, helping you identify bottlenecks in your data generation pipeline. The report includes:
- Time spent on each column/strategy
- Average execution time
- Rows processed per second

## Recent Improvements

The following improvements have been made to the data generator:

### Code Quality
- ✅ Fixed regex strategy by removing unused `null_mask` and `map_to_null`
- ✅ Added proper error handling with exceptions instead of print-based errors
- ✅ Standardized operation names: `insert` → `overwrite` and `insertIfEmpty` → `insert_if_empty`
- ✅ Added proper type checking and case-insensitive comparisons
- ✅ Implemented comprehensive logging framework
- ✅ Added debug mode with verbose output
- ✅ Updated documentation and improved README

### New Features
- ✅ Added shuffle option to randomize generated data
- ✅ Implemented intermediate columns for internal calculations
- ✅ Added performance monitoring and reporting
- ✅ Added support for additional comparison operators (<= and >=)
- ✅ Added support for more boolean operators (AND, OR) in text form

### Future Plans
- Migrate JSON-based config to YAML for better readability
- Implement more write adapters for additional output formats
- Optimize unique ID generator for large datasets
- Rename `relations` to `constraints` for clarity
- Add support for more data types in relations (floats, dates)
- Implement multiple table mapping (cross-file lookups)
- Support complex boolean expressions with parentheses
- Restructure into OOP architecture with clean interfaces
- Add API access via FastAPI or web UI
- Explore ML-based data generation methods

## Output Formats

The data generator supports multiple output formats. You can specify one or more file writers in your configuration file:

### Available File Writers

- **CSV**: Comma-separated values format
  ```json
  {
    "type": "csv",
    "params": {
      "path_or_buf": "output.csv",
      "index": false
    }
  }
  ```

- **JSON**: JavaScript Object Notation format
  ```json
  {
    "type": "json",
    "params": {
      "path_or_buf": "output.json",
      "orient": "records",
      "indent": 2
    }
  }
  ```

- **Excel**: Microsoft Excel format
  ```json
  {
    "type": "excel",
    "params": {
      "path_or_buf": "output.xlsx",
      "sheet_name": "Data"
    }
  }
  ```

- **Parquet**: Apache Parquet format (columnar storage)
  ```json
  {
    "type": "parquet",
    "params": {
      "path": "output.parquet",
      "compression": "snappy"
    }
  }
  ```

- **SQLite**: SQLite database
  ```json
  {
    "type": "sqlite",
    "params": {
      "database": "output.db",
      "table": "data",
      "if_exists": "replace"
    }
  }
  ```

- **HTML**: HTML file with optional Bootstrap styling
  ```json
  {
    "type": "html",
    "params": {
      "path_or_buf": "output.html",
      "title": "Generated Data",
      "include_bootstrap": true
    }
  }
  ```

- **Feather**: Apache Arrow Feather format
  ```json
  {
    "type": "feather",
    "params": {
      "path": "output.feather",
      "compression": "zstd"
    }
  }
  ```

You can specify multiple writers to output the same data in different formats simultaneously. See `examples/output_formats.json.example` for a complete example.

## YAML Configuration Support

The data generator now supports YAML configuration files in addition to JSON. YAML provides several advantages:

- More human-readable format with less punctuation
- Support for comments
- No need for quoting most strings
- Less error-prone (no trailing commas, etc.)

### Converting Between Formats

You can convert existing JSON configurations to YAML using either:

1. The `--convert` command-line flag:
   ```bash
   python data_generator.py config.json --convert yaml
   ```

2. The dedicated converter script for batch operations:
   ```bash
   python convert_configs.py --format yaml --backup examples/
   ```

### YAML Configuration Example

```yaml
# Data Generator YAML Configuration
column_name:
  - NAME
  - AGE
  - CITY

file_writer:
  - type: csv
    params:
      path_or_buf: output.csv

num_of_rows: 100
shuffle: true

configs:
  # Generate random names
  - names:
      - NAME
    strategy:
      name: RANDOM_NAME_STRATEGY

  # Generate ages with distribution
  - names:
      - AGE
    strategy:
      name: DISTRIBUTED_NUMBER_RANGE_STRATEGY
      params:
        ranges:
          - lowerbound: 18
            upperbound: 35
            distribution: 40
          - lowerbound: 36
            upperbound: 65
            distribution: 60

  # Generate cities based on predefined choices
  - names:
      - CITY
    strategy:
      name: DISTRIBUTED_CHOICE_STRATEGY
      params:
        choices:
          New York: 30
          Chicago: 20
          Los Angeles: 25
          Houston: 15
          Phoenix: 10
```