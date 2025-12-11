#!/usr/bin/env python3
"""
Script for building and publishing secular-equilibrium package to PyPI/TestPyPI.
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path


def run_command(cmd, check=True):
    """Run a shell command and return output."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(result.returncode)
    return result


def clean_build():
    """Clean build artifacts."""
    print("\n=== Cleaning build artifacts ===")
    run_command("rm -rf build/ dist/ *.egg-info", check=False)


def run_tests():
    """Run package tests."""
    print("\n=== Running tests ===")
    run_command("python -m pytest tests/ -v")


def build_package():
    """Build source and wheel distributions."""
    print("\n=== Building package ===")
    run_command("python -m build")


def upload_to_testpypi():
    """Upload package to TestPyPI."""
    print("\n=== Uploading to TestPyPI ===")
    run_command("python -m twine upload --repository testpypi dist/*")


def upload_to_pypi():
    """Upload package to PyPI."""
    print("\n=== Uploading to PyPI ===")
    run_command("python -m twine upload dist/*")


def check_environment():
    """Check if required tools are installed."""
    print("\n=== Checking environment ===")
    tools = ['python', 'pip', 'twine']
    for tool in tools:
        result = run_command(f"which {tool}", check=False)
        if result.returncode != 0:
            print(f"Error: {tool} not found in PATH")
            sys.exit(1)

    # Check build tool
    try:
        import build
    except ImportError:
        print("Error: 'build' package not installed. Install with: pip install build")
        sys.exit(1)


def install_dependencies():
    """Install required dependencies."""
    print("\n=== Installing dependencies ===")
    run_command("pip install -r requirements.txt")
    run_command("pip install build twine pytest")


def main():
    parser = argparse.ArgumentParser(description="Build and publish secular-equilibrium package")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")
    parser.add_argument("--test", action="store_true", help="Run tests only")
    parser.add_argument("--build", action="store_true", help="Build package only")
    parser.add_argument("--testpypi", action="store_true", help="Upload to TestPyPI")
    parser.add_argument("--pypi", action="store_true", help="Upload to PyPI")
    parser.add_argument("--all", action="store_true", help="Clean, test, build, and upload to TestPyPI")
    parser.add_argument("--release", action="store_true", help="Clean, test, build, and upload to PyPI (full release)")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # Check environment first
    check_environment()

    # Clean
    if args.clean or args.all or args.release:
        clean_build()

    # Install dependencies if needed
    if args.all or args.release:
        install_dependencies()

    # Run tests
    if args.test or args.all or args.release:
        run_tests()

    # Build
    if args.build or args.all or args.release:
        build_package()

    # Upload to TestPyPI
    if args.testpypi or args.all:
        upload_to_testpypi()

    # Upload to PyPI
    if args.pypi or args.release:
        upload_to_pypi()

    print("\n=== Done ===")


if __name__ == "__main__":
    main()