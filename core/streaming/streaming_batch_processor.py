"""
Streaming batch processor for GenXData.
Implements stateful chunked generation approach for efficient batch processing.
"""

import pandas as pd
from typing import Dict, List, Any
from abc import ABC, abstractmethod

from core.strategy_factory import StrategyFactory
from utils.logging import Logger


class BatchWriter(ABC):
    """Abstract base class for batch writers"""

    @abstractmethod
    def write_batch(self, df: pd.DataFrame, batch_info: Dict[str, Any]) -> None:
        """Write a batch to the output destination"""
        pass

    @abstractmethod
    def finalize(self) -> Dict[str, Any]:
        """Finalize writing and return summary information"""
        pass


class StreamingBatchProcessor:
    """
    Processes data generation in streaming chunks with stateful strategies.

    This approach eliminates the need for manual config parameter adjustments
    by maintaining strategy state internally and generating data continuously
    in chunks that are written when the batch size is reached.
    """

    def __init__(
        self,
        config: Dict[str, Any],
        batch_size: int,
        batch_writer: BatchWriter,
        chunk_size: int = 1000,
    ):
        """
        Initialize the streaming batch processor.

        Args:
            config: Configuration dictionary
            batch_size: Size of each batch to write
            batch_writer: Writer instance for batch output
            chunk_size: Size of chunks to generate at once (for efficiency)
        """
        self.config = config
        self.batch_size = batch_size
        self.batch_writer = batch_writer
        self.chunk_size = min(chunk_size, batch_size)  # Don't exceed batch size

        self.logger = Logger.get_logger("streaming_batch_processor")

        # Initialize processing state
        self.buffer = []
        self.total_generated = 0
        self.target_rows = config["num_of_rows"]
        self.batch_count = 0

        # Initialize stateful strategies
        self.strategies = self._initialize_strategies()

        self.logger.info(
            f"StreamingBatchProcessor initialized: target_rows={self.target_rows}, "
            f"batch_size={self.batch_size}, chunk_size={self.chunk_size}"
        )

    def _initialize_strategies(self) -> Dict[str, Any]:
        """Initialize stateful strategies for each column"""
        strategies = {}
        strategy_factory = StrategyFactory(
            self.logger
        )  # Pass logger to StrategyFactory

        for config_item in self.config["configs"]:
            strategy_name = config_item["strategy"]["name"]
            strategy_params = config_item["strategy"]["params"]

            # Create strategy instance for each column
            for col_name in config_item["names"]:
                self.logger.debug(
                    f"Initializing {strategy_name} for column '{col_name}'"
                )

                # Create strategy with column-specific parameters
                strategy_kwargs = {
                    "col_name": col_name,
                    "params": strategy_params.copy(),
                    "rows": self.target_rows,  # Total rows for context
                    "debug": self.config.get("debug", False),
                }

                strategy = strategy_factory.create_strategy(
                    strategy_name, **strategy_kwargs
                )
                strategies[col_name] = strategy

                self.logger.debug(
                    f"Strategy {strategy_name} initialized for '{col_name}'"
                )

        return strategies

    def _generate_chunk_data(self, chunk_size: int) -> List[Dict[str, Any]]:
        """
        Generate a chunk of data using stateful strategies.

        Args:
            chunk_size: Number of rows to generate

        Returns:
            List of dictionaries representing rows
        """
        self.logger.debug(f"Generating chunk of {chunk_size} rows")

        # Generate data for each column
        chunk_data = {}
        for col_name, strategy in self.strategies.items():
            if hasattr(strategy, "generate_chunk"):
                # Use stateful generation
                values = strategy.generate_chunk(chunk_size)
                self.logger.debug(
                    f"Generated {len(values)} values for column '{col_name}' using stateful method"
                )
            else:
                # Fallback to traditional generation (for non-stateful strategies)
                values = strategy.generate_data(chunk_size)
                self.logger.debug(
                    f"Generated {len(values)} values for column '{col_name}' using traditional method"
                )

            chunk_data[col_name] = values.tolist()

        # Convert to list of row dictionaries
        rows = []
        for i in range(chunk_size):
            row = {}
            for col_name, values in chunk_data.items():
                row[col_name] = values[i] if i < len(values) else None
            rows.append(row)

        return rows

    def _write_and_clear_buffer(self) -> None:
        """Write current buffer to output and clear it"""
        if not self.buffer:
            return

        # Convert buffer to DataFrame
        df = pd.DataFrame(self.buffer)

        # Apply shuffle if configured
        if self.config.get("shuffle", True):
            df = df.sample(frac=1).reset_index(drop=True)
            self.logger.debug(f"Shuffled batch of {len(df)} rows")

        # Prepare batch info
        batch_info = {
            "batch_index": self.batch_count,
            "batch_size": len(df),
            "total_generated": self.total_generated,
            "target_rows": self.target_rows,
            "config_name": self.config.get("metadata", {}).get("name", "unknown"),
            "timestamp": pd.Timestamp.now().isoformat(),
        }

        # Write batch
        self.logger.info(f"Writing batch {self.batch_count} with {len(df)} rows")
        self.batch_writer.write_batch(df, batch_info)

        # Clear buffer and update counters
        self.buffer.clear()
        self.batch_count += 1

        self.logger.debug(f"Buffer cleared, batch count: {self.batch_count}")

    def process(self) -> Dict[str, Any]:
        """
        Process the entire dataset using streaming batch approach.

        Returns:
            Dictionary with processing results and summary
        """
        self.logger.info(
            f"Starting streaming batch processing for {self.target_rows} rows"
        )

        try:
            while self.total_generated < self.target_rows:
                # Calculate how many rows to generate in this chunk
                remaining_rows = self.target_rows - self.total_generated
                chunk_size = min(self.chunk_size, remaining_rows)

                self.logger.debug(
                    f"Generating chunk: size={chunk_size}, "
                    f"total_generated={self.total_generated}, "
                    f"remaining={remaining_rows}"
                )

                # Generate chunk
                chunk_rows = self._generate_chunk_data(chunk_size)
                self.buffer.extend(chunk_rows)
                self.total_generated += chunk_size

                self.logger.debug(
                    f"Chunk generated, buffer size: {len(self.buffer)}, "
                    f"total generated: {self.total_generated}"
                )

                # Write batch if buffer is full
                if len(self.buffer) >= self.batch_size:
                    self._write_and_clear_buffer()

            # Write any remaining rows in buffer
            if self.buffer:
                self.logger.info(f"Writing final batch with {len(self.buffer)} rows")
                self._write_and_clear_buffer()

            # Finalize and get summary
            summary = self.batch_writer.finalize()

            self.logger.info(
                f"Streaming batch processing completed: "
                f"generated {self.total_generated} rows in {self.batch_count} batches"
            )

            return {
                "status": "success",
                "total_rows_generated": self.total_generated,
                "total_batches": self.batch_count,
                "batch_size": self.batch_size,
                "chunk_size": self.chunk_size,
                "summary": summary,
            }

        except Exception as e:
            self.logger.error(f"Error during streaming batch processing: {e}")
            raise

    def get_strategy_states(self) -> Dict[str, Dict[str, Any]]:
        """Get current state of all strategies for debugging"""
        states = {}
        for col_name, strategy in self.strategies.items():
            if hasattr(strategy, "get_current_state"):
                states[col_name] = strategy.get_current_state()
            else:
                states[col_name] = {"type": type(strategy).__name__, "stateful": False}
        return states

    def reset_all_strategies(self) -> None:
        """Reset all strategies to their initial state"""
        self.logger.info("Resetting all strategy states")
        for col_name, strategy in self.strategies.items():
            if hasattr(strategy, "reset_state"):
                strategy.reset_state()
                self.logger.debug(f"Reset state for strategy in column '{col_name}'")

        # Reset processor state
        self.buffer.clear()
        self.total_generated = 0
        self.batch_count = 0
