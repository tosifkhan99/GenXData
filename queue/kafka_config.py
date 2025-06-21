"""
Kafka-specific configuration implementation.
"""

from typing import Dict, Any, List
from .base import QueueConfig


class KafkaConfig(QueueConfig):
    """Configuration class for Kafka queue connections."""
    
    def validate_config(self) -> None:
        """Validate Kafka configuration parameters."""
        if 'bootstrap_servers' not in self.config:
            raise ValueError("Kafka config must contain 'bootstrap_servers' parameter")
        
        if 'topic' not in self.config:
            raise ValueError("Kafka config must contain 'topic' parameter")
        
        # Required parameters
        self.bootstrap_servers = self.config['bootstrap_servers']
        self.topic = self.config['topic']
        
        # Optional parameters with defaults
        self.client_id = self.config.get('client_id', 'genxdata-producer')
        self.acks = self.config.get('acks', 'all')
        self.retries = self.config.get('retries', 3)
        self.batch_size = self.config.get('batch_size', 16384)
        self.linger_ms = self.config.get('linger_ms', 0)
        self.buffer_memory = self.config.get('buffer_memory', 33554432)
        self.compression_type = self.config.get('compression_type', 'none')
        
        # Security settings
        self.security_protocol = self.config.get('security_protocol', 'PLAINTEXT')
        self.sasl_mechanism = self.config.get('sasl_mechanism')
        self.sasl_username = self.config.get('sasl_username')
        self.sasl_password = self.config.get('sasl_password')
        
        # SSL settings
        self.ssl_cafile = self.config.get('ssl_cafile')
        self.ssl_certfile = self.config.get('ssl_certfile')
        self.ssl_keyfile = self.config.get('ssl_keyfile')
        
        # Validate bootstrap_servers format
        if isinstance(self.bootstrap_servers, str):
            self.bootstrap_servers = [self.bootstrap_servers]
        elif not isinstance(self.bootstrap_servers, list):
            raise ValueError("bootstrap_servers must be a string or list of strings")
    
    @property
    def queue_type(self) -> str:
        """Return the queue type identifier."""
        return "kafka"
    
    def get_producer_config(self) -> Dict[str, Any]:
        """Get the producer configuration dictionary for kafka-python."""
        config = {
            'bootstrap_servers': self.bootstrap_servers,
            'client_id': self.client_id,
            'acks': self.acks,
            'retries': self.retries,
            'batch_size': self.batch_size,
            'linger_ms': self.linger_ms,
            'buffer_memory': self.buffer_memory,
            'compression_type': self.compression_type,
            'security_protocol': self.security_protocol,
        }
        
        # Add SASL settings if provided
        if self.sasl_mechanism:
            config['sasl_mechanism'] = self.sasl_mechanism
            if self.sasl_username:
                config['sasl_plain_username'] = self.sasl_username
            if self.sasl_password:
                config['sasl_plain_password'] = self.sasl_password
        
        # Add SSL settings if provided
        if self.ssl_cafile:
            config['ssl_cafile'] = self.ssl_cafile
        if self.ssl_certfile:
            config['ssl_certfile'] = self.ssl_certfile
        if self.ssl_keyfile:
            config['ssl_keyfile'] = self.ssl_keyfile
        
        return config 