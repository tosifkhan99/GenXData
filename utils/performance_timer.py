"""
Utility for measuring and reporting performance in data generation.
"""

import time
from contextlib import contextmanager
from functools import wraps


class PerformanceTracker:
    """Class to track and report performance metrics for data generation"""

    def __init__(self):
        self.metrics = {}
        self.current_operation = None

    def start_operation(self, operation_name):
        """Start timing an operation"""
        self.current_operation = operation_name
        return time.time()

    def end_operation(self, start_time, rows_processed=None):
        """End timing an operation and record metrics"""
        if not self.current_operation:
            return

        elapsed = time.time() - start_time

        if self.current_operation not in self.metrics:
            self.metrics[self.current_operation] = {
                "count": 0,
                "total_time": 0,
                "max_time": 0,
                "min_time": float("inf"),
                "rows_processed": 0,
            }

        metrics = self.metrics[self.current_operation]
        metrics["count"] += 1
        metrics["total_time"] += elapsed
        metrics["max_time"] = max(metrics["max_time"], elapsed)
        metrics["min_time"] = min(metrics["min_time"], elapsed)

        if rows_processed:
            metrics["rows_processed"] += rows_processed

        self.current_operation = None

        return elapsed

    def report(self):
        """Generate a report of all tracked performance metrics"""
        if not self.metrics:
            return "No performance data collected"

        lines = ["Performance Report:"]
        lines.append("-" * 110)
        lines.append(
            f"{'Operation':<30} {'Count':<10} {'Total (s)':<12} {'Avg (s)':<12} {'Min (s)':<12} {'Max (s)':<12} {'Rows/sec':<12}"
        )
        lines.append("-" * 110)

        for operation, data in sorted(
            self.metrics.items(), key=lambda x: x[1]["total_time"], reverse=True
        ):
            avg_time = data["total_time"] / data["count"] if data["count"] > 0 else 0
            rows_per_sec = (
                data["rows_processed"] / data["total_time"]
                if data["total_time"] > 0 and data["rows_processed"] > 0
                else None
            )

            if rows_per_sec:
                rows_per_sec_str = f"{rows_per_sec:.2f}"
            else:
                rows_per_sec_str = "N/A"

            lines.append(
                f"{operation:<50} {data['count']:<10} {data['total_time']:<12.4f} {avg_time:<12.4f} {data['min_time']:<12.4f} {data['max_time']:<12.4f} {rows_per_sec_str:<12}"
            )

        return "\n".join(lines)


# Create a global tracker instance
tracker = PerformanceTracker()


@contextmanager
def measure_time(operation_name, rows_processed=None):
    """Context manager to measure execution time of a block of code"""
    start_time = tracker.start_operation(operation_name)
    try:
        yield
    finally:
        tracker.end_operation(start_time, rows_processed)


def time_operation(func):
    """Decorator to measure execution time of a function"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        operation_name = f"{func.__module__}.{func.__name__}"
        start_time = tracker.start_operation(operation_name)
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            rows = kwargs.get("rows", None)
            tracker.end_operation(start_time, rows)

    return wrapper


def get_performance_report():
    """Generate a performance report"""
    return tracker.report()
