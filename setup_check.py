#!/usr/bin/env python3
"""
Script de configuración y verificación para mdump
"""

import subprocess
import sys
from pathlib import Path

def check_mysql_client():
    """Verifica si mysqldump está disponible"""
    try:
        result = subprocess.run(['mysqldump', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ mysqldump encontrado:", result.stdout.strip())
            return True
        else:
            print("✗ mysqldump no funciona correctamente")
            return False
    except FileNotFoundError:
        print("✗ mysqldump no encontrado en el PATH")
        print("\nPara instalar MySQL client en macOS:")
        print("brew install mysql-client")
        print("\nPara instalar en Ubuntu/Debian:")
        print("sudo apt-get install mysql-client")
        return False

def check_python_packages():
    """Verifica que los paquetes de Python estén instalados"""
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
        print("\nPaquetes faltantes. Ejecuta:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    print("=== Verificación del entorno para mdump ===\n")
    
    print("1. Verificando Python packages...")
    packages_ok = check_python_packages()
    
    print("\n2. Verificando MySQL client...")
    mysql_ok = check_mysql_client()
    
    print("\n3. Verificando estructura del proyecto...")
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
        print("✓ Todo listo! Puedes usar mdump")
        print("\nFormas de ejecutar mdump:")
        print("1. ./mdump.sh -h localhost -u root -p  (MÁS FÁCIL)")
        print("2. ./.venv/bin/python mdump.py -h localhost -u root -p")
        print("3. source .venv/bin/activate && python mdump.py -h localhost -u root -p")
        print("\n⚠️  NO uses 'python3 mdump.py' - usa el entorno virtual!")
    else:
        print("✗ Hay problemas que resolver antes de usar mdump")
        sys.exit(1)

if __name__ == '__main__':
    main()
