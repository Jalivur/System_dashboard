# 🗂️ Guía Paso a Paso: Añadir Monitor de Disco NVMe

Esta guía te enseñará a crear una ventana completa para monitorear el disco duro, incluyendo temperatura del NVMe.

---

## 📋 Índice de Pasos

1. [Detectar temperatura del NVMe](#paso-1-detectar-temperatura-del-nvme)
2. [Crear DiskMonitor en core/](#paso-2-crear-diskmonitor-en-core)
3. [Crear la ventana DiskWindow](#paso-3-crear-la-ventana-diskwindow)
4. [Añadir botón al menú principal](#paso-4-añadir-botón-al-menú-principal)
5. [Probar todo](#paso-5-probar-todo)

---

## 🎯 Objetivo Final

Crear una ventana que muestre:
- ✅ Uso de disco (%) - **Ya existe, reutilizar**
- ✅ Velocidad de lectura (MB/s) - **Ya existe, reutilizar**
- ✅ Velocidad de escritura (MB/s) - **Ya existe, reutilizar**
- 🆕 Temperatura del NVMe (°C) - **NUEVO**

---

## PASO 1: Detectar Temperatura del NVMe

### 📍 Archivo: `utils/system_utils.py`

### 🎯 Qué hacer:
Añadir una función para leer la temperatura del disco NVMe.

### 📝 Ubicación en el archivo:
Al final de la clase `SystemUtils`, después del método `run_script()`.

### 💻 Código a añadir:

```python
    @staticmethod
    def get_nvme_temp() -> float:
        """
        Obtiene la temperatura del disco NVMe
        
        Returns:
            Temperatura en °C o 0.0 si no se puede leer
        """
        try:
            # Método 1: Usar smartctl (requiere smartmontools)
            # sudo apt-get install smartmontools
            result = subprocess.run(
                ["sudo", "smartctl", "-a", "/dev/nvme0"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                # Buscar línea con "Temperature:"
                for line in result.stdout.split('\n'):
                    if 'Temperature:' in line or 'Temperature Sensor' in line:
                        # Extraer número
                        # Ejemplo: "Temperature:                        45 Celsius"
                        match = re.search(r'(\d+)\s*Celsius', line)
                        if match:
                            return float(match.group(1))
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        try:
            # Método 2: Leer desde sysfs (si existe)
            # Algunas Raspberry Pi exponen la temp del NVMe aquí
            temp_files = [
                "/sys/class/hwmon/hwmon*/temp1_input",
                "/sys/block/nvme0n1/device/hwmon/hwmon*/temp1_input"
            ]
            
            import glob
            for pattern in temp_files:
                for temp_file in glob.glob(pattern):
                    with open(temp_file, 'r') as f:
                        temp_millis = int(f.read().strip())
                        return temp_millis / 1000.0
        except (FileNotFoundError, ValueError, PermissionError):
            pass
        
        # Si no se pudo leer, retornar 0
        return 0.0
```

### 🔍 Explicación:

**¿Qué hace esta función?**
- Intenta leer la temperatura del NVMe usando `smartctl`
- Si falla, intenta leer de archivos del sistema (`sysfs`)
- Si todo falla, devuelve 0.0

**¿Por qué dos métodos?**
- `smartctl`: Más completo pero requiere instalar `smartmontools`
- `sysfs`: Integrado en el sistema pero no siempre disponible

**Imports necesarios:**
Ya están importados al inicio del archivo:
- `subprocess` ✅
- `re` ✅

Si falta `glob`, añade al inicio:
```python
import glob
```

### ⚙️ Preparación del sistema:

Para que funcione `smartctl`:
```bash
# Instalar smartmontools
sudo apt-get install smartmontools

# Dar permisos para ejecutar sin contraseña (opcional pero recomendado)
sudo visudo

# Añadir al final:
# tu_usuario ALL=(ALL) NOPASSWD: /usr/sbin/smartctl
```

### 🧪 Probar la función:

Crea un archivo `test_nvme.py` en la raíz del proyecto:

```python
#!/usr/bin/env python3
from utils.system_utils import SystemUtils

temp = SystemUtils.get_nvme_temp()
print(f"Temperatura NVMe: {temp}°C")

if temp == 0.0:
    print("⚠️ No se pudo leer la temperatura")
    print("Verifica:")
    print("  1. smartmontools instalado: sudo apt-get install smartmontools")
    print("  2. Disco es realmente NVMe: lsblk -d -o name,rota")
    print("  3. Permisos: sudo smartctl -a /dev/nvme0")
else:
    print("✅ Lectura correcta!")
```

Ejecutar:
```bash
python3 test_nvme.py
```

---

## PASO 2: Crear DiskMonitor en core/

### 📍 Archivo: `core/disk_monitor.py` (NUEVO)

### 🎯 Qué hacer:
Crear una clase que gestione todos los datos del disco (uso, I/O, temperatura).

### 💻 Código completo del archivo:

```python
"""
Monitor de disco
"""
from collections import deque
from typing import Dict
from config.settings import HISTORY
from utils.system_utils import SystemUtils
import psutil


class DiskMonitor:
    """Monitor de disco con historial"""
    
    def __init__(self):
        self.system_utils = SystemUtils()
        
        # Historiales (reutilizamos lo del SystemMonitor)
        self.usage_hist = deque(maxlen=HISTORY)
        self.read_hist = deque(maxlen=HISTORY)
        self.write_hist = deque(maxlen=HISTORY)
        self.nvme_temp_hist = deque(maxlen=HISTORY)  # NUEVO
        
        # Para calcular velocidad de I/O
        self.last_disk_io = psutil.disk_io_counters()
    
    def get_current_stats(self) -> Dict:
        """
        Obtiene estadísticas actuales del disco
        
        Returns:
            Diccionario con todas las métricas
        """
        # Uso de disco (%)
        disk_usage = psutil.disk_usage('/').percent
        
        # I/O (calcular velocidad)
        disk_io = psutil.disk_io_counters()
        read_bytes = max(0, disk_io.read_bytes - self.last_disk_io.read_bytes)
        write_bytes = max(0, disk_io.write_bytes - self.last_disk_io.write_bytes)
        self.last_disk_io = disk_io
        
        # Convertir a MB/s
        from config.settings import UPDATE_MS
        seconds = UPDATE_MS / 1000.0
        read_mb = (read_bytes / (1024 * 1024)) / seconds
        write_mb = (write_bytes / (1024 * 1024)) / seconds
        
        # Temperatura NVMe (NUEVO)
        nvme_temp = self.system_utils.get_nvme_temp()
        
        return {
            'usage': disk_usage,
            'read_mb': read_mb,
            'write_mb': write_mb,
            'nvme_temp': nvme_temp  # NUEVO
        }
    
    def update_history(self, stats: Dict) -> None:
        """
        Actualiza historiales con estadísticas actuales
        
        Args:
            stats: Diccionario con estadísticas
        """
        self.usage_hist.append(stats['usage'])
        self.read_hist.append(stats['read_mb'])
        self.write_hist.append(stats['write_mb'])
        self.nvme_temp_hist.append(stats['nvme_temp'])  # NUEVO
    
    def get_history(self) -> Dict:
        """
        Obtiene todos los historiales
        
        Returns:
            Diccionario con historiales
        """
        return {
            'usage': list(self.usage_hist),
            'read': list(self.read_hist),
            'write': list(self.write_hist),
            'nvme_temp': list(self.nvme_temp_hist)  # NUEVO
        }
    
    @staticmethod
    def level_color(value: float, warn: float, crit: float) -> str:
        """
        Determina color según nivel
        
        Args:
            value: Valor actual
            warn: Umbral de advertencia
            crit: Umbral crítico
            
        Returns:
            Color en formato hex
        """
        from config.settings import COLORS
        
        if value >= crit:
            return COLORS['danger']
        elif value >= warn:
            return COLORS['warning']
        else:
            return COLORS['primary']
```

### 🔍 Explicación:

**¿Qué hace cada método?**

1. **`__init__()`**: Inicializa los historiales (deques de 60 elementos)

2. **`get_current_stats()`**: 
   - Lee uso de disco con `psutil`
   - Calcula velocidad de lectura/escritura
   - **Lee temperatura NVMe** (NUEVO)
   - Devuelve todo en un diccionario

3. **`update_history()`**:
   - Añade valores actuales a los historiales
   - Automáticamente elimina el más viejo (maxlen=60)

4. **`get_history()`**:
   - Devuelve todos los historiales como listas
   - Para usar en las gráficas

5. **`level_color()`**:
   - Determina color según umbrales
   - Reutiliza el patrón del SystemMonitor

### 📦 Actualizar `core/__init__.py`:

Añade el nuevo monitor a las exportaciones:

```python
"""
Paquete core con lógica de negocio
"""
from .fan_controller import FanController
from .system_monitor import SystemMonitor
from .network_monitor import NetworkMonitor
from .disk_monitor import DiskMonitor  # NUEVO

__all__ = ['FanController', 'SystemMonitor', 'NetworkMonitor', 'DiskMonitor']  # NUEVO
```

---

## PASO 3: Crear la Ventana DiskWindow

### 📍 Archivo: `ui/windows/disk.py` (NUEVO)

### 🎯 Qué hacer:
Crear la ventana que muestre las gráficas del disco.

### 💻 Estructura del archivo:

```python
"""
Ventana de monitoreo de disco
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH,
                             DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS)
from ui.styles import make_futuristic_button
from ui.widgets import GraphWidget
from core.disk_monitor import DiskMonitor


class DiskWindow(ctk.CTkToplevel):
    """Ventana de monitoreo de disco"""
    
    def __init__(self, parent, disk_monitor: DiskMonitor):
        super().__init__(parent)
        
        # Referencias
        self.disk_monitor = disk_monitor
        
        # Widgets para actualización
        self.widgets = {}
        self.graphs = {}
        
        # Configurar ventana
        self.title("Monitor de Disco")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        
        # Crear interfaz
        self._create_ui()
        
        # Iniciar actualización
        self._update()
    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        # Frame principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Título
        title = ctk.CTkLabel(
            main,
            text="MONITOR DE DISCO",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold")
        )
        title.pack(pady=(10, 20))
        
        # Área de scroll
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Canvas y scrollbar
        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")
        
        from ui.styles import StyleManager
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Secciones (AQUÍ CREAS CADA SECCIÓN)
        self._create_usage_section(inner)       # Uso de disco
        self._create_read_section(inner)        # Lectura
        self._create_write_section(inner)       # Escritura
        self._create_nvme_temp_section(inner)   # Temperatura NVMe (NUEVO)
        
        # Botón cerrar
        bottom = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=10, padx=10)
        
        close_btn = make_futuristic_button(
            bottom,
            text="Cerrar",
            command=self.destroy,
            width=15,
            height=6
        )
        close_btn.pack(side="right", padx=5)
    
    def _create_usage_section(self, parent):
        """Crea la sección de uso de disco"""
        # TODO: Implementar (similar a MonitorWindow)
        # Frame con label, valor y gráfica
        pass
    
    def _create_read_section(self, parent):
        """Crea la sección de lectura"""
        # TODO: Implementar
        pass
    
    def _create_write_section(self, parent):
        """Crea la sección de escritura"""
        # TODO: Implementar
        pass
    
    def _create_nvme_temp_section(self, parent):
        """Crea la sección de temperatura NVMe"""
        # TODO: Implementar (NUEVO)
        # Similar a las otras pero con temperatura
        pass
    
    def _update(self):
        """Actualiza los datos del disco"""
        if not self.winfo_exists():
            return
        
        # Obtener estadísticas actuales
        stats = self.disk_monitor.get_current_stats()
        self.disk_monitor.update_history(stats)
        history = self.disk_monitor.get_history()
        
        # TODO: Actualizar cada sección con sus datos
        # self._update_usage(stats, history)
        # self._update_read(stats, history)
        # self._update_write(stats, history)
        # self._update_nvme_temp(stats, history)
        
        # Programar siguiente actualización
        self.after(UPDATE_MS, self._update)
```

### 📝 TU TAREA: Implementar las secciones

#### Sección 1: Uso de Disco

**Método a completar:** `_create_usage_section()`

**Patrón a seguir:** Ver `MonitorWindow._create_disk_usage_section()` en `ui/windows/monitor.py`

**Qué debe tener:**
```python
def _create_usage_section(self, parent):
    frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
    frame.pack(fill="x", pady=10, padx=10)
    
    # Label "USO DE DISCO"
    label = ctk.CTkLabel(...)
    
    # Valor "85.3 %"
    value_label = ctk.CTkLabel(...)
    
    # Gráfica
    graph = GraphWidget(frame, width=DSI_WIDTH-80, height=100)
    
    # Guardar referencias
    self.widgets['usage_label'] = label
    self.widgets['usage_value'] = value_label
    self.graphs['usage'] = {'widget': graph, 'max_val': 100}
```

#### Sección 2 y 3: Lectura y Escritura

**Patrón:** Igual que uso, pero con `read_mb` y `write_mb`

**Max val:** 50 MB/s (ajustable según tu disco)

#### Sección 4: Temperatura NVMe (NUEVA)

**Patrón:** Igual que las anteriores

**Importante:**
- Max val: 85°C (temperatura crítica NVMe)
- Umbrales:
  - Warning: 60°C
  - Critical: 70°C

**Ejemplo:**
```python
def _create_nvme_temp_section(self, parent):
    frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
    frame.pack(fill="x", pady=10, padx=10)
    
    # Label
    label = ctk.CTkLabel(
        frame,
        text="TEMPERATURA NVMe",
        text_color=COLORS['primary'],
        font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
    )
    label.pack(anchor="w", pady=(5, 0), padx=10)
    
    # Valor
    value_label = ctk.CTkLabel(
        frame,
        text="0.0 °C",
        text_color=COLORS['primary'],
        font=(FONT_FAMILY, FONT_SIZES['xlarge'])
    )
    value_label.pack(anchor="e", pady=(0, 5), padx=10)
    
    # Gráfica
    graph = GraphWidget(frame, width=DSI_WIDTH-80, height=100)
    graph.pack(pady=(0, 10))
    
    # Guardar referencias
    self.widgets['nvme_temp_label'] = label
    self.widgets['nvme_temp_value'] = value_label
    self.graphs['nvme_temp'] = {
        'widget': graph,
        'max_val': 85  # Temperatura máxima NVMe
    }
```

### 📝 TU TAREA: Implementar las actualizaciones

Completar el método `_update()`:

```python
def _update(self):
    if not self.winfo_exists():
        return
    
    stats = self.disk_monitor.get_current_stats()
    self.disk_monitor.update_history(stats)
    history = self.disk_monitor.get_history()
    
    # Uso de disco
    self._update_metric(
        'usage',
        stats['usage'],
        history['usage'],
        "%",
        60,  # warning
        80   # critical
    )
    
    # Lectura
    self._update_metric(
        'read',
        stats['read_mb'],
        history['read'],
        "MB/s",
        10,
        50
    )
    
    # Escritura
    self._update_metric(
        'write',
        stats['write_mb'],
        history['write'],
        "MB/s",
        10,
        50
    )
    
    # Temperatura NVMe (NUEVO)
    self._update_metric(
        'nvme_temp',
        stats['nvme_temp'],
        history['nvme_temp'],
        "°C",
        60,  # warning
        70   # critical
    )
    
    self.after(UPDATE_MS, self._update)

def _update_metric(self, key, value, history, unit, warn, crit):
    """Actualiza una métrica genérica"""
    # Determinar color
    color = self.disk_monitor.level_color(value, warn, crit)
    
    # Actualizar valor
    value_widget = self.widgets[f"{key}_value"]
    value_widget.configure(
        text=f"{value:.1f} {unit}",
        text_color=color
    )
    
    # Actualizar label
    label_widget = self.widgets[f"{key}_label"]
    label_widget.configure(text_color=color)
    
    # Actualizar gráfica
    graph_info = self.graphs[key]
    graph_info['widget'].update(history, graph_info['max_val'], color)
```

### 📦 Actualizar `ui/windows/__init__.py`:

```python
"""
Paquete de ventanas secundarias
"""
from .fan_control import FanControlWindow
from .monitor import MonitorWindow
from .network import NetworkWindow
from .usb import USBWindow
from .launchers import LaunchersWindow
from .theme_selector import ThemeSelector
from .disk import DiskWindow  # NUEVO

__all__ = [
    'FanControlWindow',
    'MonitorWindow', 
    'NetworkWindow',
    'USBWindow',
    'LaunchersWindow',
    'ThemeSelector',
    'DiskWindow'  # NUEVO
]
```

---

## PASO 4: Añadir Botón al Menú Principal

### 📍 Archivo: `ui/main_window.py`

### 🎯 Qué hacer:
Añadir el botón "Monitor Disco" y crear la instancia de DiskMonitor.

### Paso 4.1: Crear instancia de DiskMonitor

**Ubicación:** En `main.py`, línea ~23

**Buscar:**
```python
# Inicializar monitores
system_monitor = SystemMonitor()
fan_controller = FanController()
network_monitor = NetworkMonitor()
```

**Añadir:**
```python
# Inicializar monitores
system_monitor = SystemMonitor()
fan_controller = FanController()
network_monitor = NetworkMonitor()
disk_monitor = DiskMonitor()  # NUEVO
```

**Buscar:**
```python
# Crear interfaz
app = MainWindow(
    root,
    system_monitor=system_monitor,
    fan_controller=fan_controller,
    network_monitor=network_monitor,
    update_interval=UPDATE_MS
)
```

**Cambiar a:**
```python
# Crear interfaz
app = MainWindow(
    root,
    system_monitor=system_monitor,
    fan_controller=fan_controller,
    network_monitor=network_monitor,
    disk_monitor=disk_monitor,  # NUEVO
    update_interval=UPDATE_MS
)
```

### Paso 4.2: Actualizar constructor de MainWindow

**Ubicación:** `ui/main_window.py`, método `__init__()`

**Buscar:**
```python
def __init__(self, root, system_monitor, fan_controller, network_monitor, 
             update_interval=2000):
```

**Cambiar a:**
```python
def __init__(self, root, system_monitor, fan_controller, network_monitor,
             disk_monitor, update_interval=2000):  # NUEVO disk_monitor
```

**Buscar:**
```python
self.system_monitor = system_monitor
self.fan_controller = fan_controller
self.network_monitor = network_monitor
```

**Añadir:**
```python
self.system_monitor = system_monitor
self.fan_controller = fan_controller
self.network_monitor = network_monitor
self.disk_monitor = disk_monitor  # NUEVO
```

**Buscar:**
```python
# Referencias a ventanas secundarias
self.fan_window = None
self.monitor_window = None
self.network_window = None
self.usb_window = None
self.launchers_window = None
```

**Añadir:**
```python
# Referencias a ventanas secundarias
self.fan_window = None
self.monitor_window = None
self.network_window = None
self.usb_window = None
self.launchers_window = None
self.disk_window = None  # NUEVO
```

### Paso 4.3: Añadir botón al menú

**Ubicación:** `ui/main_window.py`, método `_create_menu_buttons()`

**Buscar:**
```python
buttons_config = [
    ("Control Ventiladores", self.open_fan_control),
    ("Monitor Placa", self.open_monitor_window),
    ("Monitor Red", self.open_network_window),
    ("Monitor USB", self.open_usb_window),
    ("Lanzadores", self.open_launchers),
    ("🎨 Cambiar Tema", self.open_theme_selector),
]
```

**Cambiar a:**
```python
buttons_config = [
    ("Control Ventiladores", self.open_fan_control),
    ("Monitor Placa", self.open_monitor_window),
    ("Monitor Red", self.open_network_window),
    ("💾 Monitor Disco", self.open_disk_window),  # NUEVO
    ("Monitor USB", self.open_usb_window),
    ("Lanzadores", self.open_launchers),
    ("🎨 Cambiar Tema", self.open_theme_selector),
]
```

### Paso 4.4: Crear método para abrir ventana

**Ubicación:** Al final de la clase `MainWindow`, después de `open_theme_selector()`

**Añadir:**
```python
def open_disk_window(self):
    """Abre la ventana de monitor de disco"""
    if self.disk_window is None or not self.disk_window.winfo_exists():
        from ui.windows.disk import DiskWindow
        self.disk_window = DiskWindow(
            self.root,
            self.disk_monitor
        )
    else:
        self.disk_window.lift()
```

---

## PASO 5: Probar Todo

### 🧪 Test 1: Temperatura NVMe

```bash
python3 test_nvme.py
```

**Resultado esperado:**
```
Temperatura NVMe: 45.0°C
✅ Lectura correcta!
```

### 🧪 Test 2: DiskMonitor

Crea `test_disk_monitor.py`:

```python
#!/usr/bin/env python3
from core.disk_monitor import DiskMonitor
import time

monitor = DiskMonitor()

for i in range(5):
    stats = monitor.get_current_stats()
    monitor.update_history(stats)
    
    print(f"\n=== Iteración {i+1} ===")
    print(f"Uso: {stats['usage']:.1f}%")
    print(f"Lectura: {stats['read_mb']:.2f} MB/s")
    print(f"Escritura: {stats['write_mb']:.2f} MB/s")
    print(f"Temp NVMe: {stats['nvme_temp']:.1f}°C")
    
    time.sleep(2)

print("\n✅ DiskMonitor funciona!")
```

Ejecutar:
```bash
python3 test_disk_monitor.py
```

### 🧪 Test 3: Ventana Completa

```bash
python3 main.py
```

**Verificar:**
1. ✅ Aparece botón "💾 Monitor Disco" en el menú
2. ✅ Al hacer clic, se abre la ventana
3. ✅ Se ven las 4 gráficas (uso, lectura, escritura, temp NVMe)
4. ✅ Los valores se actualizan cada 2 segundos
5. ✅ Los colores cambian según umbrales

---

## 📊 Checklist de Implementación

### Core:
- [ ] `utils/system_utils.py`: Añadida función `get_nvme_temp()`
- [ ] `core/disk_monitor.py`: Creado archivo completo
- [ ] `core/__init__.py`: Exportado `DiskMonitor`

### UI:
- [ ] `ui/windows/disk.py`: Creado archivo
- [ ] `ui/windows/disk.py`: Implementado `_create_usage_section()`
- [ ] `ui/windows/disk.py`: Implementado `_create_read_section()`
- [ ] `ui/windows/disk.py`: Implementado `_create_write_section()`
- [ ] `ui/windows/disk.py`: Implementado `_create_nvme_temp_section()`
- [ ] `ui/windows/disk.py`: Completado método `_update()`
- [ ] `ui/windows/__init__.py`: Exportado `DiskWindow`

### Main:
- [ ] `main.py`: Creada instancia de `DiskMonitor`
- [ ] `main.py`: Pasado `disk_monitor` a `MainWindow`
- [ ] `ui/main_window.py`: Actualizado `__init__()` con `disk_monitor`
- [ ] `ui/main_window.py`: Añadida referencia `self.disk_window`
- [ ] `ui/main_window.py`: Añadido botón en menú
- [ ] `ui/main_window.py`: Creado método `open_disk_window()`

### Testing:
- [ ] Temperatura NVMe se lee correctamente
- [ ] `DiskMonitor` funciona
- [ ] Ventana se abre sin errores
- [ ] Gráficas se actualizan
- [ ] Colores cambian según temperatura

---

## 💡 Consejos

### Si temperatura siempre es 0:

1. **Verifica que tienes un NVMe:**
```bash
lsblk -d -o name,rota
# Si rota=0, es SSD/NVMe
```

2. **Instala smartmontools:**
```bash
sudo apt-get install smartmontools
```

3. **Prueba smartctl manualmente:**
```bash
sudo smartctl -a /dev/nvme0 | grep Temperature
```

4. **Busca archivos de temperatura:**
```bash
find /sys -name "*temp*" 2>/dev/null | grep nvme
```

### Si hay errores de permisos:

```bash
# Dar permisos al usuario
sudo usermod -aG disk $USER

# O configurar sudoers
sudo visudo
# Añadir: tu_usuario ALL=(ALL) NOPASSWD: /usr/sbin/smartctl
```

### Para debugging:

Añade prints temporales:
```python
def get_nvme_temp():
    print("DEBUG: Intentando leer temperatura...")
    # ... tu código
    print(f"DEBUG: Temperatura leída: {temp}")
    return temp
```

---

## 📚 Referencias

**Archivos a copiar como ejemplo:**
- `ui/windows/monitor.py` - Para ver cómo crear secciones
- `core/system_monitor.py` - Para ver patrón de monitor
- `ui/widgets/graphs.py` - Para usar GraphWidget

**Documentación útil:**
- psutil disk: https://psutil.readthedocs.io/en/latest/#disks
- smartctl: `man smartctl`
- sysfs: `/sys/class/hwmon/`

---

¡Ahora tienes todo para implementarlo tú mismo! 🚀

¿Tienes dudas sobre algún paso específico?
