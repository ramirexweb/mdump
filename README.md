# MySQL Backup and Restore Tool (mdump)

A powerful and user-friendly command-line tool for creating and restoring MySQL database backups with intelligent output options and professional-grade features.

## 🚀 Features

### Backup Features
- **Familiar MySQL CLI syntax** - Uses the same parameters as standard MySQL tools (`-h`, `-u`, `-p`, `-P`)
- **Intelligent database discovery** - Automatically lists and filters user databases
- **Interactive selection** - Choose databases with flexible selection syntax
- **Smart output options** - Automatic timestamping, custom directories, or specific filenames
- **Professional compression** - Individual SQL files compressed into organized tar.gz archives
- **Production-ready** - Includes stored procedures, triggers, events, and proper transaction handling

### Restore Features
- **Smart tar.gz extraction** - Automatically extracts and processes backup archives
- **Database analysis** - Shows which databases exist vs. new ones before restoring
- **Conflict resolution** - Interactive options for existing databases (overwrite/skip/cancel)
- **Automatic database creation** - Creates new databases as needed during restore
- **Safe restore process** - Uses native mysql commands for reliable restoration
- **Progress tracking** - Visual feedback during the entire restore process

### General Features
- **Beautiful interface** - Color-coded output with progress indicators and formatted tables
- **Cross-platform** - Works on Linux, macOS, and Windows
- **Multiple execution methods** - Wrapper scripts, virtual environment, or direct execution

## 📦 Installation

### Quick Installation

```bash
git clone https://github.com/ramirexweb/mdump.git
cd mdump
bash install.sh
```

### Manual Installation

1. Clone or download this project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🎯 Usage

mdump has two main commands: `backup` (default) and `restore`.

### Backup Databases

**Option 1: Using the wrapper script (RECOMMENDED)**
```bash
./mdump.sh backup -h localhost -u root -p
# or just (backup is default):
./mdump.sh -h localhost -u root -p
```

**Option 2: Using virtual environment Python directly**
```bash
./.venv/bin/python mdump.py backup -h localhost -u root -p
```

### Restore Databases

**Using the wrapper script**
```bash
./mdump.sh restore -h localhost -u root -p -f backup.tar.gz
```

**Using virtual environment Python directly**
```bash
./.venv/bin/python mdump.py restore -h localhost -u root -p -f /path/to/backup.tar.gz
```

### Available parameters:

**Backup command:**
- `-h, --host`: MySQL server host (default: localhost)
- `-u, --user`: MySQL username (required)
- `-p, --password`: Prompt for password interactively
- `-P, --port`: MySQL server port (default: 3306)
- `-o, --output`: Output directory or filename

**Restore command:**
- `-h, --host`: MySQL server host (default: localhost)
- `-u, --user`: MySQL username (required)
- `-p, --password`: Prompt for password interactively
- `-P, --port`: MySQL server port (default: 3306)
- `-f, --file`: Path to tar.gz backup file to restore
- `-P, --port`: MySQL server port (default: 3306)
- `-o, --output`: Output directory or filename (see OUTPUT OPTIONS below)
- `--help`: Show complete help

### OUTPUT OPTIONS:

**Default behavior (no -o flag):**
```bash
./mdump.sh -h localhost -u root -p
# Creates: ./mysql_backup_20250901_143022/mysql_backup_20250901_143022.tar.gz
```

**Specify directory:**
```bash
./mdump.sh -h localhost -u root -p -o /path/to/backups/
# Creates: /path/to/backups/mysql_backup_20250901_143022.tar.gz
```

**Specify exact filename:**
```bash
./mdump.sh -h localhost -u root -p -o myapp_backup.tar.gz
# Creates: ./myapp_backup.tar.gz

./mdump.sh -h localhost -u root -p -o /backups/production_backup.tar.gz
# Creates: /backups/production_backup.tar.gz
```

### Backup Examples:

```bash
# Default: Creates timestamped directory with backup
./mdump.sh -h localhost -u root -p

# Specify output directory
./mdump.sh -h localhost -u root -p -o /path/to/backups/

# Specify exact backup filename
./mdump.sh -h localhost -u root -p -o myapp_backup.tar.gz

# Remote connection with custom filename
./mdump.sh -h 192.168.1.100 -P 3307 -u admin -p -o server_backup.tar.gz

# Using virtual environment Python directly
./.venv/bin/python mdump.py backup -h localhost -u root -p -o production.tar.gz
```

### Restore Examples:

```bash
# Restore from backup file in current directory
./mdump.sh restore -h localhost -u root -p -f mysql_backup_20250901_143022.tar.gz

# Restore from backup file with full path
./mdump.sh restore -h localhost -u root -p -f /backups/production_backup.tar.gz

# Restore to remote server
./mdump.sh restore -h 192.168.1.100 -P 3307 -u admin -p -f backup.tar.gz

# Using virtual environment Python directly
./.venv/bin/python mdump.py restore -h localhost -u root -p -f backup.tar.gz
```

### Restore Process:
1. **Analysis**: Tool extracts and analyzes the tar.gz backup
2. **Database Check**: Shows which databases exist vs. new ones
3. **Confirmation**: Asks for permission to proceed
4. **Conflict Resolution**: For existing databases, asks whether to:
   - `overwrite`: Drops and recreates the database (⚠️ destructive!)
   - `skip`: Leaves existing database unchanged
   - `cancel`: Stops the restore process
