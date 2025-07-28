"""
Queue management package for GenXData streaming functionality.

This package provides abstract queue interfaces and concrete implementations
for different message queue systems like AMQP and Kafka.
"""

from .base import QueueConfig, QueueProducer
from .factory import QueueFactory

__all__ = ["QueueProducer", "QueueConfig", "QueueFactory"]
