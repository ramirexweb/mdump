#!/bin/bash

# Wrapper script for mdump - makes execution easier without remembering the full path
# Usage: ./mdump.sh [backup] -h localhost -u root -p
# Usage: ./mdump.sh restore -h localhost -u root -p -f backup.tar.gz

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if virtual environment exists
if [ ! -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    echo "❌ Virtual environment not found"
    echo "Run: bash install.sh"
    exit 1
fi

# Special handling for --help when no command is specified
if [ "$#" -eq 1 ] && [ "$1" = "--help" ]; then
    echo "MySQL Database Backup and Restore Tool (mdump)"
    echo ""
    echo "USAGE:"
    echo "  ./mdump.sh [COMMAND] [OPTIONS]"
    echo ""
    echo "COMMANDS:"
    echo "  backup    Create database backups (default command)"
    echo "  restore   Restore databases from tar.gz backups"
    echo ""
    echo "BACKUP EXAMPLES:"
    echo "  ./mdump.sh -h localhost -u root -p"
    echo "  ./mdump.sh backup -h localhost -u root -p -o /backups/"
    echo "  ./mdump.sh -h localhost -u root -p -o mybackup.tar.gz"
    echo ""
    echo "RESTORE EXAMPLES:"
    echo "  ./mdump.sh restore -h localhost -u root -p -f backup.tar.gz"
    echo "  ./mdump.sh restore -h localhost -u root -p -f /backups/mysql_backup_20250902_081138.tar.gz"
    echo ""
    echo "For detailed help on each command, use:"
    echo "  ./mdump.sh backup --help"
    echo "  ./mdump.sh restore --help"
    echo ""
    exit 0
fi

# Execute mdump with virtual environment Python
exec "$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/mdump.py" "$@"
