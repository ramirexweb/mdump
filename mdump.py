#!/usr/bin/env python3
"""
MySQL Backup Tool (mdump)
A command-line tool for creating MySQL database backups
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
    """Main class for handling MySQL backups"""
    
    def __init__(self, host, user, password, port=3306, output_dir="./backups"):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.output_dir = Path(output_dir)
        self.connection = None
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def connect(self):
        """Establishes MySQL connection"""
        try:
            console.print(f"[yellow]Connecting to MySQL: {self.user}@{self.host}:{self.port}[/yellow]")
            
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            
            if self.connection.is_connected():
                console.print("[green]✓ Connection successful[/green]")
                return True
                
        except Error as e:
            console.print(f"[red]✗ Connection error: {e}[/red]")
            return False
    
    def get_databases(self):
        """Gets the list of available databases"""
        if not self.connection:
            return []
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            
            # Filter system databases
            system_dbs = ['information_schema', 'performance_schema', 'mysql', 'sys']
            user_databases = [db for db in databases if db not in system_dbs]
            
            cursor.close()
            return user_databases
            
        except Error as e:
            console.print(f"[red]Error getting databases: {e}[/red]")
            return []
    
    def display_databases(self, databases):
        """Displays databases in a nice table"""
        if not databases:
            console.print("[yellow]No user databases found[/yellow]")
            return
        
        table = Table(title="Available Databases")
        table.add_column("#", style="cyan", no_wrap=True)
        table.add_column("Database Name", style="magenta")
        table.add_column("Size", style="green")
        
        for i, db_name in enumerate(databases, 1):
            size = self.get_database_size(db_name)
            table.add_row(str(i), db_name, size)
        
        console.print(table)
    
    def get_database_size(self, db_name):
        """Gets the approximate size of a database"""
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
        """Allows user to select which databases to backup"""
        if not databases:
            return []
        
        console.print("\n[yellow]Select databases to backup:[/yellow]")
        console.print("[dim]Options:[/dim]")
        console.print("[dim]- Individual numbers: 1,3,5[/dim]")
        console.print("[dim]- Ranges: 1-3[/dim]")
        console.print("[dim]- Combinations: 1,3-5,7[/dim]")
        console.print("[dim]- 'all' for all databases[/dim]")
        console.print("[dim]- Enter to exit[/dim]")
        
        while True:
            selection = Prompt.ask("\n[cyan]Your selection[/cyan]", default="")
            
            if not selection:
                return []
            
            if selection.lower() == 'all':
                return databases
            
            try:
                selected_indices = self.parse_selection(selection, len(databases))
                selected_dbs = [databases[i-1] for i in selected_indices]
                
                # Show selection for confirmation
                console.print(f"\n[green]Selected databases:[/green]")
                for db in selected_dbs:
                    console.print(f"  • {db}")
                
                if Confirm.ask("\nContinue with this selection?", default=True):
                    return selected_dbs
                    
            except (ValueError, IndexError) as e:
                console.print(f"[red]Invalid selection: {e}[/red]")
                console.print("[yellow]Please try again[/yellow]")
    
    def parse_selection(self, selection, max_num):
        """Parses user selection (e.g., '1,3-5,7')"""
        indices = set()
        parts = selection.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                # Range
                start, end = part.split('-', 1)
                start, end = int(start.strip()), int(end.strip())
                if start < 1 or end > max_num or start > end:
                    raise ValueError(f"Invalid range: {part}")
                indices.update(range(start, end + 1))
            else:
                # Individual number
                num = int(part)
                if num < 1 or num > max_num:
                    raise ValueError(f"Number out of range: {num}")
                indices.add(num)
        
        return sorted(indices)
    
    def create_backup(self, databases):
        """Creates backup of selected databases"""
        if not databases:
            console.print("[yellow]No databases selected[/yellow]")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_files = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            for db_name in databases:
                task = progress.add_task(f"Backing up {db_name}...", total=None)
                
                sql_file = self.output_dir / f"{db_name}_{timestamp}.sql"
                
                if self.dump_database(db_name, sql_file):
                    backup_files.append(sql_file)
                    progress.update(task, description=f"✓ {db_name} completed")
                else:
                    progress.update(task, description=f"✗ {db_name} failed")
        
        if backup_files:
            return self.compress_backups(backup_files, timestamp)
        else:
            console.print("[red]Could not create any backup[/red]")
            return None
    
    def dump_database(self, db_name, output_file):
        """Executes mysqldump for a specific database"""
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
                console.print(f"[red]Error in mysqldump for {db_name}: {result.stderr}[/red]")
                # Remove partial file
                if output_file.exists():
                    output_file.unlink()
                return False
                
        except FileNotFoundError:
            console.print("[red]Error: mysqldump not found in PATH[/red]")
            console.print("[yellow]Make sure MySQL client is installed[/yellow]")
            return False
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            return False
    
    def compress_backups(self, backup_files, timestamp):
        """Compresses all backup files into a ZIP"""
        zip_file = self.output_dir / f"backup_{timestamp}.zip"
        
        try:
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for sql_file in backup_files:
                    zf.write(sql_file, sql_file.name)
            
            # Clean up individual SQL files
            for sql_file in backup_files:
                sql_file.unlink()
            
            return zip_file
            
        except Exception as e:
            console.print(f"[red]Error compressing files: {e}[/red]")
            return None
    
    def close_connection(self):
        """Closes MySQL connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            console.print("[dim]Connection closed[/dim]")


