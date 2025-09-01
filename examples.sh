#!/bin/bash
# Example script for using mdump

echo "=== WAYS TO RUN MDUMP ==="
echo ""

echo "=== Option 1: Using the wrapper (EASIEST) ==="
echo "# Default timestamped directory:"
echo "./mdump.sh -h localhost -u root -p"
echo ""
echo "# Custom directory:"
echo "./mdump.sh -h localhost -u root -p -o /path/to/backups/"
echo ""
echo "# Custom filename:"
echo "./mdump.sh -h localhost -u root -p -o myapp_backup.tar.gz"
echo ""
echo "# Remote with custom filename:"
echo "./mdump.sh -h 192.168.1.100 -P 3307 -u admin -p -o server_backup.tar.gz"
echo ""

echo "=== Option 2: Virtual environment Python directly ==="
echo "./.venv/bin/python mdump.py -h localhost -u root -p"
echo "./.venv/bin/python mdump.py -h localhost -u root -p -o production.tar.gz"
echo ""

echo "=== Option 3: Activating virtual environment first ==="
echo "source .venv/bin/activate"
echo "python mdump.py -h localhost -u root -p -o backup.tar.gz"
echo "deactivate  # to exit virtual environment"
echo ""

echo "=== OUTPUT OPTIONS ==="
echo "• No -o flag: Creates ./mysql_backup_TIMESTAMP/ directory"
echo "• -o /path/dir/: Uses specified directory"  
echo "• -o filename.tar.gz: Creates backup with exact name"
echo "• -o /path/file.tar.gz: Full path with custom name"
echo ""

echo "⚠️  IMPORTANT: DO NOT use 'python3 mdump.py' from system"
echo "   Dependencies are in the virtual environment (.venv)"
echo ""
echo "To run any example, copy and paste the corresponding command"
