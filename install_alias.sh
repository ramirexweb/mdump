#!/bin/bash

# Script para crear un alias global de mdump
# Esto permite ejecutar 'mdump' desde cualquier directorio

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MDUMP_WRAPPER="$SCRIPT_DIR/mdump.sh"

echo "=== Instalador de Alias Global para mdump ==="
echo ""

# Verificar que el wrapper existe
if [ ! -f "$MDUMP_WRAPPER" ]; then
    echo "❌ Error: mdump.sh no encontrado en $SCRIPT_DIR"
    exit 1
fi

# Opciones para crear el alias
echo "Selecciona una opción para crear el alias global:"
echo ""
echo "1. Agregar alias al .zshrc (recomendado para zsh)"
echo "2. Crear enlace simbólico en /usr/local/bin (requiere sudo)"
echo "3. Solo mostrar comando para agregar manualmente"
echo "4. Salir"
echo ""

read -p "Opción (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Agregando alias a ~/.zshrc..."
        echo "alias mdump='$MDUMP_WRAPPER'" >> ~/.zshrc
        echo "✅ Alias agregado a ~/.zshrc"
        echo ""
        echo "Para usar inmediatamente:"
        echo "source ~/.zshrc"
        echo ""
        echo "Después podrás usar: mdump -h localhost -u root -p"
        ;;
    2)
        echo ""
        echo "Creando enlace simbólico en /usr/local/bin..."
        sudo ln -sf "$MDUMP_WRAPPER" /usr/local/bin/mdump
        if [ $? -eq 0 ]; then
            echo "✅ Enlace simbólico creado"
            echo ""
            echo "Ahora puedes usar: mdump -h localhost -u root -p"
        else
            echo "❌ Error creando el enlace simbólico"
        fi
        ;;
    3)
        echo ""
        echo "Para agregar el alias manualmente, ejecuta:"
        echo ""
        echo "echo \"alias mdump='$MDUMP_WRAPPER'\" >> ~/.zshrc"
        echo "source ~/.zshrc"
        echo ""
        echo "O para bash:"
        echo "echo \"alias mdump='$MDUMP_WRAPPER'\" >> ~/.bashrc"
        echo "source ~/.bashrc"
        ;;
    4)
        echo "Saliendo..."
        exit 0
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac
