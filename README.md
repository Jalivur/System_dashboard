# Sistema de Monitoreo y Control

Sistema profesional de monitoreo del sistema con interfaz gráfica personalizable para control de ventiladores, visualización de recursos y gestión de red.

## 🏗️ Arquitectura del Proyecto

```
system_dashboard/
├── config/              # Configuración centralizada
│   ├── settings.py      # Constantes y configuración global
│   └── __init__.py
├── core/                # Lógica de negocio
│   ├── fan_controller.py    # Control de ventiladores y curvas PWM
│   ├── system_monitor.py    # Monitoreo de CPU, RAM, disco
│   ├── network_monitor.py   # Monitoreo de red y speedtest
│   └── __init__.py
├── ui/                  # Interfaz de usuario
│   ├── main_window.py       # Ventana principal
│   ├── styles.py            # Estilos y temas
│   ├── widgets/             # Componentes reutilizables
│   │   ├── buttons.py
│   │   ├── graphs.py        # Widgets de gráficas
│   │   ├── dialogs.py       # Diálogos personalizados
│   │   └── __init__.py
│   └── windows/             # Ventanas secundarias
│       ├── fan_control.py   # Ventana control ventiladores
│       ├── monitor.py       # Ventana monitor sistema
│       ├── network.py       # Ventana monitor red
│       ├── usb.py           # Ventana monitor USB
│       ├── launchers.py     # Ventana lanzadores
│       └── __init__.py
├── utils/               # Utilidades
│   ├── file_manager.py      # Gestión de archivos JSON
│   ├── system_utils.py      # Utilidades del sistema
│   └── __init__.py
├── data/                # Archivos de estado (generados)
├── scripts/             # Scripts de sistema
└── main.py              # Punto de entrada
```

## 🚀 Características

### Monitoreo del Sistema
- **CPU**: Uso en tiempo real con gráficas históricas
- **RAM**: Monitoreo de memoria con umbrales configurables
- **Temperatura**: Seguimiento de temperatura de CPU
- **Disco**: Uso de espacio y velocidad de I/O (lectura/escritura)

### Control de Ventiladores
- **Modos de operación**:
  - Auto: Basado en curva personalizable
  - Manual: Control directo del PWM
  - Presets: Silent, Normal, Performance
- **Curvas personalizadas**: Define puntos temperatura-PWM
- **Visualización**: Gráfica de la curva activa

### Monitor de Red
- **Tráfico en tiempo real**: Download/Upload
- **Escalado adaptativo**: Ajuste automático de gráficas
- **Speedtest integrado**: Medición de velocidad
- **Detección automática**: Interfaz de red activa

### Lanzadores de Scripts
- Ejecuta scripts de sistema personalizados
- Interfaz visual para acciones comunes
- Feedback de ejecución

## 📦 Instalación

### Requisitos
- Python 3.8+
- Linux (probado en Ubuntu 24)
- `lm-sensors` instalado para lectura de temperatura
- `speedtest-cli` para tests de velocidad (opcional)

### Instalación de dependencias

```bash
# Instalar dependencias del sistema
sudo apt-get update
sudo apt-get install python3-tk lm-sensors

# Opcional: speedtest
sudo apt-get install speedtest-cli

# Instalar dependencias de Python
pip install -r requirements.txt
```

## 🎯 Uso

### Ejecución básica

```bash
python main.py
```

### Configuración

Edita `config/settings.py` para personalizar:

```python
# Umbrales de advertencia
CPU_WARN = 60
CPU_CRIT = 85

# Configuración de pantalla
DSI_WIDTH = 800
DSI_HEIGHT = 480

# Scripts personalizados
LAUNCHERS = [
    {"label": "Mi Script", "script": "/path/to/script.sh"}
]
```

## 🎨 Personalización

### Colores
Los colores están centralizados en `config/settings.py`:

```python
COLORS = {
    "primary": "#00ffff",
    "secondary": "#14611E",
    "success": "#1ae313",
    "warning": "#ffaa00",
    "danger": "#ff3333",
    # ...
}
```

### Fuentes
Cambia la fuente en `config/settings.py`:

```python
FONT_FAMILY = "FiraMono Nerd Font"
FONT_SIZES = {
    "small": 14,
    "medium": 18,
    # ...
}
```

## 📁 Archivos de Estado

Los archivos de configuración se guardan automáticamente en `data/`:

- `fan_state.json`: Estado actual del control de ventiladores
- `fan_curve.json`: Curva personalizada de temperatura-PWM

## 🔧 Desarrollo

### Estructura de Módulos

#### Core (Lógica de Negocio)
- `FanController`: Gestión de ventiladores y curvas PWM
- `SystemMonitor`: Recolección de métricas del sistema
- `NetworkMonitor`: Estadísticas de red

#### Utils (Utilidades)
- `FileManager`: Gestión atómica de archivos JSON
- `SystemUtils`: Lectura de sensores y comandos del sistema

#### UI (Interfaz)
- Separación clara entre lógica y presentación
- Widgets reutilizables
- Estilos centralizados

### Agregar Nueva Funcionalidad

1. **Nueva métrica del sistema**:
   - Añade método a `SystemMonitor` en `core/`
   - Actualiza `MainWindow` para mostrar datos

2. **Nueva ventana**:
   - Crea clase en `ui/windows/`
   - Registra en `MainWindow`

3. **Nuevo widget**:
   - Crea en `ui/widgets/`
   - Exporta en `__init__.py`

## 🐛 Solución de Problemas

### No se detecta la temperatura
```bash
# Configura sensors
sudo sensors-detect
```

### Error de permisos en scripts
```bash
chmod +x scripts/*.sh
```

### Error de importación de módulos
```bash
# Asegúrate de ejecutar desde el directorio del proyecto
cd system_dashboard
python main.py
```

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📧 Contacto

Para preguntas o sugerencias, abre un issue en el repositorio.
