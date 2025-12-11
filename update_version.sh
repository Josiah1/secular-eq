#!/bin/bash
# Smart version updater for secular-equilibrium package
# Usage: ./update_version.sh [major|minor|patch|set VERSION]

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_red() { echo -e "${RED}$1${NC}"; }
echo_green() { echo -e "${GREEN}$1${NC}"; }
echo_yellow() { echo -e "${YELLOW}$1${NC}"; }
echo_blue() { echo -e "${BLUE}$1${NC}"; }

show_help() {
    echo "Smart Version Updater for Secular Equilibrium Package"
    echo "====================================================="
    echo ""
    echo "Usage: $0 [major|minor|patch|set VERSION]"
    echo ""
    echo "Options:"
    echo "  major    - Major update (X.0.0 -> (X+1).0.0)"
    echo "  minor    - Minor update (1.X.0 -> 1.(X+1).0)"
    echo "  patch    - Patch update (1.0.X -> 1.0.(X+1))"
    echo "  set      - Set to specific version (e.g., set 1.2.3)"
    echo ""
    echo "Examples:"
    echo "  $0 major          # 1.0.0 -> 2.0.0"
    echo "  $0 minor          # 1.0.0 -> 1.1.0"
    echo "  $0 patch          # 1.0.0 -> 1.0.1"
    echo "  $0 set 1.2.3      # Set version to 1.2.3"
    echo ""
    echo "Note: Automatically detects current version from project files."
    exit 0
}

# Check if argument is provided
if [ $# -eq 0 ]; then
    show_help
fi

# Function to validate version format
validate_version() {
    local version="$1"
    if ! [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo_red "Error: Invalid version format '$version'. Expected format: X.Y.Z"
        return 1
    fi
    return 0
}

# Parse arguments
UPDATE_TYPE="$1"
SET_VERSION=""

case "$UPDATE_TYPE" in
    major|minor|patch)
        ;;
    set)
        if [ $# -lt 2 ]; then
            echo_red "Error: 'set' requires a version number"
            echo "Usage: $0 set VERSION"
            echo "Example: $0 set 1.2.3"
            exit 1
        fi
        SET_VERSION="$2"
        # Validate the provided version format
        if ! validate_version "$SET_VERSION"; then
            exit 1
        fi
        ;;
    -h|--help|help)
        show_help
        ;;
    *)
        echo_red "Error: Invalid update type '$UPDATE_TYPE'"
        echo "Valid types: major, minor, patch, set"
        exit 1
        ;;
esac

# Function to extract version from a file
extract_version() {
    local file="$1"
    local version=""

    case "$file" in
        *setup.cfg)
            version=$(grep -E '^version = ' "$file" | head -1 | sed 's/version = //' | tr -d '[:space:]')
            ;;
        *pyproject.toml)
            version=$(grep -E '^version = ' "$file" | head -1 | sed 's/version = "//' | sed 's/"//' | tr -d '[:space:]')
            ;;
        *setup.py)
            version=$(grep -E 'version="[0-9]+\.[0-9]+\.[0-9]+"' "$file" | head -1 | sed 's/.*version="//' | sed 's/".*//' | tr -d '[:space:]')
            ;;
        *__init__.py)
            version=$(grep -E '__version__ = "[0-9]+\.[0-9]+\.[0-9]+"' "$file" | head -1 | sed 's/__version__ = "//' | sed 's/"//' | tr -d '[:space:]')
            ;;
        *cli.py)
            version=$(grep -E "version='%\(prog\)s [0-9]+\.[0-9]+\.[0-9]+'" "$file" | head -1 | sed "s/.*version='%(prog)s //" | sed "s/'//" | tr -d '[:space:]')
            ;;
    esac

    echo "$version"
}

# Function to increment version
increment_version() {
    local version="$1"
    local type="$2"

    IFS='.' read -r major minor patch <<< "$version"

    case "$type" in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
    esac

    echo "${major}.${minor}.${patch}"
}

# Main logic starts here
echo_blue "=== Smart Version Updater ==="
if [ "$UPDATE_TYPE" = "set" ]; then
    echo "Update type: set to $SET_VERSION"
else
    echo "Update type: $UPDATE_TYPE"
fi
echo ""

# List of files to update
FILES=(
    "setup.cfg"
    "pyproject.toml"
    "setup.py"
    "secular_equilibrium/__init__.py"
    "secular_equilibrium/cli.py"
)

# Get current version from the first file
CURRENT_VERSION=""
FIRST_FILE="${FILES[0]}"

if [ ! -f "$FIRST_FILE" ]; then
    echo_red "Error: File '$FIRST_FILE' not found"
    exit 1
fi

