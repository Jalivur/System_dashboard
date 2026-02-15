#!/bin/bash

# Script de instalación rápida para System Dashboard

echo "==================================="
echo "System Dashboard - Instalación"
echo "==================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instala Python 3.8+"
    exit 1
fi

echo "✓ Python encontrado: $(python3 --version)"

# Crear entorno virtual
echo ""
echo "Creando entorno virtual..."
python3 -m venv venv

# Activar entorno
source venv/bin/activate

# Actualizar pip
echo ""
echo "Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo ""
echo "Instalando dependencias de Python..."
pip install -r requirements.txt

echo ""
echo "==================================="
echo "✓ Instalación completada"
echo "==================================="
echo ""
echo "Para ejecutar el dashboard:"
echo "  1. Activa el entorno: source venv/bin/activate"
echo "  2. Ejecuta: python main.py"
echo ""
echo "Notas:"
echo "  - Asegúrate de tener lm-sensors instalado: sudo apt-get install lm-sensors"
echo "  - Para speedtest: sudo apt-get install speedtest-cli"
echo "  - Configura tus scripts en config/settings.py"
echo ""
