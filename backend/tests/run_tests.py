"""
Test runner script for Sri Lanka Tourism Chatbot
"""

import sys
import subprocess
from pathlib import Path


def run_all_tests():
    """Run all tests with coverage"""
    print("=" * 70)
    print("Running Sri Lanka Tourism Chatbot Test Suite")
    print("=" * 70)
    
    # Run pytest with coverage
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "backend/tests/",
            "-v",
            "--cov=backend/app",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-report=xml",
        ],
        cwd=Path(__file__).parent.parent
    )
    
    return result.returncode


def run_unit_tests():
    """Run only unit tests"""
    print("Running unit tests...")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "backend/tests/unit/",
            "-v",
            "-m",
            "unit"
        ],
        cwd=Path(__file__).parent.parent
    )
    return result.returncode


def run_api_tests():
    """Run only API tests"""
    print("Running API tests...")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "backend/tests/api/",
            "-v",
            "-m",
            "api"
        ],
        cwd=Path(__file__).parent.parent
    )
    return result.returncode


def run_integration_tests():
    """Run only integration tests"""
    print("Running integration tests...")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "backend/tests/integration/",
            "-v",
            "-m",
            "integration"
        ],
        cwd=Path(__file__).parent.parent
    )
    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type == "unit":
            sys.exit(run_unit_tests())
        elif test_type == "api":
            sys.exit(run_api_tests())
        elif test_type == "integration":
            sys.exit(run_integration_tests())
        else:
            print(f"Unknown test type: {test_type}")
            print("Usage: python run_tests.py [unit|api|integration]")
            sys.exit(1)
    else:
        sys.exit(run_all_tests())
