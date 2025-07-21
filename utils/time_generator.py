from datetime import datetime
import random


def timeGenerator(end_time_str, start_time_str, format_str="%H:%M:%S"):
    """
    Generate a random time between start_time and end_time.

    Args:
        end_time_str: End time as string
        start_time_str: Start time as string
        format_str: Time format string (default: "%H:%M:%S")

    Returns:
        Random time as formatted string
    """
    start_time = datetime.strptime(start_time_str, format_str)
    end_time = datetime.strptime(end_time_str, format_str)

    # Convert times to seconds from midnight
    start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
    end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second

    # Generate random seconds between start and end
    random_seconds = random.randint(start_seconds, end_seconds)

    # Convert back to time
    random_time = datetime(
        1900,
        1,
        1,
        random_seconds // 3600,  # hours
        (random_seconds % 3600) // 60,  # minutes
        random_seconds % 60,
    )  # seconds

    # Format and return
    return random_time.strftime(format_str)
