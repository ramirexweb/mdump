#!/usr/bin/env python3
"""
Ejemplo de script automatizado usando mdump
Este script muestra cómo automatizar backups usando mdump como librería
"""

import os
import sys
from pathlib import Path
from mdump import MySQLBackupTool

def automated_backup():
    """Ejemplo de backup automatizado"""
    
    # Configuración - CAMBIAR ESTOS VALORES
    config = {
        'host': 'localhost',
        'user': 'root', 
        'password': 'tu_password_aqui',  # ¡NO hardcodees passwords en producción!
        'port': 3306,
        'output_dir': './backups_automaticos'
    }
    
    # Bases de datos específicas a respaldar
    target_databases = ['mi_app', 'logs', 'usuarios']  # Cambiar por tus BD
    
    print("=== Backup Automatizado ===")
    
    # Crear herramienta de backup
    backup_tool = MySQLBackupTool(
        host=config['host'],
        user=config['user'],
        password=config['password'],
        port=config['port'],
        output_dir=config['output_dir']
    )
    
    try:
        # Conectar
        if not backup_tool.connect():
            print("Error conectando a MySQL")
            return False
        
        # Obtener bases de datos disponibles
        available_dbs = backup_tool.get_databases()
        
        # Filtrar solo las que queremos
        databases_to_backup = [db for db in target_databases if db in available_dbs]
        
        if not databases_to_backup:
            print("No se encontraron las bases de datos especificadas")
            return False
        
        print(f"Respaldando: {databases_to_backup}")
        
        # Crear backup
        backup_file = backup_tool.create_backup(databases_to_backup)
        
        if backup_file:
            print(f"✅ Backup exitoso: {backup_file}")
            return True
        else:
            print("❌ Error en el backup")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        backup_tool.close_connection()

def scheduled_backup_example():
    """
    Ejemplo de cómo programar backups usando cron
    
    Para programar este script en cron, agrega una línea como:
    0 2 * * * cd /path/to/mdump && python backup_automatico.py
    
    Esto ejecutará el backup todos los días a las 2 AM
    """
    
    # Para usar variables de entorno (más seguro):
    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'output_dir': os.getenv('BACKUP_DIR', './backups')
    }
    
    # El resto del código sería igual...
    pass

if __name__ == '__main__':
    print("⚠️  IMPORTANTE: Este es solo un ejemplo!")
    print("Debes modificar las variables de configuración antes de usar.")
    print("")
    
    # Descomentar la siguiente línea para ejecutar el backup:
    # automated_backup()
    
    print("Para usar este script:")
    print("1. Modifica la configuración en la función automated_backup()")
    print("2. Especifica tus bases de datos en target_databases")
    print("3. Descomenta la llamada a automated_backup()")
    print("4. Para más seguridad, usa variables de entorno para passwords")
