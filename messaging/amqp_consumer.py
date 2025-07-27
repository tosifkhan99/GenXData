"""
AMQP consumer implementation for reading messages from the queue.
"""

import json
import threading
import time
from typing import Dict, Any, List, Optional, Callable

from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container

from .amqp_config import AMQPConfig


class AMQPConsumer(MessagingHandler):
    """AMQP queue consumer implementation."""

    def __init__(self, config: AMQPConfig, message_handler: Optional[Callable] = None):
        """
        Initialize AMQP consumer.

        Args:
            config: AMQP configuration instance
            message_handler: Optional callback function to handle received messages
        """
        super().__init__()
        self.config = config
        self.message_handler = message_handler or self._default_message_handler

        self.conn = None
        self.receiver = None
        self.messages = []
        self.running = False

        # Threading for container
        self.connection_ready = threading.Event()
        self.container = None
        self.container_thread = None

        # Statistics
        self.messages_received = 0
        self.start_time = None

    def connect(self) -> None:
        """Establish connection to AMQP broker."""
        if self.running:
            return

        try:
            print(f"🔗 Connecting to AMQP broker at {self.config.url}")
            print(f"🔗 Queue: {self.config.queue}")
            print(f"🔗 Username: {self.config.username}")

            self.container = Container(self)
            self.container_thread = threading.Thread(
                target=self.container.run, daemon=True
            )
            self.container_thread.start()

            # Wait for connection to be established
            if not self.connection_ready.wait(timeout=10):
                raise Exception("Failed to establish connection within timeout")

            self.running = True
            self.start_time = time.time()
            print("✅ Successfully connected to AMQP broker")

        except Exception as e:
            print(f"❌ Failed to connect to AMQP broker: {e}")
            raise

    def disconnect(self) -> None:
        """Close connection to AMQP broker."""
        if not self.running:
            return

        print("🔌 Disconnecting from AMQP broker")
        self.running = False

        if self.conn:
            self.conn.close()

        if self.container_thread and self.container_thread.is_alive():
            self.container_thread.join(timeout=5)

        print("✅ Successfully disconnected from AMQP broker")

    def consume_messages(
        self, max_messages: Optional[int] = None, timeout: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Consume messages from the queue.

        Args:
            max_messages: Maximum number of messages to consume (None for unlimited)
            timeout: Timeout in seconds (None for no timeout)

        Returns:
            List of received messages
        """
        if not self.running:
            self.connect()

        print("📥 Starting to consume messages...")
        if max_messages:
            print(f"📥 Will consume up to {max_messages} messages")
        if timeout:
            print(f"📥 Timeout: {timeout} seconds")

        start_time = time.time()

        while self.running:
            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                print(f"⏰ Timeout reached after {timeout} seconds")
                break

            # Check max messages
            if max_messages and self.messages_received >= max_messages:
                print(f"✅ Received {max_messages} messages, stopping")
                break

            time.sleep(0.1)  # Small sleep to prevent busy waiting

        return self.messages.copy()

    def _default_message_handler(
        self, message_data: Dict[str, Any], raw_message: Message
    ) -> None:
        """Default message handler that just prints and stores messages."""
        print(f"📨 Received message #{self.messages_received + 1}")
        print(f"   Size: {len(str(message_data))} characters")

        # Show preview of data
        if "data" in message_data and isinstance(message_data["data"], list):
            row_count = len(message_data["data"])
            print(f"   Data rows: {row_count}")

        if "batch_info" in message_data:
            batch_info = message_data["batch_info"]
            print(
                f"   Batch: {batch_info.get('batch_index', '?')} of {batch_info.get('total_batches', '?')}"
            )

        if "timestamp" in message_data:
            timestamp = message_data["timestamp"]
            print(f"   Timestamp: {time.ctime(timestamp)}")

    # Proton event handlers
    def on_start(self, event):
        """Called when the container starts."""
        url = f"amqp://{self.config.username}:{self.config.password}@{self.config.url}"
        self.conn = event.container.connect(url)

    def on_connection_opened(self, event):
        """Called when connection is established."""
        print("🔗 Connection established")
        self.receiver = event.container.create_receiver(self.conn, self.config.queue)

    def on_link_opened(self, event):
        """Called when receiver link is established."""
        print(f"📥 Receiver link established for queue: {self.config.queue}")
        self.connection_ready.set()

    def on_message(self, event):
        """Called when a message is received."""
        try:
            message = event.message

            # Parse message body
            if hasattr(message.body, "decode"):
                body_str = message.body.decode("utf-8")
            else:
                body_str = str(message.body)

            message_data = json.loads(body_str)

            # Store message
            self.messages.append(message_data)
            self.messages_received += 1

            # Call message handler
            self.message_handler(message_data, message)

        except Exception as e:
            print(f"❌ Error processing message: {e}")

    def on_connection_error(self, event):
        """Called when connection error occurs."""
        print(f"❌ Connection error: {event.connection.remote_condition}")
        self.running = False

    def on_link_error(self, event):
        """Called when link error occurs."""
        print(f"❌ Link error: {event.link.remote_condition}")

    def get_stats(self) -> Dict[str, Any]:
        """Get consumer statistics."""
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        return {
            "messages_received": self.messages_received,
            "elapsed_time": elapsed_time,
            "messages_per_second": (
                self.messages_received / elapsed_time if elapsed_time > 0 else 0
            ),
            "running": self.running,
        }
