"""
GenXData - Synthetic Data Generation Tool
Main entry point for the application.

This application has been refactored into a modular structure:
- core/orchestrator.py - Main processing orchestration
- core/processing/ - Core data processing
- core/streaming/ - Streaming and batch processing
- core/batch_processing/ - Batch utilities
- utils/config_utils/ - Configuration loading
- utils/file_utils/ - File operations
- utils/ - Various utility modules
- cli/ - Command-line interface

For programmatic use, import the 'start' function:
    from main import start

For CLI use, run this file directly:
    python main.py <config_path> [options]
"""

from cli.main_cli import main

if __name__ == "__main__":
    main()
