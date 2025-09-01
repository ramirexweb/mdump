# MySQL Backup Tool (mdump)

A command-line tool for creating MySQL database backups in a simple and efficient way.

## Features

- Connect to MySQL servers with familiar parameters (like mysql cli)
- Automatic listing of available databases
- Interactive selection of databases to backup
- Individual SQL file generation per database
- Automatic compression into a single ZIP file
- User-friendly interface with colors and tables

## Installation

1. Clone or download this project
2. Install dependencies:
```bash
bash install.sh
```

Or manually:
```bash
pip install -r requirements.txt
```

## Quick Start

1. Run the setup verification:
```bash
python setup_check.py
```

2. See usage examples:
```bash
./examples.sh
```

3. Use mdump:
```bash
./mdump.sh -h localhost -u root -p
```

## Usage

### Ways to run mdump:

**Option 1: Using the wrapper script (EASIEST)**
```bash
./mdump.sh -h localhost -u root -p
```

**Option 2: Using virtual environment Python directly**
```bash
./.venv/bin/python mdump.py -h localhost -u root -p
```

**Option 3: Activating virtual environment first**
```bash
source .venv/bin/activate
python mdump.py -h localhost -u root -p
```

### Available parameters:
- `-h, --host`: MySQL server host (default: localhost)
- `-u, --user`: MySQL username (required)
- `-p, --password`: Prompt for password interactively
- `-P, --port`: MySQL server port (default: 3306)
- `-o, --output`: Output directory or filename (see OUTPUT OPTIONS below)
- `--help`: Show complete help

### OUTPUT OPTIONS:

**Default behavior (no -o flag):**
```bash
./mdump.sh -h localhost -u root -p
# Creates: ./mysql_backup_20250901_143022/mysql_backup_20250901_143022.zip
```

**Specify directory:**
```bash
./mdump.sh -h localhost -u root -p -o /path/to/backups/
# Creates: /path/to/backups/mysql_backup_20250901_143022.zip
```

**Specify exact filename:**
```bash
./mdump.sh -h localhost -u root -p -o myapp_backup.zip
# Creates: ./myapp_backup.zip

./mdump.sh -h localhost -u root -p -o /backups/production_backup.zip
# Creates: /backups/production_backup.zip
```

### Examples:

```bash
# Default: Creates timestamped directory with backup
./mdump.sh -h localhost -u root -p

# Specify output directory
./mdump.sh -h localhost -u root -p -o /path/to/backups/

# Specify exact backup filename
./mdump.sh -h localhost -u root -p -o myapp_backup.zip

# Remote connection with custom filename
./mdump.sh -h 192.168.1.100 -P 3307 -u admin -p -o server_backup.zip

# Using virtual environment Python directly
./.venv/bin/python mdump.py -h localhost -u root -p -o production.zip
```

## Workflow

1. The tool connects to the MySQL server
2. Lists all available databases
3. Allows you to select which databases to backup
4. Generates a .sql file for each selected database
5. Compresses all files into a single ZIP with timestamp
6. Cleans up temporary files

## Generated files

**Default behavior:**
```
mysql_backup_YYYYMMDD_HHMMSS/
└── mysql_backup_YYYYMMDD_HHMMSS.zip
    ├── database1_YYYYMMDD_HHMMSS.sql
    ├── database2_YYYYMMDD_HHMMSS.sql
    └── ...
```

**With custom filename:**
```
your_specified_name.zip
├── database1_YYYYMMDD_HHMMSS.sql
├── database2_YYYYMMDD_HHMMSS.sql
└── ...
```
