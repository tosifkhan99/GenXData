# 🧬 GenXData
A Complete synthetic data framework for generating realistic data for your applications.

## 🚀 Getting Started
### 🛠️ Running the tool
**Step 1**: Install dependencies
```bash
pip install -r cli-requirements.txt
```

**Step 2**: Create a configuration file. You can copy examples from the [examples](examples) directory, or create your own configs (refer to examples folder or visit documentation <TODO: INSERT DOCUMENTATION LINK> for more info).

**Step 3**: Run the script with your configuration:
```bash
python main.py generate path/to/your/config.yaml
```

For verbose output and debugging information, use the debug flag:
```bash
python main.py ./examples/all_example.yaml --debug
```

### 💻 **CLI Interface**
GenXData includes a comprehensive command-line interface for managing generators and configurations. The CLI provides several commands to explore, create, and generate data efficiently.

#### **Installation**
```bash
pip install -r cli-requirements.txt
```

#### **Global Options**
- `--help`: Show help message and available commands

#### **Available Commands**

##### **1. List Generators**
Explore available generators with optional filtering and statistics:

```bash
# List all generators (175 total across 9 domains)
python -m cli.main_cli list-generators

# Filter generators by name pattern
python -m cli.main_cli list-generators --filter NAME

# Show comprehensive statistics
python -m cli.main_cli list-generators --show-stats

# Combine verbose logging with filtering
python -m cli.main_cli --verbose list-generators --filter NAME
```

##### **2. Show Generator Details**
Get detailed information about a specific generator:

```bash
# Show details of a specific generator
python -m cli.main_cli show-generator PERSON_NAME

# Output includes strategy and parameters
python -m cli.main_cli show-generator EMAIL_PATTERN
```

##### **3. Find Generators by Strategy**
List all generators using a specific strategy:

```bash
# Find generators using RANDOM_NAME_STRATEGY
python -m cli.main_cli by-strategy RANDOM_NAME_STRATEGY

# Find generators using DATE_GENERATOR_STRATEGY
python -m cli.main_cli by-strategy DATE_GENERATOR_STRATEGY
```

##### **4. Create Configuration Files**
Generate configuration files from generator mappings:

```bash
# Create config with generator mapping
python -m cli.main_cli create-config \
  --mapping "name:FULL_NAME,age:PERSON_AGE,email:EMAIL_PATTERN" \
  --output test_config.json \
  --rows 50

# Create config with custom metadata
python -m cli.main_cli create-config \
  --mapping "product:PRODUCT_NAME,price:PRODUCT_PRICE" \
  --output ecommerce_config.yaml \
  --rows 1000 \
  --name "Ecommerce Dataset" \
  --description "Product catalog data"

# Use a mapping file instead of command line
python -m cli.main_cli create-config \
  --mapping-file mapping.json \
  --output config.yaml \
  --rows 500
```

##### **5. Generate Domain Configurations**
Create example configurations for various domains:

```bash
# Generate domain-specific configuration examples
python -m cli.main_cli create-domain-configs

# Creates configs in ./output/ for:
# - ecommerce, healthcare, education, geographic
# - transportation, business, technology, iot_sensors
```

##### **6. Generate Data**
Generate data using configuration files:

```bash
# Generate data from your configuration
python -m cli.main_cli generate test_config.json

# Generate from example configurations
python -m cli.main_cli generate examples/simple_random_number_example.yaml

# Generate data from configuration
python -m cli.main_cli generate config.yaml
```

##### **7. Show Statistics**
Display comprehensive generator statistics:

```bash
# Show detailed statistics
python -m cli.main_cli stats

# Includes:
# - Total generators count
# - Strategy distribution
# - Domain distribution
# - Available strategies list
```

#### **Command Examples & Use Cases**

**Exploring Available Data:**
```bash
# Discover what generators are available
python -m cli.main_cli list-generators --show-stats

# Find name-related generators
python -m cli.main_cli list-generators --filter NAME

# See all generators using a specific strategy
python -m cli.main_cli by-strategy RANDOM_NAME_STRATEGY

# Filter generators by name pattern
python -m cli.main_cli list-generators --filter NAME
```

**Creating Custom Datasets:**
```bash
# Create a user profile dataset
python -m cli.main_cli create-config \
  --mapping "user_id:UUID,name:FULL_NAME,email:EMAIL_PATTERN,age:PERSON_AGE" \
  --output user_profiles.yaml \
  --rows 1000

# Generate the data
python -m cli.main_cli generate user_profiles.yaml
```

**Domain-Specific Data Generation:**
```bash
# Create all domain example configs
python -m cli.main_cli create-domain-configs

# Generate healthcare data
python -m cli.main_cli generate output/healthcare_config.yaml

# Generate ecommerce data
python -m cli.main_cli generate output/ecommerce_config.yaml
```

#### **Important Notes**

