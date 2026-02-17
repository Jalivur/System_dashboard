# 🖥️ Sistema de Monitoreo y Control - Dashboard Profesional

Sistema completo de monitoreo y control para Raspberry Pi con interfaz gráfica DSI, control de ventiladores PWM, temas personalizables y gestión avanzada del sistema.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)

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
- **Escalado adaptativo**: Gráficas se ajustan automáticamente

### ⚙️ **Monitor de Procesos** ⭐ NUEVO
- **Lista en tiempo real**: Top 20 procesos con CPU/RAM
- **Búsqueda inteligente**: Por nombre o comando completo
- **Filtros**: Todos / Usuario / Sistema
- **Ordenación**: Por PID, Nombre, CPU%, RAM%
- **Terminar procesos**: Con confirmación y feedback
- **Pausa inteligente**: No se atasca durante interacciones

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

---

## 📦 Instalación

### 🔧 **Requisitos del Sistema**
- **Hardware**: Raspberry Pi 3/4/5
- **OS**: Raspberry Pi OS (Bullseye/Bookworm) o Kali Linux
- **Pantalla**: DSI 7" (800x480) o HDMI
- **Python**: 3.8 o superior
- **Extras**: Ventiladores PWM (opcional), NVMe (opcional)

### ⚡ **Instalación Rápida (Recomendada)**

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

# 4. Detectar sensores (primera vez)
sudo sensors-detect --auto

