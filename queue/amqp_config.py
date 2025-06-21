"""
AMQP-specific configuration implementation.
"""

from typing import Dict, Any
from .base import QueueConfig


class AMQPConfig(QueueConfig):
    """Configuration class for AMQP queue connections."""
    
    def validate_config(self) -> None:
        """Validate AMQP configuration parameters."""
        if 'url' not in self.config:
            raise ValueError("AMQP config must contain 'url' parameter")
        
        if 'queue' not in self.config:
            raise ValueError("AMQP config must contain 'queue' parameter")
        
        # Optional parameters with defaults
        self.url = self.config['url']
        self.queue = self.config['queue']
        self.username = self.config.get('username')
        self.password = self.config.get('password')
        self.virtual_host = self.config.get('virtual_host', '/')
        self.heartbeat = self.config.get('heartbeat', 60)
        self.queue_durable = self.config.get('queue_durable', True)
        self.queue_auto_delete = self.config.get('queue_auto_delete', False)
    
    @property
    def queue_type(self) -> str:
        """Return the queue type identifier."""
        return "amqp"
    
    def get_connection_url(self) -> str:
        """Build the complete connection URL."""
        if self.username and self.password:
            # If credentials are provided, include them in URL
            if '://' in self.url:
                protocol, rest = self.url.split('://', 1)
                return f"{protocol}://{self.username}:{self.password}@{rest}"
            else:
                return f"amqp://{self.username}:{self.password}@{self.url}"
        return self.url 