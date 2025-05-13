#!/usr/bin/env python
"""
Test runner script for the data generator.

This script discovers and runs all tests in the 'tests' directory.
"""

import unittest
import sys
import os
import logging

# Disable logging during tests
logging.disable(logging.CRITICAL)

def run_tests():
    """Discover and run all tests"""
    # Ensure tests directory is in the path
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    if not os.path.exists(tests_dir):
        print(f"Test directory '{tests_dir}' not found")
        return False
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover(tests_dir)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 