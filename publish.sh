#!/bin/bash
# Script to publish draggg to PyPI using credentials from .env file

set -e

echo "Building package..."
python3 -m build

echo "Publishing to PyPI..."
# Extract password from .env file (INI format)
if [ -f .env ]; then
    # Parse .env file to extract password after [pypi] section
    PYPI_PASSWORD=$(awk '/\[pypi\]/{flag=1; next} flag && /password/{print $3; exit}' .env)
    
    if [ -z "$PYPI_PASSWORD" ]; then
        echo "Error: Could not find password in .env file!"
        echo "Expected format:"
        echo "  [pypi]"
        echo "  username = __token__"
        echo "  password = your-token-here"
        exit 1
    fi
    
    python3 -m twine upload dist/* --username __token__ --password "$PYPI_PASSWORD"
else
    echo "Error: .env file not found!"
    echo "Please create .env file with your PyPI credentials."
    exit 1
fi

echo "Done! Check https://pypi.org/project/draggg/"
