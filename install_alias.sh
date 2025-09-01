#!/bin/bash

# Script to create a global alias for mdump
# This allows running 'mdump' from any directory

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MDUMP_WRAPPER="$SCRIPT_DIR/mdump.sh"

echo "=== Global Alias Installer for mdump ==="
echo ""

# Check if wrapper exists
if [ ! -f "$MDUMP_WRAPPER" ]; then
    echo "❌ Error: mdump.sh not found in $SCRIPT_DIR"
    exit 1
fi

# Options to create alias
echo "Select an option to create the global alias:"
echo ""
echo "1. Add alias to .zshrc (recommended for zsh)"
echo "2. Create symbolic link in /usr/local/bin (requires sudo)"
echo "3. Just show command to add manually"
echo "4. Exit"
echo ""

read -p "Option (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Adding alias to ~/.zshrc..."
        echo "alias mdump='$MDUMP_WRAPPER'" >> ~/.zshrc
        echo "✅ Alias added to ~/.zshrc"
        echo ""
        echo "To use immediately:"
        echo "source ~/.zshrc"
        echo ""
        echo "Then you can use: mdump -h localhost -u root -p"
        ;;
    2)
        echo ""
        echo "Creating symbolic link in /usr/local/bin..."
        sudo ln -sf "$MDUMP_WRAPPER" /usr/local/bin/mdump
        if [ $? -eq 0 ]; then
            echo "✅ Symbolic link created"
            echo ""
            echo "Now you can use: mdump -h localhost -u root -p"
        else
            echo "❌ Error creating symbolic link"
        fi
        ;;
    3)
        echo ""
        echo "To add the alias manually, run:"
        echo ""
        echo "echo \"alias mdump='$MDUMP_WRAPPER'\" >> ~/.zshrc"
        echo "source ~/.zshrc"
        echo ""
        echo "Or for bash:"
        echo "echo \"alias mdump='$MDUMP_WRAPPER'\" >> ~/.bashrc"
        echo "source ~/.bashrc"
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac
