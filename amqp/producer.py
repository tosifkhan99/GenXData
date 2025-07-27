import json
import threading
import time

from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container


class AMQPProducer(MessagingHandler):
    def __init__(self, url, queue):
        super().__init__()
        self.url = url
        self.queue = queue
        self.conn = None
        self.sender = None

        # Streaming mode only
        self.connected = False
        self.connection_ready = threading.Event()
        self.container = None
        self.container_thread = None

        self._start_connection()

    def _start_connection(self):
        """Start the AMQP connection in streaming mode"""
        self.container = Container(self)
        self.container_thread = threading.Thread(target=self.container.run, daemon=True)
        self.container_thread.start()

        # Wait for connection to be established
        if not self.connection_ready.wait(timeout=10):
            raise ConnectionError(
                f"Failed to connect to AMQP broker at {self.url} within 10 seconds"
            )

    def on_start(self, event):
        """Called when the container starts"""
        try:
            self.conn = event.container.connect(self.url)
            self.sender = event.container.create_sender(self.conn, self.queue)
            self.connected = True
            self.connection_ready.set()
        except Exception:
            self.connection_ready.set()  # Unblock waiting thread even on failure
            raise

    def on_sendable(self, event):
        """Called when the sender is ready to send messages"""
        # In streaming mode, messages are sent immediately via send_dataframe_immediate
        pass

    def send_dataframe(self, df, batch_info=None):
        """
        Send a DataFrame immediately to the queue

        Args:
            df (pd.DataFrame): DataFrame to send
            batch_info (dict): Optional metadata about the batch
        """
        if not self.connected or not self.sender:
            raise ConnectionError("AMQP connection not established")

        try:
            # Convert DataFrame to JSON
            data = {
                "batch_info": batch_info or {},
                "data": df.to_dict(orient="records"),
                "metadata": {
                    "rows": len(df),
                    "columns": list(df.columns),
                    "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                },
            }

            message_body = json.dumps(data, default=str)
            message = Message(body=message_body)

            # Send immediately
            self.sender.send(message)

        except Exception:
            raise

    def send_message(self, message_data):
        """
        Send a custom message to the queue

        Args:
            message_data (str or dict): Message data to send
        """
        if isinstance(message_data, dict):
            message_data = json.dumps(message_data, default=str)

        if not self.connected or not self.sender:
            raise ConnectionError("AMQP connection not established")
        message = Message(body=message_data)
        self.sender.send(message)

    def close_connection(self):
        """Close the connection and sender"""
        if self.sender:
            self.sender.close()
        if self.conn:
            self.conn.close()
        self.connected = False

    def run(self):
        """Start the container and process messages"""

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure connection is closed"""
        self.close_connection()
        if self.container_thread and self.container_thread.is_alive():
            # Give the container thread a moment to clean up
            time.sleep(0.1)


# Example usage (commented out to prevent auto-execution)
# if __name__ == '__main__':
#     # Streaming mode only
#     with AMQPProducer('localhost:5672', 'data-gen-queue') as producer:
#         producer.send_message("Hello from AMQP Producer!")
