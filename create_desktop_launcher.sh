#!/bin/bash

# Script para crear lanzador de escritorio
# Para Sistema de Monitoreo

CURRENT_DIR=$(pwd)
DESKTOP_FILE="$HOME/.local/share/applications/system-dashboard.desktop"
ICON_FILE="$CURRENT_DIR/dashboard_icon.png"

echo "Creando lanzador de escritorio..."

# Crear directorio si no existe
mkdir -p "$HOME/.local/share/applications"

# Crear archivo .desktop
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=System Dashboard
Comment=Monitor del sistema con control de ventiladores
Exec=python3 $CURRENT_DIR/main.py
Path=$CURRENT_DIR
Icon=utilities-system-monitor
Terminal=false
Categories=System;Monitor;
Keywords=monitor;cpu;ram;temperature;fan;
StartupNotify=false
EOF

echo "✓ Lanzador creado en: $DESKTOP_FILE"
echo ""
echo "Ahora puedes:"
echo "  1. Buscar 'System Dashboard' en el menú de aplicaciones"
echo "  2. O ejecutar directamente: python3 main.py"
echo ""

# Preguntar si quiere autostart
read -p "¿Quieres que inicie automáticamente al encender? (s/n): " autostart
if [[ "$autostart" == "s" || "$autostart" == "S" ]]; then
    AUTOSTART_DIR="$HOME/.config/autostart"
    mkdir -p "$AUTOSTART_DIR"
    cp "$DESKTOP_FILE" "$AUTOSTART_DIR/"
    echo "✓ Configurado para iniciar automáticamente"
fi

echo ""
echo "¡Listo! 🎉"