# 5. Ejecutar
python3 main.py
```

### 📋 **Dependencias Python**
```
customtkinter==5.2.0
psutil==5.9.5
Pillow==10.0.0
```

---

## 🎯 Uso

### **Ejecutar el Dashboard**
```bash
cd system-dashboard
python3 main.py
```

### **Menú Principal**
El dashboard muestra 9 botones principales:
- **Control Ventiladores**: Configura modos y curvas PWM
- **Monitor Placa**: CPU, RAM, temperatura
- **Monitor Red**: Tráfico, speedtest, interfaces
- **Monitor USB**: Dispositivos y expulsión segura
- **Monitor Disco**: Espacio, temperatura NVMe, I/O
- **Lanzadores**: Ejecuta scripts personalizados
- **Monitor Procesos**: Gestión avanzada de procesos ⭐ NUEVO
- **Cambiar Tema**: Selecciona entre 15 temas
- **Salir**: Cierra el dashboard con confirmación

### **Atajos de Teclado**
- `Esc`: Cerrar ventana activa
- `F11`: Toggle fullscreen (si aplica)

---

## 🎨 Temas Disponibles

El dashboard incluye **15 temas profesionales** pre-configurados:

| Tema | Descripción | Colores |
|------|-------------|---------|
| **Cyberpunk** | Original cyan neón | Cyan + Verde |
| **Matrix** | Verde Matrix | Verde brillante |
| **Sunset** | Atardecer cálido | Naranja + Púrpura |
| **Ocean** | Azul océano | Azul + Aqua |
| **Dracula** | Colores pastel | Púrpura + Rosa |
| **Nord** | Minimalista nórdico | Azul hielo |
| **Tokyo Night** | Noche de Tokio | Azul + Púrpura |
| **Monokai** | IDE clásico | Cyan + Verde |
| **Gruvbox** | Retro cálido | Naranja + Beige |
| **Solarized Dark** | Elegante oscuro | Azul + Cyan |
| **One Dark** | Atom editor | Azul claro |
| **Synthwave 84** | Neón retro | Rosa + Verde |
| **GitHub Dark** | Estilo GitHub | Azul GitHub |
| **Material Dark** | Material Design | Azul material |
| **Ayu Dark** | Moderno minimalista | Azul cielo |

**Cambiar tema:**
1. Clic en "Cambiar Tema"
2. Selecciona tu favorito
3. Clic en "Aplicar y Reiniciar"
4. ✨ Reinicio automático con nuevo tema

---

## ⚙️ Configuración

### **Archivo Principal: `config/settings.py`**

#### **Pantalla DSI**
```python
DSI_WIDTH = 800
DSI_HEIGHT = 480
DSI_X = 0      # Posición X
DSI_Y = 0      # Posición Y
```

#### **Control de Ventiladores**
```python
PWM_PIN = 18           # Pin GPIO para PWM
PWM_FREQ = 25000       # Frecuencia 25kHz
```

#### **Actualización**
```python
UPDATE_MS = 2000       # Actualiza cada 2 segundos
```

#### **Lanzadores Personalizados**
```python
LAUNCHERS = [
    {
        "label": "Apagar Sistema",
        "script": "/usr/bin/poweroff"
    },
    {
        "label": "Reiniciar",
        "script": "/usr/bin/reboot"
    },
    # Añade los tuyos aquí
]
```

---

## 📊 Arquitectura del Proyecto

```
system_dashboard/
├── config/                      # Configuración
│   ├── settings.py             # Constantes globales
│   └── themes.py               # 15 temas pre-configurados
├── core/                        # Lógica de negocio
│   ├── fan_controller.py       # Control PWM y curvas
│   ├── fan_auto_service.py     # Servicio background singleton
│   ├── system_monitor.py       # CPU, RAM, temperatura
│   ├── network_monitor.py      # Red, speedtest, interfaces
│   ├── disk_monitor.py         # Disco, NVMe, I/O
│   └── process_monitor.py      # Gestión de procesos ⭐
├── ui/                          # Interfaz gráfica
│   ├── main_window.py          # Ventana principal
│   ├── styles.py               # Estilos y botones
│   ├── widgets/                # Componentes reutilizables
│   │   ├── graphs.py           # Gráficas personalizadas
│   │   └── dialogs.py          # Diálogos confirm/alert
│   └── windows/                # Ventanas secundarias
│       ├── monitor.py          # Monitor de placa
│       ├── network.py          # Monitor de red
│       ├── usb.py              # Monitor USB
│       ├── disk.py             # Monitor de disco
│       ├── process.py          # Monitor de procesos ⭐
│       ├── fan_control.py      # Control de ventiladores
│       ├── launchers.py        # Lanzadores
│       └── theme_selector.py   # Selector de temas
├── utils/                       # Utilidades
│   ├── file_manager.py         # Gestión de JSON
│   └── system_utils.py         # Utilidades del sistema
├── data/                        # Estados persistentes
│   ├── fan_state.json          # Estado de ventiladores
│   └── theme_config.json       # Tema seleccionado
├── scripts/                     # Scripts personalizados
├── main.py                      # Punto de entrada
└── requirements.txt             # Dependencias Python
```

**Total: ~3500 líneas de código Python en 30 archivos**

---

## 🔧 Características Técnicas

### **Patrón de Diseño**
- **MVC**: Model (core) - View (ui) - Controller (main)
- **Singleton**: FanAutoService (thread-safe)
- **Observer**: Actualización reactiva de UI

### **Gestión de Estado**
- **Persistencia**: JSON para configuración
- **Thread-safe**: Locks para acceso concurrente
- **Atomic writes**: Previene corrupción de archivos

### **Interfaz Gráfica**
- **Framework**: CustomTkinter (themed Tkinter)
- **Responsive**: Grid layout adaptable
- **Sin bordes**: `overrideredirect=True` para DSI
- **Posicionamiento preciso**: Withdraw/deiconify pattern

### **Servicios Background**
- **FanAutoService**: Daemon thread para modo auto
- **Actualización inteligente**: Pausa durante interacciones
- **Graceful shutdown**: Cleanup con `atexit`

---

## 🐛 Troubleshooting

### **Problema: No se ve la interfaz**
**Causa**: Posición de ventana incorrecta  
**Solución**:
```python
# config/settings.py
DSI_X = 0  # Ajustar según tu pantalla
DSI_Y = 0
```

### **Problema: Ventiladores no funcionan**
**Causa**: Pin PWM incorrecto o sin permisos  
**Solución**:
```bash
# Verificar GPIO
gpio readall

