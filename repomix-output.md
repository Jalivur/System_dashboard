This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: README.md, IDEAS_EXPANSION.md, INDEX.md, QUICKSTART.md
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
IDEAS_EXPANSION.md
INDEX.md
QUICKSTART.md
README.md
```

# Files

## File: QUICKSTART.md
````markdown
# 🚀 Inicio Rápido - Dashboard v4.0

---

## ⚡ Instalación (2 Comandos)

```bash
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard
chmod +x install_system.sh
sudo ./install_system.sh
python3 main.py
```

El script instala automáticamente las dependencias del sistema y Python, la CLI oficial de Ookla para speedtest, y pregunta si quieres configurar sensores de temperatura.

---

## 🔁 Alternativa con Entorno Virtual

```bash
chmod +x install.sh
./install.sh
source venv/bin/activate
python3 main.py
```

> Recuerda activar el entorno (`source venv/bin/activate`) cada vez que quieras ejecutar.

---

## 📋 Requisitos Mínimos

- ✅ Raspberry Pi 3/4/5
- ✅ Raspberry Pi OS (cualquier versión)
- ✅ Python 3.8+
- ✅ Conexión a internet (para instalación)

---

## 🖥️ Config por máquina (multi-Pi)

Si tienes varias Pi con configuraciones distintas, crea `config/local_settings.py` (en `.gitignore`, no se sube a git):

```python
# Ejemplo Pi 3B+ con Xvfb
DSI_X = 0
DSI_Y = 0
DSI_WIDTH = 1024
DSI_HEIGHT = 762
```

También puedes editarlo directamente desde la UI con el **Editor de Configuración**.

---

## 🗂️ Menú por Pestañas (v4.0)

El menú está organizado en **6 pestañas con scroll horizontal táctil**. Cada pestaña agrupa los botones por categoría:

| Pestaña | Botones |
|---------|---------|
| **Sistema** | Resumen, Monitor Placa, Control Ventiladores, LEDs RGB, Brillo, Cámara, Lanzadores |
| **Red** | Monitor Red, Red Local, Pi-hole, VPN, Homebridge, Monitor WiFi |
| **Hardware** | Info Hardware, Monitor Disco, Monitor USB |
| **Servicios** | Monitor Servicios, Servicios Dashboard, Monitor Procesos, Gestor Crontab, Actualizaciones |
| **Registros** | Visor Logs, Histórico Datos, Historial Alertas, Monitor SSH |
| **Config** | Editor Config, Cambiar Tema, Gestor Botones |

El **footer** (Gestor Botones, Reiniciar, Salir) es siempre visible independientemente de la pestaña activa.

> Puedes ocultar botones que no uses con el **Gestor de Botones**.

---

## 🖥️ Las 27 Ventanas

**1. Info Hardware** — Modelo, revision, SoC, RAM, almacenamiento, uptime

**2. Control Ventiladores** — Modo Auto/Manual/Silent/Normal/Performance, curvas PWM

**3. LEDs RGB** — 6 modos (auto, apagado, color fijo, secuencial, respiración, arcoíris)

**4. Monitor Placa** — CPU, RAM, temperatura, temperatura chasis, fan duty real

**5. Monitor Red** — Download/Upload, speedtest Ookla, lista de IPs

**6. Monitor USB** — Dispositivos conectados, expulsión segura

**7. Monitor Disco** — Espacio, temperatura NVMe, velocidad I/O, SMART extendido

**8. Lanzadores** — Scripts personalizados con terminal en vivo

**9. Monitor Procesos** — Top 20 procesos, búsqueda, matar procesos

**10. Monitor Servicios** — Start/Stop/Restart systemd, ver logs

**11. Servicios Dashboard** — Activar/desactivar servicios background del dashboard

**12. Gestor Crontab** — Ver/añadir/editar/eliminar entradas del crontab por usuario

**13. Histórico Datos** — 8 gráficas CPU/RAM/Temp/Red/Disco/PWM en 24h, 7d, 30d

**14. Actualizaciones** — Estado de paquetes, instalar con terminal integrada

**15. Homebridge** — Control de 5 tipos de dispositivos HomeKit

**16. Visor de Logs** — Filtros por nivel, módulo, texto e intervalo; exportación

**17. Red Local** — Escáner arp-scan con IP, MAC y fabricante

**18. Pi-hole** — Estadísticas de bloqueo DNS en tiempo real (solo v6)

**19. Gestor VPN** — Estado, badge en menú, conectar/desconectar

**20. Historial Alertas** — Registro persistente de alertas Telegram enviadas

**21. Brillo Pantalla** — Control brillo DSI, modo ahorro, encendido/apagado

**22. Resumen Sistema** — Vista unificada de todas las métricas (ideal como reposo)

**23. Cámara / Escáner OCR** — Foto con OV5647 + OCR Tesseract local

**24. Cambiar Tema** — 15 temas (Cyberpunk, Matrix, Dracula, Nord...)

**25. Monitor SSH** — Sesiones activas e historial SSH con textos legibles

**26. Monitor WiFi** — Señal dBm, calidad, SSID, bitrate, tráfico RX/TX

**27. Editor Config** — Edita `local_settings.py` con preview de iconos en tiempo real

---

## 🔧 Configuración Básica

### Ajustar posición en pantalla:
Edita `config/settings.py` o usa el **Editor de Configuración** directamente desde la UI:
```python
DSI_X = 0
DSI_Y = 0
DSI_WIDTH = 800
DSI_HEIGHT = 480
```

### Añadir scripts en Lanzadores:
```python
LAUNCHERS = [
    {"label": "Mi Script", "script": str(SCRIPTS_DIR / "mi_script.sh")},
]
```

---

## 🏠 Configurar Homebridge

```env
HOMEBRIDGE_HOST=192.168.1.X
HOMEBRIDGE_PORT=8581
HOMEBRIDGE_USER=admin
HOMEBRIDGE_PASS=tu_contraseña
```

> Activa el **Insecure Mode** en Homebridge.

---

## 📲 Configurar Alertas Telegram

```env
TELEGRAM_TOKEN=123456789:ABCdefGHI...
TELEGRAM_CHAT_ID=987654321
```

---

## 📋 Ver Logs del Sistema

```bash
tail -f data/logs/dashboard.log
grep ERROR data/logs/dashboard.log
```

---

## ❓ Problemas Comunes

| Problema | Solución |
|----------|----------|
| No arranca | `pip3 install --break-system-packages -r requirements.txt` |
| Temperatura 0 | `sudo sensors-detect --auto` |
| NVMe temp 0 | `sudo apt install smartmontools` |
| Speedtest falla | Instalar CLI Ookla: `sudo apt install speedtest` |
| USB no expulsa | `sudo apt install udisks2` |
| Homebridge no conecta | Revisar `.env` y activar Insecure Mode |
| WiFi no muestra datos | `sudo apt install wireless-tools` |
| SSH monitor vacío | Verificar que `who` y `last` funcionan en el sistema |
| No puedo escribir en entries (VNC) | Verificar que se usa `make_entry()` de `ui/styles.py` |
| Foco perdido tras inactividad (Wayland) | `gsettings set org.gnome.desktop.session idle-delay 0` |
| Dashboard no visible por VNC en Pi 5 | `wayvnc --output=DSI-2 0.0.0.0 5901` |
| Ver qué falla | `grep ERROR data/logs/dashboard.log` |

---

## 📚 Más Información

**[README.md](README.md)** — Documentación completa
**[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** — Instalación detallada
**[INDEX.md](INDEX.md)** — Índice de toda la documentación

---

**Dashboard v4.0** 🚀
````

## File: README.md
````markdown
# 🖥️ Sistema de Monitoreo y Control - Dashboard v4.0

Sistema completo de monitoreo y control para Raspberry Pi con interfaz gráfica DSI, menú por pestañas con scroll táctil, control de ventiladores PWM, temas personalizables, histórico de datos, gestión avanzada del sistema, integración con Homebridge, alertas externas por Telegram, escáner de red local, integración Pi-hole, gestor VPN, control de brillo, pantalla de resumen, LEDs RGB inteligentes, alertas de audio con voz TTS, cámara con OCR, SMART extendido de NVMe, monitor WiFi, monitor SSH y editor de configuración local.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)
[![Version](https://img.shields.io/badge/Version-4.0-orange.svg)]()

---

## ✨ Características Principales

### 🗂️ **Menú por Pestañas con Scroll Táctil** *(v4.0)*
- **6 pestañas categorizadas**: Sistema, Red, Hardware, Servicios, Registros, Config
- **Scroll horizontal táctil** en la barra de pestañas — ancho fijo 130px por pestaña, escala a cualquier número sin encoger
- **Footer siempre visible**: Gestor Botones, Reiniciar, Salir — accesibles desde cualquier pestaña
- Pestañas definidas en `config/settings.py → class UI` — añadir una pestaña nueva es solo una línea de configuración

### 🖥️ **Monitoreo Completo del Sistema**
- **CPU**: Uso en tiempo real, frecuencia, gráficas históricas
- **RAM**: Memoria usada/total, porcentaje, visualización dinámica
- **Temperatura**: Monitoreo de CPU con alertas por color
- **Disco**: Espacio usado/disponible, temperatura NVMe, I/O en tiempo real

### 🪟 **UI Unificada con Header Táctil**
- **Header en todas las ventanas**: título + status dinámico + botón ✕ (52×42px táctil)
- **Status en tiempo real** en el header: CPU/RAM/Temp (Monitor Placa), Disco/NVMe (Monitor Disco), interfaz/velocidades (Monitor Red)
- Función `make_window_header()` centralizada en `ui/styles.py`

### 🌡️ **Control Inteligente de Ventiladores**
- **5 Modos**: Auto (curva), Manual, Silent (30%), Normal (50%), Performance (100%)
- **Curvas personalizables**: Define hasta 8 puntos temperatura-PWM
- **Servicio background**: Funciona incluso con ventana cerrada

### 🌐 **Monitor de Red Avanzado**
- **Tráfico en tiempo real**: Download/Upload con gráficas
- **Auto-detección**: Interfaz activa (eth0, wlan0, tun0)
- **Speedtest integrado**: CLI oficial de Ookla

### 󰖩 **Monitor WiFi** *(v3.8)*
- Señal en tiempo real: dBm, calidad de enlace, SSID, bitrate
- Barras visuales de señal (▂▄▆█) y gráfica histórica
- Tráfico RX/TX con gráficas independientes

### **Monitor SSH** *(v3.8)*
- Sesiones activas en tiempo real con IP de origen y hora de conexión
- Historial con duración formateada y detección de cortes
- Textos legibles: `pts/0` → `Sesión 1`, IPs locales etiquetadas

### 🔧 **Editor de Configuración** *(v3.8)*
- Edita `config/local_settings.py` por máquina sin tocar `settings.py`
- Parámetros editables: pantalla, tiempos, umbrales CPU/Temp/RAM/Red
- Iconos editables con preview en tiempo real, merge inteligente

### 🖧 **Escáner de Red Local**
- Escaneo con arp-scan: IP, MAC y fabricante (OUI lookup)
- Auto-refresco cada 60s en background

### 🕳️ **Integración Pi-hole v6**
- API v6 nativa, estadísticas en tiempo real
- Badge en menú: 🔴 si Pi-hole está offline

### 📲 **Alertas Externas por Telegram**
- Sin dependencias nuevas: usa `urllib` de stdlib
- Anti-spam: edge-trigger + sustain de 60s

### 🏠 **Integración Homebridge Extendida**
- 5 tipos de dispositivo: switch, luz, termostato, sensor, persiana
- 3 badges en el menú: offline, encendidos, con fallo

### ⚙️ **Monitor de Servicios systemd**
- Gestión completa: Start/Stop/Restart, estado visual, logs en tiempo real

### ⚙️ **Servicios Dashboard** *(v3.5/v3.6)*
- ServiceRegistry: registro centralizado de todos los servicios
- ServicesManagerWindow: activar/desactivar servicios desde la UI

### 🔧 **Gestor de Botones del Menú** *(v3.6.5)*
- Mostrar/ocultar botones del menú principal por máquina

### 🕐 **Gestor de Crontab** *(v3.7)*
- Ver, añadir, editar y eliminar entradas del crontab
- Selector de usuario: usuario / root

### 📊 **Histórico de Datos**
- Recolección automática cada 5 minutos en background (SQLite)
- 8 gráficas en 24h, 7d, 30d con exportación CSV

### 🔒 **Gestor de Conexiones VPN**
- Estado en tiempo real, badge en menú, conectar/desconectar
- Compatible con WireGuard y OpenVPN

### 💡 **Control LEDs RGB**
- 6 modos: auto, apagado, color fijo, secuencial, respiración, arcoíris

### 🔊 **Alertas de Audio**
- Voz TTS en español con `espeak-ng` + tono sintético
- 11 archivos .wav

### 📷 **Cámara + Escáner OCR**
- Cámara OV5647 via `rpicam-still`, OCR con Tesseract local

### 󰔎 **15 Temas Personalizables**
- Cambio con un clic, preview en vivo

---

## 🖥️ Soporte Multi-máquina

`config/local_settings.py` (en `.gitignore`) permite configuración independiente por máquina sin tocar git. El **Editor de Configuración** genera y mantiene este fichero desde la propia UI.

### Pi 5 (pantalla DSI física + Wayland)
- Compositor: **labwc** sobre Wayland
- Acceso remoto: `wayvnc --output=DSI-2 0.0.0.0 5901`
- Resolución DSI: 800×480
- Idle desactivado: `gsettings set org.gnome.desktop.session idle-delay 0`

### Pi 3B+ (sin pantalla física + X11)
- Display virtual `:1` con **Xvfb**
- Acceso remoto: x11vnc en puerto `5901` sobre `:1`
- `local_settings.py`: `DSI_X=0, DSI_Y=0, DSI_WIDTH=1024, DSI_HEIGHT=762`

---

## 📦 Instalación

### ⚡ Instalación Recomendada

```bash
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard
chmod +x install_system.sh
sudo ./install_system.sh
python3 main.py
```

### 🛠️ Instalación Manual

```bash
sudo apt-get update
sudo apt-get install -y lm-sensors usbutils udisks2 smartmontools arp-scan wireless-tools

