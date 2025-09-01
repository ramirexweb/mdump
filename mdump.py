#!/usr/bin/env python3
"""
MySQL Backup Tool (mdump)
Una herramienta de línea de comandos para hacer backups de bases de datos MySQL
"""

import os
import sys
import zipfile
import subprocess
import getpass
from datetime import datetime
from pathlib import Path
import click
import mysql.connector
from mysql.connector import Error
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from tabulate import tabulate

console = Console()


class MySQLBackupTool:
    """Clase principal para manejar backups de MySQL"""
    
    def __init__(self, host, user, password, port=3306, output_dir="./backups"):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.output_dir = Path(output_dir)
        self.connection = None
        
        # Crear directorio de salida si no existe
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def connect(self):
        """Establece conexión con MySQL"""
        try:
            console.print(f"[yellow]Conectando a MySQL: {self.user}@{self.host}:{self.port}[/yellow]")
            
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            
            if self.connection.is_connected():
                console.print("[green]✓ Conexión exitosa[/green]")
                return True
                
        except Error as e:
            console.print(f"[red]✗ Error de conexión: {e}[/red]")
            return False
    
    def get_databases(self):
        """Obtiene la lista de bases de datos disponibles"""
        if not self.connection:
            return []
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            
            # Filtrar bases de datos del sistema
            system_dbs = ['information_schema', 'performance_schema', 'mysql', 'sys']
            user_databases = [db for db in databases if db not in system_dbs]
            
            cursor.close()
            return user_databases
            
        except Error as e:
            console.print(f"[red]Error obteniendo bases de datos: {e}[/red]")
            return []
    
    def display_databases(self, databases):
        """Muestra las bases de datos en una tabla bonita"""
        if not databases:
            console.print("[yellow]No se encontraron bases de datos de usuario[/yellow]")
            return
        
        table = Table(title="Bases de Datos Disponibles")
        table.add_column("#", style="cyan", no_wrap=True)
        table.add_column("Nombre de la Base de Datos", style="magenta")
        table.add_column("Tamaño", style="green")
        
        for i, db_name in enumerate(databases, 1):
            size = self.get_database_size(db_name)
            table.add_row(str(i), db_name, size)
        
        console.print(table)
    
    def get_database_size(self, db_name):
        """Obtiene el tamaño aproximado de una base de datos"""
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT 
                    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'DB Size in MB'
                FROM information_schema.tables 
                WHERE table_schema = %s
                GROUP BY table_schema
            """
            cursor.execute(query, (db_name,))
            result = cursor.fetchone()
            cursor.close()
            
            if result and result[0]:
                return f"{result[0]} MB"
            else:
                return "< 1 MB"
                
        except Error:
            return "N/A"
    
    def select_databases(self, databases):
        """Permite al usuario seleccionar qué bases de datos respaldar"""
        if not databases:
            return []
        
        console.print("\n[yellow]Selecciona las bases de datos a respaldar:[/yellow]")
        console.print("[dim]Opciones:[/dim]")
        console.print("[dim]- Números individuales: 1,3,5[/dim]")
        console.print("[dim]- Rangos: 1-3[/dim]")
        console.print("[dim]- Combinaciones: 1,3-5,7[/dim]")
        console.print("[dim]- 'all' para todas[/dim]")
        console.print("[dim]- Enter para salir[/dim]")
        
        while True:
            selection = Prompt.ask("\n[cyan]Tu selección[/cyan]", default="")
            
            if not selection:
                return []
            
            if selection.lower() == 'all':
                return databases
            
            try:
                selected_indices = self.parse_selection(selection, len(databases))
                selected_dbs = [databases[i-1] for i in selected_indices]
                
                # Mostrar selección para confirmar
                console.print(f"\n[green]Bases de datos seleccionadas:[/green]")
                for db in selected_dbs:
                    console.print(f"  • {db}")
                
                if Confirm.ask("\n¿Continuar con esta selección?", default=True):
                    return selected_dbs
                    
            except (ValueError, IndexError) as e:
                console.print(f"[red]Selección inválida: {e}[/red]")
                console.print("[yellow]Por favor, intenta de nuevo[/yellow]")
    
    def parse_selection(self, selection, max_num):
        """Parsea la selección del usuario (ej: '1,3-5,7')"""
        indices = set()
        parts = selection.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                # Rango
                start, end = part.split('-', 1)
                start, end = int(start.strip()), int(end.strip())
                if start < 1 or end > max_num or start > end:
                    raise ValueError(f"Rango inválido: {part}")
                indices.update(range(start, end + 1))
            else:
                # Número individual
                num = int(part)
                if num < 1 or num > max_num:
                    raise ValueError(f"Número fuera de rango: {num}")
                indices.add(num)
        
        return sorted(indices)
    
    def create_backup(self, databases):
        """Crea backup de las bases de datos seleccionadas"""
        if not databases:
            console.print("[yellow]No hay bases de datos seleccionadas[/yellow]")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_files = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            for db_name in databases:
                task = progress.add_task(f"Respaldando {db_name}...", total=None)
                
                sql_file = self.output_dir / f"{db_name}_{timestamp}.sql"
                
                if self.dump_database(db_name, sql_file):
                    backup_files.append(sql_file)
                    progress.update(task, description=f"✓ {db_name} completado")
                else:
                    progress.update(task, description=f"✗ {db_name} falló")
        
        if backup_files:
            return self.compress_backups(backup_files, timestamp)
        else:
            console.print("[red]No se pudo crear ningún backup[/red]")
            return None
    
    def dump_database(self, db_name, output_file):
        """Ejecuta mysqldump para una base de datos específica"""
        try:
            cmd = [
                'mysqldump',
                f'--host={self.host}',
                f'--user={self.user}',
                f'--password={self.password}',
                f'--port={self.port}',
                '--single-transaction',
                '--routines',
                '--triggers',
                '--events',
                '--add-drop-database',
                '--create-options',
                db_name
            ]
            
            with open(output_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                return True
            else:
                console.print(f"[red]Error en mysqldump para {db_name}: {result.stderr}[/red]")
                # Eliminar archivo parcial
                if output_file.exists():
                    output_file.unlink()
                return False
                
        except FileNotFoundError:
            console.print("[red]Error: mysqldump no encontrado en el PATH[/red]")
            console.print("[yellow]Asegúrate de que MySQL client esté instalado[/yellow]")
            return False
        except Exception as e:
            console.print(f"[red]Error inesperado: {e}[/red]")
            return False
    
    def compress_backups(self, backup_files, timestamp):
        """Comprime todos los archivos de backup en un ZIP"""
        zip_file = self.output_dir / f"backup_{timestamp}.zip"
        
        try:
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for sql_file in backup_files:
                    zf.write(sql_file, sql_file.name)
            
            # Limpiar archivos SQL individuales
            for sql_file in backup_files:
                sql_file.unlink()
            
            return zip_file
            
        except Exception as e:
            console.print(f"[red]Error comprimiendo archivos: {e}[/red]")
            return None
    
    def close_connection(self):
        """Cierra la conexión a MySQL"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            console.print("[dim]Conexión cerrada[/dim]")


