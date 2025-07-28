#!/usr/bin/env python3
"""
Apache Artemis Console Checker

This script provides information about checking your Apache Artemis
message broker through the web console and REST API.
"""

import argparse
import sys
from pathlib import Path

try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.config_utils.config_loader import ConfigLoader


def check_artemis_rest_api(host, port, username, password, queue_name):
    """Check Artemis queue via REST API."""
    base_url = f"http://{host}:{port}/console/jolokia"

    try:
        # Get queue information
        queue_url = f'{base_url}/read/org.apache.activemq.artemis:broker="*",component=addresses,address="{queue_name}",subcomponent=queues,routing-type="anycast",queue="{queue_name}"'

        print("🌐 Checking Artemis REST API...")
        print(f"🔗 URL: {queue_url}")

        response = requests.get(queue_url, auth=(username, password), timeout=10)

        if response.status_code == 200:
            data = response.json()

            if data.get("status") == 200:
                queue_info = data.get("value", {})

                print("✅ Queue information retrieved successfully:")
                print(f"   • Queue name: {queue_info.get('Name', 'N/A')}")
                print(f"   • Message count: {queue_info.get('MessageCount', 'N/A')}")
                print(f"   • Messages added: {queue_info.get('MessagesAdded', 'N/A')}")
                print(
                    f"   • Messages acknowledged: {queue_info.get('MessagesAcknowledged', 'N/A')}"
                )
                print(f"   • Consumer count: {queue_info.get('ConsumerCount', 'N/A')}")
                print(f"   • Durable: {queue_info.get('Durable', 'N/A')}")
                print(f"   • Auto delete: {queue_info.get('AutoDelete', 'N/A')}")

                return True
            else:
                print(f"❌ API returned error status: {data.get('status')}")
                print(f"   Error: {data.get('error', 'Unknown error')}")

        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"   Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

    return False


def main():
    parser = argparse.ArgumentParser(
        description="Check Apache Artemis console and queue status",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This tool helps you verify your Apache Artemis broker status and queue information.

Examples:
  # Check with default config
  python tools/check_artemis_console.py

  # Check with custom config
  python tools/check_artemis_console.py --config examples/my_stream_config.yaml

  # Check specific host/port
  python tools/check_artemis_console.py --host localhost --port 8161
        """,
    )

    parser.add_argument(
        "--config",
        default="examples/amqp_stream_config.yaml",
        help="Path to streaming configuration file",
    )

    parser.add_argument(
        "--host", default="localhost", help="Artemis host (default: localhost)"
    )

    parser.add_argument(
        "--console-port",
        type=int,
        default=8161,
        help="Artemis console port (default: 8161)",
    )

    parser.add_argument(
        "--no-api-check",
        action="store_true",
        help="Skip REST API check, just show console info",
    )

    args = parser.parse_args()

    try:
        print("🖥️  Apache Artemis Console Checker")
        print("=" * 50)

        # Load configuration if available
        username = "artemis"
        password = "artemis"
        queue_name = "genxdata-queue"
        broker_host = args.host

        try:
            print(f"📋 Loading config from: {args.config}")
            config_data = ConfigLoader.load_config(args.config)

            if "amqp" in config_data:
                amqp_config = config_data["amqp"]
                username = amqp_config.get("username", username)
                password = amqp_config.get("password", password)
                queue_name = amqp_config.get("queue", queue_name)

                # Extract host from URL if provided
                url = amqp_config.get("url", f"{broker_host}:61616")
                if ":" in url:
                    broker_host = url.split(":")[0]

                print("✅ Configuration loaded")
            else:
                print("⚠️  No AMQP config found, using defaults")

        except Exception as e:
            print(f"⚠️  Could not load config: {e}")
            print("📋 Using default values")

        print("\n📊 Broker Information:")
        print(f"   • Host: {broker_host}")
        print("   • AMQP Port: 61616 (assumed)")
        print(f"   • Console Port: {args.console_port}")
        print(f"   • Username: {username}")
        print(f"   • Queue: {queue_name}")

        # Web Console Information
        print("\n🌐 Web Console Access:")
        console_url = f"http://{broker_host}:{args.console_port}/console"
        print(f"   • URL: {console_url}")
        print(f"   • Username: {username}")
        print(f"   • Password: {password}")

        print("\n📋 How to check your queue in the web console:")
        print(f"   1. Open: {console_url}")
        print(f"   2. Login with username '{username}' and password '{password}'")
        print(f"   3. Navigate to 'Artemis' → 'Addresses' → '{queue_name}'")
        print("   4. Check the 'Message Count' to see queued messages")
        print("   5. Click on the queue name to see message details")

        # REST API Check
        if not args.no_api_check:
            print("\n🔍 REST API Check:")
            if HAS_REQUESTS:
                success = check_artemis_rest_api(
                    broker_host, args.console_port, username, password, queue_name
                )

                if not success:
                    print("\n💡 If REST API check failed:")
                    print("   • Make sure Artemis is running")
                    print(f"   • Check if console port {args.console_port} is correct")
                    print(f"   • Verify username/password: {username}/{password}")
                    print(f"   • Try accessing web console manually: {console_url}")
            else:
                print("⚠️  'requests' library not available, skipping REST API check")
                print("   Install with: pip install requests")
                print(f"   Or use web console manually: {console_url}")

        print("\n🛠️  Alternative verification methods:")
        print("   • Use message verification tool:")
        print("     python tools/verify_queue_messages.py --max-messages 5")
        print("   • Use round-trip test:")
        print("     python tools/test_queue_roundtrip.py")
        print("   • Check Artemis logs for connection/message activity")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
