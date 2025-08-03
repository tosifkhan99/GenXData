import json
from pathlib import Path
from typing import Any

import yaml

from exceptions.param_exceptions import InvalidConfigParamException


def load_all_generators() -> dict[str, dict[str, Any]]:
    """Load all generators from all generator files."""
    generators = {}
    generators_dir = Path("generators")

    if not generators_dir.exists():
        generators_dir = Path("../generators")  # Try relative path

    if not generators_dir.exists():
        return {}

    for json_file in generators_dir.glob("*.json"):
        try:
            with open(json_file) as f:
                file_generators = json.load(f)
                generators.update(file_generators)
        except Exception:
            pass

    return generators


def list_available_generators(filter_by: str | None = None) -> list[str]:
    """
    List all available generators, optionally filtered by domain or strategy type.

    Args:
        filter_by: Optional filter string to search in generator names

    Returns:
        List of generator names
    """
    generators = load_all_generators()
    generator_names = list(generators.keys())

    if filter_by:
        filter_by = filter_by.upper()
        generator_names = [name for name in generator_names if filter_by in name]

    return sorted(generator_names)


def get_generator_info(generator_name: str) -> dict[str, Any]:
    """
    Get detailed information about a specific generator.

    Args:
        generator_name: Name of the generator

    Returns:
        Generator configuration details
    """
    generators = load_all_generators()

    if generator_name not in generators:
        available = list_available_generators()
        raise ValueError(
            f"Generator '{generator_name}' not found. Available generators: {available[:10]}..."
        )

    return generators[generator_name]


def get_generators_by_strategy(strategy_name: str) -> list[str]:
    """
    Get all generators that use a specific strategy implementation.

    Args:
        strategy_name: Name of the strategy (e.g., 'RANDOM_NAME_STRATEGY')

    Returns:
        List of generator names using that strategy
    """
    generators = load_all_generators()
    matching_generators = []

    for gen_name, gen_config in generators.items():
        if gen_config.get("implementation") == strategy_name:
            matching_generators.append(gen_name)

    return sorted(matching_generators)


def create_all_example_config() -> dict[str, Any]:
    """
    Create a configuration that matches the structure of all_example.json using generators.

    Returns:
        Configuration dictionary matching all_example.json structure
    """
    return generator_to_config(
        {
            "employee_id": "EMPLOYEE_ID",
            "first_name": "PERSON_NAME",
            "last_name": "LAST_NAME",
            "email": "EMAIL_PATTERN",
            "phone": "PHONE_NUMBER",
            "department": "DEPARTMENT",
            "join_date": "RECENT_DATE",
            "salary": "SALARY",
            "performance_rating": "PRIORITY_LEVEL",
            "bonus": "PERCENTAGE",
            "project_code": "PRODUCT_SKU",
        },
        num_rows=100,
        metadata={
            "name": "all_example_from_generators",
            "description": "Employee dataset generated using pre-configured generators",
            "version": "1.0.0",
            "author": "GenXData Generator System",
        },
    )


