# 🧬 GenXData
A Complete synthetic data framework for generating realistic data for your applications.

## 🚀 Getting Started

### 📦 Installation

GenXData uses Poetry for dependency management, which provides better dependency resolution and virtual environment management.

#### **🎯 Recommended: Poetry Installation**

**Step 1**: Install Poetry (if not already installed)
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Or using pip
pip install poetry
```

**Step 2**: Install project dependencies
```bash
# Install all dependencies (including dev dependencies)
poetry install

# Install only production dependencies
poetry install --only=main
```

**Step 3**: Activate the virtual environment
```bash
# Activate Poetry shell
poetry shell

# Or run commands with Poetry
poetry run python main.py --help
```

#### **📋 Alternative: Pip Installation**

If you prefer using pip, you can install dependencies directly:

```bash
# Install CLI dependencies
pip install -r cli-requirements.txt

# For API server and web interface
pip install fastapi uvicorn httpx

# For development
pip install -r cli-requirements.txt pytest black ruff
```

### 🛠️ Running the tool

**Step 1**: Create a configuration file. You can copy examples from the [examples](examples) directory, or create your own configs (refer to examples folder or visit documentation in [dev-docs](dev-docs) for more info).

**Step 2**: Run the script with your configuration:

**Using Poetry (Recommended):**
```bash
# Generate data with Poetry
poetry run python main.py generate path/to/your/config.yaml

# With verbose output and debugging
poetry run python main.py ./examples/all_example.yaml --debug
```

**Using Direct Python:**
```bash
# Generate data directly
python main.py generate path/to/your/config.yaml

# With verbose output and debugging
python main.py ./examples/all_example.yaml --debug
```

### 🔧 Development Setup

For contributors and developers:

```bash
# Clone the repository
git clone <repository-url>
cd GenXData

# Install with development dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run ruff check --fix .
```

### 💻 **CLI Interface**
GenXData includes a comprehensive command-line interface for managing generators and configurations. The CLI provides several commands to explore, create, and generate data efficiently.

#### **Installation**

**Using Poetry (Recommended):**
```bash
poetry install
poetry shell
```

**Using Pip:**
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
poetry run python -m cli.main_cli  # or: python -m cli.main_cli list-generators

# Filter generators by name pattern
poetry run python -m cli.main_cli  # or: python -m cli.main_cli list-generators --filter NAME

# Show comprehensive statistics
poetry run python -m cli.main_cli  # or: python -m cli.main_cli list-generators --show-stats

# Combine verbose logging with filtering
poetry run python -m cli.main_cli  # or: python -m cli.main_cli --verbose list-generators --filter NAME
```

##### **2. Show Generator Details**
Get detailed information about a specific generator:

```bash
# Show details of a specific generator
poetry run python -m cli.main_cli  # or: python -m cli.main_cli show-generator PERSON_NAME

# Output includes strategy and parameters
poetry run python -m cli.main_cli  # or: python -m cli.main_cli show-generator EMAIL_PATTERN
```

##### **3. Find Generators by Strategy**
List all generators using a specific strategy:

```bash
# Find generators using RANDOM_NAME_STRATEGY
poetry run python -m cli.main_cli  # or: python -m cli.main_cli by-strategy RANDOM_NAME_STRATEGY

# Find generators using DATE_GENERATOR_STRATEGY
poetry run python -m cli.main_cli  # or: python -m cli.main_cli by-strategy DATE_GENERATOR_STRATEGY
```

##### **4. Create Configuration Files**
Generate configuration files from generator mappings:

```bash
# Create config with generator mapping
poetry run python -m cli.main_cli  # or: python -m cli.main_cli create-config \
  --mapping "name:FULL_NAME,age:PERSON_AGE,email:EMAIL_PATTERN" \
  --output test_config.json \
  --rows 50

# Create config with custom metadata
poetry run python -m cli.main_cli  # or: python -m cli.main_cli create-config \
  --mapping "product:PRODUCT_NAME,price:PRODUCT_PRICE" \
  --output ecommerce_config.yaml \
  --rows 1000 \
  --name "Ecommerce Dataset" \
  --description "Product catalog data"

# Use a mapping file instead of command line
poetry run python -m cli.main_cli  # or: python -m cli.main_cli create-config \
  --mapping-file mapping.json \
  --output config.yaml \
  --rows 500
```

##### **5. Generate Domain Configurations**
Create example configurations for specific domains:

```bash
# Generate domain-specific configuration examples
poetry run python -m cli.main_cli  # or: python -m cli.main_cli generate-domain-configs

# Creates configs in ./output/ for:
# - ecommerce, healthcare, education, geographic
# - transportation, business, technology, iot_sensors
```

