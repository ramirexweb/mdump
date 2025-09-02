#!/usr/bin/env python3
"""
MySQL Backup Tool (mdump)
A command-line tool for creating MySQL database backups
"""

import os
import sys
import tarfile
import subprocess
import getpass
import shutil
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
    
    def __init__(self, host, user, password, port=3306, output_path=None):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
        self.output_path = output_path
        self.output_dir = None
        self.custom_filename = None
        
        # Setup output path
        self._setup_output_path()
    
    def _setup_output_path(self):
        """Setup output path - can be directory or specific filename"""
        if self.output_path is None:
            # Default: create timestamped directory in current location
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = Path(f"./mysql_backup_{timestamp}")
            self.custom_filename = None
        else:
            output_path = Path(self.output_path)
            
            # Check if it's meant to be a specific file
            if output_path.suffix in ['.zip', '.tar', '.tar.gz']:
                # User specified a specific filename
                self.output_dir = output_path.parent
                self.custom_filename = output_path.name
            else:
                # User specified a directory
                self.output_dir = output_path
                self.custom_filename = None
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        console.print(f"[dim]Output directory: {self.output_dir}[/dim]")
        if self.custom_filename:
            console.print(f"[dim]Custom filename: {self.custom_filename}[/dim]")
    
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
                
                # SQL files now use only the database name without timestamp
                sql_file = self.output_dir / f"{db_name}.sql"
                
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
        """Compresses all backup files into a tar.gz archive"""
        if self.custom_filename:
            # User specified exact filename
            tar_file = self.output_dir / self.custom_filename
            # Ensure it has .tar.gz extension
            if not str(tar_file).endswith('.tar.gz'):
                if tar_file.suffix in ['.zip', '.tar']:
                    tar_file = tar_file.with_suffix('.tar.gz')
                else:
                    tar_file = tar_file.with_suffix(tar_file.suffix + '.tar.gz')
        else:
            # Generate default filename
            tar_file = self.output_dir / f"mysql_backup_{timestamp}.tar.gz"
        
        try:
            with tarfile.open(tar_file, 'w:gz') as tf:
                for sql_file in backup_files:
                    tf.add(sql_file, arcname=sql_file.name)
            
            # Clean up individual SQL files
            for sql_file in backup_files:
                sql_file.unlink()
            
            return tar_file
            
        except Exception as e:
            console.print(f"[red]Error compressing files: {e}[/red]")
            return None
    
    def close_connection(self):
        """Closes MySQL connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            console.print("[dim]Connection closed[/dim]")


class MySQLRestoreTool:
    """Class for handling MySQL backup restoration from tar.gz files"""
    
    def __init__(self, host, user, password, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
    
    def connect(self):
        """Establishes connection to MySQL server"""
        try:
            console.print(f"[cyan]Connecting to MySQL server at {self.host}:{self.port}...[/cyan]")
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            
            if self.connection.is_connected():
                console.print("[green]✓ Connected to MySQL server[/green]")
                return True
            else:
                console.print("[red]✗ Failed to connect[/red]")
                return False
                
        except Error as e:
            console.print(f"[red]Connection error: {e}[/red]")
            return False
    
    def extract_backup(self, tar_file_path):
        """Extract tar.gz backup file and return list of SQL files"""
        tar_path = Path(tar_file_path)
        if not tar_path.exists():
            console.print(f"[red]Error: Backup file {tar_file_path} not found[/red]")
            return None
        
        # Create extraction directory
        extract_dir = tar_path.parent / f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        extract_dir.mkdir(exist_ok=True)
        
        try:
            console.print(f"[cyan]Extracting backup file...[/cyan]")
            with tarfile.open(tar_path, 'r:gz') as tf:
                tf.extractall(extract_dir)
            
            # Find all SQL files
            sql_files = list(extract_dir.glob("*.sql"))
            if not sql_files:
                console.print("[red]No SQL files found in backup[/red]")
                return None
            
            console.print(f"[green]✓ Extracted {len(sql_files)} SQL files[/green]")
            return sql_files
            
        except Exception as e:
            console.print(f"[red]Error extracting backup: {e}[/red]")
            return None
    
    def database_exists(self, database_name):
        """Check if database exists"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            cursor.close()
            return database_name in databases
        except Error as e:
            console.print(f"[red]Error checking database: {e}[/red]")
            return False
    
    def create_database(self, database_name):
        """Create a new database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE `{database_name}`")
            cursor.close()
            console.print(f"[green]✓ Created database: {database_name}[/green]")
            return True
        except Error as e:
            console.print(f"[red]Error creating database {database_name}: {e}[/red]")
            return False
    
    def drop_database(self, database_name):
        """Drop an existing database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DROP DATABASE `{database_name}`")
            cursor.close()
            console.print(f"[yellow]⚠ Dropped database: {database_name}[/yellow]")
            return True
        except Error as e:
            console.print(f"[red]Error dropping database {database_name}: {e}[/red]")
            return False
    
    def restore_database(self, sql_file):
        """Restore database from SQL file using mysql command"""
        database_name = sql_file.stem  # Get filename without extension
        
        try:
            # Build mysql command
            mysql_cmd = [
                'mysql',
                f'--host={self.host}',
                f'--port={self.port}',
                f'--user={self.user}',
                f'--password={self.password}',
                database_name
            ]
            
            console.print(f"[cyan]Restoring {database_name} from {sql_file.name}...[/cyan]")
            
            with open(sql_file, 'r', encoding='utf-8') as f:
                result = subprocess.run(
                    mysql_cmd,
                    stdin=f,
                    capture_output=True,
                    text=True,
                    check=True
                )
            
            console.print(f"[green]✓ Successfully restored database: {database_name}[/green]")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error restoring {database_name}: {e.stderr}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]Unexpected error restoring {database_name}: {e}[/red]")
            return False
    
    def restore_backup(self, tar_file_path):
        """Main method to restore backup from tar.gz file"""
        if not self.connect():
            return False
        
        # Extract backup files
        sql_files = self.extract_backup(tar_file_path)
        if not sql_files:
            return False
        
        # Show found databases
        console.print(f"\n[bold blue]Found {len(sql_files)} database backup(s):[/bold blue]")
        table = Table(show_header=True)
        table.add_column("Database Name", style="cyan")
        table.add_column("File Size", style="green")
        table.add_column("Status", style="yellow")
        
        for sql_file in sql_files:
            database_name = sql_file.stem
            file_size = sql_file.stat().st_size / 1024  # KB
            exists = self.database_exists(database_name)
            status = "EXISTS" if exists else "NEW"
            table.add_row(database_name, f"{file_size:.1f} KB", status)
        
        console.print(table)
        
        # Confirm restore
        if not Confirm.ask("\n[bold yellow]Do you want to proceed with the restore?[/bold yellow]"):
            console.print("[yellow]Restore cancelled[/yellow]")
            return False
        
        # Process each database
        success_count = 0
        for sql_file in sql_files:
            database_name = sql_file.stem
            
            if self.database_exists(database_name):
                # Database exists, ask what to do
                console.print(f"\n[yellow]Database '{database_name}' already exists[/yellow]")
                action = Prompt.ask(
                    "What would you like to do?",
                    choices=["overwrite", "skip", "cancel"],
                    default="skip"
                )
                
                if action == "cancel":
                    console.print("[yellow]Restore cancelled[/yellow]")
                    break
                elif action == "skip":
                    console.print(f"[yellow]Skipped: {database_name}[/yellow]")
                    continue
                elif action == "overwrite":
                    if not self.drop_database(database_name):
                        continue
                    if not self.create_database(database_name):
                        continue
            else:
                # Create new database
                if not self.create_database(database_name):
                    continue
            
            # Restore database
            if self.restore_database(sql_file):
                success_count += 1
        
        # Cleanup extraction directory
        import shutil
        shutil.rmtree(sql_files[0].parent, ignore_errors=True)
        
        console.print(f"\n[bold green]✅ Restore completed: {success_count}/{len(sql_files)} databases restored[/bold green]")
        return success_count > 0
    
    def close_connection(self):
        """Closes MySQL connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            console.print("[dim]Connection closed[/dim]")


@click.group()
def cli():
    """MySQL Database Backup and Restore Tool (mdump)"""
    pass


@cli.command()
@click.option('-h', '--host', default='localhost', help='MySQL server host')
@click.option('-u', '--user', required=True, help='MySQL username')
@click.option('-p', '--password', is_flag=True, help='Prompt for password')
@click.option('-P', '--port', default=3306, help='MySQL server port')
@click.option('-o', '--output', default=None, help='Output directory or filename (default: ./mysql_backup_TIMESTAMP/)')
def backup(host, user, password, port, output):
    """
    MySQL Backup Tool - Tool for creating MySQL database backups
    
    OUTPUT OPTIONS:
    - No -o flag: Creates ./mysql_backup_YYYYMMDD_HHMMSS/ directory
    - -o /path/to/dir: Uses specified directory
    - -o /path/to/backup.tar.gz: Creates backup with exact filename
    - -o backup.tar.gz: Creates backup.tar.gz in current directory
    
    Usage examples:
    
    ./mdump.sh -h localhost -u root -p
    ./mdump.sh -h localhost -u root -p -o /backups/
    ./mdump.sh -h localhost -u root -p -o /backups/myapp_backup.tar.gz
    ./mdump.sh -h 192.168.1.100 -P 3307 -u admin -p -o server_backup.tar.gz
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


