"""
Test runner script to execute all endpoint tests
Usage: python -m pytest backend/tests/run_all_endpoint_tests.py -v
Or: pytest backend/tests/api/ -v -m api
"""

import pytest
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


def main():
    """Run all endpoint tests"""
    # Test files to run
    test_files = [
        "backend/tests/api/test_all_endpoints_comprehensive.py",
        "backend/tests/api/test_additional_endpoints.py",
        "backend/tests/api/test_auth_api.py",
        "backend/tests/api/test_chat_api.py",
        "backend/tests/api/test_attractions_api.py",
    ]
    
    # Run pytest
    pytest_args = [
        "-v",  # Verbose
        "--tb=short",  # Short traceback format
        "-m", "api",  # Only run tests marked with 'api'
        "--asyncio-mode=auto",  # Auto async mode
    ]
    
    # Add test files
    pytest_args.extend(test_files)
    
    # Run tests
    exit_code = pytest.main(pytest_args)
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)