##### **6. Generate Data**
Generate data from configurations:

```bash
# Generate data from your configuration
poetry run python -m cli.main_cli  # or: python -m cli.main_cli generate config.json

# Generate from example configurations
poetry run python -m cli.main_cli  # or: python -m cli.main_cli generate ./examples/person_example.yaml

# Generate data from configuration
poetry run python -m cli.main_cli  # or: python -m cli.main_cli generate config.yaml --stream streaming_config.yaml
```

##### **7. Show Statistics**
View generator and strategy statistics:

```bash
# Show detailed statistics
poetry run python -m cli.main_cli  # or: python -m cli.main_cli stats

# Includes:
# - Total generators count
# - Strategy distribution
# - Domain distribution
# - Available strategies list
```

#### **Command Examples & Use Cases**

```bash
# Discover what generators are available
poetry run python -m cli.main_cli  # or: python -m cli.main_cli list-generators

# Find name-related generators
poetry run python -m cli.main_cli  # or: python -m cli.main_cli list-generators --filter NAME

# See all generators using a specific strategy
poetry run python -m cli.main_cli  # or: python -m cli.main_cli by-strategy RANDOM_NAME_STRATEGY

# Filter generators by name pattern
poetry run python -m cli.main_cli  # or: python -m cli.main_cli list-generators --filter PERSON

# Create a user profile dataset
poetry run python -m cli.main_cli  # or: python -m cli.main_cli create-config \
  --mapping "name:FULL_NAME,email:EMAIL_PATTERN,age:PERSON_AGE" \
  --output user_profiles.json \
  --rows 1000

# Generate the data
poetry run python -m cli.main_cli  # or: python -m cli.main_cli generate user_profiles.json

# Create all domain example configs
poetry run python -m cli.main_cli  # or: python -m cli.main_cli generate-domain-configs

# Generate healthcare data
poetry run python -m cli.main_cli  # or: python -m cli.main_cli generate ./output/healthcare_config.yaml

# Generate ecommerce data
poetry run python -m cli.main_cli  # or: python -m cli.main_cli generate ./output/ecommerce_config.yaml
```

#### **Important Notes**
- The CLI supports both JSON and YAML configuration formats
- Use `--verbose` for detailed logging and debugging
- Generator mappings can be provided via command line or file
- All generated configurations are validated before data generation
- The CLI is designed for both interactive use and automation scripts

**Domain Coverage**: GenXData includes 175+ generators across 9 domains:
  - **Person** (31 generators): Names, demographics, contact information
  - **Geographic** (28 generators): Addresses, locations, coordinates
  - **Business** (23 generators): Company data, financial information
  - **Healthcare** (22 generators): Medical conditions, treatments, patient data
  - **Technology** (20 generators): Software versions, hardware specs, network data
  - **IoT Sensors** (20 generators): Device readings, environmental data
  - **Education** (19 generators): Academic subjects, grades, institutions
  - **Transportation** (19 generators): Vehicle data, logistics
  - **Ecommerce** (18 generators): Product data, pricing, orders

### 🌐 **REST API & Web Interface**

GenXData provides a comprehensive REST API built with FastAPI, offering programmatic access to all data generation capabilities. The API is designed for integration with web applications, microservices, and automated workflows.

#### **🔌 API Server**

**Quick Start:**

**Using Poetry (Recommended):**
```bash
# Start the API server with Poetry
poetry run uvicorn api:app --reload

# Server will be available at:
# - API: http://localhost:8000
# - Documentation: http://localhost:8000/api/docs
# - Alternative docs: http://localhost:8000/api/redoc
```

**Using Direct Python:**
```bash
# Start the API server directly
uvicorn api:app --reload
```

**Production Deployment:**
```bash
# Production server with Poetry
poetry run uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4

# Or directly
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

#### **📋 API Endpoints Overview**

##### **Health & Information**
- `GET /ping` - Simple health check
- `GET /api/health` - Comprehensive health status with features
- `GET /api/version` - API version and capabilities

##### **Strategy Management**
- `GET /get_all_strategies` - List all 13+ available strategies
- `GET /get_strategy_schemas` - Get detailed strategy parameter schemas

##### **Data Generation**
- `POST /generate_data` - Generate data and return as JSON
- `POST /generate_and_download` - Generate data and download as ZIP file
- `POST /api/streaming/generate` - Real-time streaming data generation
- `POST /api/batch/generate` - Large-scale batch data processing

##### **Configuration**
- `POST /api/config/validate` - Validate configuration before generation
- `GET /api/schemas/config` - Get complete configuration schema

##### **Frontend Serving**
- `GET /` - Serve React web interface
- `GET /{filename:path}` - Serve static assets

#### **📄 API Usage Examples**

**Python Client:**
```python
import requests

