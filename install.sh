#!/bin/bash

# Installation script for mdump
# Run: bash install.sh

set -e

echo "=== MySQL Backup Tool (mdump) Installer ==="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    echo "Please install Python3 first"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "📥 Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
echo ""
echo "🔍 Verifying installation..."
python setup_check.py

echo ""
echo "🎉 Installation completed!"
echo ""
echo "To use mdump:"
echo "1. Make sure you have a working MySQL server"
echo "2. Run: ./mdump.sh -h localhost -u your_username -p"
echo ""
echo "For more information check README.md"
