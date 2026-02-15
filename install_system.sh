#!/bin/bash

# Script de instalación DIRECTA en el sistema (sin venv)
# Para Sistema de Monitoreo

echo "==================================="
echo "System Dashboard - Instalación"
echo "Instalación DIRECTA en el sistema"
echo "==================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instala Python 3.8+"
    exit 1
fi

echo "✓ Python encontrado: $(python3 --version)"

# Instalar dependencias del sistema
echo ""
echo "Instalando dependencias del sistema..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-tk lm-sensors

# Opcional: speedtest
read -p "¿Instalar speedtest-cli? (s/n): " install_speedtest
if [[ "$install_speedtest" == "s" || "$install_speedtest" == "S" ]]; then
    sudo apt-get install -y speedtest-cli
fi

# Instalar dependencias Python DIRECTAMENTE en el sistema
echo ""
echo "Instalando dependencias de Python en el sistema..."

# Usar --break-system-packages para sistemas modernos
echo "Usando --break-system-packages (necesario en Ubuntu 23.04+/Debian 12+)..."
sudo pip3 install --break-system-packages customtkinter psutil

# Alternativa: Si lo anterior falla, instalar para el usuario
if [ $? -ne 0 ]; then
    echo "Instalación con sudo falló, intentando instalación de usuario..."
    pip3 install --user --break-system-packages customtkinter psutil
fi

# Configurar sensors (opcional)
echo ""
read -p "¿Configurar sensors para lectura de temperatura? (s/n): " config_sensors
if [[ "$config_sensors" == "s" || "$config_sensors" == "S" ]]; then
    echo "Configurando sensors..."
    sudo sensors-detect --auto
fi

echo ""
echo "==================================="
echo "✓ Instalación completada"
echo "==================================="
echo ""
echo "Para ejecutar el dashboard:"
echo "  python3 main.py"
echo ""
echo "O crear un lanzador de escritorio (recomendado):"
echo "  ./create_desktop_launcher.sh"
echo ""
