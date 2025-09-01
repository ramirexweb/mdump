#!/bin/bash

# Script de instalación para mdump
# Ejecuta: bash install.sh

set -e

echo "=== Instalador de MySQL Backup Tool (mdump) ==="
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    echo "Por favor instala Python3 primero"
    exit 1
fi

echo "✅ Python3 encontrado: $(python3 --version)"

# Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv .venv
else
    echo "✅ Entorno virtual ya existe"
fi

# Activar entorno virtual e instalar dependencias
echo "📥 Instalando dependencias..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Verificar instalación
echo ""
echo "🔍 Verificando instalación..."
python setup_check.py

echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "Para usar mdump:"
echo "1. Asegúrate de tener un servidor MySQL funcionando"
echo "2. Ejecuta: python mdump.py -h localhost -u tu_usuario -p"
echo ""
echo "Para más información consulta README.md"
