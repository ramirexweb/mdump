#!/bin/bash

# Wrapper script para mdump - facilita la ejecución sin tener que recordar la ruta completa
# Uso: ./mdump.sh -h localhost -u root -p

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Verificar que el entorno virtual existe
if [ ! -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    echo "❌ Entorno virtual no encontrado"
    echo "Ejecuta: bash install.sh"
    exit 1
fi

# Ejecutar mdump con el Python del entorno virtual
exec "$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/mdump.py" "$@"
