#!/bin/bash

# Demo script to show different output options
# This script shows the behavior without actually running backups

echo "=== MySQL Backup Tool - Output Options Demo ==="
echo ""

echo "This demo shows how different -o options affect the output:"
echo ""

echo "1. No -o flag (default):"
echo "   Command: ./mdump.sh -h localhost -u root -p"
echo "   Result: Creates ./mysql_backup_YYYYMMDD_HHMMSS/ directory"
echo "           with mysql_backup_YYYYMMDD_HHMMSS.zip inside"
echo ""

echo "2. Directory only:"
echo "   Command: ./mdump.sh -h localhost -u root -p -o /backups/"
echo "   Result: Creates /backups/mysql_backup_YYYYMMDD_HHMMSS.zip"
echo ""

echo "3. Filename only:"
echo "   Command: ./mdump.sh -h localhost -u root -p -o myapp.zip"
echo "   Result: Creates ./myapp.zip"
echo ""

echo "4. Full path with filename:"
echo "   Command: ./mdump.sh -h localhost -u root -p -o /backups/prod_backup.zip"
echo "   Result: Creates /backups/prod_backup.zip"
echo ""

echo "5. Relative path with filename:"
echo "   Command: ./mdump.sh -h localhost -u root -p -o backups/daily.zip"
echo "   Result: Creates ./backups/daily.zip"
echo ""

echo "=== BEST PRACTICES ==="
echo ""
echo "For daily use:"
echo "  ./mdump.sh -h localhost -u root -p"
echo ""
echo "For scheduled backups:"
echo "  ./mdump.sh -h localhost -u root -p -o /backups/\$(date +%Y%m%d)_backup.zip"
echo ""
echo "For specific applications:"
echo "  ./mdump.sh -h localhost -u root -p -o myapp_backup.zip"
echo ""

echo "To actually run a backup, execute one of the commands above!"
