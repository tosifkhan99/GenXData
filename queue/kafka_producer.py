"""
Kafka producer implementation.
"""

import json
import logging
from typing import Dict, Any, Optional

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
        self.logger = logging.getLogger("genxdata.kafka_producer")
    
    def connect(self) -> None:
        """Establish connection to Kafka cluster."""
        if self._connected:
            return
        
        try:
            # Import kafka-python here to make it optional
            from kafka import KafkaProducer as KafkaClient
            
            producer_config = self.config.get_producer_config()
            
            # Add value serializer for JSON
            producer_config['value_serializer'] = lambda v: json.dumps(v, default=str).encode('utf-8')
            
            self.producer = KafkaClient(**producer_config)
            self._connected = True
            
            self.logger.info(f"Connected to Kafka cluster: {self.config.bootstrap_servers}, topic: {self.config.topic}")
            
        except ImportError as e:
            raise ImportError(f"Kafka library not available. Install kafka-python: {e}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Kafka: {e}")
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
            self.logger.info("Disconnected from Kafka cluster")
            
        except Exception as e:
            self.logger.error(f"Error during Kafka disconnect: {e}")
    
    def send_dataframe(self, df: pd.DataFrame, batch_info: Optional[Dict[str, Any]] = None) -> None:
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
                'batch_info': batch_info or {},
                'data': df.to_dict(orient='records'),
                'metadata': {
                    'rows': len(df),
                    'columns': list(df.columns),
                    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
                }
            }
            
            # Send message to Kafka topic
            future = self.producer.send(self.config.topic, value=message_data)
            
            # Optional: wait for confirmation (can be made configurable)
            record_metadata = future.get(timeout=10)
            
            self.logger.info(f"Sent DataFrame message with {len(df)} rows to topic {self.config.topic} "
                           f"(partition: {record_metadata.partition}, offset: {record_metadata.offset})")
            
        except Exception as e:
            self.logger.error(f"Error sending DataFrame message to Kafka: {str(e)}")
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
            future = self.producer.send(self.config.topic, value=message_data)
            
            # Optional: wait for confirmation
            record_metadata = future.get(timeout=10)
            
            self.logger.info(f"Sent custom message to topic {self.config.topic} "
                           f"(partition: {record_metadata.partition}, offset: {record_metadata.offset})")
            
        except Exception as e:
            self.logger.error(f"Error sending custom message to Kafka: {str(e)}")
            raise
    
    def flush(self, timeout: int = 10) -> None:
        """
        Flush any pending messages.
        
        Args:
            timeout: Timeout in seconds
        """
        if self.producer:
            self.producer.flush(timeout=timeout) 