# Generate data
config = {
    "metadata": {"name": "User Dataset"},
    "column_name": ["name", "email", "age"],
    "num_of_rows": 100,
    "configs": [
        {
            "names": ["name"],
            "strategy": {"name": "RANDOM_NAME_STRATEGY", "params": {}}
        },
        {
            "names": ["email"],
            "strategy": {"name": "PATTERN_STRATEGY", "params": {"regex": "[a-z]{5}@example.com"}}
        },
        {
            "names": ["age"],
            "strategy": {"name": "NUMBER_RANGE_STRATEGY", "params": {"min_value": 18, "max_value": 65}}
        }
    ],
    "file_writer": {"type": "CSV_WRITER", "params": {"output_path": "users.csv"}}
}

response = requests.post("http://localhost:8000/generate_data", json=config)
data = response.json()
```

**JavaScript/Node.js Client:**
```javascript
// Generate and download data
const config = {
    metadata: { name: "Product Catalog" },
    column_name: ["product_name", "price", "category"],
    num_of_rows: 500,
    configs: [
        {
            names: ["product_name"],
            strategy: { name: "RANDOM_NAME_STRATEGY", params: {} }
        },
        {
            names: ["price"],
            strategy: { name: "NUMBER_RANGE_STRATEGY", params: { min_value: 10, max_value: 1000 } }
        }
    ]
};

fetch('http://localhost:8000/generate_and_download', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
})
.then(response => response.blob())
.then(blob => {
    // Handle file download
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'generated_data.zip';
    a.click();
});
```

**cURL Examples:**
```bash
# Health check
curl http://localhost:8000/ping

# Get all strategies
curl http://localhost:8000/get_all_strategies

# Generate data
curl -X POST http://localhost:8000/generate_data \
  -H "Content-Type: application/json" \
  -d @config.json

# Validate configuration
curl -X POST http://localhost:8000/api/config/validate \
  -H "Content-Type: application/json" \
  -d @config.json
```

#### **⚛️ React Frontend**

**Development Setup:**
```bash
cd frontend
npm install
npm run dev
# Frontend available at http://localhost:5173
```

**Frontend Features:**
- 🎨 **Interactive Configuration Builder**: Visual form-based config creation
- 📊 **Real-time Preview**: See generated data samples before full generation
- 📁 **Multiple Export Formats**: CSV, Excel, JSON, Parquet, and more
- 🎯 **Strategy Selection**: Choose from 13+ generation strategies with parameter forms
- 📋 **Project Management**: Save and load configurations with metadata
- 🔧 **Validation**: Real-time configuration validation and error feedback

#### **🐳 Docker Deployment**

**Quick Start:**
```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the application:
# - Frontend: http://localhost:3000
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/api/docs
```

**Manual Docker Build:**
```bash
# Build the image
docker build -t genxdata .

# Run the container
docker run -p 8000:8000 genxdata

# Or pull the pre-built image
docker pull genxdata:latest
```

**Production Docker:**
```bash
# Production deployment with environment variables
docker run -d \
  -p 8000:8000 \
  -e WORKERS=4 \
  -e LOG_LEVEL=info \
  --name genxdata-prod \
  genxdata:latest
```

#### **🔒 API Security & Performance**

**Security Features:**
- ✅ **CORS Support**: Configurable cross-origin resource sharing
- ✅ **Input Validation**: Comprehensive request validation and sanitization
- ✅ **Error Handling**: Safe error messages without sensitive data exposure
- ✅ **Rate Limiting**: Built-in protection against abuse (configurable)

**Performance Optimizations:**
- ⚡ **Async Processing**: FastAPI async support for concurrent requests
- 💾 **Memory Management**: Efficient data generation with streaming support
- 📦 **Response Compression**: ZIP compression for large datasets
- 🔄 **Batch Processing**: Handle large-scale data generation efficiently


## 🏗️ Project Structure

```
GenXData/
├── core/                   # Core data generation engine
│   ├── orchestrator.py     # Main processing orchestrator
│   ├── strategies/         # 13 generation strategies
│   ├── processors/         # Normal, streaming, and batch processors
│   └── streaming/          # Streaming and batch processing
├── cli/                    # Command-line interface
├── utils/                  # Utility functions and helpers
├── configs/                # Configuration files and settings
├── generators/             # 175+ pre-built generators (9 domains)
├── exceptions/             # Custom exception hierarchy
├── messaging/              # Message queue integration (AMQP, Kafka)
├── frontend/               # React web interface
├── dev-docs/               # Architecture and API documentation
├── examples/               # Example configurations
└── api.py                  # FastAPI server