# Ejecutar con sudo (temporal)
sudo python3 main.py
```

### **Problema: Temperatura no se muestra**
**Causa**: Sensores no detectados  
**Solución**:
```bash
sudo sensors-detect --auto
sudo systemctl restart lm-sensors
sensors  # Verificar
```

### **Problema: Speedtest falla**
**Causa**: speedtest-cli no instalado  
**Solución**:
```bash
sudo apt install speedtest-cli
```

### **Problema: Tema no se aplica**
**Causa**: Reinicio manual necesario  
**Solución**: Usa "Aplicar y Reiniciar" (reinicia automáticamente)

### **Problema: Monitor de procesos laggy**
**Causa**: Actualización muy frecuente  
**Solución**: Ya implementado - pausa automática durante interacciones

---

## 🚀 Características Avanzadas

### **Auto-detección de Red**
Cambia automáticamente entre interfaces activas:
```
WiFi activo → muestra wlan0
Conectas Ethernet → cambia a eth0
Conectas VPN → cambia a tun0
```

### **Curvas PWM Personalizadas**
Define hasta 8 puntos temperatura-PWM:
```
Ejemplo curva agresiva:
30°C → 30% PWM
40°C → 50% PWM
50°C → 70% PWM
60°C → 100% PWM
```

### **Búsqueda de Procesos**
Busca en nombre Y comando completo:
```
"chrome" → Encuentra todos los Chrome con URLs
"python" → Encuentra scripts Python con argumentos
```

### **Expulsión Segura USB**
Secuencia completa:
1. Unmount del filesystem
2. Eject del dispositivo
3. Confirmación visual
4. Feedback de éxito/error

---

## 📈 Rendimiento

- **Uso CPU**: ~5-10% en idle
- **Uso RAM**: ~80-120 MB
- **Actualización**: 2 segundos (configurable)
- **Threads**: 2 (main + FanAutoService)
- **Tiempo inicio**: ~2 segundos

---

## 🤝 Contribuir

¿Quieres mejorar el dashboard? ¡Genial!

1. Fork del repositorio
2. Crea una rama: `git checkout -b mi-mejora`
3. Commit: `git commit -am 'Añade nueva función'`
4. Push: `git push origin mi-mejora`
5. Pull Request

---

## 📝 Changelog

### **v2.0.0** - 2026-02-16 ⭐ ACTUAL
- ✅ **NUEVO**: Monitor de Procesos completo
- ✅ **NUEVO**: 15 temas profesionales
- ✅ **MEJORA**: Reinicio automático al cambiar tema
- ✅ **MEJORA**: Sliders y scrollbars usan colores de tema
- ✅ **MEJORA**: Tema Matrix colores corregidos
- ✅ **MEJORA**: 11 temas con `secondary` corregido
- ✅ **MEJORA**: Monitor red con IPs de interfaces
- ✅ **MEJORA**: Auto-detección interfaz activa
- ✅ **MEJORA**: Speedtest conversión Mbit/s → MB/s corregida
- ✅ **MEJORA**: FanAutoService funciona con ventana cerrada
- ✅ **MEJORA**: Lanzadores con layout grid
- ✅ **FIX**: Slider PWM se actualiza en modo auto
- ✅ **FIX**: Botones con confirmación consistente
- ✅ **FIX**: Posicionamiento estable de ventanas

### **v1.0.0** - 2025-01
- ✅ Release inicial modular
- ✅ 8 ventanas funcionales
- ✅ Control de ventiladores
- ✅ Tema Cyberpunk

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 🙏 Agradecimientos

- **CustomTkinter**: Por el framework de UI moderno
- **psutil**: Por las utilidades del sistema
- **Raspberry Pi Foundation**: Por el hardware increíble

---

## 📧 Contacto

¿Preguntas o sugerencias?  
Abre un **Issue** en GitHub

---

**¡Disfruta de tu dashboard profesional!** 🚀✨