@click.command()
@click.option('-h', '--host', default='localhost', help='MySQL server host')
@click.option('-u', '--user', required=True, help='MySQL username')
@click.option('-p', '--password', is_flag=True, help='Prompt for password')
@click.option('-P', '--port', default=3306, help='MySQL server port')
@click.option('-o', '--output', default='./backups', help='Output directory')
def main(host, user, password, port, output):
    """
    MySQL Backup Tool - Tool for creating MySQL database backups
    
    Usage examples:
    
    ./mdump.sh -h localhost -u root -p
    
    ./mdump.sh -h 192.168.1.100 -P 3307 -u admin -p -o /path/to/backups
    """
    
    # Banner
    console.print(Panel.fit(
        "[bold blue]MySQL Backup Tool (mdump)[/bold blue]\n"
        "[dim]Tool for MySQL database backups[/dim]",
        border_style="blue"
    ))
    
    # Request password if needed
    if password:
        db_password = getpass.getpass(f"Password for {user}@{host}: ")
    else:
        console.print("[red]Error: You must specify -p to enter password[/red]")
        sys.exit(1)
    
    # Create tool instance
    backup_tool = MySQLBackupTool(host, user, db_password, port, output)
    
    try:
        # Connect to MySQL
        if not backup_tool.connect():
            sys.exit(1)
        
        # Get databases
        databases = backup_tool.get_databases()
        if not databases:
            console.print("[yellow]No user databases found[/yellow]")
            sys.exit(0)
        
        # Display available databases
        backup_tool.display_databases(databases)
        
        # Select databases
        selected_databases = backup_tool.select_databases(databases)
        if not selected_databases:
            console.print("[yellow]No databases selected. Exiting...[/yellow]")
            sys.exit(0)
        
        # Create backup
        console.print(f"\n[cyan]Starting backup of {len(selected_databases)} database(s)...[/cyan]")
        backup_file = backup_tool.create_backup(selected_databases)
        
        if backup_file:
            file_size = backup_file.stat().st_size / (1024 * 1024)  # MB
            console.print(f"\n[green]✓ Backup completed successfully![/green]")
            console.print(f"[green]File: {backup_file}[/green]")
            console.print(f"[green]Size: {file_size:.2f} MB[/green]")
        else:
            console.print("[red]✗ Error creating backup[/red]")
            sys.exit(1)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)
    finally:
        backup_tool.close_connection()


if __name__ == '__main__':
    main()