Key Files:
├── api.py                  # REST API server (FastAPI)
├── main.py                 # Programmatic entry point
├── pyproject.toml          # Poetry dependency management
├── docker-compose.yml      # Docker deployment configuration
└── Dockerfile              # Container build configuration
```

## ✨ Features

### 🚀 **Comprehensive Data Generation Strategies**
- 🔢 **Numeric Data**: Random numbers, ranges, distributions, series
- 📅 **Date/Time Data**: Date ranges, time series, custom formats
- 📝 **Text Data**: Names, patterns, concatenation, replacements
- 🎲 **Choice Data**: Categorical data with custom probability distributions
- 🔗 **Relationship Data**: Foreign keys, references, dependencies
- 🎭 **Pattern Masking**: Apply masking patterns to sensitive data generation
- 🔢 **Series Generation**: Create sequential or arithmetic series data
- 🔄 **Value Replacement**: Replace or delete specific values based on conditions

### 📁 **Multiple Output Formats**
- 📊 **CSV**: Comma-separated values with custom delimiters
- 📈 **Excel**: Multi-sheet Excel files with formatting
- 🗃️ **JSON**: Structured JSON data with nested objects
- 🚀 **Parquet**: High-performance columnar storage
- ⚡ **Feather**: Fast binary format for data interchange

### ⚙️ **Flexible Configuration**
- 📝 **YAML/JSON Support**: Human-readable configuration files
- 🎯 **Generator Mappings**: 175+ pre-built generators across 9 domains
- 🔧 **Custom Parameters**: Fine-tune generation with strategy-specific parameters
- 📋 **Metadata Support**: Project information, versioning, and documentation

### 🎯 **Advanced Capabilities**
- 🎭 **Pattern Masking**: Apply masking patterns to sensitive data generation
- 🔢 **Series Generation**: Create sequential or arithmetic series data
- 🔄 **Value Replacement**: Replace or delete specific values based on conditions

### 🌐 **Streaming & Queue Integration**
- 📡 **Abstract Queue System**: Support for multiple message queue systems (AMQP, Kafka)
- 🔄 **Real-time Streaming**: Stream data batches to message queues as they're generated
- 🏭 **Enterprise Ready**: Support for Apache Artemis, RabbitMQ, Apache Kafka, and more
- 🔧 **Extensible Architecture**: Easy to add support for new queue systems

### 🖥️ **User-Friendly Interfaces**
- 💻 **Command Line Interface**: Comprehensive CLI with 175+ generators and domain-specific commands
- ⚛️ **React Frontend**: Modern web interface with interactive configuration builder and real-time preview
- 🔌 **REST API**: FastAPI-powered backend with 12+ endpoints for programmatic access and integration
- 🐳 **Docker Support**: Containerized deployment with single-command setup and production-ready configuration
- 📚 **API Documentation**: Interactive Swagger/OpenAPI documentation at `/api/docs`
- 🔧 **Development Tools**: Hot reload, debugging support, and comprehensive error handling

### 📈 **Performance & Monitoring**
- 📊 **Performance Profiling**: Built-in performance monitoring with detailed timing reports
- 💾 **Memory Optimization**: Efficient data generation for large datasets with streaming support
- ⏳ **Progress Tracking**: Real-time progress indicators for long-running generations
- 🏗️ **Scalable Architecture**: Handle datasets from thousands to millions of rows
- ⚡ **Async Processing**: Non-blocking API operations with concurrent request handling

### 🔧 **Developer Experience**
- 🧩 **Extensible Design**: Easy to add custom strategies and generators
- 🛡️ **Type Safety**: Full type hints and validation throughout the codebase
- 📖 **Comprehensive Documentation**: Detailed examples, configuration guides, and API reference
- 🚨 **Error Handling**: Clear error messages and validation feedback
- 🔍 **Debugging Tools**: Verbose logging, performance monitoring, and diagnostic endpoints

## 🧠 Key Concepts

### 🎯 Strategies (`strategy`)
A strategy defines how the data is going to be generated for a column.

Strategies are the core of the framework. They are the building blocks of the data generation pipeline. Another way to think about it is that strategies are the functions that are used to generate the data. They are the lower-level APIs that are used to generate the data.

### 🏗️ Generators (`generator`)
A generator is a wrapper around a collection of strategies that are used to generate the data for a column.

Generators are the higher-level APIs, an abstraction to hide the parameters of strategies and generate data seamlessly.

For example, Person Name can be a generator that is a wrapper around the [Random Name Strategy](./core/strategies/random_name_strategy.py)

Or a Date of Birth can be a generator that is a wrapper around the [Date Generator Strategy](./core/strategies/date_generator_strategy.py) that is used to generate this kind of data.

**Pre-built Generators**: GenXData now includes domain-specific generator collections in the `generators/` directory:
- 🛒 **ecommerce_generators.json**: Product categories, pricing, order statuses, payment methods
- 🏥 **healthcare_generators.json**: Medical conditions, treatments, patient data
- 🎓 **education_generators.json**: Academic subjects, grades, enrollment data

## 📋 About the tool

GenXData is a comprehensive synthetic data generation framework designed for developers, data scientists, and QA engineers who need realistic test data for their applications. With 13+ generation strategies, 175+ pre-built generators, and support for multiple interfaces (CLI, REST API, Web UI), GenXData provides everything you need to generate high-quality synthetic data at scale.

## 🎲 Available Strategies

1. **RANDOM_NUMBER_RANGE_STRATEGY** - Generate random numbers within specified ranges
2. **DISTRIBUTED_NUMBER_RANGE_STRATEGY** - Generate numbers with custom probability distributions
3. **DATE_GENERATOR_STRATEGY** - Generate dates within specified ranges and formats
4. **DISTRIBUTED_DATE_RANGE_STRATEGY** - Generate dates with weighted distributions
5. **PATTERN_STRATEGY** - Generate data matching regular expression patterns
6. **SERIES_STRATEGY** - Generate sequential or arithmetic series
7. **DISTRIBUTED_CHOICE_STRATEGY** - Generate categorical data with custom probabilities
8. **TIME_RANGE_STRATEGY** - Generate time values within specified ranges
9. **DISTRIBUTED_TIME_RANGE_STRATEGY** - Generate time values with weighted distributions
10. **REPLACEMENT_STRATEGY** - Replace or transform existing values
11. **CONCAT_STRATEGY** - Concatenate multiple columns or values
12. **RANDOM_NAME_STRATEGY** - Generate realistic names with gender and type filtering
13. **DELETE_STRATEGY** - Conditionally delete or nullify values

Each strategy is highly configurable and can be combined to create complex data generation scenarios.

### 📊 Performance Monitoring

GenXData includes built-in performance monitoring capabilities:

```bash
# Enable performance reporting
python main.py generate config.yaml --perf-report