def generator_to_config(
    generator_mapping: dict[str, str] | list[dict[str, str]] | str,
    num_rows: int = 100,
    output_config: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Convert generator names to valid GenXData configuration format.

    Args:
        generator_mapping: Can be:
            - Dict mapping column names to generator names: {"name": "FULL_NAME", "age": "PERSON_AGE"}
            - List of dicts with column-generator mappings: [{"column": "name", "generator": "FULL_NAME"}]
            - Single generator name as string: "FULL_NAME" (will use generator name as column name)
        num_rows: Number of rows to generate
        output_config: Optional output configuration (file writers)
        metadata: Optional metadata for the configuration

    Returns:
        Dictionary containing valid GenXData configuration
    """

    # Load all available generators
    all_generators = load_all_generators()

    # Normalize input to column->generator mapping
    if isinstance(generator_mapping, str):
        # Single generator - use generator name as column name
        column_generator_map = {generator_mapping.lower(): generator_mapping}
    elif isinstance(generator_mapping, list):
        # List of mappings
        column_generator_map = {}
        for item in generator_mapping:
            if isinstance(item, dict):
                if "column" in item and "generator" in item:
                    column_generator_map[item["column"]] = item["generator"]
                else:
                    # Assume first key is column, first value is generator
                    key, value = next(iter(item.items()))
                    column_generator_map[key] = value
            else:
                raise ValueError(f"Invalid list item format: {item}")
    elif isinstance(generator_mapping, dict):
        # Direct column->generator mapping
        column_generator_map = generator_mapping
    else:
        raise ValueError(f"Invalid generator_mapping type: {type(generator_mapping)}")

    # Build the configuration
    config = {
        "metadata": metadata
        or {
            "name": "generated_config",
            "description": "Auto-generated configuration from generators",
            "version": "1.0.0",
        },
        "column_name": list(column_generator_map.keys()),
        "num_of_rows": num_rows,
        "shuffle": True,
        "configs": [],
    }

    # Add output configuration if provided
    if output_config:
        config["file_writer"] = output_config
    else:
        # Default JSON output
        config["file_writer"] = [
            {
                "type": "JSON_WRITER",
                "params": {
                    "output_path": "./output/generated_data.json",
                    "orient": "records",
                    "date_format": "iso",
                    "indent": 2,
                },
            }
        ]

    # Convert each generator to config format
    for column_name, generator_name in column_generator_map.items():
        if generator_name not in all_generators:
            raise ValueError(
                f"Generator '{generator_name}' not found. Available generators: {list(all_generators.keys())[:10]}..."
            )

        generator_def = all_generators[generator_name]

        # Convert generator format to config format
        config_entry = {
            "names": [column_name],
            "strategy": {
                "name": generator_def["implementation"],
                "params": generator_def["params"],
            },
        }

        config["configs"].append(config_entry)

    return config


def save_config_as_yaml(config: dict[str, Any], output_path: str) -> None:
    """Save configuration as YAML file."""
    from .file_utils import ensure_output_dir

    output_path = Path(output_path)
    ensure_output_dir(str(output_path.parent))

    with open(output_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, indent=2, sort_keys=False)


def save_config_as_json(config: dict[str, Any], output_path: str) -> None:
    """Save configuration as JSON file."""
    from .file_utils import ensure_output_dir

    output_path = Path(output_path)
    ensure_output_dir(str(output_path.parent))

    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)


def create_domain_configs_example():
    """Create configuration files for different domains using generators."""

    domains = {
        "healthcare": {
            "patient_id": "PATIENT_ID",
            "patient_name": "FULL_NAME",
            "age": "PATIENT_AGE",
            "blood_type": "BLOOD_TYPE",
            "condition": "MEDICAL_CONDITION",
            "department": "HOSPITAL_DEPARTMENT",
            "heart_rate": "VITAL_SIGNS_HEART_RATE",
            "temperature": "BODY_TEMPERATURE",
            "insurance": "INSURANCE_TYPE",
        },
        "iot_sensors": {
            "sensor_id": "SENSOR_ID",
            "temperature": "TEMPERATURE_CELSIUS",
            "humidity": "HUMIDITY_PERCENT",
            "pressure": "PRESSURE_HPA",
            "light_level": "LIGHT_LUX",
            "sound_level": "SOUND_DB",
            "battery_level": "BATTERY_LEVEL_PERCENT",
            "device_status": "DEVICE_STATUS",
        },
        "transportation": {
            "vehicle_type": "VEHICLE_TYPE",
            "manufacturer": "VEHICLE_MANUFACTURER",
            "fuel_type": "FUEL_TYPE",
            "color": "VEHICLE_COLOR",
            "year": "VEHICLE_YEAR",
            "mileage": "MILEAGE",
            "speed": "SPEED_KMH",
            "shipping_status": "SHIPPING_STATUS",
        },
        "education": {
            "student_id": "STUDENT_ID",
            "grade": "STUDENT_GRADE",
            "gpa": "GPA",
            "academic_year": "ACADEMIC_YEAR",
            "semester": "SEMESTER",
            "major": "MAJOR",
            "class_year": "CLASS_YEAR",
            "attendance": "ATTENDANCE_RATE",
        },
        "ecommerce": {
            "order_id": "ORDER_ID",
            "product_name": "PRODUCT_NAME",
            "product_category": "PRODUCT_CATEGORY",
            "price": "PRODUCT_PRICE",
            "quantity": "ORDER_QUANTITY",
            "customer_email": "EMAIL_PATTERN",
            "payment_method": "PAYMENT_METHOD",
            "order_status": "ORDER_STATUS",
        },
    }

    for domain_name, generators in domains.items():
        try:
            config = generator_to_config(
                generators,
                num_rows=500,
                metadata={
                    "name": f"{domain_name}_dataset",
                    "description": f"Generated {domain_name} dataset using pre-configured generators",
                    "version": "1.0.0",
                    "domain": domain_name,
                },
            )

            # Save both YAML and JSON versions
            save_config_as_yaml(config, f"./output/{domain_name}_config.yaml")
            save_config_as_json(config, f"./output/{domain_name}_config.json")

        except Exception:
            pass


def validate_generator_config(config: dict[str, Any]) -> bool:
    # todo: make it class based validation
    """
    Basic Validatation that a configuration dictionary is properly formatted for GenXData.

    Args:
        config: Configuration dictionary to validate

    Returns:
        True if valid, raises ValueError if invalid
    """
    required_fields = ["column_name", "num_of_rows", "configs", "file_writer"]

    for field in required_fields:
        if field not in config:
            raise InvalidConfigParamException(f"Missing required field: {field}")

    if not isinstance(config["configs"], list):
        raise InvalidConfigParamException("'configs' must be a list")

    for i, config_entry in enumerate(config["configs"]):
        if "names" not in config_entry:
            raise InvalidConfigParamException(f"Config entry {i} missing 'names' field")
        if "strategy" not in config_entry:
            raise InvalidConfigParamException(
                f"Config entry {i} missing 'strategy' field"
            )
        if "name" not in config_entry["strategy"]:
            raise InvalidConfigParamException(
                f"Config entry {i} strategy missing 'name' field"
            )
        if "params" not in config_entry["strategy"]:
            raise InvalidConfigParamException(
                f"Config entry {i} strategy missing 'params' field"
            )

    if not isinstance(config["file_writer"], dict):
        raise InvalidConfigParamException("'file_writer' must be a dictionary")
    if "type" not in config["file_writer"]:
        raise InvalidConfigParamException("'file_writer' must be a dictionary with a 'type' field")

    return True


def get_generator_stats() -> dict[str, Any]:
    """
    Get statistics about available generators.

    Returns:
        Dictionary with generator statistics
    """
    generators = load_all_generators()

    # Count generators by strategy
    strategy_counts = {}
    for gen_config in generators.values():
        strategy = gen_config.get("implementation", "unknown")
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

    # Count generators by domain (based on naming patterns)
    domain_patterns = {
        "healthcare": ["PATIENT", "MEDICAL", "HOSPITAL", "BLOOD", "VITAL", "INSURANCE"],
        "business": ["EMPLOYEE", "COMPANY", "DEPARTMENT", "SALARY", "PROJECT"],
        "ecommerce": ["PRODUCT", "ORDER", "PAYMENT", "CUSTOMER", "SUBSCRIPTION"],
        "education": ["STUDENT", "GRADE", "GPA", "ACADEMIC", "SEMESTER", "MAJOR"],
        "geographic": ["STATE", "CITY", "COUNTRY", "ADDRESS", "COORDINATE"],
        "technology": ["API", "DEVICE", "SOFTWARE", "SERVER", "DATABASE"],
        "iot": ["SENSOR", "TEMPERATURE", "HUMIDITY", "PRESSURE", "BATTERY"],
        "transportation": ["VEHICLE", "SHIPPING", "FLIGHT", "CARGO", "SPEED"],
    }

    domain_counts = dict.fromkeys(domain_patterns.keys(), 0)
    domain_counts["generic"] = 0

    for gen_name in generators.keys():
        gen_name_upper = gen_name.upper()
        matched_domain = False

        for domain, patterns in domain_patterns.items():
            if any(pattern in gen_name_upper for pattern in patterns):
                domain_counts[domain] += 1
                matched_domain = True
                break

        if not matched_domain:
            domain_counts["generic"] += 1

    return {
        "total_generators": len(generators),
        "strategy_distribution": strategy_counts,
        "domain_distribution": domain_counts,
        "available_strategies": list(strategy_counts.keys()),
    }
