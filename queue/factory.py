"""
Factory for creating queue producers based on configuration.
"""

from typing import Dict, Any

from .base import QueueProducer, QueueConfig
from .amqp_config import AMQPConfig
from .amqp_producer import AMQPProducer
from .kafka_config import KafkaConfig
from .kafka_producer import KafkaProducer


class QueueFactory:
    """Factory class for creating queue producers and configurations."""
    
    # Registry of available queue types
    _config_registry = {
        'amqp': AMQPConfig,
        'kafka': KafkaConfig,
    }
    
    _producer_registry = {
        'amqp': AMQPProducer,
        'kafka': KafkaProducer,
    }
    
    @classmethod
    def create_config(cls, queue_type: str, config_data: Dict[str, Any]) -> QueueConfig:
        """
        Create a queue configuration instance.
        
        Args:
            queue_type: Type of queue ('amqp', 'kafka', etc.)
            config_data: Configuration data dictionary
        
        Returns:
            QueueConfig instance
        
        Raises:
            ValueError: If queue type is not supported
        """
        if queue_type not in cls._config_registry:
            available_types = ', '.join(cls._config_registry.keys())
            raise ValueError(f"Unsupported queue type '{queue_type}'. Available types: {available_types}")
        
        config_class = cls._config_registry[queue_type]
        return config_class(config_data)
    
    @classmethod
    def create_producer(cls, config: QueueConfig) -> QueueProducer:
        """
        Create a queue producer instance.
        
        Args:
            config: Queue configuration instance
        
        Returns:
            QueueProducer instance
        
        Raises:
            ValueError: If queue type is not supported
        """
        queue_type = config.queue_type
        
        if queue_type not in cls._producer_registry:
            available_types = ', '.join(cls._producer_registry.keys())
            raise ValueError(f"Unsupported queue type '{queue_type}'. Available types: {available_types}")
        
        producer_class = cls._producer_registry[queue_type]
        return producer_class(config)
    
    @classmethod
    def create_from_config(cls, stream_config: Dict[str, Any]) -> QueueProducer:
        """
        Create a queue producer directly from a streaming configuration.
        
        Args:
            stream_config: Streaming configuration dictionary
        
        Returns:
            QueueProducer instance
        
        Raises:
            ValueError: If configuration is invalid or queue type not supported
        """
        # Determine queue type from config keys
        queue_type = None
        queue_config_data = None
        
        if 'amqp' in stream_config:
            queue_type = 'amqp'
            queue_config_data = stream_config['amqp']
        elif 'kafka' in stream_config:
            queue_type = 'kafka'
            queue_config_data = stream_config['kafka']
        else:
            available_types = ', '.join(cls._config_registry.keys())
            raise ValueError(f"No supported queue configuration found in stream config. "
                           f"Expected one of: {available_types}")
        
        # Create config and producer
        config = cls.create_config(queue_type, queue_config_data)
        return cls.create_producer(config)
    
    @classmethod
    def register_queue_type(cls, queue_type: str, config_class: type, producer_class: type) -> None:
        """
        Register a new queue type.
        
        Args:
            queue_type: Name of the queue type
            config_class: Configuration class (must inherit from QueueConfig)
            producer_class: Producer class (must inherit from QueueProducer)
        
        Raises:
            TypeError: If classes don't inherit from the correct base classes
        """
        if not issubclass(config_class, QueueConfig):
            raise TypeError(f"Config class must inherit from QueueConfig")
        
        if not issubclass(producer_class, QueueProducer):
            raise TypeError(f"Producer class must inherit from QueueProducer")
        
        cls._config_registry[queue_type] = config_class
        cls._producer_registry[queue_type] = producer_class
    
    @classmethod
    def get_supported_queue_types(cls) -> list:
        """Get list of supported queue types."""
        return list(cls._config_registry.keys()) 