- **Configuration Formats**: Both JSON and YAML configuration files are supported.

- **Supported Formats**: Configuration files can be in JSON or YAML format. The output format is determined by the file extension.

- **Generator Domains**: 175 generators across 9 domains:
  - **Generic** (25 generators): Basic data types, IDs, patterns
  - **Geographic** (24 generators): Addresses, coordinates, locations
  - **IoT Sensors** (23 generators): Device data, telemetry, readings
  - **Education** (22 generators): Academic data, courses, grades
  - **Business** (21 generators): Company data, financial metrics
  - **Healthcare** (21 generators): Medical data, patient information
  - **Technology** (20 generators): Software, hardware, tech specs
  - **Transportation** (19 generators): Vehicle data, logistics
  - **Ecommerce** (18 generators): Product data, pricing, orders

### 🌐 Running the Frontend and API Server
Note: A React frontend app is present inside the [frontend](frontend) directory, built solely to quickly bootstrap the config, and to showcase the capabilities of the tool for demo showcase.

#### ⚛️ Running the Frontend
```bash
cd frontend
yarn install
yarn dev
```

#### 🔌 Running the API Server
```bash
uvicorn api:app --reload
```

#### 🐳 Docker
The docker image will serve the frontend, a fast api server, to generate config or data

#### Build the image
```bash
docker build -t genxdata .
```

#### Run the container
```bash
docker run -p 8000:8000 -it genxdata
```

#### Or Pull the image
```bash
docker pull tosifhkhan/genxdata:latest
```

then run the container

```bash
docker run -p 8000:8000 -it tosifkhan/genxdata:latest
```

visit the frontend at `http://localhost:8000`
see the api server docs at `http://localhost:8000/docs`


## 🏗️ Project Structure

GenXData has been refactored into a modular structure for better maintainability and extensibility:

```
GenXData/
├── cli/                    # 💻 Command-line interface (7 commands, 175+ generators)
│   └── main_cli.py         # Full-featured CLI with generator management
├── core/                   # Core processing modules
│   ├── orchestrator.py     # Main processing orchestration
│   ├── processing/         # Core data processing
│   ├── streaming/          # Streaming and batch processing
│   └── strategies/         # Data generation strategies (13 strategies)
├── generators/             # 🎯 Pre-built data generators (9 domains)
│   ├── generic_generator.json        # 25 basic generators
│   ├── geographic_generators.json    # 24 location generators
│   ├── iot_sensors_generators.json   # 23 IoT generators
│   ├── education_generators.json     # 22 academic generators
│   ├── business_generators.json      # 21 business generators
│   ├── healthcare_generators.json    # 21 medical generators
│   ├── technology_generators.json    # 20 tech generators
│   ├── transportation_generators.json # 19 transport generators
│   └── ecommerce_generators.json     # 18 ecommerce generators
├── utils/                  # Utility modules
│   ├── config_utils/       # Configuration loading
│   ├── file_utils/         # File operations
│   ├── generator_utils.py  # Generator management and CLI utilities
│   └── writers/            # Output format writers (7 formats)
├── queue/                  # Queue system implementations
├── examples/               # Configuration examples
├── frontend/               # React web interface
├── main.py                 # Main entry point
└── api.py                  # FastAPI server
```

## ✨ Features

### 🚀 **Comprehensive Data Generation Strategies**
- 🎲 **12+ Built-in Strategies**: From simple random numbers to complex pattern matching and date distributions
- 👥 **Smart Name Generation**: Parameterized name generation with gender selection, case formatting, and name types (first/last/full)
- 🔍 **Pattern-Based Generation**: Create data matching specific regex patterns or templates
- 📊 **Distribution-Based Generation**: Generate data following custom statistical distributions
- ⏰ **Date & Time Generation**: Flexible date and time generation with range controls
- 🔗 **Concatenation & Dependencies**: Create columns that depend on or combine other columns
- 🎛️ **Pre-built Generators**: Ready-to-use generators for common domains (ecommerce, healthcare, education, etc.)

### 📁 **Multiple Output Formats**
- 💾 **7 File Formats Supported**: CSV, Excel, JSON, Parquet, SQLite, HTML, and Feather
- ⚡ **Simultaneous Multi-Format Export**: Generate the same dataset in multiple formats at once
- 🏎️ **Optimized Writers**: Each format writer is optimized for performance and memory efficiency

### ⚙️ **Flexible Configuration**
- 📝 **YAML & JSON Support**: Choose between human-readable YAML or traditional JSON configuration
- ✅ **Schema Validation**: Built-in validation ensures your configurations are correct before execution
- 📚 **Extensive Examples**: 20+ example configurations covering different use cases and strategies

