#!/usr/bin/env python3
"""
Queue Round-Trip Test Tool

This script sends a test message to your AMQP queue and then consumes it
to verify that the complete messaging pipeline is working.
"""

import argparse
import sys
import time
import uuid
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from messaging.amqp_consumer import AMQPConsumer
from messaging.factory import QueueFactory
from utils.config_utils.config_loader import ConfigLoader


def create_test_message():
    """Create a test message with identifiable content."""
    test_id = str(uuid.uuid4())[:8]
    timestamp = time.time()

    return {
        "test_id": test_id,
        "test_type": "roundtrip_verification",
        "timestamp": timestamp,
        "message": f"Test message generated at {time.ctime(timestamp)}",
        "data": [
            {"id": 1, "name": "Test User 1", "value": 42.5},
            {"id": 2, "name": "Test User 2", "value": 87.3},
            {"id": 3, "name": "Test User 3", "value": 19.8},
        ],
        "metadata": {
            "source": "queue_roundtrip_test",
            "version": "1.0",
            "row_count": 3,
        },
    }


def test_message_handler(expected_test_id):
    """Create a message handler that looks for our test message."""

    def handler(message_data, raw_message):
        print("📨 Received message:")

        # Check if this is our test message
        if message_data.get("test_id") == expected_test_id:
            print(f"✅ Found our test message! ID: {expected_test_id}")
            print(f"📊 Message size: {len(str(message_data))} characters")
            print(
                f"⏰ Roundtrip time: {time.time() - message_data['timestamp']:.3f} seconds"
            )

            # Verify message content
            if "data" in message_data:
                print(f"📋 Data rows: {len(message_data['data'])}")
            if "metadata" in message_data:
                print(f"🏷️  Metadata items: {len(message_data['metadata'])}")

            return True  # Signal that we found our message
        else:
            test_id = message_data.get("test_id", "unknown")
            print(f"📨 Different message (ID: {test_id})")

        return False

    return handler


def main():
    parser = argparse.ArgumentParser(
        description="Test AMQP queue round-trip messaging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This tool performs a complete round-trip test:
1. Connects to the queue as a producer
2. Sends a test message with unique ID
3. Connects as a consumer
4. Verifies the test message is received

Examples:
  # Basic round-trip test
  python tools/test_queue_roundtrip.py

  # Test with custom config
  python tools/test_queue_roundtrip.py --config examples/my_stream_config.yaml

  # Test with longer timeout
  python tools/test_queue_roundtrip.py --timeout 30
        """,
    )

    parser.add_argument(
        "--config",
        default="examples/amqp_stream_config.yaml",
        help="Path to streaming configuration file (default: examples/amqp_stream_config.yaml)",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="Timeout in seconds to wait for message (default: 15.0)",
    )

    args = parser.parse_args()

    try:
        print("🔄 Queue Round-Trip Test")
        print("=" * 50)

        # Load configuration
        print(f"📋 Loading config from: {args.config}")
        config_data = ConfigLoader.load_config(args.config)

        # Create test message
        test_message = create_test_message()
        test_id = test_message["test_id"]

        print(f"🆔 Test message ID: {test_id}")
        print(f"📊 Message size: {len(str(test_message))} characters")

        # Step 1: Send test message
        print("\n" + "=" * 30)
        print("📤 STEP 1: SENDING MESSAGE")
        print("=" * 30)

        config, producer = QueueFactory.create_from_stream_config(config_data)

        try:
            producer.connect()
            print("✅ Connected to queue as producer")

            producer.send_message(test_message)
            print("✅ Test message sent successfully")

        finally:
            producer.disconnect()
            print("🔌 Producer disconnected")

        # Wait a moment for message to be queued
        print("\n⏳ Waiting 2 seconds for message to be queued...")
        time.sleep(2)

        # Step 2: Consume and verify message
        print("\n" + "=" * 30)
        print("📥 STEP 2: CONSUMING MESSAGE")
        print("=" * 30)

        amqp_config = config
        found_message = False

        # Create custom handler that looks for our test message
        def custom_handler(message_data, raw_message):
            nonlocal found_message
            if message_data.get("test_id") == test_id:
                print(f"✅ Found our test message! ID: {test_id}")
                print(f"📊 Message size: {len(str(message_data))} characters")
                print(
                    f"⏰ Roundtrip time: {time.time() - message_data['timestamp']:.3f} seconds"
                )

                # Verify message content
                if "data" in message_data:
                    print(f"📋 Data rows: {len(message_data['data'])}")
                if "metadata" in message_data:
                    print(f"🏷️  Metadata items: {len(message_data['metadata'])}")

                found_message = True
            else:
                msg_id = message_data.get("test_id", "no-id")
                print(f"📨 Different message (ID: {msg_id})")

        consumer = AMQPConsumer(amqp_config, custom_handler)

        try:
            print("🔗 Connecting as consumer...")
            consumer.connect()
            print("✅ Connected to queue as consumer")

            # Consume messages with timeout
            print(f"📥 Consuming messages (timeout: {args.timeout}s)...")
            start_time = time.time()

            while consumer.running and not found_message:
                if time.time() - start_time > args.timeout:
                    print(f"⏰ Timeout reached after {args.timeout} seconds")
                    break
                time.sleep(0.1)

        finally:
            consumer.disconnect()

        # Results
        print("\n" + "=" * 50)
        print("🎯 ROUND-TRIP TEST RESULTS")
        print("=" * 50)

        stats = consumer.get_stats()
        print(f"📊 Messages received: {stats['messages_received']}")
        print(f"⏱️  Time elapsed: {stats['elapsed_time']:.2f} seconds")

        if found_message:
            print("\n🎉 SUCCESS: Round-trip test completed!")
            print("✅ Message was successfully sent and received")
            print("✅ Queue messaging pipeline is working correctly")
            return 0
        else:
            print("\n❌ FAILURE: Test message not found")
            print("⚠️  Possible issues:")
            print("   • Message not delivered to queue")
            print("   • Queue connection problems")
            print("   • Message consumed by another consumer")
            print("   • Timeout too short")
            return 1

    except FileNotFoundError:
        print(f"❌ Config file not found: {args.config}")
        return 1
    except Exception as e:
        print(f"❌ Error during round-trip test: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
