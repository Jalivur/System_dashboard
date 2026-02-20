# 🖥️ Sistema de Monitoreo y Control - Dashboard v2.5.1

Sistema completo de monitoreo y control para Raspberry Pi con interfaz gráfica DSI, control de ventiladores PWM, temas personalizables, histórico de datos, gestión avanzada del sistema y logging completo.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)
[![Version](https://img.shields.io/badge/Version-2.5.1-orange.svg)]()

---

## ✨ Características Principales

### 🖥️ **Monitoreo Completo del Sistema**
- **CPU**: Uso en tiempo real, frecuencia, gráficas históricas
- **RAM**: Memoria usada/total, porcentaje, visualización dinámica
- **Temperatura**: Monitoreo de CPU con alertas por color
- **Disco**: Espacio usado/disponible, temperatura NVMe, I/O en tiempo real

### 🌡️ **Control Inteligente de Ventiladores**
- **5 Modos**: Auto (curva), Manual, Silent (30%), Normal (50%), Performance (100%)
- **Curvas personalizables**: Define hasta 8 puntos temperatura-PWM
- **Servicio background**: Funciona incluso con ventana cerrada
- **Visualización en vivo**: Gráfica de curva activa y PWM actual

### 🌐 **Monitor de Red Avanzado**
- **Tráfico en tiempo real**: Download/Upload con gráficas
- **Auto-detección**: Interfaz activa (eth0, wlan0, tun0)
- **Lista de IPs**: Todas las interfaces con iconos por tipo
- **Speedtest integrado**: Test de velocidad con resultados instantáneos

### ⚙️ **Monitor de Procesos**
- **Lista en tiempo real**: Top 20 procesos con CPU/RAM
- **Búsqueda inteligente**: Por nombre o comando completo
- **Filtros**: Todos / Usuario / Sistema
- **Terminar procesos**: Con confirmación y feedback

### ⚙️ **Monitor de Servicios systemd**
- **Gestión completa**: Start/Stop/Restart servicios
- **Estado visual**: active, inactive, failed con iconos
- **Autostart**: Enable/Disable con confirmación
- **Logs en tiempo real**: Ver últimas 50 líneas

### 📊 **Histórico de Datos**
- **Recolección automática**: Cada 5 minutos en background
- **Base de datos SQLite**: Ligera y eficiente
- **Visualización gráfica**: CPU, RAM, Temperatura con matplotlib
- **Periodos**: 24 horas, 7 días, 30 días
- **Estadísticas**: Promedios, mínimos, máximos
- **Detección de anomalías**: Alertas automáticas
- **Exportación CSV**: Para análisis externo

### 󱇰 **Monitor USB**
- **Detección automática**: Dispositivos conectados
- **Separación inteligente**: Mouse/teclado vs almacenamiento
- **Expulsión segura**: Unmount + eject con confirmación

###  **Monitor de Disco**
- **Particiones**: Uso de espacio de todas las unidades
- **Temperatura NVMe**: Monitoreo térmico del SSD (smartctl/sysfs)
- **Velocidad I/O**: Lectura/escritura en MB/s

### 󱓞 **Lanzadores de Scripts**
- **Terminal integrada**: Visualiza la ejecución en tiempo real
- **Layout en grid**: Organización visual en columnas
- **Confirmación previa**: Diálogo antes de ejecutar

### 󰆧 **Actualizaciones del Sistema**
- **Verificación al arranque**: En background sin bloquear la UI
- **Sistema de caché 12h**: No repite `apt update` innecesariamente
- **Terminal integrada**: Instala viendo el output en vivo
- **Botón Buscar**: Fuerza comprobación manual

### 󰆧 **15 Temas Personalizables**
- **Cambio con un clic**: Reinicio automático
- **Paletas completas**: Cyberpunk, Matrix, Dracula, Nord, Tokyo Night, etc.
- **Preview en vivo**: Ve los colores antes de aplicar

### /󰿅 **Reinicio y Apagado**
- **Botón Reiniciar**: Reinicia el dashboard aplicando cambios de código
- **Botón Salir**: Salir de la app o apagar el sistema
- **Terminal de apagado**: Visualiza `apagado.sh` en tiempo real
- **Con confirmación**: Evita acciones accidentales

### 📋 **Sistema de Logging Completo**
- **Cobertura total**: Todos los módulos core y UI
- **Niveles diferenciados**: DEBUG, INFO, WARNING, ERROR
- **Rotación automática**: 2MB máximo con backup
- **Ubicación**: `data/logs/dashboard.log`

---

## 📦 Instalación

###  **Requisitos del Sistema**
- **Hardware**: Raspberry Pi 3/4/5
- **OS**: Raspberry Pi OS (Bullseye/Bookworm) o Kali Linux
- **Pantalla**: Touchscreen DSI 4,5" (800x480) o HDMI
- **Python**: 3.8 o superior

### ⚡ **Instalación Recomendada**

Usa el script de instalación directa (sin entorno virtual):

```bash
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard
chmod +x install_system.sh
sudo ./install_system.sh
python3 main.py
```

El script `install_system.sh` instala automáticamente:
- Dependencias del sistema (`lm-sensors`, `usbutils`, `udisks2`)
- Dependencias Python con `--break-system-packages`
- Pregunta si instalar `speedtest-cli`
- Ofrece configurar sensores de temperatura

### 🛠️ **Instalación Manual**

Si prefieres instalar paso a paso:

```bash
# 1. Dependencias del sistema
sudo apt-get update
sudo apt-get install -y lm-sensors usbutils udisks2 smartmontools speedtest-cli

# 2. Detectar sensores
sudo sensors-detect --auto

# 3. Dependencias Python
pip3 install --break-system-packages -r requirements.txt

# 4. Ejecutar
python3 main.py
```

###  **Alternativa con Entorno Virtual**

Si prefieres aislar las dependencias Python:

```bash
chmod +x install.sh
./install.sh
source venv/bin/activate
python3 main.py
```

> **Nota**: Con venv necesitas activar el entorno (`source venv/bin/activate`) cada vez antes de ejecutar.

---

## 󰍜 Menú Principal (13 botones)

```
┌─────────────────────────────────────┐
│  Control         │  Monitor          │
│  Ventiladores    │  Placa            │
├──────────────────┼───────────────────┤
│  Monitor         │  Monitor          │
│  Red             │  USB              │
├──────────────────┼───────────────────┤
│  Monitor         │  Lanzadores       │
│  Disco           │                   │
├──────────────────┼───────────────────┤
│  Monitor         │  Monitor          │
│  Procesos        │  Servicios        │
├──────────────────┼───────────────────┤
│  Histórico       │  Actualizaciones  │
│  Datos           │                   │
├──────────────────┼───────────────────┤
│  Cambiar Tema    │  Reiniciar        │
├──────────────────┼───────────────────┤
│  Salir           │                   │
└──────────────────┴───────────────────┘
```

### **Las 13 Ventanas:**

1. **Control Ventiladores** - Configura modos y curvas PWM
2. **Monitor Placa** - CPU, RAM, temperatura en tiempo real
3. **Monitor Red** - Tráfico, speedtest, interfaces e IPs
4. **Monitor USB** - Dispositivos y expulsión segura
5. **Monitor Disco** - Espacio, temperatura NVMe, I/O
6. **Lanzadores** - Ejecuta scripts con terminal en vivo
7. **Monitor Procesos** - Gestión avanzada de procesos
8. **Monitor Servicios** - Control de servicios systemd
9. **Histórico Datos** - Visualización de métricas históricas
10. **Actualizaciones** - Gestión de paquetes del sistema
11. **Cambiar Tema** - Selecciona entre 15 temas
12. **Reiniciar** - Reinicia el dashboard
13. **Salir** - Cierra la app o apaga el sistema

---

## 󰔎 Temas Disponibles

| Tema | Colores | Estilo |
|------|---------|--------|
| **Cyberpunk** | Cyan + Verde | Original neón |
| **Matrix** | Verde brillante | Película Matrix |
| **Sunset** | Naranja + Púrpura | Atardecer cálido |
| **Ocean** | Azul + Aqua | Océano refrescante |
| **Dracula** | Púrpura + Rosa | Elegante oscuro |
| **Nord** | Azul hielo | Minimalista nórdico |
| **Tokyo Night** | Azul + Púrpura | Noche de Tokio |
| **Monokai** | Cyan + Verde | IDE clásico |
| **Gruvbox** | Naranja + Beige | Retro cálido |
| **Solarized** | Azul + Cyan | Científico |
| **One Dark** | Azul claro | Atom editor |
| **Synthwave** | Rosa + Verde | Neón 80s |
| **GitHub Dark** | Azul GitHub | Profesional |
| **Material** | Azul material | Google Design |
| **Ayu Dark** | Azul cielo | Minimalista |

---

## 📊 Arquitectura del Proyecto

```
system_dashboard/
├── config/
│   ├── settings.py                 # Constantes globales y LAUNCHERS
│   └── themes.py                   # 15 temas pre-configurados
├── core/
│   ├── fan_controller.py           # Control PWM y curvas
│   ├── fan_auto_service.py         # Servicio background ventiladores
│   ├── system_monitor.py           # CPU, RAM, temperatura
│   ├── network_monitor.py          # Red, speedtest, interfaces
│   ├── disk_monitor.py             # Disco, NVMe, I/O
│   ├── process_monitor.py          # Gestión de procesos
│   ├── service_monitor.py          # Servicios systemd
│   ├── update_monitor.py           # Actualizaciones con caché 12h
│   ├── data_logger.py              # SQLite logging
│   ├── data_analyzer.py            # Análisis histórico
│   ├── data_collection_service.py  # Recolección automática (singleton)
│   └── __init__.py
├── ui/
│   ├── main_window.py              # Ventana principal (13 botones)
│   ├── styles.py                   # Estilos y botones
│   ├── widgets/
│   │   ├── graphs.py               # Gráficas personalizadas
│   │   └── dialogs.py              # custom_msgbox, confirm_dialog, terminal_dialog
│   └── windows/
│       ├── monitor.py, network.py, usb.py, disk.py
│       ├── process_window.py, service.py, history.py
│       ├── update.py, fan_control.py
│       ├── launchers.py, theme_selector.py
│       └── __init__.py
├── utils/
│   ├── file_manager.py             # Gestión de JSON (escritura atómica)
│   ├── system_utils.py             # Utilidades del sistema
│   └── logger.py                   # DashboardLogger (rotación 2MB)
├── data/                            # Auto-generado al ejecutar
│   ├── fan_state.json, fan_curve.json, theme_config.json
│   ├── history.db                  # SQLite histórico
│   └── logs/dashboard.log          # Log del sistema
├── scripts/                         # Scripts personalizados del usuario
├── install_system.sh               # Instalación directa (recomendada)
├── install.sh                      # Instalación con venv (alternativa)
├── test_logging.py                 # Prueba del sistema de logging
├── main.py
└── requirements.txt
```

---

##  Configuración

### **`config/settings.py`**

```python
# Posición en pantalla DSI
DSI_WIDTH = 800
DSI_HEIGHT = 480
DSI_X = 0
DSI_Y = 0

# Scripts personalizados en Lanzadores
LAUNCHERS = [
    {"label": "Montar NAS",   "script": str(SCRIPTS_DIR / "montarnas.sh")},
    {"label": "Conectar VPN", "script": str(SCRIPTS_DIR / "conectar_vpn.sh")},
    # Añade tus scripts aquí
]
```

---

## 📋 Sistema de Logging

```bash
# Ver logs en tiempo real
tail -f data/logs/dashboard.log

# Solo errores
grep ERROR data/logs/dashboard.log

# Eventos de hoy
grep "$(date +%Y-%m-%d)" data/logs/dashboard.log
```

**Niveles:** `DEBUG` (operaciones normales) · `INFO` (eventos importantes) · `WARNING` (degradación) · `ERROR` (fallos)

---

## 📈 Rendimiento

- **Uso CPU**: ~5-10% en idle
- **Uso RAM**: ~100-150 MB
- **Base de datos**: ~5 MB por 10,000 registros
- **Actualización UI**: 2 segundos (configurable en `UPDATE_MS`)
- **Threads background**: 3 (main + FanAuto + DataCollection)
- **Log**: máx. 2MB con rotación automática

---

##  Troubleshooting

| Problema | Solución |
|----------|----------|
| No arranca | `pip3 install --break-system-packages -r requirements.txt` |
| Temperatura 0 | `sudo sensors-detect --auto && sudo systemctl restart lm-sensors` |
| NVMe temp 0 | `sudo apt install smartmontools` |
| Ventiladores no responden | `sudo python3 main.py` |
| Speedtest falla | `sudo apt install speedtest-cli` |
| USB no expulsa | `sudo apt install udisks2` |
| Ver qué falla | `grep ERROR data/logs/dashboard.log` |

---

## 📚 Documentación

- [QUICKSTART.md](QUICKSTART.md) — Inicio rápido
- [INSTALL_GUIDE.md](INSTALL_GUIDE.md) — Instalación detallada
- [THEMES_GUIDE.md](THEMES_GUIDE.md) — Guía de temas
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) — Integración con OLED
- [INDEX.md](INDEX.md) — Índice completo

---

## 📊 Estadísticas del Proyecto

| Métrica | Valor |
|---------|-------|
| Versión | 2.5.1 |
| Archivos Python | 41 |
| Líneas de código | ~12,500 |
| Ventanas | 13 |
| Temas | 15 |
| Servicios background | 2 (FanAuto + DataCollection) |
| Cobertura logging | 100% módulos core y UI |

---

## Changelog

### **v2.5.1** - 2026-02-19 ⭐ ACTUAL
- ✅ **NUEVO**: Sistema de logging completo en todos los módulos core y UI
- ✅ **NUEVO**: Ventana Actualizaciones con terminal integrada y caché 12h
- ✅ **NUEVO**: Comprobación de actualizaciones al arranque en background
- ✅ **NUEVO**: `terminal_dialog` con callback `on_close`
- ✅ **FIX**: Bug `atexit` en `DataCollectionService` (se detenía a los 3s del arranque)
- ✅ **FIX**: Apagado usa `terminal_dialog` en lugar de subprocess silencioso
- ✅ **MEJORA**: `update_monitor` con caché 12h y parámetro `force`

### **v2.5** - 2026-02-17
- ✅ Monitor de Servicios systemd, Histórico de Datos SQLite, Botón Reiniciar
- ✅ Recolección automática background, Exportación CSV, Detección de anomalías

### **v2.0** - 2026-02-16
- ✅ Monitor de Procesos, 15 temas, fix Speedtest Mbit/s → MB/s

### **v1.0** - 2025-01
- ✅ Release inicial, 8 ventanas, control ventiladores, tema Cyberpunk

---

## Licencia

MIT License

---

## Agradecimientos

**CustomTkinter** · **psutil** · **matplotlib** · **Raspberry Pi Foundation**

---

**Dashboard v2.5.1: Profesional, Completo, Monitoreado** 
