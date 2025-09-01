#!/bin/bash
# Example script for using mdump

echo "=== WAYS TO RUN MDUMP ==="
echo ""

echo "=== Option 1: Using the wrapper (EASIEST) ==="
echo "./mdump.sh -h localhost -u root -p"
echo "./mdump.sh -h 192.168.1.100 -P 3307 -u admin -p"
echo "./mdump.sh -h localhost -u root -p -o /path/to/backups"
echo ""

echo "=== Option 2: Virtual environment Python directly ==="
echo "./.venv/bin/python mdump.py -h localhost -u root -p"
echo "./.venv/bin/python mdump.py -h 192.168.1.100 -P 3307 -u admin -p"
echo ""

echo "=== Option 3: Activating virtual environment first ==="
echo "source .venv/bin/activate"
echo "python mdump.py -h localhost -u root -p"
echo "deactivate  # to exit virtual environment"
echo ""

echo "⚠️  IMPORTANT: DO NOT use 'python3 mdump.py' from system"
echo "   Dependencies are in the virtual environment (.venv)"
echo ""
echo "To run any example, copy and paste the corresponding command"
