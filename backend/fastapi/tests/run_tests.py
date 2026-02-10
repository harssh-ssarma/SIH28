"""
Test Runner Script
Quick way to run all tests with coverage
"""
import pytest
import sys

def run_tests():
    """Run all tests with coverage report"""
    args = [
        'tests/',                    # Test directory
        '-v',                        # Verbose
        '--tb=short',                # Short traceback
        '--color=yes',               # Colored output
        '--cov=.',                   # Coverage for all modules
        '--cov-report=term-missing', # Show missing lines
        '--cov-report=html',         # Generate HTML report
    ]
    
    return pytest.main(args)

if __name__ == '__main__':
    sys.exit(run_tests())
