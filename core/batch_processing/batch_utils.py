"""
Batch processing utilities for GenXData.
"""

import copy
import configs.GENERATOR_SETTINGS as SETTINGS


# State-dependent strategies that need parameter adjustment across batches
STATE_DEPENDENT_STRATEGIES = {
    "SERIES_STRATEGY": ["start"],
    "INCREMENTAL_STRATEGY": ["start"],
    "TIME_RANGE_STRATEGY": ["start_time", "end_time"],
    "DATE_RANGE_STRATEGY": ["start_date", "end_date"],
    "TIME_INCREMENT_STRATEGY": ["start_time", "end_time"],
    "DATE_INCREMENT_STRATEGY": ["start_date", "end_date"],
}


def get_batches(batch_size, rows):
    """
    Calculate batch sizes for processing.

    Args:
        batch_size (int): Desired batch size
        rows (int): Total number of rows

    Returns:
        list: List of batch sizes
    """
    full_batches = rows // batch_size
    remainder = rows % batch_size
    batches = [batch_size] * full_batches

    if remainder:
        if remainder <= 100 and batches:
            batches[-1] += remainder
        else:
            batches.append(remainder)

    return batches


def prepare_batch_config(original_config, batch_size, batch_index, strategy_states):
    """
    Prepare config for a specific batch, adjusting parameters for state-dependent strategies.

    Args:
        original_config (dict): Original configuration
        batch_size (int): Size of current batch
        batch_index (int): Index of current batch
        strategy_states (dict): State tracking for strategies

    Returns:
        dict: Modified configuration for the batch
    """
    batch_config = copy.deepcopy(original_config)
    batch_config["num_of_rows"] = batch_size
    batch_config["write_output"] = False

    # Calculate cumulative rows processed so far
    cumulative_rows = sum(
        get_batches(SETTINGS.STREAM_BATCH_SIZE, original_config["num_of_rows"])[
            :batch_index
        ]
    )

    # Adjust parameters for state-dependent strategies
    for config_item in batch_config["configs"]:
        strategy_name = config_item["strategy"]["name"]

        if strategy_name in STATE_DEPENDENT_STRATEGIES:
            for col_name in config_item["names"]:
                adjust_strategy_params(
                    config_item, col_name, cumulative_rows, strategy_states
                )

    return batch_config


def adjust_strategy_params(config_item, col_name, cumulative_rows, strategy_states):
    """
    Adjust strategy parameters based on previous batches.

    Args:
        config_item (dict): Configuration item for the strategy
        col_name (str): Column name
        cumulative_rows (int): Number of rows processed so far
        strategy_states (dict): State tracking for strategies
    """
    strategy_name = config_item["strategy"]["name"]
    params = config_item["strategy"]["params"]

    if strategy_name == "SERIES_STRATEGY":
        # For series strategy, adjust the start value
        original_start = params.get("start", 1)
        step = params.get("step", 1)

        # Calculate new start value based on cumulative rows
        new_start = original_start + (cumulative_rows * step)
        params["start"] = new_start

        # Store state for potential future use
        strategy_states[f"{strategy_name}_{col_name}"] = {
            "last_value": new_start + (config_item.get("batch_size", 100) * step) - step
        }