# CLI oficial de Ookla (speedtest)
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
sudo apt-get install speedtest

sudo sensors-detect --auto
pip3 install --break-system-packages -r requirements.txt

echo "$(whoami) ALL=(ALL) NOPASSWD: /usr/sbin/arp-scan" | sudo tee /etc/sudoers.d/arp-scan
echo "$(whoami) ALL=(ALL) NOPASSWD: /usr/bin/smartctl"  | sudo tee /etc/sudoers.d/smartctl

# Hardware FNK0100K — cámara y OCR (opcional)
sudo apt install rpicam-apps tesseract-ocr tesseract-ocr-spa espeak-ng
pip install pytesseract --break-system-packages

python3 main.py
```

---

## 📊 Arquitectura del Proyecto (v4.0)

```
system_dashboard/
├── config/
│   ├── settings.py                 # Constantes globales + class Icons + class UI (pestañas)
│   ├── button_labels.py            # Labels de botones (fuente única de verdad)
│   ├── themes.py                   # 15 temas pre-configurados
│   ├── services.json               # Config servicios y UI (auto-generado, en .gitignore)
│   └── local_settings.py           # Overrides por máquina (en .gitignore)
├── core/
│   ├── service_registry.py
│   ├── system_monitor.py
│   ├── fan_controller.py, fan_auto_service.py
│   ├── network_monitor.py, network_scanner.py
│   ├── disk_monitor.py, process_monitor.py
│   ├── service_monitor.py, update_monitor.py
│   ├── homebridge_monitor.py, pihole_monitor.py
│   ├── alert_service.py, led_service.py
│   ├── hardware_monitor.py, audio_alert_service.py
│   ├── display_service.py, vpn_monitor.py
│   ├── crontab_service.py, camera_service.py
│   ├── ssh_monitor.py, wifi_monitor.py
│   ├── data_logger.py, data_analyzer.py
│   ├── data_collection_service.py, cleanup_service.py
│   └── hardware_info_monitor.py
├── ui/
│   ├── main_window.py              # Layout, pestañas, coordinación (~450 líneas)
│   ├── main_badges.py              # BadgeManager — crear y actualizar badges *(v4.0)*
│   ├── main_update_loop.py         # UpdateLoop — reloj, uptime, loop de badges *(v4.0)*
│   ├── main_system_actions.py      # exit_application, restart_application *(v4.0)*
│   ├── window_lifecycle.py         # WindowLifecycleManager *(v4.0)*
│   ├── window_manager.py           # Visibilidad botones via JSON, patrón callback
│   ├── styles.py
│   ├── widgets/
│   │   ├── graphs.py
│   │   └── dialogs.py
│   └── windows/
│       └── (una ventana por fichero — 27 ventanas)
├── utils/
│   ├── file_manager.py, system_utils.py, logger.py
├── data/                           # Auto-generado al ejecutar
├── scripts/
│   ├── sounds/
│   └── generate_sounds.py
├── .env, .env.example
├── install_system.sh, install.sh
├── main.py
└── requirements.txt
```

### Módulos ui/ (v4.0)

| Fichero | Responsabilidad |
|---------|----------------|
| `main_window.py` | Layout, pestañas, coordinación (~450 líneas) |
| `main_badges.py` | `BadgeManager`: crear y actualizar badges de menú |
| `main_update_loop.py` | `UpdateLoop`: reloj, uptime, loop de badges |
| `main_system_actions.py` | `exit_application`, `restart_application` |
| `window_lifecycle.py` | `WindowLifecycleManager`: ciclo de vida ventanas hijas |
| `window_manager.py` | Visibilidad de botones via JSON, patrón callback |

---

## 🗂️ Menú por Pestañas (v4.0)

El menú está organizado en 6 pestañas con scroll horizontal táctil. La configuración vive en `config/settings.py → class UI`:

| Pestaña | Contenido |
|---------|-----------|
| **Sistema** | Resumen, Monitor Placa, Control Ventiladores, LEDs RGB, Brillo, Cámara, Lanzadores |
| **Red** | Monitor Red, Red Local, Pi-hole, VPN, Homebridge, Monitor WiFi |
| **Hardware** | Info Hardware, Monitor Disco, Monitor USB |
| **Servicios** | Monitor Servicios, Servicios Dashboard, Monitor Procesos, Gestor Crontab, Actualizaciones |
| **Registros** | Visor Logs, Histórico Datos, Historial Alertas, Monitor SSH |
| **Config** | Editor Config, Cambiar Tema, Gestor Botones |

> El footer (Gestor Botones, Reiniciar, Salir) es fijo y visible desde cualquier pestaña.

---

## 🔗 Relación fase1.py ↔ Dashboard

`fase1.py` es un proceso independiente que corre en paralelo. Comunicación exclusivamente via JSON:

| Fichero | Quién escribe | Quién lee |
|---------|--------------|-----------|
| `data/fan_state.json` | Dashboard (`FanController`) | `fase1.py` |
| `data/led_state.json` | Dashboard (`LedService`) | `fase1.py` |
| `data/hardware_state.json` | `fase1.py` | Dashboard (`HardwareMonitor`) |

El hardware I²C del módulo Expansion Freenove (ventiladores, LEDs, OLED) es **exclusivo de fase1.py** — nunca se accede desde el dashboard.

---

## 🏠 Configuración de Homebridge

```env
HOMEBRIDGE_HOST=192.168.1.X
HOMEBRIDGE_PORT=8581
HOMEBRIDGE_USER=admin
HOMEBRIDGE_PASS=tu_contraseña
```

---

## 🕳️ Configuración de Pi-hole

```env
PIHOLE_HOST=192.168.1.X
PIHOLE_PORT=80
PIHOLE_PASSWORD=tu_contraseña
```

> Compatible exclusivamente con **Pi-hole v6**.

---

## 📲 Configuración de Alertas Telegram

```env
TELEGRAM_TOKEN=123456789:ABCdefGHI...
TELEGRAM_CHAT_ID=987654321
```

---

## 🔧 Troubleshooting

| Problema | Solución |
|----------|----------|
| No arranca | `pip3 install --break-system-packages -r requirements.txt` |
| Temperatura 0 | `sudo sensors-detect --auto && sudo systemctl restart lm-sensors` |
| NVMe temp 0 | `sudo apt install smartmontools` |
| Speedtest falla | Instalar CLI oficial Ookla |
| USB no expulsa | `sudo apt install udisks2` |
| Homebridge no conecta | Verificar `.env` y activar Insecure Mode |
| Red Local no escanea | `sudo apt install arp-scan` y configurar sudoers |
| Pi-hole no conecta | Verificar `.env`; solo compatible con v6 |
| WiFi no muestra datos | `sudo apt install wireless-tools` |
| SSH monitor vacío | Verificar que `who` y `last` funcionan en el sistema |
| No puedo escribir en entries (VNC) | Verificar que se usa `make_entry()` de `ui/styles.py` |
| Foco perdido tras inactividad (Wayland) | `gsettings set org.gnome.desktop.session idle-delay 0` |
| Dashboard no visible por VNC en Pi 5 | `wayvnc --output=DSI-2 0.0.0.0 5901` |
| Audio no suena | `aplay -l` → verificar dispositivo HDMI |
| Cámara no encontrada | `sudo apt install rpicam-apps` |
| Ver qué falla | `grep ERROR data/logs/dashboard.log` |

---

## 📚 Documentación

- [QUICKSTART.md](QUICKSTART.md) — Inicio rápido
- [INSTALL_GUIDE.md](INSTALL_GUIDE.md) — Instalación detallada
- [THEMES_GUIDE.md](THEMES_GUIDE.md) — Guía de temas
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) — Integración con fase1.py / OLED
- [COMPATIBILIDAD.md](COMPATIBILIDAD.md) — Compatibilidad multiplataforma
- [IDEAS_EXPANSION.md](IDEAS_EXPANSION.md) — Roadmap y backlog
- [INDEX.md](INDEX.md) — Índice completo

---

## 📊 Estadísticas del Proyecto

| Métrica | v3.8 | v4.0 |
|---------|------|------|
| Versión | 3.8 | **4.0** |
| Archivos Python | 68 | **73** |
| Ventanas | 27 | 27 |
| Temas | 15 | 15 |
| Badges en menú | 12 | 12 |
| Servicios background | 16 | 16 |
| Módulos ui/main_* | 1 | **5** |
| Documentos | 9 | 9 |

---

## Changelog

### **v4.0** - 2026-03-05 ⭐ ACTUAL — Refactorización Arquitectural

- ✅ **NUEVO**: Menú por pestañas con scroll horizontal táctil — 6 pestañas (Sistema, Red, Hardware, Servicios, Registros, Config), ancho fijo 130px táctil, scroll automático al añadir más
- ✅ **NUEVO**: `WindowLifecycleManager` (`ui/window_lifecycle.py`) — elimina 27 métodos `open_*` de `main_window.py`, unifica ciclo de vida de todas las ventanas hijas
- ✅ **NUEVO**: `BadgeManager` (`ui/main_badges.py`) — gestión de badges extraída de `main_window.py`
- ✅ **NUEVO**: `UpdateLoop` (`ui/main_update_loop.py`) — loops de reloj y badges extraídos
- ✅ **NUEVO**: `main_system_actions.py` — `exit_application` y `restart_application` extraídos
- ✅ **REFACTOR**: `main_window.py` 891 → 451 líneas (−49%), solo layout y coordinación
- ✅ **REFACTOR**: `WindowManager` — patrón callback (`set_rerender_callback`) en lugar de reGrid directo
- ✅ **REFACTOR**: `config/settings.py → class UI` — pestañas como configuración pura (`MENU_COLUMNS`, `MENU_TABS`)

### **v3.8** - 2026-03-XX
- ✅ Monitor WiFi (`WiFiMonitor` + `WiFiWindow`)
- ✅ Monitor SSH (`SSHMonitor` + `SSHWindow`)
- ✅ Editor de Configuración (`ConfigEditorWindow`)
- ✅ Refactor arquitectónico: `crontab_service.py` y `camera_service.py` a `core/`
- ✅ Fix `RuntimeError` al salir — `StringVar`/`IntVar` con `master=` explícito

### **v3.7** - 2026-03-02
- ✅ Gestor Crontab, fix grab modal, `make_entry()`, soporte dual-Pi

### **v3.6.5** - 2026-02-XX
- ✅ Gestor de Botones (`ButtonManagerWindow` + `WindowManager`)

### **v3.6** - 2026-02-XX
- ✅ Servicios Dashboard (`ServicesManagerWindow`)

### **v3.5** - 2026-02-XX
- ✅ `ServiceRegistry`

### **v3.4** - 2026-02-27
- ✅ LEDs RGB, temperatura chasis, alertas audio, cámara OCR, SMART NVMe extendido

### **v3.3** - 2026-02-27
- ✅ Resumen Sistema, control brillo DSI, gestor VPN

### **v3.2** - 2026-02-27
- ✅ Escáner red local, Pi-hole v6, historial alertas

### **v3.1** - 2026-02-26
- ✅ Alertas Telegram, Homebridge extendido (5 tipos)

### **v3.0** - 2026-02-26
- ✅ Visor de Logs

### v2.x
- Monitor completo, servicios systemd, histórico SQLite, 15 temas, badges

### v1.0 - 2025-01
- Release inicial

---

## Licencia

MIT License

---

## Agradecimientos

CustomTkinter · psutil · matplotlib · Ookla Speedtest CLI · Homebridge · Pi-hole · Raspberry Pi Foundation
````

## File: IDEAS_EXPANSION.md
````markdown
# 💡 IDEAS_EXPANSION.md
## Expansión y Roadmap — Sistema de Monitoreo v4.0

---

## ✅ Implementado

### v4.0 (actual) — Refactorización Arquitectural

- **Menú por pestañas con scroll horizontal táctil**
  - 6 pestañas categorizadas: Sistema, Red, Hardware, Servicios, Registros, Config
  - Ancho fijo 130px por pestaña — táctil, escala sin límite
  - Footer fijo (Gestor Botones, Reiniciar, Salir) visible desde cualquier pestaña
  - Pestañas definidas en `config/settings.py → class UI` — configuración pura

- **`WindowLifecycleManager`** (`ui/window_lifecycle.py`)
  - Elimina 27 métodos `open_*` dispersos en `main_window.py`
  - Ciclo de vida unificado: factory, lift, `_btn_active`/`_btn_idle`, bind `<Destroy>`
  - Registro en una línea por ventana: `r("clave", BL.LABEL, lambda: Ventana(...))`

- **Modularización de `main_window.py`** (891 → 451 líneas, −49%)
  - `ui/main_badges.py` — `BadgeManager`: crear y actualizar badges
  - `ui/main_update_loop.py` — `UpdateLoop`: reloj, uptime, loop de badges
  - `ui/main_system_actions.py` — `exit_application`, `restart_application`

- **`WindowManager` refactorizado** — patrón callback (`set_rerender_callback`) en lugar de reGrid directo

### v3.8 — SSH + WiFi + Config Editor + Refactors

- **Monitor SSH** (`SSHMonitor` + `SSHWindow`)
  - Sesiones activas en tiempo real con IP de origen, usuario y hora de conexión
  - Historial de sesiones con duración formateada (`1h 30min`, `15 min`)
  - Textos humanizados: `pts/0` → `Sesión 1`, IPs locales etiquetadas como `(red local)`

- **Monitor WiFi** (`WiFiMonitor` + `WiFiWindow`)
  - Señal en tiempo real: SSID, dBm, calidad de enlace, bitrate
  - Barras visuales de señal (▂▄▆█) y gráfica histórica
  - Tráfico RX/TX con gráficas independientes

- **Editor de Configuración** (`ConfigEditorWindow`)
  - Edita `config/local_settings.py` por máquina sin tocar `settings.py`
  - Iconos editables con preview en tiempo real, merge inteligente

- **Refactor arquitectónico**
  - `core/crontab_service.py` y `core/camera_service.py` extraídos de UI a `core/`
  - Fix `StringVar`/`IntVar` con `master=` explícito — elimina `RuntimeError` al salir

### v3.7 — Crontab + Fixes + Multi-Pi
- **Gestor Crontab** — ver/añadir/editar/eliminar entradas crontab, selector usuario/root
- **Fix grab modal** — `grab_release()` garantizado al cerrar diálogos
- **`make_entry()`** — soluciona escritura en VNC con `overrideredirect(True)`
- **Soporte dual-Pi** — `config/local_settings.py`, Pi 3B+ Xvfb + Pi 5 Wayland

### v3.6.5
- **Gestor de Botones** (`ButtonManagerWindow` + `WindowManager`) — persistencia en `services.json`

### v3.6
- **Servicios Dashboard** (`ServicesManagerWindow`) — persistencia en `services.json`

### v3.5
- **ServiceRegistry** — registro centralizado de todos los servicios del dashboard

### v3.4 — Hardware FNK0100K
- **LEDs RGB inteligentes** — 6 modos, sin destellos
- **Temperatura chasis + Fan duty real** — via `hardware_state.json`
- **Alertas de audio** — 11 .wav, TTS español, 4 métricas
- **Cámara OV5647 + Escáner OCR** — Tesseract local
- **NVMe SMART extendido** — TBW, horas, ciclos, % vida útil

### v3.3
- **Resumen del Sistema** (`OverviewWindow`)
- **Control de Brillo DSI** (`DisplayService` + `DisplayWindow`)
- **Gestor VPN** (`VpnMonitor` + `VpnWindow`)

### v3.2
- **Escáner Red Local** (`NetworkScanner`) — arp-scan
- **Pi-hole v6** (`PiholeMonitor`) — API v6
- **Historial de Alertas** (`AlertHistoryWindow`)

### v3.1
- **Alertas Telegram**, Homebridge extendido — 5 tipos de dispositivo

### v3.0
- Visor de Logs con filtros y exportación

### v2.x
- Control Ventiladores PWM, monitores completos, 15 temas, badges, logging, SQLite

---

## 🔄 Ideas en evaluación para v4.1

### 🎵 Audio Monitor / Control
- Control de volumen ALSA desde la UI (jack + óptico del kit Freenove)
- Sin dependencias nuevas (`subprocess amixer/aplay`)
- Más simple de implementar — recomendado como primera feature v4.1

### 🌦️ Widget de Clima
- Open-Meteo (sin clave API, gratuita)
- Temperatura exterior + previsión 3 días
- Independiente del resto del sistema

### 🔌 I²C Scanner
- `smbus2` en modo solo lectura
- Detecta dispositivos conectados al bus I²C del Pi
- Seguro — no interfiere con fase1.py

### ⚡ GPIO Monitor / Control
- `gpiozero` — requiere planificación previa de pines libres
- Más complejo: inventariar pines ya usados por fase1.py antes de implementar

### 🌐 API REST local
- Endpoint `/status` en JSON — `http.server` de stdlib, sin deps nuevas
- Permitiría integración con otros sistemas de la red

### 💾 Backup automático de configuración
- Copiar `data/` a NAS o USB al detectar dispositivo montado
- Restauración desde la UI

---

## 💭 Ideas futuras (backlog)

- **Notificaciones push locales** — avisos en pantalla sin Telegram
- **Historial de comandos crontab** — log de ejecuciones con resultado
- **Perfiles de configuración** — múltiples `local_settings.py` intercambiables
- **Dashboard web espejo** — servir la UI como página HTML desde el propio Pi
- **Multi-pantalla / modo kiosk** — detectar HDMI y extender la UI

---

## 🗺️ Roadmap

```
v2.x   ✅ Monitor completo, temas, SQLite, badges
v3.0   ✅ Visor Logs
v3.1   ✅ Telegram + Homebridge extendido
v3.2   ✅ Red Local + Pi-hole v6 + Historial Alertas
v3.3   ✅ Resumen Sistema + Brillo DSI + Gestor VPN
v3.4   ✅ LEDs RGB + Temp Chasis + Audio + Cámara OCR + SMART
v3.5   ✅ ServiceRegistry
v3.6   ✅ ServicesManagerWindow
v3.6.5 ✅ ButtonManagerWindow
v3.7   ✅ CrontabWindow + Fixes VNC/Wayland + Multi-Pi
v3.8   ✅ Monitor SSH + Monitor WiFi + Editor Config + Refactor core/
v4.0   ✅ Pestañas táctiles + WindowLifecycleManager + Modularización main_*  ← ACTUAL
v4.1   💭 Audio Control + Clima + I²C Scanner + GPIO?
```

---

## 📊 Cobertura por módulo (v4.0)

| Área | Cobertura | Notas |
|------|-----------|-------|
| Hardware CPU/RAM/Temp/Disco | ✅ Completa | SystemMonitor + DiskMonitor |
| NVMe SMART | ✅ Completa | TBW, horas, vida útil, ciclos |
| Red | ✅ Completa | NetworkMonitor + NetworkScanner |
| WiFi | ✅ Completa | WiFiMonitor — señal, calidad, tráfico |
| Procesos / Servicios systemd | ✅ Completa | ProcessMonitor + ServiceMonitor |
| Servicios Dashboard | ✅ Completa | ServiceRegistry + ServicesManagerWindow |
| Fans | ✅ Completa | FanController + FanAutoService |
| Crontab | ✅ Completa | CrontabWindow, usuario/root |
| Menú configurable | ✅ Completa | ButtonManagerWindow + WindowManager |
| Pantalla | ✅ Completa | DisplayService (brillo DSI) |
| VPN | ✅ Básica | VpnMonitor (estado + conectar/desconectar) |
| Homebridge / HomeKit | ✅ Avanzada | 5 tipos de dispositivo |
| Pi-hole | ✅ Completa | API v6, estadísticas, badge |
| Alertas Telegram | ✅ Completa | edge-trigger + historial JSON |
| Alertas Audio | ✅ Completa | 11 sonidos TTS español, 4 métricas |
| Histórico / Análisis | ✅ Completa | SQLite + matplotlib |
| LEDs RGB GPIO Board | ✅ Completa | 6 modos, sin destellos |
| Temperatura chasis | ✅ Completa | Via fase1.py + hardware_state.json |
| Fan duty real | ✅ Completa | Via fase1.py + hardware_state.json |
| Cámara OV5647 | ✅ Completa | rpicam-still + OCR Tesseract |
| Monitor SSH | ✅ Completa | Sesiones activas + historial humanizado |
| Config por máquina | ✅ Completa | local_settings.py + Editor Config UI |
| Multi-Pi / local_settings | ✅ Completa | Pi 5 Wayland + Pi 3 Xvfb |
| Audio Control | ❌ Pendiente | v4.1 |
| Widget Clima | ❌ Pendiente | v4.1 |
| I²C Scanner | ❌ Pendiente | v4.1 |
| GPIO Monitor | ❌ Pendiente | v4.1 |
| API REST local | ❌ Pendiente | futuro |
| Backup automático | ❌ Pendiente | futuro |
````

## File: INDEX.md
````markdown
# 📚 Índice de Documentación - System Dashboard v4.0

---

## 🚀 Documentos Esenciales

**[README.md](README.md)** ⭐ — Documentación completa v4.0. **Empieza aquí.**

**[QUICKSTART.md](QUICKSTART.md)** ⚡ — Instalación y ejecución en 5 minutos.

---

## 📖 Guías por tema

### 🎨 Personalización
**[THEMES_GUIDE.md](THEMES_GUIDE.md)** — 15 temas, crear personalizados.

### 🔧 Instalación
**[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** — RPi OS, Kali, venv, script automático.

### 🏠 Homebridge
Configuración: ver sección en README.md.
5 tipos: `switch`, `light`, `thermostat`, `sensor`, `blind`.

### 🕳️ Pi-hole (v3.2)
Solo compatible con **Pi-hole v6**.
Añadir `PIHOLE_HOST`, `PIHOLE_PORT`, `PIHOLE_PASSWORD` al `.env`.

### 🖧 Red Local (v3.2)
Instalar: `sudo apt install arp-scan`.
Sudoers: `usuario ALL=(ALL) NOPASSWD: /usr/sbin/arp-scan`.

### 📲 Alertas Telegram
Configurar `TELEGRAM_TOKEN` + `TELEGRAM_CHAT_ID` en `.env`.

### 🤝 Integración con fase1.py
**[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** — Compartir estado fans/LEDs via JSON, OLED.

### 💡 Ideas y Expansión
**[IDEAS_EXPANSION.md](IDEAS_EXPANSION.md)** — Roadmap v4.1+, backlog, cobertura por módulo.

### 🖥️ Multi-Pi (v3.7)
Crear `config/local_settings.py` (en `.gitignore`) con los valores de `DSI_X/Y/WIDTH/HEIGHT` para cada máquina.
El **Editor de Configuración** *(v3.8)* permite editar este fichero directamente desde la UI sin SSH.
- **Pi 5 Wayland**: `wayvnc --output=DSI-2 0.0.0.0 5901` + `gsettings set org.gnome.desktop.session idle-delay 0`
- **Pi 3B+ Xvfb**: display virtual `:1`, VNC puerto `5901`, resolución configurable

### 🗂️ Menú por Pestañas (v4.0)
Pestañas definidas en `config/settings.py → class UI`:
- `MENU_COLUMNS` — número de columnas de botones
- `MENU_TABS` — lista de `(clave, icono, label, [claves_BL])`
Añadir una pestaña nueva es añadir una línea a `MENU_TABS`.

---

## 📋 Archivos de configuración

| Archivo | En git | Gestiona |
|---------|--------|---------|
| `config/settings.py` | ✅ | Constantes globales, Icons, UI (pestañas), LAUNCHERS |
| `config/button_labels.py` | ✅ | Labels de botones (fuente única de verdad) |
| `config/themes.py` | ✅ | 15 temas |
| `config/services.json` | ❌ | Estado servicios + visibilidad botones UI |
| `config/local_settings.py` | ❌ | Overrides por máquina (editable via Config Editor) |
| `.env` | ❌ | Credenciales (Homebridge, PiHole, Telegram, VPN) |

---

## 🗂️ Estructura de documentos v4.0

```
📚 Documentación/
├── README.md                         ⭐ Principal v4.0
├── QUICKSTART.md                     ⚡ Inicio rápido
├── INDEX.md                          📑 Este archivo
├── REQUIREMENTS.md                   📋 Requisitos
├── INSTALL_GUIDE.md                  🔧 Instalación
├── THEMES_GUIDE.md                   🎨 Temas
├── INTEGRATION_GUIDE.md              🤝 Integración fase1
├── IDEAS_EXPANSION.md                💡 Roadmap v4.1+
└── COMPATIBILIDAD.md                 🌐 Compatibilidad
```

---

## 🎯 Flujo de lectura recomendado

**Usuario nuevo:**
1. README.md → sección Características
2. QUICKSTART.md → instalar y ejecutar
3. Explorar las 27 ventanas 🎉

**Usuario avanzado / configurar integraciones:**
1. README.md completo
2. Sección Homebridge → `.env` + Insecure Mode
3. Sección Pi-hole → `.env` + compatibilidad v6
4. Sección Telegram → `.env`
5. Sección Multi-Pi → `local_settings.py` + wayvnc / Xvfb
6. **Editor de Configuración** *(v3.8)* → ajustar umbrales e iconos desde la UI

**Desarrollador / extender:**
1. README.md sección Arquitectura
2. `config/settings.py → class UI` → entender estructura de pestañas
3. `ui/window_lifecycle.py` → patrón de registro de ventanas
4. `ui/styles.py` → `make_window_header()` y `make_entry()` para nuevas ventanas
5. `core/service_registry.py` → registrar nuevos servicios
6. IDEAS_EXPANSION.md → ver qué se puede añadir en v4.1

---

## 🔍 Buscar por problema

| Problema | Dónde mirar |
|----------|-------------|
| No arranca | QUICKSTART.md → Problemas Comunes |
| VPN badge siempre rojo | README.md Troubleshooting (interfaz `tun0`/`wg0`) |
| Pi-hole no conecta | README.md Troubleshooting (solo v6) |
| Red Local no escanea | README.md Troubleshooting (arp-scan + sudoers) |
| No puedo escribir en entries (VNC) | README.md → `make_entry()` en `ui/styles.py` |
| Foco perdido tras inactividad (Pi 5) | `gsettings set org.gnome.desktop.session idle-delay 0` |
| Dashboard no visible por VNC en Pi 5 | `wayvnc --output=DSI-2 0.0.0.0 5901` |
| Configuración distinta por máquina | `config/local_settings.py` o Editor de Configuración |
| Homebridge no conecta | README.md Troubleshooting |
| Alertas Telegram no llegan | README.md sección Telegram / `.env` |
| SMART muestra N/D | Sudoers smartctl + `sudo smartctl -A /dev/nvme0` |
| Audio no suena | `aplay -l` → verificar dispositivo HDMI activo |
| Cámara no encuentra rpicam-still | `sudo apt install rpicam-apps` |
| WiFi no muestra datos | `sudo apt install wireless-tools` |
| SSH monitor vacío | Verificar que `who` y `last` funcionan en el sistema |
| Ver errores | `grep ERROR data/logs/dashboard.log` |

---

## 📊 Estadísticas del proyecto v4.0

| Métrica | v3.8 | v4.0 |
|---------|------|------|
| Versión | 3.8 | **4.0** |
| Archivos Python | 68 | **73** |
| Ventanas | 27 | 27 |
| Temas | 15 | 15 |
| Badges en menú | 12 | 12 |
| Servicios background | 16 | 16 |
| Módulos ui/main_* | 1 | **5** |
| Documentos | 9 | 9 |

### Cambios arquitecturales en v4.0
- `ui/main_badges.py` — `BadgeManager` (nuevo)
- `ui/main_update_loop.py` — `UpdateLoop` (nuevo)
- `ui/main_system_actions.py` — exit/restart (nuevo)
- `ui/window_lifecycle.py` — `WindowLifecycleManager` (nuevo)
- `ui/main_window.py` — 891 → 451 líneas (refactorizado)
- `config/settings.py → class UI` — definición de pestañas (nuevo)
````
