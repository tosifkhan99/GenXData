# Queue Verification Tools

This directory contains tools to verify that your AMQP queue messaging is working correctly with Apache Artemis.

## 🛠️ Available Tools

### 1. Message Consumer (verify_queue_messages.py)
Connects to your queue and consumes existing messages to verify delivery.

### 2. Round-Trip Test (test_queue_roundtrip.py)
Sends a test message and then verifies it can be consumed - complete end-to-end test.

### 3. Artemis Console Checker (check_artemis_console.py)
Provides information about accessing the Apache Artemis web console and REST API.

## 🚀 Quick Start

1. Generate streaming data: python -m cli.main_cli generate examples/data_config_for_streaming.yaml --stream examples/amqp_stream_config.yaml
2. Verify messages: python tools/verify_queue_messages.py --max-messages 3 --detailed
3. Test pipeline: python tools/test_queue_roundtrip.py

Run any tool with --help for detailed usage information.
