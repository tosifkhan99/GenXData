from typing import Any, TypedDict


class ErrorContext(TypedDict, total=False):
    """Type definition for error context options"""

    generator: str | None
    strategy_name: str | None
    strategy_params: dict[str, Any] | None
    config: dict[str, Any] | None
    batch: dict[str, Any] | None
    stream: dict[str, Any] | None
    perf_report: dict[str, Any] | None
    log_level: str | None
    column: str | None
    row: int | None
    value: Any | None
    config_path: str | None
