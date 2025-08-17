#!/usr/bin/env python3
"""
Test runner script for Claude CLI Multi-Agent A2A System
"""
import subprocess
import sys
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False, parallel=False):
    """Run tests with specified options"""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Test selection
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "a2a":
        cmd.extend(["-m", "a2a"])
    elif test_type == "agents":
        cmd.append("tests/test_agents.py")
    elif test_type == "task_manager":
        cmd.append("tests/test_task_manager.py")
    elif test_type == "protocol":
        cmd.append("tests/test_a2a_protocol.py")
    elif test_type == "all":
        cmd.append("tests/")
    
    # Output options
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Coverage options
    if coverage:
        cmd.extend([
            "--cov=agents",
            "--cov=shared",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing"
        ])
    
    # Parallel execution
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # Run tests
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def install_test_dependencies():
    """Install test dependencies"""
    cmd = ["pip", "install", "-r", "tests/requirements.txt"]
    print(f"Installing test dependencies: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Test runner for Claude CLI Multi-Agent A2A System")
    
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "a2a", "agents", "task_manager", "protocol"],
        default="all",
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install test dependencies first"
    )
    
    args = parser.parse_args()
    
    # Install dependencies if requested
    if args.install_deps:
        exit_code = install_test_dependencies()
        if exit_code != 0:
            print("Failed to install test dependencies")
            return exit_code
    
    # Run tests
    exit_code = run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=args.coverage,
        parallel=args.parallel
    )
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())