# 🚀 Instalación Sin Entorno Virtual

Esta guía es para instalar el Sistema de Monitoreo **directamente en tu sistema** sin usar entornos virtuales.

---

## ⚡ Instalación Rápida (Método Automático)

```bash
cd system_dashboard
chmod +x install_system.sh
sudo ./install_system.sh
```

El script instalará:
- ✅ Dependencias del sistema (python3-pip, python3-tk, lm-sensors)
- ✅ Dependencias Python (customtkinter, psutil)
- ✅ Speedtest-cli (opcional)
- ✅ Configurará sensors

---

## 📝 Instalación Manual (Paso a Paso)

### 1. Instalar Dependencias del Sistema

```bash
# Actualizar repositorios
sudo apt-get update

# Instalar herramientas necesarias
sudo apt-get install -y python3 python3-pip python3-tk lm-sensors

# Opcional: speedtest
sudo apt-get install -y speedtest-cli
```

### 2. Instalar Dependencias Python

```bash
# Para sistemas MODERNOS (Ubuntu 23.04+, Debian 12+)
# Usar --break-system-packages (es seguro, solo omite protección PEP 668)
sudo pip3 install --break-system-packages customtkinter psutil

# Para sistemas ANTIGUOS (Ubuntu 22.04 y anteriores)
sudo pip3 install customtkinter psutil

# Alternativa SIN sudo (instala solo para tu usuario)
pip3 install --user --break-system-packages customtkinter psutil
```

**⚠️ Si te sale error "externally-managed-environment":**
Lee la guía completa en **[INSTALL_MODERN_LINUX.md](INSTALL_MODERN_LINUX.md)**

### 3. Configurar Sensores de Temperatura

```bash
# Detectar sensores automáticamente
sudo sensors-detect --auto

# Verificar que funciona
sensors
```

---

## 🎮 Ejecutar el Dashboard

### Opción 1: Desde Terminal

```bash
cd /ruta/a/system_dashboard
python3 main.py
```

### Opción 2: Crear Lanzador de Escritorio

```bash
cd system_dashboard
chmod +x create_desktop_launcher.sh
./create_desktop_launcher.sh
```

Luego busca "System Dashboard" en tu menú de aplicaciones.

### Opción 3: Autostart al Encender

El script `create_desktop_launcher.sh` te preguntará si quieres que inicie automáticamente.

O hazlo manualmente:

```bash
# Copiar lanzador a autostart
mkdir -p ~/.config/autostart
cp ~/.local/share/applications/system-dashboard.desktop ~/.config/autostart/
```

---

## 🔧 Verificar Instalación

### Comprobar que todo está instalado:

```bash
# Python 3
python3 --version
# Debe mostrar: Python 3.x.x

# CustomTkinter
python3 -c "import customtkinter; print('CustomTkinter OK')"

# psutil
python3 -c "import psutil; print('psutil OK')"

# Sensors
sensors
# Debe mostrar temperaturas
```

---

## 📂 Ubicación de Archivos

Una vez instalado en el sistema:

- **Código**: `/ruta/donde/descargaste/system_dashboard/`
- **Lanzador**: `~/.local/share/applications/system-dashboard.desktop`
- **Autostart**: `~/.config/autostart/system-dashboard.desktop`
- **Datos**: `system_dashboard/data/` (se crea automáticamente)

---

## 🎨 Personalizar

Edita `config/settings.py` para cambiar:
- Colores
- Fuentes  
- Umbrales de advertencia
- Scripts de lanzadores
- Intervalos de actualización

```python
# Ejemplo: cambiar color principal
COLORS = {
    "primary": "#00ffff",  # Tu color favorito
    # ...
}
```

---

## 🐛 Solución de Problemas

### Error: "pip3: command not found"

```bash
sudo apt-get install python3-pip
```

### Error: "No module named 'customtkinter'"

```bash
# Instalar con sudo
sudo pip3 install customtkinter

# O sin sudo
pip3 install --user customtkinter
```

### Error: "Temperatura siempre en 0"

```bash
# Configurar sensors
sudo sensors-detect --auto

# Reiniciar
sudo reboot
```

### Dashboard no inicia

```bash
# Verificar Python
python3 --version

# Ejecutar con debug
python3 main.py 2>&1 | tee debug.log
```

---

## 🗑️ Desinstalar

### Eliminar código:
```bash
rm -rf /ruta/a/system_dashboard
```

### Eliminar dependencias Python:
```bash
sudo pip3 uninstall customtkinter psutil
```

### Eliminar lanzador:
```bash
rm ~/.local/share/applications/system-dashboard.desktop
rm ~/.config/autostart/system-dashboard.desktop
```

---

## 📊 Ventajas Sin Entorno Virtual

✅ Más fácil de instalar
✅ Se ejecuta más rápido
✅ Disponible para todos los usuarios del sistema
✅ Fácil de poner en autostart
✅ Sin necesidad de activar entornos

## ⚠️ Consideraciones

❗ Las dependencias se instalan en todo el sistema
❗ Pueden haber conflictos con otras aplicaciones Python
❗ Necesitas permisos sudo para instalar

---

## 💡 Tips

### Ejecutar en segundo plano:
```bash
python3 main.py &
```

### Ver logs:
```bash
python3 main.py 2>&1 | tee dashboard.log
```

### Hacer ejecutable:
```bash
# Añadir shebang al inicio de main.py
# #!/usr/bin/env python3

chmod +x main.py
./main.py
```

---

## 🎯 Resumen de Comandos

```bash
# 1. Instalar
cd system_dashboard
sudo ./install_system.sh

# 2. Crear lanzador (opcional)
./create_desktop_launcher.sh

# 3. Ejecutar
python3 main.py

# ¡Listo! 🎉
```

---

**¿Problemas?** Ejecuta con debug y revisa el error:
```bash
python3 main.py 2>&1 | tee error.log
```
