#!/bin/bash

# MySQL Restore Examples - mdump tool

echo "================================================================"
echo "             MySQL Restore Tool (mdump) - Examples"
echo "================================================================"
echo ""

echo "BASIC USAGE:"
echo ""

echo "# Restore from tar.gz backup (local):"
echo "./mdump.sh restore -h localhost -u root -p -f mysql_backup_20250901_143022.tar.gz"
echo ""

echo "# Restore from tar.gz backup (remote server):"
echo "./mdump.sh restore -h 192.168.1.100 -P 3307 -u admin -p -f /backups/production_backup.tar.gz"
echo ""

echo "# Restore with full path:"
echo "./mdump.sh restore -h localhost -u root -p -f /path/to/backups/mysql_backup_20250901_143022.tar.gz"
echo ""

echo "DIRECT PYTHON USAGE:"
echo ""

echo "# Direct Python execution:"
echo "./.venv/bin/python mdump.py restore -h localhost -u root -p -f backup.tar.gz"
echo ""

echo "# If using system Python (not recommended):"
echo "python mdump.py restore -h localhost -u root -p -f backup.tar.gz"
echo ""

echo "OUTPUT OPTIONS:"
echo ""
echo "• -f filename.tar.gz: Restores from exact backup file"
echo "• -f /path/file.tar.gz: Full path to backup file"
echo "• The tool will extract, analyze, and restore each database"
echo "• For existing databases, you'll be asked: overwrite, skip, or cancel"
echo ""

echo "WORKFLOW:"
echo ""
echo "1. Tool connects to MySQL server"
echo "2. Extracts tar.gz backup file"
echo "3. Lists all databases found in backup"
echo "4. Shows which databases exist vs. new ones"
echo "5. Asks for confirmation to proceed"
echo "6. For each existing database: asks overwrite/skip/cancel"
echo "7. Creates new databases as needed"
echo "8. Restores SQL dumps using mysql command"
echo "9. Cleans up temporary extraction files"
echo ""

echo "TIPS:"
echo ""
echo "• Make sure mysql command is in your PATH"
echo "• Have your MySQL password ready"
echo "• Backup files should contain database_name.sql files"
echo "• Database names are taken from SQL filenames"
echo "• Use 'overwrite' carefully - it will DROP existing databases!"
echo ""

echo "================================================================"
