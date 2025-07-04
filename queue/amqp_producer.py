"""
AMQP producer implementation.
"""

import json
import logging
import threading
import time
from typing import Dict, Any, Optional

import pandas as pd
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container

from .base import QueueProducer
from .amqp_config import AMQPConfig


class AMQPProducer(QueueProducer, MessagingHandler):
    """AMQP queue producer implementation."""
    
    def __init__(self, config: AMQPConfig):
        """
        Initialize AMQP producer.
        
        Args:
            config: AMQP configuration instance
        """
        QueueProducer.__init__(self, config)
        MessagingHandler.__init__(self)
        
        self.conn = None
        self.sender = None
        self.logger = logging.getLogger("genxdata.amqp_producer")
        
        # Threading for container
        self.connection_ready = threading.Event()
        self.container = None
        self.container_thread = None
    
    def connect(self) -> None:
        """Establish connection to AMQP broker."""
        if self._connected:
            return
        
        try:
            self.container = Container(self)
            self.container_thread = threading.Thread(target=self.container.run, daemon=True)
            self.container_thread.start()
            
            # Wait for connection to be established
            if not self.connection_ready.wait(timeout=10):
                raise ConnectionError(f"Failed to connect to AMQP broker at {self.config.url} within 10 seconds")
            
            if not self._connected:
                raise ConnectionError("Failed to establish AMQP connection")
            
            self.logger.info(f"Connected to AMQP broker at {self.config.url}, queue: {self.config.queue}")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to AMQP broker: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close connection to AMQP broker."""
        if not self._connected:
            return
        
        try:
            if self.sender:
                self.sender.close()
            if self.conn:
                self.conn.close()
            
            self._connected = False
            self.logger.info("Disconnected from AMQP broker")
            
            # Give the container thread a moment to clean up
            if self.container_thread and self.container_thread.is_alive():
                time.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"Error during AMQP disconnect: {e}")
    
    def send_dataframe(self, df: pd.DataFrame, batch_info: Optional[Dict[str, Any]] = None) -> None:
        """
        Send a DataFrame to the AMQP queue.
        
        Args:
            df: DataFrame to send
            batch_info: Optional metadata about the batch
        """
        if not self._connected or not self.sender:
            raise ConnectionError("AMQP connection not established")
        
        try:
            # Convert DataFrame to JSON message format
            data = {
                'batch_info': batch_info or {},
                'data': df.to_dict(orient='records'),
                'metadata': {
                    'rows': len(df),
                    'columns': list(df.columns),
                    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
                }
            }
            
            message_body = json.dumps(data, default=str)
            message = Message(body=message_body)
            
            # Send message
            self.sender.send(message)
            self.logger.info(f"Sent DataFrame message with {len(df)} rows to queue {self.config.queue}")
            
        except Exception as e:
            self.logger.error(f"Error sending DataFrame message: {str(e)}")
            raise
    
    def send_message(self, message_data: Any) -> None:
        """
        Send a custom message to the AMQP queue.
        
        Args:
            message_data: Message data to send
        """
        if not self._connected or not self.sender:
            raise ConnectionError("AMQP connection not established")
        
        try:
            if isinstance(message_data, dict):
                message_body = json.dumps(message_data, default=str)
            else:
                message_body = str(message_data)
            
            message = Message(body=message_body)
            self.sender.send(message)
            self.logger.info(f"Sent custom message to queue {self.config.queue}")
            
        except Exception as e:
            self.logger.error(f"Error sending custom message: {str(e)}")
            raise
    
    # Proton MessagingHandler methods
    def on_start(self, event):
        """Called when the container starts."""
        try:
            connection_url = self.config.get_connection_url()
            self.conn = event.container.connect(connection_url)
            self.sender = event.container.create_sender(self.conn, self.config.queue)
            self._connected = True
            self.connection_ready.set()
            
        except Exception as e:
            self.logger.error(f"Failed to start AMQP connection: {e}")
            self.connection_ready.set()  # Unblock waiting thread even on failure
            raise
    
    def on_sendable(self, event):
        """Called when the sender is ready to send messages."""
        # Messages are sent immediately via send_dataframe/send_message
        pass
    
    def on_connection_error(self, event):
        """Handle connection errors."""
        self.logger.error(f"AMQP connection error: {event.connection.condition}")
        self._connected = False
        self.connection_ready.set()
    
    def on_link_error(self, event):
        """Handle link errors."""
        self.logger.error(f"AMQP link error: {event.link.condition}") 