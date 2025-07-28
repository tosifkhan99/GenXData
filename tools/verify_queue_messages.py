#!/usr/bin/env python3
"""
Queue Message Verification Tool

This script connects to your AMQP queue and consumes messages to verify
that your streaming is working correctly.
"""

import argparse
import json
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from messaging.amqp_config import AMQPConfig
from messaging.amqp_consumer import AMQPConsumer
from utils.config_utils.config_loader import load_config


def detailed_message_handler(message_data, raw_message):
    """Detailed message handler that shows comprehensive message info."""
    print("=" * 60)
    print("📨 MESSAGE RECEIVED")
    print("=" * 60)

    # Basic info
    print(f"📊 Message size: {len(str(message_data))} characters")
    print(f"🕐 Received at: {time.ctime()}")

    # Message structure
    print("\n📋 Message structure:")
    for key in message_data.keys():
        print(f"   • {key}")

    # Data content
    if "data" in message_data:
        data = message_data["data"]
        if isinstance(data, list):
            print("\n📊 Data content:")
            print(f"   • Row count: {len(data)}")
            if data:
                print(
                    f"   • Columns: {list(data[0].keys()) if isinstance(data[0], dict) else 'N/A'}"
                )
                print(f"   • First row preview: {str(data[0])[:100]}...")

    # Batch information
    if "batch_info" in message_data:
        batch_info = message_data["batch_info"]
        print("\n📦 Batch information:")
        for key, value in batch_info.items():
            print(f"   • {key}: {value}")

    # Metadata
    if "metadata" in message_data:
        metadata = message_data["metadata"]
        print("\n🏷️  Metadata:")
        for key, value in metadata.items():
            if isinstance(value, dict):
                print(f"   • {key}: {len(value)} items")
            else:
                print(f"   • {key}: {value}")

    # Timestamp info
    if "timestamp" in message_data:
        timestamp = message_data["timestamp"]
        print("\n⏰ Timestamp info:")
        print(f"   • Generated: {time.ctime(timestamp)}")
        print(f"   • Age: {time.time() - timestamp:.2f} seconds")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Verify messages in AMQP queue",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Consume up to 5 messages with 30 second timeout
  python tools/verify_queue_messages.py --max-messages 5 --timeout 30

  # Consume messages from custom config
  python tools/verify_queue_messages.py --config examples/my_stream_config.yaml

  # Show detailed message information
  python tools/verify_queue_messages.py --detailed --max-messages 1
        """,
    )

    parser.add_argument(
        "--config",
        default="examples/amqp_stream_config.yaml",
        help="Path to streaming configuration file (default: examples/amqp_stream_config.yaml)",
    )

    parser.add_argument(
        "--max-messages",
        type=int,
        help="Maximum number of messages to consume (default: unlimited)",
    )

    parser.add_argument(
        "--timeout", type=float, default=10.0, help="Timeout in seconds (default: 10.0)"
    )

    parser.add_argument(
        "--detailed", action="store_true", help="Show detailed message information"
    )

    parser.add_argument("--save-messages", help="Save received messages to JSON file")

    args = parser.parse_args()

    try:
        print("🔍 Queue Message Verification Tool")
        print("=" * 50)

        # Load configuration
        print(f"📋 Loading config from: {args.config}")
        config_data = load_config(args.config)

        if "amqp" not in config_data:
            print("❌ No AMQP configuration found in config file")
            return 1

        # Create AMQP config
        amqp_config = AMQPConfig(config_data["amqp"])

        print(f"🔗 Connecting to: {amqp_config.url}")
        print(f"📥 Queue: {amqp_config.queue}")
        print(f"👤 Username: {amqp_config.username}")

        # Create consumer
        message_handler = detailed_message_handler if args.detailed else None
        consumer = AMQPConsumer(amqp_config, message_handler)

        # Consume messages
        try:
            messages = consumer.consume_messages(
                max_messages=args.max_messages, timeout=args.timeout
            )

            # Show results
            print("\n" + "=" * 50)
            print("📊 VERIFICATION RESULTS")
            print("=" * 50)

            stats = consumer.get_stats()
            print(f"✅ Messages received: {stats['messages_received']}")
            print(f"⏱️  Time elapsed: {stats['elapsed_time']:.2f} seconds")
            print(f"📈 Rate: {stats['messages_per_second']:.2f} messages/second")

            if messages:
                print("\n🎉 SUCCESS: Messages are being delivered to the queue!")

                # Show summary of message types
                batch_counts = {}
                for msg in messages:
                    if "batch_info" in msg:
                        batch_idx = msg["batch_info"].get("batch_index", "unknown")
                        batch_counts[batch_idx] = batch_counts.get(batch_idx, 0) + 1

                if batch_counts:
                    print("\n📦 Batch summary:")
                    for batch_idx, count in sorted(batch_counts.items()):
                        print(f"   • Batch {batch_idx}: {count} messages")

                # Save messages if requested
                if args.save_messages:
                    with open(args.save_messages, "w") as f:
                        json.dump(messages, f, indent=2, default=str)
                    print(f"💾 Messages saved to: {args.save_messages}")

            else:
                print(f"\n⚠️  No messages received within {args.timeout} seconds")
                print("   This could mean:")
                print("   • No messages in the queue")
                print("   • Messages were already consumed")
                print("   • Queue connection issues")
                print("   • Different queue name/configuration")

        finally:
            consumer.disconnect()

        return 0

    except FileNotFoundError:
        print(f"❌ Config file not found: {args.config}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
