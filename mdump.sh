#!/bin/bash

# Wrapper script for mdump - makes execution easier without remembering the full path
# Usage: ./mdump.sh -h localhost -u root -p

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if virtual environment exists
if [ ! -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    echo "❌ Virtual environment not found"
    echo "Run: bash install.sh"
    exit 1
fi

# Execute mdump with virtual environment Python
exec "$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/mdump.py" "$@"
