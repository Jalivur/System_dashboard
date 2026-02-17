# 🖥️ Sistema de Monitoreo y Control - Dashboard v2.5

Sistema completo de monitoreo y control para Raspberry Pi con interfaz gráfica DSI, control de ventiladores PWM, temas personalizables, histórico de datos y gestión avanzada del sistema.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)
[![Version](https://img.shields.io/badge/Version-2.5-orange.svg)]()

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
- **Ordenación**: Por PID, Nombre, CPU%, RAM%
- **Terminar procesos**: Con confirmación y feedback

### 🔧 **Monitor de Servicios systemd** ⭐ NUEVO
- **Gestión completa**: Start/Stop/Restart servicios
- **Estado visual**: active, inactive, failed con iconos
- **Autostart**: Enable/Disable con confirmación
- **Logs en tiempo real**: Ver últimas 50 líneas
- **Búsqueda y filtros**: Por nombre o estado

### 📊 **Histórico de Datos** ⭐ NUEVO
- **Recolección automática**: Cada 5 minutos en background
- **Base de datos SQLite**: Ligera y eficiente
- **Visualización gráfica**: CPU, RAM, Temperatura en 3 gráficas
- **Periodos**: 24 horas, 7 días, 30 días
- **Estadísticas**: Promedios, mínimos, máximos
- **Detección de anomalías**: Alertas automáticas
- **Exportación CSV**: Para análisis externo

### 🔌 **Monitor USB**
- **Detección automática**: Dispositivos conectados
- **Separación inteligente**: Mouse/teclado vs almacenamiento
- **Expulsión segura**: Unmount + eject con confirmación
- **Actualización en vivo**: Detecta conexiones/desconexiones

### 💾 **Monitor de Disco**
- **Particiones**: Uso de espacio de todas las unidades
- **Temperatura NVMe**: Monitoreo térmico del SSD
- **Velocidad I/O**: Lectura/escritura en MB/s
- **Gráficas históricas**: Actividad del disco

### 🚀 **Lanzadores de Scripts**
- **Ejecuta scripts personalizados**: Con confirmación previa
- **Layout en grid**: Organización visual en columnas
- **Feedback visual**: Mensajes de éxito/error

### 🎨 **15 Temas Personalizables**
- **Cambio con un clic**: Reinicio automático
- **Paletas completas**: Cyberpunk, Matrix, Dracula, Nord, Tokyo Night, etc.
- **Preview en vivo**: Ve los colores antes de aplicar
- **Persistente**: Guarda tu elección

### 🔄 **Reinicio Rápido** ⭐ NUEVO
- **Botón de reinicio**: Reinicia el dashboard con un clic
- **Aplica cambios**: Código, configuración, todo
- **Con confirmación**: Evita reinicios accidentales
- **Perfecto para desarrollo**: Cambios rápidos

---

## 📦 Instalación

### 🔧 **Requisitos del Sistema**
- **Hardware**: Raspberry Pi 3/4/5
- **OS**: Raspberry Pi OS (Bullseye/Bookworm) o Kali Linux
- **Pantalla**: DSI 7" (800x480) o HDMI
- **Python**: 3.8 o superior
- **Extras**: Ventiladores PWM (opcional), NVMe (opcional)

### ⚡ **Instalación Rápida**

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard

# 2. Ejecutar instalador automático
chmod +x install.sh
./install.sh

# 3. Ejecutar
python3 main.py
```

### 🛠️ **Instalación Manual**

```bash
# 1. Instalar dependencias del sistema
sudo apt update
sudo apt install -y python3 python3-pip python3-venv lm-sensors speedtest-cli

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias Python
pip install -r requirements.txt

# 4. Detectar sensores
sudo sensors-detect --auto

# 5. Ejecutar
python3 main.py
```

---

## 🎯 Uso

### **Menú Principal (12 botones):**
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
│  Histórico       │  Cambiar          │
│  Datos           │  Tema             │
├──────────────────┼───────────────────┤
│  Reiniciar       │  Salir            │
└──────────────────┴───────────────────┘
```

### **Ventanas Disponibles:**

1. **Control Ventiladores** - Configura modos y curvas PWM
2. **Monitor Placa** - CPU, RAM, temperatura en tiempo real
3. **Monitor Red** - Tráfico, speedtest, interfaces
4. **Monitor USB** - Dispositivos y expulsión segura
5. **Monitor Disco** - Espacio, temperatura NVMe, I/O
6. **Lanzadores** - Ejecuta scripts personalizados
7. **Monitor Procesos** - Gestión avanzada de procesos ⭐
8. **Monitor Servicios** - Control de servicios systemd ⭐
9. **Histórico Datos** - Visualización de métricas históricas ⭐
10. **Cambiar Tema** - Selecciona entre 15 temas
11. **Reiniciar** - Reinicia el dashboard ⭐
12. **Salir** - Cierra con confirmación

---

## 🎨 Temas Disponibles

El dashboard incluye **15 temas profesionales**:

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

**Cambiar tema**: Menú → "Cambiar Tema" → Seleccionar → "Aplicar y Reiniciar"

---

## 📊 Arquitectura del Proyecto

```
system_dashboard/
├── config/                      # Configuración
│   ├── settings.py             # Constantes globales
│   └── themes.py               # 15 temas pre-configurados
├── core/                        # Lógica de negocio (11 archivos)
│   ├── fan_controller.py       # Control PWM y curvas
│   ├── fan_auto_service.py     # Servicio background
│   ├── system_monitor.py       # CPU, RAM, temperatura
│   ├── network_monitor.py      # Red, speedtest, interfaces
│   ├── disk_monitor.py         # Disco, NVMe, I/O
│   ├── process_monitor.py      # Gestión de procesos
│   ├── service_monitor.py      # Servicios systemd ⭐
│   ├── data_logger.py          # SQLite logging ⭐
│   ├── data_analyzer.py        # Análisis histórico ⭐
│   ├── data_collection_service.py  # Recolección auto ⭐
│   └── __init__.py
├── ui/                          # Interfaz gráfica
│   ├── main_window.py          # Ventana principal
│   ├── styles.py               # Estilos y botones
│   ├── widgets/                # Componentes reutilizables
│   │   ├── graphs.py           # Gráficas personalizadas
│   │   └── dialogs.py          # Diálogos confirm/alert
│   └── windows/                # Ventanas secundarias (11)
│       ├── monitor.py          # Monitor de placa
│       ├── network.py          # Monitor de red
│       ├── usb.py              # Monitor USB
│       ├── disk.py             # Monitor de disco
│       ├── process_window.py   # Monitor de procesos
│       ├── service.py          # Monitor de servicios ⭐
│       ├── history.py          # Histórico de datos ⭐
│       ├── fan_control.py      # Control ventiladores
│       ├── launchers.py        # Lanzadores
│       └── theme_selector.py   # Selector de temas
├── utils/                       # Utilidades
│   ├── file_manager.py         # Gestión de JSON
│   └── system_utils.py         # Utilidades del sistema
├── data/                        # Estados persistentes
│   ├── fan_state.json          # Estado ventiladores
│   ├── theme_config.json       # Tema seleccionado
│   └── history.db              # Base de datos histórico ⭐
├── scripts/                     # Scripts personalizados
├── main.py                      # Punto de entrada
└── requirements.txt             # Dependencias Python
```

**Total: ~5,500 líneas de código Python en 35+ archivos**

---

## 🔧 Configuración

### **Archivo Principal: `config/settings.py`**

#### **Pantalla DSI:**
```python
DSI_WIDTH = 800
DSI_HEIGHT = 480
DSI_X = 0      # Posición X
DSI_Y = 0      # Posición Y
```

#### **Control de Ventiladores:**
```python
PWM_PIN = 18           # Pin GPIO para PWM
PWM_FREQ = 25000       # Frecuencia 25kHz
```

#### **Histórico de Datos:**
```python
DATA_COLLECTION_INTERVAL = 5  # Minutos entre recolecciones
DATA_RETENTION_DAYS = 90      # Días de retención
```

---

## 🆕 Novedades en v2.5

### **✨ Nuevas Características:**
- ✅ **Monitor de Servicios** - Control completo de systemd
- ✅ **Histórico de Datos** - Base de datos SQLite con gráficas
- ✅ **Botón Reiniciar** - Reinicio rápido del dashboard
- ✅ **Recolección automática** - Background service cada 5 min
- ✅ **Exportación CSV** - Descarga datos históricos
- ✅ **Detección de anomalías** - Alertas automáticas
- ✅ **Logs de servicios** - Ver últimas 50 líneas

### **🔧 Mejoras:**
- ✅ Sliders y scrollbars usan colores de tema
- ✅ Monitor de procesos con pausa inteligente
- ✅ Speedtest corregido (Mbit/s → MB/s)
- ✅ 11 temas con `secondary` corregido
- ✅ FanAutoService singleton thread-safe
- ✅ Layout grid configurable en lanzadores

---

## 📈 Rendimiento

- **Uso CPU**: ~5-10% en idle
- **Uso RAM**: ~100-150 MB
- **Base de datos**: ~5 MB por 10,000 registros
- **Actualización**: 2 segundos (configurable)
- **Threads**: 3 (main + FanAuto + DataCollection)
- **Tiempo inicio**: ~2-3 segundos

---

## 🐛 Troubleshooting

### **No arranca**
```bash
python3 --version  # Debe ser 3.8+
pip install -r requirements.txt
```

### **No detecta temperatura**
```bash
sudo sensors-detect --auto
sudo systemctl restart lm-sensors
sensors  # Verificar
```

### **Ventiladores no responden**
```bash
gpio readall
sudo python3 main.py  # Temporal
```

### **Speedtest no funciona**
```bash
sudo apt install speedtest-cli
```

### **Base de datos crece mucho**
```bash
# Limpiar datos >90 días desde Histórico Datos
# O manualmente:
sqlite3 data/history.db "DELETE FROM metrics WHERE timestamp < datetime('now', '-90 days');"
```

---

## 📚 Documentación Completa

### **Guías Disponibles:**
- [README.md](README.md) - Este archivo
- [QUICKSTART.md](QUICKSTART.md) - Inicio rápido 5 minutos
- [INSTALL_GUIDE.md](INSTALL_GUIDE.md) - Instalación detallada
- [THEMES_GUIDE.md](THEMES_GUIDE.md) - Guía de temas
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Integración OLED
- [INDEX.md](INDEX.md) - Índice completo

---

## 📊 Estadísticas del Proyecto

- **Versión**: 2.5
- **Archivos Python**: 35+
- **Líneas de código**: ~5,500
- **Ventanas**: 11 ventanas funcionales
- **Temas**: 15 temas pre-configurados
- **Documentos**: 10+ guías

---

## 🤝 Contribuir

¿Quieres mejorar el dashboard?

1. Fork del repositorio
2. Crea una rama: `git checkout -b mi-mejora`
3. Commit: `git commit -am 'Añade nueva función'`
4. Push: `git push origin mi-mejora`
5. Pull Request

---

## 📝 Changelog

### **v2.5** - 2026-02-17 ⭐ ACTUAL
- ✅ **NUEVO**: Monitor de Servicios systemd completo
- ✅ **NUEVO**: Histórico de Datos con SQLite
- ✅ **NUEVO**: Botón Reiniciar en menú
- ✅ **NUEVO**: Recolección automática background
- ✅ **NUEVO**: Exportación CSV
- ✅ **NUEVO**: Detección de anomalías
- ✅ **MEJORA**: 12 botones en menú (vs 9)

### **v2.0** - 2026-02-16
- ✅ **NUEVO**: Monitor de Procesos completo
- ✅ **NUEVO**: 15 temas profesionales
- ✅ **MEJORA**: Reinicio automático al cambiar tema
- ✅ **MEJORA**: Sliders y scrollbars temáticos
- ✅ **FIX**: Speedtest conversión correcta

### **v1.0** - 2025-01
- ✅ Release inicial modular
- ✅ 8 ventanas funcionales
- ✅ Control de ventiladores
- ✅ Tema Cyberpunk

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 🙏 Agradecimientos

- **CustomTkinter**: Framework de UI moderno
- **psutil**: Utilidades del sistema
- **matplotlib**: Visualización de gráficas
- **Raspberry Pi Foundation**: Hardware increíble

---

## 📧 Contacto

¿Preguntas o sugerencias?  
Abre un **Issue** en GitHub

---

**¡Dashboard profesional v2.5 con todas las funciones!** 🚀✨
