"""
Kafka producer implementation.
"""

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd

from .base import QueueProducer
from .kafka_config import KafkaConfig


class KafkaProducer(QueueProducer):
    """Kafka queue producer implementation."""

    def __init__(self, config: KafkaConfig):
        """
        Initialize Kafka producer.

        Args:
            config: Kafka configuration instance
        """
        super().__init__(config)
        self.producer = None

    def connect(self) -> None:
        """Establish connection to Kafka cluster."""
        if self._connected:
            return

        try:
            # Import kafka-python here to make it optional
            from kafka import KafkaProducer as KafkaClient

            producer_config = self.config.get_producer_config()

            # Add value serializer for JSON
            producer_config["value_serializer"] = lambda v: json.dumps(
                v, default=str
            ).encode("utf-8")

            self.producer = KafkaClient(**producer_config)
            self._connected = True

        except ImportError as e:
            raise ImportError(
                f"Kafka library not available. Install kafka-python: {e}"
            ) from e
        except Exception:
            raise

    def disconnect(self) -> None:
        """Close connection to Kafka cluster."""
        if not self._connected or not self.producer:
            return

        try:
            # Flush any pending messages
            self.producer.flush(timeout=10)
            self.producer.close(timeout=10)

            self._connected = False

        except Exception:
            pass

    def send_dataframe(
        self, df: "pd.DataFrame", batch_info: dict[str, Any] | None = None
    ) -> None:
        """
        Send a DataFrame to the Kafka topic.

        Args:
            df: DataFrame to send
            batch_info: Optional metadata about the batch
        """
        if not self._connected or not self.producer:
            raise ConnectionError("Kafka connection not established")

        try:
            # Convert DataFrame to message format
            message_data = {
                "batch_info": batch_info or {},
                "data": df.to_dict(orient="records"),
                "metadata": {
                    "rows": len(df),
                    "columns": list(df.columns),
                    "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                },
            }

            # Send message to Kafka topic
            self.producer.send(self.config.topic, value=message_data)

        except Exception:
            raise

    def send_message(self, message_data: Any) -> None:
        """
        Send a custom message to the Kafka topic.

        Args:
            message_data: Message data to send
        """
        if not self._connected or not self.producer:
            raise ConnectionError("Kafka connection not established")

        try:
            # Send message to Kafka topic
            self.producer.send(self.config.topic, value=message_data)

        except Exception:
            raise

    def flush(self, timeout: int = 10) -> None:
        """
        Flush any pending messages.

        Args:
            timeout: Timeout in seconds
        """
        if self.producer:
            self.producer.flush(timeout=timeout)
