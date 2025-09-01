#!/usr/bin/env python3
"""
Example of automated script using mdump
This script shows how to automate backups using mdump as a library
"""

import os
import sys
from pathlib import Path
from mdump import MySQLBackupTool

def automated_backup():
    """Example of automated backup"""
    
    # Configuration - CHANGE THESE VALUES
    config = {
        'host': 'localhost',
        'user': 'root', 
        'password': 'your_password_here',  # DON'T hardcode passwords in production!
        'port': 3306,
        'output_path': './automated_backups/'  # Can be directory or specific filename
    }
    
    # Specific databases to backup
    target_databases = ['my_app', 'logs', 'users']  # Change for your DBs
    
    print("=== Automated Backup ===")
    
    # Create backup tool
    backup_tool = MySQLBackupTool(
        host=config['host'],
        user=config['user'],
        password=config['password'],
        port=config['port'],
        output_path=config['output_path']  # Note: changed from output_dir
    )
    
    try:
        # Connect
        if not backup_tool.connect():
            print("Error connecting to MySQL")
            return False
        
        # Get available databases
        available_dbs = backup_tool.get_databases()
        
        # Filter only the ones we want
        databases_to_backup = [db for db in target_databases if db in available_dbs]
        
        if not databases_to_backup:
            print("Specified databases not found")
            return False
        
        print(f"Backing up: {databases_to_backup}")
        
        # Create backup
        backup_file = backup_tool.create_backup(databases_to_backup)
        
        if backup_file:
            print(f"✅ Backup successful: {backup_file}")
            return True
        else:
            print("❌ Backup error")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        backup_tool.close_connection()

def scheduled_backup_example():
    """
    Example of how to schedule backups using cron
    
    To schedule this script in cron, add a line like:
    0 2 * * * cd /path/to/mdump && python backup_automatico.py
    
    This will run the backup every day at 2 AM
    """
    
    # To use environment variables (more secure):
    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'output_path': os.getenv('BACKUP_PATH', './backups/')  # Can be dir or filename
    }
    
    # The rest of the code would be the same...
    pass

if __name__ == '__main__':
    print("⚠️  IMPORTANT: This is just an example!")
    print("You must modify the configuration variables before using.")
    print("")
    
    # Uncomment the following line to run the backup:
    # automated_backup()
    
    print("To use this script:")
    print("1. Modify the configuration in the automated_backup() function")
    print("2. Specify your databases in target_databases")
    print("3. Uncomment the call to automated_backup()")
    print("4. For more security, use environment variables for passwords")
