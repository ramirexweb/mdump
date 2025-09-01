# MySQL Backup Tool (mdump)

Una herramienta de línea de comandos para hacer backups de bases de datos MySQL de forma simple y eficiente.

## Características

- Conexión a servidores MySQL con parámetros familiares (como mysql cli)
- Lista automática de bases de datos disponibles
- Selección interactiva de las bases de datos a respaldar
- Generación de archivos SQL individuales por base de datos
- Compresión automática en un archivo ZIP
- Interfaz amigable con colores y tablas

## Instalación

1. Clona o descarga este proyecto
2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Formas de ejecutar mdump:

**Opción 1: Usando el wrapper script (más fácil)**
```bash
./mdump.sh -h localhost -u root -p
```

**Opción 2: Usando el Python del entorno virtual directamente**
```bash
./.venv/bin/python mdump.py -h localhost -u root -p
```

**Opción 3: Activando el entorno virtual primero**
```bash
source .venv/bin/activate
python mdump.py -h localhost -u root -p
```

### Parámetros disponibles:
- `-h, --host`: Host del servidor MySQL (default: localhost)
- `-u, --user`: Usuario de MySQL (requerido)
- `-p, --password`: Solicitar contraseña de forma interactiva
- `-P, --port`: Puerto del servidor MySQL (default: 3306)
- `-o, --output`: Directorio de salida para los backups (default: ./backups)
- `--help`: Muestra ayuda completa

### Ejemplos:

```bash
# Conexión local con usuario root (usando wrapper)
./mdump.sh -h localhost -u root -p

# Conexión remota con puerto específico
./mdump.sh -h 192.168.1.100 -P 3307 -u admin -p

# Especificar directorio de salida
./mdump.sh -h localhost -u root -p -o /path/to/backups

# Usando el Python del entorno virtual directamente
./.venv/bin/python mdump.py -h localhost -u root -p
```

## Flujo de trabajo

1. La herramienta se conecta al servidor MySQL
2. Lista todas las bases de datos disponibles
3. Permite seleccionar cuáles bases de datos respaldar
4. Genera un archivo .sql por cada base de datos seleccionada
5. Comprime todos los archivos en un solo ZIP con timestamp
6. Limpia los archivos temporales

## Archivos generados

Los backups se guardan con el formato:
```
backup_YYYYMMDD_HHMMSS.zip
├── database1_YYYYMMDD_HHMMSS.sql
├── database2_YYYYMMDD_HHMMSS.sql
└── ...
```