5. **Restoration**: Creates new databases and restores from SQL files

## 🗂️ Database Selection

The tool provides flexible database selection options:

- **Individual numbers**: `1,3,5`
- **Ranges**: `1-3`
- **Combinations**: `1,3-5,7`
- **All databases**: `all`
- **Interactive confirmation** before proceeding

## 📁 Generated Files

**Default behavior:**
```
mysql_backup_YYYYMMDD_HHMMSS/
└── mysql_backup_YYYYMMDD_HHMMSS.tar.gz
    ├── database1.sql
    ├── database2.sql
    └── ...
```

**With custom filename:**
```
your_specified_name.tar.gz
├── database1.sql
├── database2.sql
└── ...
```

## 🔄 Workflow

### Backup Workflow
1. **Connect**: Establishes secure connection to MySQL server
2. **Discover**: Lists all available user databases (filters system databases)
3. **Select**: Interactive selection with flexible syntax
4. **Backup**: Creates individual SQL dumps with full schema and data
5. **Compress**: Combines all files into organized tar.gz archive
6. **Cleanup**: Removes temporary SQL files automatically

### Restore Workflow
1. **Connect**: Establishes secure connection to MySQL server
2. **Extract**: Decompresses tar.gz backup and locates SQL files
3. **Analyze**: Lists databases in backup and checks for existing conflicts
4. **Confirm**: Shows restore plan and asks for user confirmation
5. **Resolve**: Handles existing database conflicts (overwrite/skip/cancel)
6. **Restore**: Creates databases and executes SQL files using native mysql
7. **Cleanup**: Removes temporary extraction files

## ⚙️ Advanced Features

### Automated Backups

Use the included `automated_backup.py` template for scheduled backups:

```python
# Example cron job
0 2 * * * cd /path/to/mdump && ./mdump.sh -h localhost -u backup_user -p -o /backups/$(date +\%Y\%m\%d)_backup.tar.gz
```

### Global Alias Installation

Create a system-wide `mdump` command:

```bash
./install_alias.sh
```

### Environment Variables (Production)

For security in production environments:

```bash
export MYSQL_HOST=localhost
export MYSQL_USER=backup_user
export MYSQL_PASSWORD=secure_password
export BACKUP_PATH=/secure/backups/
```

## 🔧 Technical Details

### MySQL Dump Options

The tool uses optimized `mysqldump` parameters:
- `--single-transaction`: Ensures consistency
- `--routines`: Includes stored procedures and functions
- `--triggers`: Includes trigger definitions
- `--events`: Includes event scheduler events
- `--add-drop-database`: Enables easy restoration
- `--create-options`: Preserves table creation options

### Dependencies

- `mysql-connector-python`: MySQL database connectivity
- `click`: Modern command-line interface
- `rich`: Beautiful terminal output and progress indicators
- `tabulate`: Formatted table display

### System Requirements

- Python 3.7 or higher
- MySQL client tools (`mysqldump`)
- MySQL server access
- Sufficient disk space for backups

## 🚨 Best Practices

### Security
- Never hardcode passwords in scripts
- Use environment variables for automated backups
- Restrict file permissions on backup directories
- Use dedicated backup user accounts with minimal privileges

### Performance
- Run backups during low-traffic periods
- Monitor disk space before creating backups
- Consider compression ratios for large databases
- Use `--single-transaction` for InnoDB tables

### Organization
- Use descriptive filenames for important backups
- Implement backup retention policies
- Test restore procedures regularly
- Document backup and restore processes

## 🛠️ Development

### Project Structure
```
mdump/
├── mdump.py                 # Main backup and restore tool
├── mdump.sh                 # Wrapper script
├── setup_check.py          # Environment verification
├── install.sh              # Installation script
├── examples.sh             # Backup usage examples
├── restore_examples.sh     # Restore usage examples
├── automated_backup.py     # Automation template
├── output_demo.sh          # Output options demo
├── install_alias.sh        # Global alias installer
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

### Testing

```bash
# Verify installation
./setup_check.py

# View backup examples
./examples.sh

# View restore examples
./restore_examples.sh

# See output options
./output_demo.sh
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

If you encounter any issues or have questions:

1. Check the documentation above
2. Run `./setup_check.py` to verify your environment
3. View examples with `./examples.sh`
4. Open an issue on GitHub

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

If you encounter any issues or have questions:

1. Check the documentation above
2. Run `./setup_check.py` to verify your environment
3. View examples with `./examples.sh`
4. Open an issue on GitHub

## 🏗️ Author

**Ramiro Dávalos**
- GitHub: [@ramirexweb](https://github.com/ramirexweb)
- Email: [ramirex@gmail.com](mailto:ramirex@gmail.com)

---

⭐ If this tool helps you, please consider giving it a star on GitHub!

## 📊 Version History

- **v1.0.0** - Initial release with core backup functionality
- **v1.1.0** - Added intelligent output options and improved UX
- **v1.2.0** - Enhanced database selection and automation features

## 📊 Version History

- **v1.0.0** - Initial release with core backup functionality
- **v1.1.0** - Added intelligent output options and improved UX
- **v1.2.0** - Enhanced database selection and automation features