@click.command()
@click.option('-h', '--host', default='localhost', help='Host del servidor MySQL')
@click.option('-u', '--user', required=True, help='Usuario de MySQL')
@click.option('-p', '--password', is_flag=True, help='Solicitar contraseña')
@click.option('-P', '--port', default=3306, help='Puerto del servidor MySQL')
@click.option('-o', '--output', default='./backups', help='Directorio de salida')
def main(host, user, password, port, output):
    """
    MySQL Backup Tool - Herramienta para hacer backups de bases de datos MySQL
    
    Ejemplos de uso:
    
    python mdump.py -h localhost -u root -p
    
    python mdump.py -h 192.168.1.100 -P 3307 -u admin -p -o /path/to/backups
    """
    
    # Banner
    console.print(Panel.fit(
        "[bold blue]MySQL Backup Tool (mdump)[/bold blue]\n"
        "[dim]Herramienta para backups de MySQL[/dim]",
        border_style="blue"
    ))
    
    # Solicitar contraseña si es necesario
    if password:
        db_password = getpass.getpass(f"Contraseña para {user}@{host}: ")
    else:
        console.print("[red]Error: Debes especificar -p para ingresar la contraseña[/red]")
        sys.exit(1)
    
    # Crear instancia de la herramienta
    backup_tool = MySQLBackupTool(host, user, db_password, port, output)
    
    try:
        # Conectar a MySQL
        if not backup_tool.connect():
            sys.exit(1)
        
        # Obtener bases de datos
        databases = backup_tool.get_databases()
        if not databases:
            console.print("[yellow]No se encontraron bases de datos de usuario[/yellow]")
            sys.exit(0)
        
        # Mostrar bases de datos disponibles
        backup_tool.display_databases(databases)
        
        # Seleccionar bases de datos
        selected_databases = backup_tool.select_databases(databases)
        if not selected_databases:
            console.print("[yellow]No se seleccionaron bases de datos. Saliendo...[/yellow]")
            sys.exit(0)
        
        # Crear backup
        console.print(f"\n[cyan]Iniciando backup de {len(selected_databases)} base(s) de datos...[/cyan]")
        backup_file = backup_tool.create_backup(selected_databases)
        
        if backup_file:
            file_size = backup_file.stat().st_size / (1024 * 1024)  # MB
            console.print(f"\n[green]✓ Backup completado exitosamente![/green]")
            console.print(f"[green]Archivo: {backup_file}[/green]")
            console.print(f"[green]Tamaño: {file_size:.2f} MB[/green]")
        else:
            console.print("[red]✗ Error creando el backup[/red]")
            sys.exit(1)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Operación cancelada por el usuario[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error inesperado: {e}[/red]")
        sys.exit(1)
    finally:
        backup_tool.close_connection()


if __name__ == '__main__':
    main()
