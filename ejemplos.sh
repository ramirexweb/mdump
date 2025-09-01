#!/bin/bash
# Script de ejemplo para usar mdump

echo "=== FORMAS DE EJECUTAR MDUMP ==="
echo ""

echo "=== Opción 1: Usando el wrapper (MÁS FÁCIL) ==="
echo "./mdump.sh -h localhost -u root -p"
echo "./mdump.sh -h 192.168.1.100 -P 3307 -u admin -p"
echo "./mdump.sh -h localhost -u root -p -o /path/to/backups"
echo ""

echo "=== Opción 2: Python del entorno virtual directamente ==="
echo "./.venv/bin/python mdump.py -h localhost -u root -p"
echo "./.venv/bin/python mdump.py -h 192.168.1.100 -P 3307 -u admin -p"
echo ""

echo "=== Opción 3: Activando entorno virtual primero ==="
echo "source .venv/bin/activate"
echo "python mdump.py -h localhost -u root -p"
echo "deactivate  # para salir del entorno virtual"
echo ""

echo "⚠️  IMPORTANTE: NO uses 'python3 mdump.py' del sistema"
echo "   Las dependencias están en el entorno virtual (.venv)"
echo ""
echo "Para ejecutar algún ejemplo, copia y pega el comando correspondiente"