### 🎯 **Advanced Capabilities**
- 🔄 **Dependent Column Generation**: Create realistic relationships between data columns
- 📈 **Custom Distributions**: Define your own probability distributions for more realistic data
- 🎭 **Pattern Masking**: Apply masking patterns to sensitive data generation
- 🔢 **Series Generation**: Create sequential or arithmetic series data
- 🔄 **Value Replacement**: Replace or delete specific values based on conditions

### 🌐 **Streaming & Queue Integration**
- 📡 **Abstract Queue System**: Support for multiple message queue systems (AMQP, Kafka)
- 🔄 **Real-time Streaming**: Stream data batches to message queues as they're generated
- 🏭 **Enterprise Ready**: Support for Apache Artemis, RabbitMQ, Apache Kafka, and more
- 🔧 **Extensible Architecture**: Easy to add support for new queue systems

### 🖥️ **User-Friendly Interfaces**
- 💻 **Command Line Interface**: Simple CLI with debug and performance monitoring options
- ⚛️ **React Frontend**: Interactive web interface for configuration building and data preview
- 🔌 **REST API**: FastAPI-powered backend for programmatic access and integration
- 🐳 **Docker Support**: Containerized deployment with single-command setup

### 📈 **Performance & Monitoring**
- 📊 **Performance Profiling**: Built-in performance monitoring with detailed timing reports
- 💾 **Memory Optimization**: Efficient data generation for large datasets
- ⏳ **Progress Tracking**: Real-time progress indicators for long-running generations
- 🏗️ **Scalable Architecture**: Handle datasets from thousands to millions of rows

### 🔧 **Developer Experience**
- 🧩 **Extensible Design**: Easy to add custom strategies and generators
- 🛡️ **Type Safety**: Full type hints and validation throughout the codebase
- 📖 **Comprehensive Documentation**: Detailed examples and configuration guides
- 🚨 **Error Handling**: Clear error messages and validation feedback




## 🧠 Key Concepts

### 🎯 Strategies (`strategy`)
A strategy defines how the data is going to be generated for a column.

Strategies are the core of the framework. They are the building blocks of the data generation pipeline. another way to think about it is that strategies are the functions that are used to generate the data. they are the lower-level apis that are used to generate the data.

### 🏗️ Generators (`generator`)
A generator is a wrapper around a collection of strategies that are used to generate the data for a column.

Generators are the higher-level apis, an abstraction to hide the parameters of strategies. and generating data seemlessly.

for example, Person Name can be a generator that is a wrapper around the [Random Name Strategy](./strategies/random_name_strategy.py)

or a Date of Birth can be a generator that is a wrapper around the [Date Generator Strategy](./strategies/date_generator_strategy.py) that is used to generate this kind of data.

**Pre-built Generators**: GenXData now includes domain-specific generator collections in the `generators/` directory:
- 🛒 **ecommerce_generators.json**: Product categories, pricing, order statuses, payment methods
- 🏥 **healthcare_generators.json**: Medical conditions, treatments, patient data
- 🎓 **education_generators.json**: Academic subjects, grades, enrollment data
- 🌍 **geographic_generators.json**: Countries, cities, coordinates, addresses
- 🚗 **transportation_generators.json**: Vehicle types, routes, logistics data
- 💼 **business_generators.json**: Company data, financial metrics, market segments
- 🔧 **technology_generators.json**: Software versions, hardware specs, tech stack data
- 🏭 **iot_sensors_generators.json**: Sensor readings, device data, telemetry

and so on, There can be 100s of generators

## 📋 About the tool

The `main.py` reads a config file in `yaml` format and applies data generation strategies based on the config file to the columns. The script uses various data generation strategies such as regular expression, series, random names, and distribution-based data generation. It is capable of generating data independently or dependent on other columns for each column.


## 🎲 Available Strategies

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

Although there could be more strategies, but the above ones can be the foundation for most of the data generation needs. and above that you can use generators to create more complex data generation logic.

### 📊 Performance Monitoring
You can generate a performance report for your data generation by using the `--perf` flag:

```bash
python main.py ./examples/config.yaml --perf
```
This will show detailed timing information for each operation, helping you identify bottlenecks in your data generation pipeline. The report includes:
- Time spent on each column/strategy
- Average execution time
- Rows processed per second


## 📁 Output Formats
The data generator supports multiple output formats. You can specify one or more file writers in your configuration file:

### 💾 Available File Writers
- CSV
- Excel
- JSON
- Parquet
- SQLite
- HTML
- Feather

You can specify multiple writers to output the same data in different formats simultaneously. See `examples` for a complete example.

## 📝 YAML Configuration Support

The data generator now supports a more readable YAML configuration, see `examples/all_example.yaml` for a complete example.


Consider dropping a star ⭐️ if you like the project.
Or I Would glad to hear any questions, feedback, feature requests or bug reports.
[twitter](https://x.com/@beingkarnage)
[linkedin](https://www.linkedin.com/in/tosifkhan99/)
[khantosif94@gmail.com](mailto:khantosif94@gmail.com)