# CLI with performance monitoring
poetry run python -m cli.main_cli  # or: python -m cli.main_cli generate config.yaml --verbose
```

Performance reports include:
- Generation time per strategy
- Memory usage statistics
- Row generation rates
- Bottleneck identification

## 📁 Output Formats

GenXData supports multiple output formats to fit your workflow:

### 💾 Available File Writers

- **CSV_WRITER**: Comma-separated values with custom delimiters
- **EXCEL_WRITER**: Multi-sheet Excel files with formatting options
- **JSON_WRITER**: Structured JSON with nested object support
- **PARQUET_WRITER**: High-performance columnar storage format
- **FEATHER_WRITER**: Fast binary format for data interchange
- **HTML_WRITER**: HTML tables for web display and reporting
- **SQLITE_WRITER**: SQLite database files for direct querying

## 📝 YAML Configuration Support

GenXData fully supports YAML configuration files for better readability and maintainability:

```yaml
metadata:
  name: "User Dataset"
  description: "Sample user data for testing"
  version: "1.0.0"

column_name:
  - name
  - email
  - age

num_of_rows: 1000

configs:
  - names: ["name"]
    strategy:
      name: "RANDOM_NAME_STRATEGY"
      params: {}

  - names: ["email"]
    strategy:
      name: "PATTERN_STRATEGY"
      params:
        regex: "[a-z]{5}@example.com"

file_writer:
  type: "CSV_WRITER"
  params:
    output_path: "users.csv"
```

---

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## �� Links

- **Documentation**: [dev-docs/](dev-docs/)
- **API Reference**: http://localhost:8000/api/docs (when server is running)
- **Examples**: [examples/](examples/)
- **Architecture**: [dev-docs/architecture.mmd](dev-docs/architecture.mmd)
- **API Endpoints**: [dev-docs/api-endpoints.mmd](dev-docs/api-endpoints.mmd)
