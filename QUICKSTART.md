# 🚀 Inicio Rápido - Sistema de Monitoreo

## ⚡ Instalación y Ejecución en 3 Pasos

### 1️⃣ Instalar Dependencias del Sistema

```bash
# Actualizar sistema
sudo apt-get update

# Instalar herramientas necesarias
sudo apt-get install -y python3 python3-pip python3-venv lm-sensors

# Opcional: para speedtest
sudo apt-get install -y speedtest-cli

# Configurar sensors (primera vez)
sudo sensors-detect
# Responde 'YES' a todas las preguntas
```

### 2️⃣ Instalar Dependencias de Python

```bash
cd system_dashboard

# Opción A: Usar script de instalación automática
chmod +x install.sh
./install.sh

# Opción B: Manual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3️⃣ Ejecutar

```bash
# Si usaste el script de instalación
source venv/bin/activate
python main.py

# O directamente
./venv/bin/python main.py
```

---

## 🎛️ Configuración Rápida (Opcional)

### Personalizar Scripts de Lanzadores

Edita `config/settings.py`:

```python
LAUNCHERS = [
    {
        "label": "Montar NAS",
        "script": "/ruta/a/tu/script.sh"
    },
    {
        "label": "Backup",
        "script": "/ruta/a/backup.sh"
    },
    # Añade más scripts aquí
]
```

### Cambiar Colores y Fuentes

En `config/settings.py`:

```python
# Cambiar color principal
COLORS = {
    "primary": "#00ffff",  # Cyan por defecto
    "secondary": "#14611E",
    # ...
}

# Cambiar fuente
FONT_FAMILY = "FiraMono Nerd Font"  # Tu fuente favorita
```

### Ajustar Umbrales de Advertencia

```python
# En config/settings.py
CPU_WARN = 60   # Advertencia a 60%
CPU_CRIT = 85   # Crítico a 85%

TEMP_WARN = 60  # Advertencia a 60°C
TEMP_CRIT = 75  # Crítico a 75°C

# Similar para RAM, RED, etc.
```

---

## 📊 Características Principales

### Control de Ventiladores
- ✅ 5 modos: Auto, Manual, Silent, Normal, Performance
- ✅ Curva personalizable temperatura-PWM
- ✅ Añadir/eliminar puntos en la curva
- ✅ Interpolación automática

### Monitor del Sistema
- ✅ CPU, RAM, Temperatura en tiempo real
- ✅ Uso de disco y velocidad I/O
- ✅ Gráficas históricas (últimos 60 valores)
- ✅ Colores dinámicos por umbral

### Monitor de Red
- ✅ Download/Upload en MB/s
- ✅ Escalado adaptativo de gráficas
- ✅ Detección automática de interfaz activa
- ✅ Speedtest integrado

### Monitor USB
- ✅ Lista de dispositivos conectados
- ✅ Actualización en tiempo real
- ✅ Información detallada de cada dispositivo

### Lanzadores
- ✅ Ejecuta scripts del sistema
- ✅ Feedback visual de estado
- ✅ Timeout de seguridad
- ✅ Completamente configurable

---

## 🐛 Solución de Problemas Comunes

### Error: "sensors: command not found"
```bash
sudo apt-get install lm-sensors
sudo sensors-detect
```

### Error: Temperatura siempre en 0°C
```bash
# Configurar sensors
sudo sensors-detect

# Verificar que funciona
sensors

# Si aún no funciona, el código usa fallback de /sys/class/thermal
```

### Error: "speedtest-cli: command not found"
```bash
sudo apt-get install speedtest-cli

# O alternativamente con pip
pip install speedtest-cli
```

### La ventana no aparece en la pantalla secundaria
El código detecta automáticamente la posición del DSI. Si no funciona:
1. Verifica que la pantalla esté conectada
2. Ajusta `DSI_X` y `DSI_Y` en `config/settings.py`

### Scripts de lanzadores no ejecutan
```bash
# Asegúrate de que sean ejecutables
chmod +x /ruta/a/tu/script.sh

# Verifica la ruta en config/settings.py
```

---

## 📚 Documentación Completa

- **README.md**: Documentación detallada del proyecto
- **CHANGELOG.md**: Estado completo de implementación y características
- **MIGRATION_MAP.md**: Mapeo del código original
- **IMPLEMENTATION_GUIDE.md**: Guía para extender el proyecto

---

## 🎯 Uso Básico

1. **Ejecuta el dashboard**: `python main.py`
2. **Selecciona una opción** del menú principal:
   - Control Ventiladores
   - Monitor Placa
   - Monitor Red
   - Monitor USB
   - Lanzadores
3. **Interactúa** con la ventana seleccionada
4. **Cierra** con el botón "Cerrar" o "Salir"

---

## ⚙️ Configuración Avanzada

### Cambiar Intervalo de Actualización

```python
# En config/settings.py
UPDATE_MS = 2000  # Milisegundos (2000 = 2 segundos)
```

### Cambiar Tamaño del Historial

```python
# En config/settings.py
HISTORY = 60  # Número de puntos en gráficas
```

### Interfaz de Red Específica

```python
# En config/settings.py
NET_INTERFACE = "eth0"  # O "wlan0", None para auto
```

---

## 🚀 Ejecutar al Inicio del Sistema

### Opción 1: systemd (Recomendado)

Crea `/etc/systemd/system/dashboard.service`:

```ini
[Unit]
Description=System Dashboard
After=graphical.target

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/ruta/a/system_dashboard
Environment="DISPLAY=:0"
ExecStart=/ruta/a/system_dashboard/venv/bin/python main.py
Restart=always

[Install]
WantedBy=graphical.target
```

Luego:
```bash
sudo systemctl enable dashboard.service
sudo systemctl start dashboard.service
```

### Opción 2: Autostart Desktop Entry

Crea `~/.config/autostart/dashboard.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=System Dashboard
Exec=/ruta/a/system_dashboard/venv/bin/python /ruta/a/system_dashboard/main.py
Hidden=false
X-GNOME-Autostart-enabled=true
```

---

## 💡 Tips y Trucos

### Tema Completo
Todos los colores están en un solo lugar (`config/settings.py`). Cambia `COLORS` para personalizar todo el dashboard.

### Añadir Nueva Funcionalidad
El proyecto sigue patrones claros. Mira ventanas existentes como referencia.

### Debugging
Ejecuta con:
```bash
python main.py 2>&1 | tee dashboard.log
```

### Performance
Si el dashboard va lento, aumenta `UPDATE_MS` a 3000 o 5000.

---

## ✨ ¡Disfruta tu Dashboard!

El proyecto está completo y listo para usar. ¡Personalízalo a tu gusto! 🎉
