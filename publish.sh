#!/bin/bash
# Script for building and publishing secular-equilibrium package

set -e  # Exit on error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_red() { echo -e "${RED}$1${NC}"; }
echo_green() { echo -e "${GREEN}$1${NC}"; }
echo_yellow() { echo -e "${YELLOW}$1${NC}"; }

show_help() {
    echo "Usage: $0 [option]"
    echo
    echo "Options:"
    echo "  clean     - Clean build artifacts"
    echo "  test      - Run tests only"
    echo "  build     - Build package only"
    echo "  testpypi  - Upload to TestPyPI"
    echo "  pypi      - Upload to PyPI"
    echo "  all       - Clean, test, build, and upload to TestPyPI"
    echo "  release   - Clean, test, build, and upload to PyPI (full release)"
    echo "  help      - Show this help message"
    echo
    echo "Examples:"
    echo "  $0 test      # Run tests"
    echo "  $0 build     # Build package"
    echo "  $0 all       # Full TestPyPI release"
    echo "  $0 release   # Full PyPI release"
}

check_env() {
    echo_yellow "=== Checking environment ==="
    command -v python3 >/dev/null 2>&1 || { echo_red "Error: python3 not found"; exit 1; }
    command -v pip3 >/dev/null 2>&1 || { echo_red "Error: pip3 not found"; exit 1; }
    command -v twine >/dev/null 2>&1 || { echo_yellow "Warning: twine not found, installing..."; pip3 install twine; }
    python3 -c "import build" 2>/dev/null || { echo_yellow "Warning: build package not found, installing..."; pip3 install build; }
}

clean_build() {
    echo_yellow "=== Cleaning build artifacts ==="
    rm -rf build/ dist/ *.egg-info 2>/dev/null || true
    echo_green "✓ Build artifacts cleaned"
}

run_tests() {
    echo_yellow "=== Running tests ==="
    python3 -m pytest tests/ -v
    echo_green "✓ Tests passed"
}

build_package() {
    echo_yellow "=== Building package ==="
    python3 -m build
    echo_green "✓ Package built"
}

upload_testpypi() {
    echo_yellow "=== Uploading to TestPyPI ==="
    python3 -m twine upload --repository testpypi dist/*
    echo_green "✓ Uploaded to TestPyPI"
}

upload_pypi() {
    echo_yellow "=== Uploading to PyPI ==="
    python3 -m twine upload dist/*
    echo_green "✓ Uploaded to PyPI"
}

install_deps() {
    echo_yellow "=== Installing dependencies ==="
    pip3 install -r requirements.txt
    pip3 install build twine pytest
    echo_green "✓ Dependencies installed"
}

# Main logic
case "${1:-help}" in
    clean)
        clean_build
        ;;
    test)
        check_env
        run_tests
        ;;
    build)
        check_env
        build_package
        ;;
    testpypi)
        check_env
        clean_build
        install_deps
        run_tests
        build_package
        upload_testpypi
        ;;
    pypi)
        check_env
        clean_build
        install_deps
        run_tests
        build_package
        upload_pypi
        ;;
    all)
        check_env
        clean_build
        install_deps
        run_tests
        build_package
        upload_testpypi
        ;;
    release)
        check_env
        clean_build
        install_deps
        run_tests
        build_package
        upload_pypi
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo_red "Unknown option: $1"
        show_help
        exit 1
        ;;
esac

echo_green "=== Done ==="