CURRENT_VERSION=$(extract_version "$FIRST_FILE")

if [ -z "$CURRENT_VERSION" ]; then
    echo_red "Error: Could not extract version from '$FIRST_FILE'"
    exit 1
fi

echo "Current version: $CURRENT_VERSION"

# Validate current version
if ! validate_version "$CURRENT_VERSION"; then
    exit 1
fi

# Calculate new version
if [ "$UPDATE_TYPE" = "set" ]; then
    NEW_VERSION="$SET_VERSION"
else
    NEW_VERSION=$(increment_version "$CURRENT_VERSION" "$UPDATE_TYPE")
fi
echo "New version: $NEW_VERSION"
echo ""

# Confirm update
echo_yellow "Files to be updated:"
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  - $file"
    else
        echo_red "  - $file (NOT FOUND)"
    fi
done

echo ""
# Skip confirmation if NO_CONFIRM is set
if [ "${NO_CONFIRM}" != "1" ]; then
    read -p "Continue with update? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo_red "Update cancelled."
        exit 0
    fi
else
    echo_yellow "Skipping confirmation (NO_CONFIRM=1)"
fi

# Update each file
echo ""
echo_blue "Updating files..."

for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo_yellow "  Skipping '$file' (not found)"
        continue
    fi

    echo "  Updating $file..."

    case "$file" in
        setup.cfg)
            sed -i '' "s/version = $CURRENT_VERSION/version = $NEW_VERSION/" "$file"
            ;;
        pyproject.toml)
            sed -i '' "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" "$file"
            ;;
        setup.py)
            sed -i '' "s/version=\"$CURRENT_VERSION\"/version=\"$NEW_VERSION\"/" "$file"
            ;;
        secular_equilibrium/__init__.py)
            sed -i '' "s/__version__ = \"$CURRENT_VERSION\"/__version__ = \"$NEW_VERSION\"/" "$file"
            ;;
        secular_equilibrium/cli.py)
            sed -i '' "s/version='%(prog)s $CURRENT_VERSION'/version='%(prog)s $NEW_VERSION'/" "$file"
            ;;
    esac

    # Verify update
    UPDATED_VERSION=$(extract_version "$file")
    if [ "$UPDATED_VERSION" = "$NEW_VERSION" ]; then
        echo_green "    ✓ Updated to $UPDATED_VERSION"
    else
        echo_red "    ✗ Failed to update $file (got $UPDATED_VERSION)"
    fi
done

# Update PUBLISHING.md documentation (optional)
if [ -f "PUBLISHING.md" ]; then
    echo ""
    echo_blue "Updating PUBLISHING.md..."

    # Update version in checklist - match any version pattern after "（当前："
    # Use -CSD for UTF-8 support on macOS
    perl -CSD -i -pe "s/（当前：\d+\.\d+\.\d+）/（当前：$NEW_VERSION）/g" "PUBLISHING.md"

    # Update other occurrences
    perl -CSD -i -pe "s/secular_equilibrium-\d+\.\d+\.\d+/secular_equilibrium-$NEW_VERSION/g" "PUBLISHING.md"
    perl -CSD -i -pe "s/secular-equilibrium==\d+\.\d+\.\d+/secular-equilibrium==$NEW_VERSION/g" "PUBLISHING.md"

    echo_green "  ✓ PUBLISHING.md updated"
fi

echo ""
echo_green "=== Version Update Complete ==="
echo ""
echo "Summary:"
echo "  Old version: $CURRENT_VERSION"
echo "  New version: $NEW_VERSION"
if [ "$UPDATE_TYPE" = "set" ]; then
    echo "  Update type: set to $SET_VERSION"
else
    echo "  Update type: $UPDATE_TYPE"
fi
echo ""
echo "Next steps:"
echo "  1. Run tests: ./publish.sh test"
echo "  2. Build package: ./publish.sh build"
echo "  3. Publish to TestPyPI: ./publish.sh all"
echo "  4. Publish to PyPI: ./publish.sh release"
echo "  5. Create git tag: git tag -a v$NEW_VERSION -m \"Release v$NEW_VERSION\""
echo ""

# Verify all files have consistent version
echo_blue "Verifying version consistency..."
ALL_CONSISTENT=true
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        file_version=$(extract_version "$file")
        if [ "$file_version" = "$NEW_VERSION" ]; then
            echo_green "  ✓ $file: $file_version"
        else
            echo_red "  ✗ $file: $file_version (expected $NEW_VERSION)"
            ALL_CONSISTENT=false
        fi
    fi
done

if $ALL_CONSISTENT; then
    echo_green "✓ All files have consistent version: $NEW_VERSION"
else
    echo_red "✗ Version inconsistency detected!"
    exit 1
fi