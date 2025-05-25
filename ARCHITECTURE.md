# Data Generator Architecture

## Overview

Data Generator is a comprehensive synthetic data generation tool with both a command-line interface and a web UI. It consists of a Python backend using pandas for data manipulation and a React frontend for interactive use.

## System Architecture

```
┌─────────────────────┐     ┌─────────────────────┐
│   React Frontend    │     │    CLI Interface    │
│   (Vite + React)    │     │    (main.py)        │
└──────────┬──────────┘     └──────────┬──────────┘
           │                           │
           │ HTTP/REST API             │ Direct Call
           │                           │
           ▼                           ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Backend (api.py)           │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│           Core Data Generation Engine           │
│                  (main.py)                      │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│              Strategy Framework                 │
│   ┌─────────────┐  ┌──────────────────┐         │
│   │  Factory    │  │  Base Strategy   │         │
│   └─────────────┘  └──────────────────┘         │
│            │                │                   │
│            ▼                ▼                   │
│   ┌─────────────────────────────────┐           │
│   │    12 Strategy Implementations   │          │
│   └─────────────────────────────────┘           │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│              Output Writers                     │
│  CSV │ JSON │ Excel │ Parquet │ SQLite │ HTML   │
└─────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend (React + TypeScript)
- **Location**: `/frontend`
- **Technology**: React 19, TypeScript, Vite, Tailwind CSS
- **Purpose**: Interactive web UI for data generation
- **Key Components**:
  - Pages for different workflows
  - Reusable UI components
  - Type-safe interfaces
  - Modern, responsive design

### 2. API Layer (FastAPI)
- **Location**: `/api.py`
- **Purpose**: REST API for frontend communication
- **Endpoints**:
  - `GET /ping` - Health check
  - `GET /get_all_strategies` - List available strategies
  - `GET /get_strategy_schemas` - Get strategy configurations
  - `POST /generate_data` - Generate data from config
  - `POST /generate_config` - Generate configuration

### 3. Core Engine
- **Location**: `/main.py`
- **Purpose**: Main data generation orchestrator
- **Key Functions**:
  - Configuration loading (JSON/YAML)
  - DataFrame initialization
  - Strategy execution
  - Output writing
  - Performance monitoring

### 4. Strategy Framework

#### Base Strategy (`/core/base_strategy.py`)
Abstract base class defining the interface:
```python
class BaseStrategy(ABC):
    def __init__(self, **kwargs)
    def _validate_params(self)
    def generate_data(self, count: int) -> pd.Series
```

#### Strategy Factory (`/core/strategy_factory.py`)
- Creates strategy instances
- Validates configurations
- Executes strategies on DataFrames

#### Strategy Mapping (`/core/strategy_mapping.py`)
- Registry of available strategies
- Maps strategy names to implementations

#### Strategy Config (`/core/strategy_config.py`)
- Configuration validation classes
- Type-safe parameter handling
- Built-in validation rules

### 5. Available Strategies

| Strategy                            | Purpose                          | Key Parameters               |
|-------------------------------------|----------------------------------|------------------------------|
| `RANDOM_NUMBER_RANGE_STRATEGY`      | Random numbers in range          | min, max, precision          |
| `DISTRIBUTED_NUMBER_RANGE_STRATEGY` | Numbers with custom distribution | ranges with weights          |
| `DATE_GENERATOR_STRATEGY`           | Random dates                     | start_date, end_date, format |
| `PATTERN_STRATEGY`                  | Regex-based data                 | regex pattern                |
| `SERIES_STRATEGY`                   | Sequential series                | start, step                  |
| `DISTRIBUTED_CHOICE_STRATEGY`       | Weighted categorical data        | choices with percentages     |
| `TIME_RANGE_STRATEGY`               | Random times                     | start_time, end_time         |
| `REPLACEMENT_STRATEGY`              | Replace values                   | from_value, to_value         |
| `CONCAT_STRATEGY`                   | Concatenate columns              | lhs_col, rhs_col, separator  |
| `RANDOM_NAME_STRATEGY`              | Random names                     | No specific params           |
| `DELETE_STRATEGY`                   | Delete/null values               | No specific params           |

### 6. Output Writers (`/utils/file_writers/`)
- Modular output format support
- Each writer handles specific format
- Common interface for all writers
- Supported formats:
  - CSV
  - JSON
  - Excel
  - Parquet
  - SQLite
  - HTML
  - Feather

### 7. Utilities (`/utils/`)
- Configuration loaders (JSON/YAML)
- Performance monitoring
- Intermediate column handling
- Data type conversions
- Configuration converters

### 8. Configuration System
- Supports JSON and YAML formats
- Hierarchical configuration structure
- Validation at multiple levels
- Extensible parameter system

## Data Flow

1. **Configuration Input**
   - User provides YAML/JSON config
   - Config validated against schema

2. **Strategy Execution**
   - Factory creates strategy instances
   - Each strategy generates column data
   - Data applied to pandas DataFrame

3. **Post-Processing**
   - Optional data shuffling
   - Intermediate column filtering
   - Data validation (proposed)

4. **Output Generation**
   - Multiple writers can be specified
   - Each writer exports to its format
   - Performance metrics collected

## Design Patterns

1. **Strategy Pattern**: Core data generation logic
2. **Factory Pattern**: Strategy instantiation
3. **Registry Pattern**: Strategy mapping
4. **Abstract Base Class**: Common interface
5. **Configuration Pattern**: Validated configs

## Extension Points

1. **New Strategies**: Implement `BaseStrategy`
2. **New Output Formats**: Add to `/utils/file_writers/`
3. **Custom Validators**: Plugin validation system
4. **API Endpoints**: Extend FastAPI routes

## Performance Considerations

- Vectorized pandas operations
- Configurable batch processing
- Performance monitoring built-in
- Memory-efficient data generation

## Future Architecture Improvements

1. **Microservices**: Separate API and engine
2. **Queue-based Processing**: For large datasets
3. **Distributed Generation**: Multi-node support
4. **Plugin System**: Dynamic strategy loading
5. **Caching Layer**: For repeated operations 