@cli.command()
@click.option('-h', '--host', default='localhost', help='MySQL server host')
@click.option('-u', '--user', required=True, help='MySQL username')
@click.option('-p', '--password', is_flag=True, help='Prompt for password')
@click.option('-P', '--port', default=3306, help='MySQL server port')
@click.option('-f', '--file', required=True, help='Path to tar.gz backup file to restore')
def restore(host, user, password, port, file):
    """
    MySQL Restore Tool - Tool for restoring MySQL databases from tar.gz backups
    
    Usage examples:
    
    ./mdump.sh restore -h localhost -u root -p -f backup.tar.gz
    ./mdump.sh restore -h localhost -u root -p -f /backups/mysql_backup_20250901_143022.tar.gz
    """
    
    # Banner
    console.print(Panel.fit(
        "[bold green]MySQL Restore Tool (mdump)[/bold green]\n"
        "[dim]Tool for MySQL database restoration[/dim]",
        border_style="green"
    ))
    
    # Request password if needed
    if password:
        db_password = getpass.getpass(f"Password for {user}@{host}: ")
    else:
        console.print("[red]Error: You must specify -p to enter password[/red]")
        sys.exit(1)
    
    # Create restore tool instance
    restore_tool = MySQLRestoreTool(host, user, db_password, port)
    
    try:
        # Restore backup
        console.print(f"\n[cyan]Starting restore from {file}...[/cyan]")
        success = restore_tool.restore_backup(file)
        
        if success:
            console.print(f"\n[green]✓ Restore completed successfully![/green]")
        else:
            console.print("[red]✗ Error during restore process[/red]")
            sys.exit(1)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)
    finally:
        restore_tool.close_connection()


if __name__ == '__main__':
    # If no command provided, default to backup for backward compatibility
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1].startswith('-')):
        sys.argv.insert(1, 'backup')
    cli()
