# 💡 IDEAS_EXPANSION.md
## Expansión y Roadmap — Sistema de Monitoreo v3.7

---

## ✅ Implementado

### v3.7 (actual) — Crontab + Fixes + Multi-Pi
- **Gestor Crontab** (`CrontabWindow`)
  - Ver, añadir, editar y eliminar entradas del crontab
  - Selector de usuario: usuario / root
  - Accesos rápidos de programación (@reboot, cada hora, cada día, etc.)
  - Preview legible de la expresión cron

- **Fix grab modal** (`dialogs.py` + `main_window.py`)
  - `grab_release()` garantizado al cerrar `terminal_dialog` y `exit_application`
  - Elimina el bloqueo de foco en toda la app al cerrar diálogos

- **`make_entry()`** (`ui/styles.py`)
  - Reemplaza `ctk.CTkEntry()` en ventanas con entries
  - Fuerza foco al widget interno con `focus_force()` al hacer clic
  - Soluciona escritura en VNC con `overrideredirect(True)`

- **Soporte dual-Pi** (`config/local_settings.py`)
  - Configuración independiente por máquina sin tocar git
  - Pi 3B+: Xvfb `:1`, resolución 1024×762, VNC puerto 5901
  - Pi 5: Wayland + labwc, wayvnc `--output=DSI-2`, idle-delay 0

### v3.6.5
- **Gestor de Botones** (`ButtonManagerWindow` + `WindowManager`)
  - Mostrar/ocultar botones del menú principal desde la UI
  - Persistencia en `data/button_config.json`

### v3.6
- **Servicios Dashboard** (`ServicesManagerWindow`)
  - Activar/desactivar servicios background del dashboard desde la UI
  - Persistencia en `data/services.json`

### v3.5
- **ServiceRegistry** (`core/service_registry.py`)
  - Registro centralizado de todos los servicios del dashboard
  - Base para `ServicesManagerWindow` y `ButtonManagerWindow`

### v3.4 — Hardware FNK0100K
- **LEDs RGB inteligentes** (`LedService` + `LedWindow`) — 6 modos, sin destellos
- **Temperatura chasis + Fan duty real** (`HardwareMonitor`) — via `hardware_state.json`
- **Alertas de audio** (`AudioAlertService`) — 11 .wav, TTS español, 4 métricas
- **Cámara OV5647 + Escáner OCR** (`CameraWindow`) — Tesseract local, `.txt` y `.md`
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
- **Alertas Telegram** (`AlertService`)
- **Homebridge extendido** — 5 tipos de dispositivo

### v3.0
- Visor de Logs con filtros y exportación

### v2.x
- Control Ventiladores PWM, monitores completos, 15 temas, badges, logging, SQLite

---

## 🔄 Ideas en evaluación para v3.8+

### 🖥️ Información del Hardware
- Modelo de Pi, revisión, memoria total, versión del SO, kernel
- Ventana estática tipo "Acerca de este equipo"
- Sin dependencias nuevas — `vcgencmd`, `/proc/cpuinfo`, `uname`

### 🔒 Monitor SSH
- Leer `/var/log/auth.log` y mostrar intentos fallidos de acceso
- Badge con contador de intentos en las últimas 24h
- Lista con IP origen, usuario y timestamp de cada intento

### 📡 Monitor WiFi
- Intensidad de señal en dBm, calidad, SSID conectado, canal
- Gráfica histórica de señal
- Badge si la señal baja de umbral configurable

### 📝 Editor de Configuración
- Editar `config/settings.py`, `config/local_settings.py` y `.env` desde la UI
- Sin necesidad de SSH para cambios rápidos de configuración
- Solo las secciones relevantes para el usuario (posición pantalla, launchers, credenciales)

---

## 💭 Ideas futuras (backlog)

### API REST local
- Endpoint `/status` que devuelva el estado del sistema en JSON
- `http.server` de stdlib

### Backup automático de configuración
- Copiar `data/` a NAS o USB al detectar dispositivo montado

### Multi-pantalla / modo kiosk
- Detectar pantalla HDMI conectada y extender la UI

---

## 🗺️ Roadmap

```
v3.0  ✅ Visor Logs
v3.1  ✅ Telegram + Homebridge extendido
v3.2  ✅ Red Local + Pi-hole v6 + Historial Alertas
v3.3  ✅ Resumen Sistema + Brillo DSI + Gestor VPN
v3.4  ✅ LEDs RGB + Temp Chasis + Audio + Cámara OCR + SMART
v3.5  ✅ ServiceRegistry
v3.6  ✅ ServicesManagerWindow
v3.6.5 ✅ ButtonManagerWindow
v3.7  ✅ CrontabWindow + Fixes VNC/Wayland + Multi-Pi  ← ACTUAL
v3.8  🔄 Info Hardware + Monitor SSH + Monitor WiFi + Editor Config
v4.0  💭 API REST + Backup + Multi-pantalla?
```

---

## 📊 Cobertura por módulo (v3.7)

| Área | Cobertura | Notas |
|------|-----------|-------|
| Hardware CPU/RAM/Temp/Disco | ✅ Completa | SystemMonitor + DiskMonitor |
| NVMe SMART | ✅ Completa | TBW, horas, vida útil, ciclos |
| Red | ✅ Completa | NetworkMonitor + NetworkScanner |
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
| Multi-Pi / local_settings | ✅ Completa | Pi 5 Wayland + Pi 3 Xvfb |
| Info Hardware | ❌ Pendiente | v3.8 
| Monitor SSH | ❌ Pendiente | v3.8 |
| Monitor WiFi | ❌ Pendiente | v3.8 |
| Editor Configuración | ❌ Pendiente | v3.8 |
