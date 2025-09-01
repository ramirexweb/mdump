#!/usr/bin/env python3
"""
Configuration and verification script for mdump
"""

import subprocess
import sys
from pathlib import Path

def check_mysql_client():
    """Verifies if mysqldump is available"""
    try:
        result = subprocess.run(['mysqldump', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ mysqldump found:", result.stdout.strip())
            return True
        else:
            print("✗ mysqldump is not working properly")
            return False
    except FileNotFoundError:
        print("✗ mysqldump not found in PATH")
        print("\nTo install MySQL client on macOS:")
        print("brew install mysql-client")
        print("\nTo install on Ubuntu/Debian:")
        print("sudo apt-get install mysql-client")
        return False

def check_python_packages():
    """Verifies that Python packages are installed"""
    required_packages = ['mysql.connector', 'click', 'rich', 'tabulate']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'mysql.connector':
                import mysql.connector
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print("\nMissing packages. Run:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    print("=== Environment verification for mdump ===\n")
    
    print("1. Checking Python packages...")
    packages_ok = check_python_packages()
    
    print("\n2. Checking MySQL client...")
    mysql_ok = check_mysql_client()
    
    print("\n3. Checking project structure...")
    required_files = ['mdump.py', 'requirements.txt', 'README.md']
    files_ok = True
    
    for file in required_files:
        if Path(file).exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file}")
            files_ok = False
    
    print("\n" + "="*50)
    if packages_ok and mysql_ok and files_ok:
        print("✓ Everything ready! You can use mdump")
        print("\nWays to run mdump:")
        print("1. ./mdump.sh -h localhost -u root -p  (EASIEST)")
        print("2. ./.venv/bin/python mdump.py -h localhost -u root -p")
        print("3. source .venv/bin/activate && python mdump.py -h localhost -u root -p")
        print("\n⚠️  DO NOT use 'python3 mdump.py' - use the virtual environment!")
    else:
        print("✗ There are issues to resolve before using mdump")
        sys.exit(1)

if __name__ == '__main__':
    main()
