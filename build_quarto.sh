#!/bin/bash
# Build Quarto documentation site

set -e

echo "Building Quarto documentation..."

# Check if quarto is installed
if ! command -v quarto &> /dev/null; then
    echo "Error: Quarto is not installed."
    echo "Install from: https://quarto.org/docs/get-started/"
    exit 1
fi

# Move to project root
cd "$(dirname "$0")"

# Build the site
quarto render

echo "Documentation built successfully!"
echo "Output directory: docs/"
echo ""
echo "To preview locally:"
echo "  quarto preview"
