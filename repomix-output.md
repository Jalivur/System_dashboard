This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
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
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
config/
  __init__.py
  settings.py
  themes.py
core/
  __init__.py
  cleanup_service.py
  data_analyzer.py
  data_collection_service.py
  data_logger.py
  disk_monitor.py
  fan_auto_service.py
  fan_controller.py
  network_monitor.py
  process_monitor.py
  service_monitor.py
  system_monitor.py
  update_monitor.py
ui/
  widgets/
    __init__.py
    dialogs.py
    graphs.py
  windows/
    __init__.py
    disk.py
    fan_control.py
    history.py
    launchers.py
    monitor.py
    network.py
    process_window.py
    service.py
    theme_selector.py
    update.py
    usb.py
  __init__.py
  main_window.py
  styles.py
utils/
  __init__.py
  file_manager.py
  logger.py
  system_utils.py
.gitignore
COMPATIBILIDAD.md
create_desktop_launcher.sh
IDEAS_EXPANSION.md
INDEX.md
INSTALL_GUIDE.md
install_system.sh
install.sh
integration_fase1.py
INTEGRATION_GUIDE.md
main.py
migratelogger.sh
QUICKSTART.md
README.md
REQUIREMENTS.md
requirements.txt
setup.py
test_logging.py
THEMES_GUIDE.md
```

# Files

## File: core/cleanup_service.py
````python
"""
Servicio de limpieza automática de archivos exportados y datos antiguos
"""
import os
import glob
import threading
import time
from typing import Optional
from config.settings import DATA_DIR
from utils.logger import get_logger

logger = get_logger(__name__)


class CleanupService:
    """
    Servicio background que limpia periódicamente archivos exportados
    y datos antiguos de la base de datos.

    Características:
    - Singleton: Solo una instancia en toda la aplicación
    - Thread-safe: Seguro para concurrencia
    - Daemon: Se cierra automáticamente con el programa
    - Configurable: límites de archivos y antigüedad ajustables
    """

    _instance: Optional['CleanupService'] = None
    _lock = threading.Lock()

    # ── Configuración por defecto ─────────────────────────────────────────────
    DEFAULT_MAX_CSV        = 10      # Máx. archivos CSV a conservar
    DEFAULT_MAX_PNG        = 10      # Máx. archivos PNG a conservar
    DEFAULT_DB_DAYS        = 30      # Días de datos a conservar en BD
    DEFAULT_INTERVAL_HOURS = 24      # Cada cuántas horas limpiar

    def __new__(cls, *args, **kwargs):
        """Singleton: solo una instancia"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        data_logger=None,
        max_csv: int = DEFAULT_MAX_CSV,
        max_png: int = DEFAULT_MAX_PNG,
        db_days: int = DEFAULT_DB_DAYS,
        interval_hours: float = DEFAULT_INTERVAL_HOURS,
    ):
        """
        Inicializa el servicio (solo la primera vez).

        Args:
            data_logger:     Instancia de DataLogger para limpiar la BD.
                             Si es None, solo se limpian archivos.
            max_csv:         Número máximo de CSV exportados a conservar.
            max_png:         Número máximo de PNG exportados a conservar.
            db_days:         Días de histórico a conservar en la BD.
            interval_hours:  Horas entre ejecuciones del ciclo de limpieza.
        """
        if hasattr(self, '_initialized'):
            return

        self.data_logger    = data_logger
        self.max_csv        = max_csv
        self.max_png        = max_png
        self.db_days        = db_days
        self.interval_hours = interval_hours

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._initialized = True

        logger.info(
            f"[CleanupService] Configurado — "
            f"CSV: {max_csv}, PNG: {max_png}, "
            f"BD: {db_days}d, intervalo: {interval_hours}h"
        )

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self):
        """Inicia el servicio en segundo plano."""
        if self._running:
            logger.info("[CleanupService] Ya está corriendo")
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="CleanupService"
        )
        self._thread.start()
        logger.info("[CleanupService] Servicio iniciado")

    def stop(self):
        """Detiene el servicio."""
        if not self._running:
            return
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("[CleanupService] Servicio detenido")

    def _run(self):
        """Bucle principal: limpia al arrancar y luego cada interval_hours."""
        # Primera limpieza inmediata al arrancar
        self._cleanup_cycle()

        interval_seconds = self.interval_hours * 3600
        elapsed = 0.0
        while self._running:
            time.sleep(0.5)
            elapsed += 0.5
            if elapsed >= interval_seconds:
                self._cleanup_cycle()
                elapsed = 0.0

    # ── Lógica de limpieza ────────────────────────────────────────────────────

    def _cleanup_cycle(self):
        """Ejecuta un ciclo completo de limpieza."""
        logger.info("[CleanupService] Iniciando ciclo de limpieza")
        self.clean_csv()
        self.clean_png()
        if self.data_logger:
            self.clean_db()
        logger.info("[CleanupService] Ciclo de limpieza completado")

    def clean_csv(self, max_files: int = None) -> int:
        """
        Elimina los CSV exportados más antiguos que superen el límite.

        Args:
            max_files: Límite a aplicar. Si es None usa self.max_csv.

        Returns:
            Número de archivos eliminados.
        """
        limit = max_files if max_files is not None else self.max_csv
        pattern = os.path.join(str(DATA_DIR), "history_*.csv")
        return self._trim_files(pattern, limit, "CSV")

    def clean_png(self, max_files: int = None) -> int:
        """
        Elimina los PNG exportados más antiguos que superen el límite.

        Args:
            max_files: Límite a aplicar. Si es None usa self.max_png.

        Returns:
            Número de archivos eliminados.
        """
        limit = max_files if max_files is not None else self.max_png
        pattern = os.path.join(str(DATA_DIR), "screenshots", "*.png")
        return self._trim_files(pattern, limit, "PNG")

    def clean_db(self, days: int = None) -> bool:
        """
        Elimina registros de la BD más antiguos que 'days' días.

        Args:
            days: Antigüedad máxima. Si es None usa self.db_days.

        Returns:
            True si la limpieza fue exitosa.
        """
        if not self.data_logger:
            logger.warning("[CleanupService] No hay data_logger configurado")
            return False

        d = days if days is not None else self.db_days
        try:
            self.data_logger.clean_old_data(days=d)
            logger.info(f"[CleanupService] BD limpiada — registros >'{d}' días eliminados")
            return True
        except Exception as e:
            logger.error(f"[CleanupService] Error limpiando BD: {e}")
            return False

    def _trim_files(self, pattern: str, max_files: int, label: str) -> int:
        """
        Elimina los archivos más antiguos que superen max_files.

        Args:
            pattern:   Patrón glob de los archivos a gestionar.
            max_files: Número máximo a conservar.
            label:     Etiqueta para el log.

        Returns:
            Número de archivos eliminados.
        """
        try:
            files = sorted(glob.glob(pattern), key=os.path.getmtime)
            to_delete = files[:-max_files] if len(files) > max_files else []
            for f in to_delete:
                try:
                    os.remove(f)
                    logger.info(f"[CleanupService] {label} eliminado: {os.path.basename(f)}")
                except Exception as e:
                    logger.warning(f"[CleanupService] No se pudo eliminar {f}: {e}")
            if to_delete:
                logger.info(
                    f"[CleanupService] {label}: {len(to_delete)} eliminados, "
                    f"{len(files) - len(to_delete)} conservados"
                )
            return len(to_delete)
        except Exception as e:
            logger.error(f"[CleanupService] Error en _trim_files ({label}): {e}")
            return 0

    # ── Información y estado ──────────────────────────────────────────────────

    def get_status(self) -> dict:
        """
        Devuelve el estado actual del servicio.

        Returns:
            Diccionario con configuración y estado del hilo.
        """
        csv_files = glob.glob(os.path.join(str(DATA_DIR), "history_*.csv"))
        png_files = glob.glob(os.path.join(str(DATA_DIR), "screenshots", "*.png"))
        return {
            'running':        self._running,
            'thread_alive':   self._thread.is_alive() if self._thread else False,
            'interval_hours': self.interval_hours,
            'max_csv':        self.max_csv,
            'max_png':        self.max_png,
            'db_days':        self.db_days,
            'csv_count':      len(csv_files),
            'png_count':      len(png_files),
        }

    def force_cleanup(self) -> dict:
        """
        Fuerza un ciclo de limpieza inmediato desde fuera del hilo.
        Útil para llamadas manuales desde la UI.

        Returns:
            Diccionario con el número de archivos eliminados y resultado de BD.
        """
        logger.info("[CleanupService] Limpieza forzada manualmente")
        deleted_csv = self.clean_csv()
        deleted_png = self.clean_png()
        db_ok = self.clean_db() if self.data_logger else False
        logger.info(
            f"[CleanupService] Limpieza manual completada — "
            f"CSV: {deleted_csv}, PNG: {deleted_png}, BD: {db_ok}"
        )
        return {'deleted_csv': deleted_csv, 'deleted_png': deleted_png, 'db_ok': db_ok}

    def is_running(self) -> bool:
        """Verifica si el servicio está corriendo."""
        return self._running
````

## File: ui/widgets/graphs.py
````python
"""
Widgets para gráficas y visualización
"""
import customtkinter as ctk
from typing import List
from config.settings import GRAPH_WIDTH, GRAPH_HEIGHT


class GraphWidget:
    """Widget para gráficas de línea"""
    
    def __init__(self, parent, width: int = None, height: int = None):
        """
        Inicializa el widget de gráfica
        
        Args:
            parent: Widget padre
            width: Ancho del canvas
            height: Alto del canvas
        """
        self.width = width or GRAPH_WIDTH
        self.height = height or GRAPH_HEIGHT
        
        self.canvas = ctk.CTkCanvas(
            parent, 
            width=self.width, 
            height=self.height,
            bg="#111111", 
            highlightthickness=0
        )
        
        self.lines = []
        self._create_lines()
    
    def _create_lines(self) -> None:
        """Crea las líneas en el canvas"""
        self.lines = [
            self.canvas.create_line(0, 0, 0, 0, fill="#00ffff", width=2)
            for _ in range(self.width)
        ]
    
    def update(self, data: List[float], max_val: float, color: str = "#00ffff") -> None:
        """
        Actualiza la gráfica con nuevos datos
        
        Args:
            data: Lista de valores a graficar
            max_val: Valor máximo para normalización
            color: Color de las líneas
        """
        if not data or max_val <= 0:
            return
        
        n = len(data)
        if n < 2:
            return
        
        # Calcular puntos
        x_step = self.width / max(n - 1, 1)
        
        for i in range(min(n - 1, len(self.lines))):
            val1 = max(0, min(max_val, data[i]))
            val2 = max(0, min(max_val, data[i + 1]))
            
            y1 = self.height - (val1 / max_val) * self.height
            y2 = self.height - (val2 / max_val) * self.height
            
            x1 = i * x_step
            x2 = (i + 1) * x_step
            
            self.canvas.coords(self.lines[i], x1, y1, x2, y2)
            self.canvas.itemconfig(self.lines[i], fill=color)
    
    def recolor(self, color: str) -> None:
        """
        Cambia el color de todas las líneas
        
        Args:
            color: Nuevo color
        """
        for line in self.lines:
            self.canvas.itemconfig(line, fill=color)
    
    def pack(self, **kwargs):
        """Pack del canvas"""
        self.canvas.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid del canvas"""
        self.canvas.grid(**kwargs)


def update_graph_lines(canvas, lines: List, data: List[float], max_val: float) -> None:
    """
    Actualiza líneas de gráfica (función legacy para compatibilidad)
    
    Args:
        canvas: Canvas de tkinter
        lines: Lista de IDs de líneas
        data: Datos a graficar
        max_val: Valor máximo
    """
    if not data or max_val <= 0:
        return
    
    n = len(data)
    if n < 2:
        return
    
    width = canvas.winfo_width() or GRAPH_WIDTH
    height = canvas.winfo_height() or GRAPH_HEIGHT
    
    x_step = width / max(n - 1, 1)
    
    for i in range(min(n - 1, len(lines))):
        val1 = max(0, min(max_val, data[i]))
        val2 = max(0, min(max_val, data[i + 1]))
        
        y1 = height - (val1 / max_val) * height
        y2 = height - (val2 / max_val) * height
        
        x1 = i * x_step
        x2 = (i + 1) * x_step
        
        canvas.coords(lines[i], x1, y1, x2, y2)


def recolor_lines(canvas, lines: List, color: str) -> None:
    """
    Cambia el color de las líneas (función legacy)
    
    Args:
        canvas: Canvas de tkinter
        lines: Lista de IDs de líneas
        color: Nuevo color
    """
    for line in lines:
        canvas.itemconfig(line, fill=color)
````

## File: ui/__init__.py
````python

````

## File: .gitignore
````
# ============================================
# System Dashboard - .gitignore
# ============================================
# 
# Excluye archivos temporales, compilados, 
# datos personales y configuraciones locales
#
# ============================================

# ============================================
# Python
# ============================================

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Virtual Environments
venv/
env/
ENV/
env.bak/
venv.bak/
.venv/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/


# ============================================
# IDEs y Editores
# ============================================

# VSCode
.vscode/
*.code-workspace

# PyCharm
.idea/
*.iml
*.iws

# Sublime Text
*.sublime-project
*.sublime-workspace

# Vim
*.swp
*.swo
*~
.*.sw[op]

# Emacs
*~
\#*\#
.\#*

# Nano
*.save
*.swp


# ============================================
# Sistema Operativo
# ============================================

# macOS
.DS_Store
.AppleDouble
.LSOverride
Icon
._*
.DocumentRevisions-V100
.fseventsd
.Spotlight-V100
.TemporaryItems
.Trashes
.VolumeIcon.icns
.com.apple.timemachine.donotpresent

# Windows
Thumbs.db
Thumbs.db:encryptable
ehthumbs.db
ehthumbs_vista.db
*.stackdump
[Dd]esktop.ini
$RECYCLE.BIN/
*.cab
*.msi
*.msix
*.msm
*.msp
*.lnk

# Linux
.directory
.Trash-*
.nfs*


# ============================================
# Archivos del Proyecto
# ============================================

# Datos persistentes y estado
data/
!data/.gitkeep
*.json
!requirements.json
!package.json
fan_state.json
fan_curve.json
theme_config.json

# Logs
*.log
logs/
*.log.*

# Archivos temporales
*.tmp
*.temp
*.bak
*.backup
*~
.~*

# Scripts personales del usuario
scripts/
!scripts/.gitkeep
!scripts/README.md

# Configuración local
.env
.env.local
.env.*.local
config.local.py
settings.local.py


# ============================================
# Documentación y Builds
# ============================================

# Sphinx documentation
docs/_build/
docs/_static/
docs/_templates/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py


# ============================================
# Específico del Dashboard
# ============================================

# Capturas de pantalla de desarrollo
screenshots/
*.png
*.jpg
*.jpeg
!docs/images/
!assets/images/

# Archivos de calibración de hardware
calibration/
*.calibration

# Datos de sensores históricos
sensor_data/
historical_data/

# Backups automáticos
backups/
*.backup

# Testing local
test_output/
test_results/


# ============================================
# Dependencias y Builds
# ============================================

# Node modules (si usas Node para algo)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
package-lock.json
yarn.lock

# Compiled files
*.pyc
*.pyo
*.pyd


# ============================================
# Git
# ============================================

# Parches
*.patch
*.diff

# Merge files
*.orig


# ============================================
# Archivos Sensibles
# ============================================

# API Keys y Secretos
secrets.py
secrets.json
.secrets
api_keys.txt
credentials.json

# SSH Keys
*.pem
*.key
id_rsa
id_rsa.pub

# Certificados
*.crt
*.cer
*.p12


# ============================================
# Base de Datos
# ============================================

# SQLite
*.db
*.sqlite
*.sqlite3
*.db-journal


# ============================================
# Compresión y Empaquetado
# ============================================

# Archives
*.zip
*.tar
*.tar.gz
*.tgz
*.rar
*.7z
*.bz2
*.gz
*.xz

# Pero MANTENER releases
!releases/*.zip
!dist/*.tar.gz


# ============================================
# Excepciones (Archivos a INCLUIR)
# ============================================

# Mantener estructura de directorios vacíos
!**/.gitkeep

# Mantener ejemplos y templates
!examples/
!templates/

# Mantener archivos de configuración base
!config/settings.py
!config/themes.py

# Mantener documentación
!*.md
!docs/

# Mantener requirements
!requirements.txt
!requirements-dev.txt


# ============================================
# Testing y CI/CD
# ============================================

# pytest
.pytest_cache/
.coverage

# tox
.tox/

# Coverage reports
htmlcov/

# GitHub Actions
.github/workflows/*.log


# ============================================
# Varios
# ============================================

# Thumbnails
*.thumb

# Profile data
*.prof

# Session data
.session

# PID files
*.pid


# ============================================
# NOTAS IMPORTANTES
# ============================================
#
# - Este .gitignore está diseñado para:
#   * Excluir archivos temporales y compilados
#   * Proteger datos sensibles (API keys, passwords)
#   * Mantener limpio el repositorio
#   * Permitir configuración local sin conflictos
#
# - Los datos en data/ NO se suben (configuraciones locales)
# - Los scripts en scripts/ NO se suben (personalizados)
# - Los logs NO se suben
#
# - Para INCLUIR algo que está ignorado:
#   git add -f archivo.txt
#
# ============================================
````

## File: COMPATIBILIDAD.md
````markdown
# 🌐 Compatibilidad Multiplataforma - Resumen

## 🎯 ¿En qué sistemas funciona?

### ✅ Funciona al 100% (TODO)
- **Raspberry Pi OS** (Raspbian)
- **Kali Linux** (en Raspberry Pi)

### ✅ Funciona al ~85% (sin control de ventiladores)
- **Ubuntu** (20.04, 22.04, 23.04+)
- **Debian** (11, 12+)
- **Linux Mint**
- **Fedora, CentOS, RHEL**
- **Arch Linux, Manjaro**

---

## 📊 Tabla de Compatibilidad

| Componente | Raspberry Pi | Otros Linux | Notas |
|------------|--------------|-------------|-------|
| **Interfaz gráfica** | ✅ | ✅ | 100% compatible |
| **Monitor sistema** | ✅ | ✅ | CPU, RAM, Temp, Disco |
| **Monitor red** | ✅ | ✅ | Download, Upload, Speedtest |
| **Monitor USB** | ✅ | ✅ | Con dependencias |
| **Lanzadores** | ✅ | ✅ | Scripts bash |
| **Temas** | ✅ | ✅ | 15 temas |
| **Control ventiladores** | ✅ | ❌ | Solo con GPIO |

---

## 🔧 Dependencias por Sistema

### Ubuntu/Debian/Raspberry Pi:
```bash
sudo apt-get install lm-sensors usbutils udisks2
pip3 install --break-system-packages customtkinter psutil
```

### Fedora/RHEL:
```bash
sudo dnf install lm-sensors usbutils udisks2
pip3 install customtkinter psutil
```

### Arch Linux:
```bash
sudo pacman -S lm-sensors usbutils udisks2
pip3 install customtkinter psutil
```

---

## ⚠️ Limitación: Control de Ventiladores

El control de ventiladores PWM **SOLO funciona en Raspberry Pi** porque requiere:
- GPIO pins
- Hardware específico
- Librería de control GPIO

**En otros sistemas Linux:** El botón de ventiladores no funcionará, pero el resto del dashboard (85%) funciona perfectamente.

---

## 💡 Uso Recomendado

- **Raspberry Pi:** Usa TODO al 100%
- **Ubuntu/Debian Desktop:** Monitor de sistema completo (sin ventiladores)
- **Servidores:** Requiere X11 para la interfaz gráfica
- **Kali Linux (RPi):** Funciona al 100% igual que Raspbian

---

## 🚀 Verificación Rápida

```bash
# Verificar Python
python3 --version  # Debe ser 3.8+

# Verificar temperatura
sensors  # o vcgencmd measure_temp

# Verificar USB
lsusb
lsblk
```

---

**Conclusión:** El dashboard funciona en cualquier Linux con interfaz gráfica. Solo el control de ventiladores es específico de Raspberry Pi con GPIO.
````

## File: create_desktop_launcher.sh
````bash
#!/bin/bash

# Script para crear lanzador de escritorio
# Para Sistema de Monitoreo

CURRENT_DIR=$(pwd)
DESKTOP_FILE="$HOME/.local/share/applications/system-dashboard.desktop"
ICON_FILE="$CURRENT_DIR/dashboard_icon.png"

echo "Creando lanzador de escritorio..."

# Crear directorio si no existe
mkdir -p "$HOME/.local/share/applications"

# Crear archivo .desktop
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=System Dashboard
Comment=Monitor del sistema con control de ventiladores
Exec=python3 $CURRENT_DIR/main.py
Path=$CURRENT_DIR
Icon=utilities-system-monitor
Terminal=false
Categories=System;Monitor;
Keywords=monitor;cpu;ram;temperature;fan;
StartupNotify=false
EOF

echo "✓ Lanzador creado en: $DESKTOP_FILE"
echo ""
echo "Ahora puedes:"
echo "  1. Buscar 'System Dashboard' en el menú de aplicaciones"
echo "  2. O ejecutar directamente: python3 main.py"
echo ""

# Preguntar si quiere autostart
read -p "¿Quieres que inicie automáticamente al encender? (s/n): " autostart
if [[ "$autostart" == "s" || "$autostart" == "S" ]]; then
    AUTOSTART_DIR="$HOME/.config/autostart"
    mkdir -p "$AUTOSTART_DIR"
    cp "$DESKTOP_FILE" "$AUTOSTART_DIR/"
    echo "✓ Configurado para iniciar automáticamente"
fi

echo ""
echo "¡Listo! 🎉"
````

## File: INSTALL_GUIDE.md
````markdown
# 🔧 Guía de Instalación Completa

Guía detallada para instalar el Dashboard en cualquier sistema Linux.

---

## 🎯 Sistemas Soportados

### ✅ **Soporte Completo (100%)**
- Raspberry Pi OS (Bullseye, Bookworm)
- Kali Linux (en Raspberry Pi)

### ✅ **Soporte Parcial (~85%)**
- Ubuntu (20.04, 22.04, 23.04+, 24.04)
- Debian (11, 12+)
- Linux Mint
- Fedora / CentOS / RHEL
- Arch Linux / Manjaro

**Nota**: En sistemas no-Raspberry Pi, el control de ventiladores PWM puede no funcionar. Todo lo demás funciona perfectamente.

---

## ⚡ Método 1: Instalación Automática (Recomendado)

### **Script de Instalación**

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard

# 2. Dar permisos y ejecutar
chmod +x install.sh
./install.sh

# 3. Ejecutar
python3 main.py
```

**El script instalará automáticamente:**
- ✅ Dependencias del sistema (python3-pip, python3-tk, lm-sensors)
- ✅ Dependencias Python (customtkinter, psutil, Pillow)
- ✅ Speedtest-cli (opcional)
- ✅ Configurará sensores

---

## 🛠️ Método 2: Instalación Manual con Entorno Virtual

### **Paso 1: Instalar Dependencias del Sistema**

```bash
# Actualizar repositorios
sudo apt update

# Instalar herramientas básicas
sudo apt install -y python3 python3-pip python3-venv python3-tk git

# Instalar lm-sensors para temperatura
sudo apt install -y lm-sensors

# Opcional: Speedtest
sudo apt install -y speedtest-cli

# Detectar sensores (primera vez)
sudo sensors-detect --auto
```

### **Paso 2: Clonar Repositorio**

```bash
cd ~
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard
```

### **Paso 3: Crear Entorno Virtual**

```bash
# Crear venv
python3 -m venv venv

# Activar venv
source venv/bin/activate

# Tu prompt debería cambiar a: (venv) user@host:~$
```

### **Paso 4: Instalar Dependencias Python**

```bash
# Dentro del venv
pip install --upgrade pip
pip install -r requirements.txt
```

### **Paso 5: Ejecutar**

```bash
# Asegurarte que el venv está activo
source venv/bin/activate

# Ejecutar
python3 main.py
```

### **Paso 6: Crear Launcher (Opcional)**

```bash
# Para ejecutar sin activar venv manualmente
chmod +x create_desktop_launcher.sh
./create_desktop_launcher.sh
```

---

## 🚀 Método 3: Instalación Sin Entorno Virtual

**⚠️ Advertencia**: En Ubuntu 23.04+ y Debian 12+ necesitarás usar `--break-system-packages` o el script automático.

### **Opción A: Usar Script Automático** ⭐

```bash
cd system-dashboard
sudo ./install_system.sh
```

### **Opción B: Manual**

```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install -y python3 python3-pip python3-tk lm-sensors speedtest-cli

# Instalar dependencias Python (método según tu sistema)
```

#### **En sistemas antiguos (Ubuntu 22.04, Debian 11):**
```bash
pip install -r requirements.txt
```

#### **En sistemas modernos (Ubuntu 23.04+, Debian 12+):**
```bash
pip install -r requirements.txt --break-system-packages
```

**O usar pipx:**
```bash
sudo apt install pipx
pipx install customtkinter
pipx install psutil
pipx install Pillow
```

### **Ejecutar**

```bash
python3 main.py
```

---

## 🐛 Solución de Problemas

### **Error: externally-managed-environment**

**Síntoma:**
```
error: externally-managed-environment
```

**Causa**: Sistema moderno (Ubuntu 23.04+, Debian 12+) que protege paquetes del sistema.

**Soluciones:**

1. **Opción 1: Usar venv** (Recomendado)
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Opción 2: Usar --break-system-packages**
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```

3. **Opción 3: Usar pipx**
   ```bash
   sudo apt install pipx
   pipx install customtkinter psutil Pillow
   ```

---

### **Error: ModuleNotFoundError: No module named 'customtkinter'**

**Causa**: Dependencias no instaladas.

**Solución:**
```bash
# Si usas venv
source venv/bin/activate
pip install customtkinter

# Si no usas venv
pip install customtkinter --break-system-packages
```

---

### **Error: No se detecta temperatura**

**Síntoma:**
```
Temp: N/A
```

**Solución:**
```bash
# Detectar sensores
sudo sensors-detect --auto

# Reiniciar servicio
sudo systemctl restart lm-sensors

# Verificar que funciona
sensors
# Debería mostrar: coretemp-isa-0000, etc.
```

**Si aún no funciona:**
```bash
# Cargar módulos manualmente
sudo modprobe coretemp
```

---

### **Error: Ventiladores no responden**

**Causa**: Pin GPIO incorrecto o sin permisos.

**Solución:**

1. **Verificar pin:**
   ```bash
   gpio readall
   # Verificar que PWM_PIN=18 corresponde a un pin PWM
   ```

2. **Probar con sudo** (temporal):
   ```bash
   sudo python3 main.py
   ```

3. **Añadir usuario a grupo gpio** (permanente):
   ```bash
   sudo usermod -a -G gpio $USER
   # Cerrar sesión y volver a entrar
   ```

---

### **Error: ImportError: libGL.so.1**

**Causa**: Falta librería OpenGL.

**Solución:**
```bash
sudo apt install -y libgl1-mesa-glx
```

---

### **Error: Speedtest no funciona**

**Causa**: speedtest-cli no instalado.

**Solución:**
```bash
sudo apt install speedtest-cli

# Verificar
speedtest-cli --version
```

---

### **Error: No se ve la ventana**

**Causa**: Posición incorrecta.

**Solución**: Editar `config/settings.py`:
```python
DSI_X = 0  # Cambiar según tu pantalla
DSI_Y = 0
DSI_WIDTH = 800   # Ajustar a tu resolución
DSI_HEIGHT = 480
```

---

## 📦 Dependencias Completas

### **Dependencias del Sistema:**
```bash
python3          # >= 3.8
python3-pip      # Gestor de paquetes
python3-venv     # Entornos virtuales (opcional)
python3-tk       # Tkinter
lm-sensors       # Lectura de sensores
speedtest-cli    # Tests de velocidad (opcional)
git              # Control de versiones
```

### **Dependencias Python:**
```
customtkinter==5.2.0    # UI moderna
psutil==5.9.5           # Info del sistema
Pillow==10.0.0          # Procesamiento de imágenes
```

---

## 🔐 Permisos

### **GPIO (para ventiladores):**

```bash
# Añadir usuario a grupos necesarios
sudo usermod -a -G gpio,i2c,spi $USER

# Cerrar sesión y volver a entrar
```

### **Ejecutar sin sudo:**

El dashboard debería funcionar sin sudo, excepto:
- Control de ventiladores (requiere acceso GPIO)
- Algunos scripts en Lanzadores

---

## 🚀 Autoarranque (Opcional)

### **Método 1: systemd**

```bash
# Crear servicio
sudo nano /etc/systemd/system/dashboard.service
```

Contenido:
```ini
[Unit]
Description=System Dashboard
After=graphical.target

[Service]
Type=simple
User=tu-usuario
WorkingDirectory=/home/tu-usuario/system-dashboard
ExecStart=/home/tu-usuario/system-dashboard/venv/bin/python3 main.py
Restart=on-failure

[Install]
WantedBy=graphical.target
```

Activar:
```bash
sudo systemctl enable dashboard.service
sudo systemctl start dashboard.service
```

---

### **Método 2: autostart**

```bash
# Crear archivo autostart
mkdir -p ~/.config/autostart
nano ~/.config/autostart/dashboard.desktop
```

Contenido:
```ini
[Desktop Entry]
Type=Application
Name=System Dashboard
Exec=/home/tu-usuario/system-dashboard/venv/bin/python3 /home/tu-usuario/system-dashboard/main.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
```

---

## 🧪 Verificación de Instalación

### **Test completo:**

```bash
# 1. Verificar Python
python3 --version  # Debe ser >= 3.8

# 2. Verificar módulos
python3 -c "import customtkinter; print('CustomTkinter OK')"
python3 -c "import psutil; print('psutil OK')"
python3 -c "import PIL; print('Pillow OK')"

# 3. Verificar sensores
sensors  # Debe mostrar temperaturas

# 4. Verificar speedtest
speedtest-cli --version

# 5. Ejecutar dashboard
python3 main.py
```

---

## 💡 Tips de Instalación

1. **Usa el script automático** si es tu primera vez
2. **Usa venv** si quieres mantener el sistema limpio
3. **No uses sudo** para instalar paquetes Python (usa venv)
4. **Detecta sensores** la primera vez con `sudo sensors-detect`
5. **Revisa los logs** si algo falla: `journalctl -xe`

---

## 📊 Tiempos de Instalación

| Método | Tiempo | Dificultad |
|--------|--------|------------|
| Script automático | ~5 min | ⭐ Fácil |
| Manual con venv | ~10 min | ⭐⭐ Media |
| Manual sin venv | ~8 min | ⭐⭐ Media |

---

## 🆘 Ayuda Adicional

**¿Problemas con la instalación?**

1. Revisa esta guía completa
2. Verifica [QUICKSTART.md](QUICKSTART.md) para problemas comunes
3. Revisa [README.md](README.md) sección Troubleshooting
4. Abre un Issue en GitHub con:
   - Sistema operativo y versión
   - Versión de Python
   - Mensaje de error completo
   - Comando que ejecutaste

---

**¡Instalación completa!** 🎉
````

## File: install_system.sh
````bash
#!/bin/bash

# Script de instalación DIRECTA en el sistema (sin venv)
# Para Sistema de Monitoreo

echo "==================================="
echo "System Dashboard - Instalación"
echo "Instalación DIRECTA en el sistema"
echo "==================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instala Python 3.8+"
    exit 1
fi

echo "✓ Python encontrado: $(python3 --version)"

# Instalar dependencias del sistema
echo ""
echo "Instalando dependencias del sistema..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-tk lm-sensors

# Opcional: speedtest
read -p "¿Instalar speedtest-cli? (s/n): " install_speedtest
if [[ "$install_speedtest" == "s" || "$install_speedtest" == "S" ]]; then
    sudo apt-get install -y speedtest-cli
fi

# Instalar dependencias Python DIRECTAMENTE en el sistema
echo ""
echo "Instalando dependencias de Python en el sistema..."

# Usar --break-system-packages para sistemas modernos
echo "Usando --break-system-packages (necesario en Ubuntu 23.04+/Debian 12+)..."
sudo pip3 install --break-system-packages customtkinter psutil

# Alternativa: Si lo anterior falla, instalar para el usuario
if [ $? -ne 0 ]; then
    echo "Instalación con sudo falló, intentando instalación de usuario..."
    pip3 install --user --break-system-packages customtkinter psutil
fi

# Configurar sensors (opcional)
echo ""
read -p "¿Configurar sensors para lectura de temperatura? (s/n): " config_sensors
if [[ "$config_sensors" == "s" || "$config_sensors" == "S" ]]; then
    echo "Configurando sensors..."
    sudo sensors-detect --auto
fi

echo ""
echo "==================================="
echo "✓ Instalación completada"
echo "==================================="
echo ""
echo "Para ejecutar el dashboard:"
echo "  python3 main.py"
echo ""
echo "O crear un lanzador de escritorio (recomendado):"
echo "  ./create_desktop_launcher.sh"
echo ""
````

## File: install.sh
````bash
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
````

## File: integration_fase1.py
````python
import time
import psutil
import subprocess
from PIL import Image, ImageDraw, ImageFont
import os
import sys
sys.path.append("/home/jalivur/Documents/proyectopantallas")
from Code.expansion import Expansion
from Code.oled import OLED
import json
import os
import signal

# ========================================
# CONFIGURACIÓN INTEGRADA CON EL DASHBOARD
# ========================================

# Ruta al archivo de estado del dashboard
# Cambia esto a donde extraigas el proyecto system_dashboard
STATE_FILE = "/ruta/a/system_dashboard/data/fan_state.json"

# Ejemplo si lo pones en tu home:
# STATE_FILE = "/home/jalivur/system_dashboard/data/fan_state.json"

# Ejemplo si lo pones en Documents:
# STATE_FILE = "/home/jalivur/Documents/system_dashboard/data/fan_state.json"


# ========================================
# FUNCIONES
# ========================================

def read_fan_state():
    """Lee el estado de los ventiladores guardado por el dashboard"""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return None


stop_flag = False

def handle_exit(signum, frame):
    """Maneja la señal de salida limpia"""
    global stop_flag
    print(f"Señal {signum} recibida, saliendo...")
    stop_flag = True

# Capturar SIGTERM (pkill normal) y SIGINT (Ctrl+C)
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)


def get_cpu_temp():
    """Obtiene temperatura de la CPU"""
    temp = subprocess.check_output(
        ["vcgencmd", "measure_temp"]
    ).decode()
    return float(temp.replace("temp=", "").replace("'C\n", ""))


def fan_curve(temp):
    """Curva de ventilador por defecto (fallback)"""
    if temp < 40:
        return 40
    elif temp > 75:
        return 255
    else:
        return int((temp - 40) * (215 / 35) + 40)


def temp_to_color(temp):
    """Convierte temperatura a color RGB para LEDs"""
    if temp < 40:
        return (0, 255, 0)  # Verde
    elif temp > 75:
        return (255, 0, 0)  # Rojo
    else:
        ratio = (temp - 40) / 35
        r = int(255 * ratio)
        g = int(255 * (1 - ratio))
        return (r, g, 0)  # Degradado verde->amarillo->rojo


def smooth(prev, target, step=10):
    """Suaviza transición de colores"""
    return tuple(
        prev[i] + max(-step, min(step, target[i] - prev[i]))
        for i in range(3)
    )


def get_ip():
    """Obtiene IP principal"""
    for _ in range(10):  # hasta 10 intentos
        ip_output = subprocess.getoutput("hostname -I").split()
        if ip_output:
            return ip_output[0]
        time.sleep(1)
    return "No IP"


def get_ip_of_interface(iface_name="tun0"):
    """Obtiene IP de una interfaz específica (ej: VPN)"""
    addrs = psutil.net_if_addrs()
    if iface_name in addrs:
        for addr in addrs[iface_name]:
            if addr.family.name == "AF_INET":  # IPv4
                return addr.address
    return "No IP"


# ========================================
# INICIALIZACIÓN
# ========================================

board = Expansion()
oled = OLED()
oled.clear()
font = ImageFont.load_default()

# Estado anterior para optimizar actualizaciones OLED
last_state = {
    "cpu": None,
    "ram": None,
    "temp": None,
    "ip": None,
    "tun_ip": None,
    "fan0_duty": None,
    "fan1_duty": None
}


def draw_oled_smart(cpu, ram, temp, ip, tun_ip, fan0_duty, fan1_duty):
    """
    Dibuja en OLED solo si hay cambios
    Optimiza para reducir parpadeos
    """
    changed = (
        round(cpu, 1) != last_state["cpu"] or
        round(ram, 1) != last_state["ram"] or
        int(temp) != last_state["temp"] or
        ip != last_state["ip"] or
        tun_ip != last_state["tun_ip"] or
        fan0_duty != last_state["fan0_duty"] or
        fan1_duty != last_state["fan1_duty"]
    )

    if not changed:
        return

    oled.clear()
    oled.draw_text(f"CPU: {cpu:>5.1f} %", (0, 0))
    oled.draw_text(f"RAM: {ram:>5.1f} %", (0, 12))
    oled.draw_text(f"TEMP:{temp:>5.1f} C", (0, 24))
    oled.draw_text(f"IP: {ip}", (0, 36))
    
    # Mostrar IP VPN o estado ventiladores
    if tun_ip != "No IP":
        oled.draw_text(f"VPN: {tun_ip}", (0, 48))
    else:
        oled.draw_text(f"Fan1:{fan0_duty}% Fan2:{fan1_duty}%", (0, 48))
    
    oled.show()

    # Guardar estado
    last_state["cpu"] = round(cpu, 1)
    last_state["ram"] = round(ram, 1)
    last_state["temp"] = int(temp)
    last_state["ip"] = ip
    last_state["tun_ip"] = tun_ip
    last_state["fan0_duty"] = fan0_duty
    last_state["fan1_duty"] = fan1_duty


# ========================================
# BUCLE PRINCIPAL
# ========================================

try:
    print("Iniciando monitor OLED + Control de ventiladores...")
    print(f"Leyendo estado desde: {STATE_FILE}")
    
    board.set_fan_mode(1)  # Manual
    board.set_led_mode(1)  # RGB fijo
    
    current_color = (0, 255, 0)
    last_pwm = None
    last_ip = None
    last_ip_time = 0
    last_state_file = None
    last_state_time = 0
    last_temp = None
    last_temp_time = 0
    
    while not stop_flag:
        # CPU y RAM
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        # Temperatura (cada 1 segundo)
        now = time.time()
        if now - last_temp_time > 1:
            last_temp = get_cpu_temp()
            last_temp_time = now
        temp = last_temp
        
        # IP (cada 20 segundos)
        now = time.time()
        if now - last_ip_time > 20:
            last_ip = get_ip()
            last_tun_ip = get_ip_of_interface("tun0")
            last_ip_time = now
        ip = last_ip
        tun_ip = last_tun_ip

        # ========================================
        # LEER ESTADO DEL DASHBOARD (cada 1 segundo)
        # ========================================
        now = time.time()
        if now - last_state_time > 1:
            state = read_fan_state()
            last_state_file = state
            last_state_time = now
            
            # Debug: mostrar estado leído
            if state:
                print(f"Estado leído: modo={state.get('mode')}, PWM={state.get('target_pwm')}")
        else:
            state = last_state_file

        # Determinar PWM según estado del dashboard
        fan_pwm = None

        if state:
            mode = state.get("mode")
            
            # El dashboard ya calcula el PWM para todos los modos
            # Solo necesitamos leer target_pwm
            fan_pwm = state.get("target_pwm")
            
            if fan_pwm is not None:
                print(f"Usando PWM del dashboard: {fan_pwm} (modo: {mode})")

        # Fallback de seguridad (si no hay estado o archivo)
        if fan_pwm is None:
            fan_pwm = fan_curve(temp)
            print(f"Usando curva local (fallback): PWM={fan_pwm}")

        # Aplicar PWM solo si cambia
        if fan_pwm != last_pwm:
            board.set_fan_duty(fan_pwm, fan_pwm)
            last_pwm = fan_pwm

        # Calcular porcentaje para OLED
        fan_percent = int(fan_pwm * 100 / 255) if fan_pwm else 0
        fan0_duty = fan_percent
        fan1_duty = fan_percent

        # Actualizar color de LEDs según temperatura
        target_color = temp_to_color(temp)
        current_color = smooth(current_color, target_color)
        board.set_all_led_color(*current_color)

        # Actualizar OLED
        draw_oled_smart(cpu, ram, temp, ip, tun_ip, fan0_duty, fan1_duty)

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Salida limpia (Ctrl+C)")
except Exception as e:
    print(f"Error inesperado: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("Limpiando...")
    oled.clear()
    board.set_all_led_color(0, 0, 0)
    board.set_fan_duty(0, 0)
    print("Apagado completo.")
````

## File: INTEGRATION_GUIDE.md
````markdown
# 🔗 Guía de Integración con fase1.py

Esta guía explica cómo integrar tu aplicación OLED (`fase1.py`) con el Dashboard para que ambos funcionen juntos.

---

## 🎯 ¿Cómo Funciona la Integración?

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  DASHBOARD (system_dashboard)                          │
│  - Interfaz gráfica                                    │
│  - Control de ventiladores                             │
│  - Guarda estado en: data/fan_state.json              │
│                                                         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Escribe fan_state.json
                   │ {"mode": "auto", "target_pwm": 128}
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  ARCHIVO COMPARTIDO                                     │
│  📄 data/fan_state.json                                │
│  {"mode": "auto", "target_pwm": 128}                   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Lee fan_state.json
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  OLED MONITOR (fase1.py / integration_fase1.py)       │
│  - Muestra CPU, RAM, Temp en OLED                     │
│  - Controla LEDs RGB                                   │
│  - Aplica PWM de ventiladores                         │
│  - Lee estado desde: data/fan_state.json              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Pasos de Integración

### 1️⃣ Instalar el Dashboard

```bash
# Descargar y extraer system_dashboard
cd ~
unzip system_dashboard_WITH_THEMES.zip
cd system_dashboard

# Instalar dependencias
sudo ./install_system.sh
```

### 2️⃣ Configurar Ruta en fase1.py

Edita tu `fase1.py` (o usa el nuevo `integration_fase1.py`):

```python
# En la línea ~13, cambia:
STATE_FILE = "/home/jalivur/system_dashboard/data/fan_state.json"

# Ajusta la ruta donde hayas puesto el proyecto
```

### 3️⃣ Ejecutar Ambos Programas

**Terminal 1** - Dashboard:
```bash
cd ~/system_dashboard
python3 main.py
```

**Terminal 2** - OLED Monitor:
```bash
cd /ruta/a/tu/fase1
python3 integration_fase1.py
# O tu fase1.py modificado
```

---

## 🔄 Flujo de Datos

### Cuando Cambias el Modo en el Dashboard:

1. **Usuario** hace clic en "Control Ventiladores"
2. **Dashboard** cambia el modo a "Manual" y PWM a 200
3. **Dashboard** guarda en `data/fan_state.json`:
   ```json
   {
     "mode": "manual",
     "target_pwm": 200
   }
   ```
4. **fase1.py** lee el archivo cada 1 segundo
5. **fase1.py** aplica PWM=200 a los ventiladores
6. **OLED** muestra "Fan1:78% Fan2:78%" (200/255 = 78%)

### Sincronización:

- ✅ Dashboard escribe cada vez que cambias algo
- ✅ fase1 lee cada 1 segundo
- ✅ PWM se aplica inmediatamente si cambia
- ✅ Sin conflictos (escritura atómica con .tmp)

---

## ⚙️ Modos Disponibles

El Dashboard soporta 5 modos:

| Modo | PWM | Descripción |
|------|-----|-------------|
| **Auto** | Dinámico | Basado en curva temperatura-PWM |
| **Manual** | Usuario | Tú eliges el valor (0-255) |
| **Silent** | 77 | Silencioso (30%) |
| **Normal** | 128 | Normal (50%) |
| **Performance** | 255 | Máximo (100%) |

El archivo `fan_state.json` siempre tiene `target_pwm` calculado, independientemente del modo.

---

## 🛠️ Configuración Avanzada

### Opción 1: Usar Rutas Relativas (Recomendado)

Modifica `integration_fase1.py`:

```python
import os
from pathlib import Path

# Ruta relativa al home del usuario
HOME = Path.home()
STATE_FILE = HOME / "system_dashboard" / "data" / "fan_state.json"
```

### Opción 2: Variable de Entorno

```bash
# En ~/.bashrc o ~/.profile
export DASHBOARD_DATA="/home/jalivur/system_dashboard/data"

# En fase1.py
STATE_FILE = os.environ.get("DASHBOARD_DATA", "/home/jalivur/system_dashboard/data") + "/fan_state.json"
```

### Opción 3: Enlace Simbólico

```bash
# Crear enlace en ubicación fija
ln -s ~/system_dashboard/data/fan_state.json /tmp/fan_state.json

# En fase1.py
STATE_FILE = "/tmp/fan_state.json"
```

---

## 🚀 Autostart de Ambos Programas

### Método 1: systemd (Recomendado)

**Dashboard:**
```bash
# Crear servicio
sudo nano /etc/systemd/system/dashboard.service
```

```ini
[Unit]
Description=System Dashboard
After=graphical.target

[Service]
Type=simple
User=jalivur
WorkingDirectory=/home/jalivur/system_dashboard
Environment="DISPLAY=:0"
ExecStart=/usr/bin/python3 /home/jalivur/system_dashboard/main.py
Restart=always

[Install]
WantedBy=graphical.target
```

**OLED Monitor:**
```bash
sudo nano /etc/systemd/system/oled-monitor.service
```

```ini
[Unit]
Description=OLED Monitor
After=network.target

[Service]
Type=simple
User=jalivur
WorkingDirectory=/home/jalivur/proyectopantallas
ExecStart=/usr/bin/python3 /home/jalivur/proyectopantallas/integration_fase1.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Activar:**
```bash
sudo systemctl enable dashboard.service
sudo systemctl enable oled-monitor.service

sudo systemctl start dashboard.service
sudo systemctl start oled-monitor.service

# Ver logs
sudo journalctl -u dashboard.service -f
sudo journalctl -u oled-monitor.service -f
```

### Método 2: Crontab @reboot

```bash
crontab -e
```

Añadir:
```cron
@reboot sleep 30 && DISPLAY=:0 /usr/bin/python3 /home/jalivur/system_dashboard/main.py &
@reboot sleep 10 && /usr/bin/python3 /home/jalivur/proyectopantallas/integration_fase1.py &
```

---

## 🐛 Solución de Problemas

### El OLED no muestra cambios de ventilador

**Verificar que el archivo existe:**
```bash
ls -la ~/system_dashboard/data/fan_state.json
```

**Ver contenido:**
```bash
cat ~/system_dashboard/data/fan_state.json
# Debe mostrar: {"mode": "...", "target_pwm": ...}
```

**Ver logs de fase1:**
```bash
# Añadir debug al inicio
python3 integration_fase1.py
# Verás: "Estado leído: modo=auto, PWM=128"
```

### El PWM no cambia

**Verificar permisos:**
```bash
chmod 644 ~/system_dashboard/data/fan_state.json
```

**Verificar que fase1 lee el archivo:**
```python
# Añadir en el código de fase1:
if state:
    print(f"DEBUG: Estado leído = {state}")
```

### Los dos programas pelean por los ventiladores

**Esto NO debería pasar** porque:
- Dashboard solo ESCRIBE el estado
- fase1 solo LEE el estado
- fase1 es quien aplica el PWM físicamente

Si pasa:
1. Cierra el Dashboard
2. Solo ejecuta fase1
3. Verifica que funciona
4. Vuelve a abrir Dashboard

---

## 💡 Tips y Trucos

### Ver Estado en Tiempo Real

```bash
# Terminal dedicado
watch -n 1 cat ~/system_dashboard/data/fan_state.json
```

### Script de Debug

```bash
#!/bin/bash
# debug_integration.sh

echo "=== Estado del Dashboard ==="
cat ~/system_dashboard/data/fan_state.json | python3 -m json.tool

echo ""
echo "=== Procesos corriendo ==="
ps aux | grep -E "main.py|fase1.py|integration_fase1.py"

echo ""
echo "=== Temperatura actual ==="
vcgencmd measure_temp
```

### Notificaciones de Cambio

Añade a `integration_fase1.py`:

```python
last_mode = None

# En el bucle:
if state and state.get("mode") != last_mode:
    new_mode = state.get("mode")
    print(f"🔔 Modo cambiado: {last_mode} → {new_mode}")
    # Opcionalmente, mostrar en OLED temporalmente
    last_mode = new_mode
```

---

## 📊 Monitoreo

### Ver Logs en Tiempo Real

```bash
# Dashboard
tail -f ~/system_dashboard/dashboard.log

# OLED Monitor
tail -f ~/proyectopantallas/oled_monitor.log
```

### Crear Logs

Añade al inicio de `integration_fase1.py`:

```python
import logging

logging.basicConfig(
    filename='/home/jalivur/proyectopantallas/oled_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# En el bucle:
if state:
    logging.info(f"PWM aplicado: {fan_pwm}, Modo: {state.get('mode')}")
```

---

## ✅ Checklist de Integración

- [ ] Dashboard instalado y funcionando
- [ ] Archivo `fan_state.json` se crea al cambiar modo
- [ ] Ruta correcta configurada en fase1.py
- [ ] fase1.py lee el archivo correctamente
- [ ] PWM se aplica a los ventiladores físicos
- [ ] OLED muestra el porcentaje correcto
- [ ] Ambos programas arrancan al inicio (opcional)
- [ ] Logs configurados (opcional)

---

## 🎯 Resultado Final

Una vez integrado correctamente:

✅ Cambias modo en Dashboard → Ventiladores responden inmediatamente
✅ OLED muestra estado actual de ventiladores
✅ LEDs cambian color según temperatura
✅ Todo funciona sin conflictos
✅ Puedes cerrar Dashboard, fase1 sigue funcionando
✅ Puedes cerrar fase1, Dashboard sigue guardando estado

---

## 📞 ¿Problemas?

Si tienes problemas con la integración:

1. Verifica rutas con `ls -la`
2. Verifica contenido con `cat`
3. Añade `print()` para debug
4. Ejecuta manualmente primero (no autostart)
5. Revisa logs de systemd si usas servicios

---

**¡Disfruta de tu sistema integrado!** 🎉
````

## File: migratelogger.sh
````bash
# Script: migrate_to_logging.sh
#!/bin/bash

# Reemplazar prints por logging
find . -name "*.py" -type f -exec sed -i 's/print(f"\[/logger.info("/g' {} \;
find . -name "*.py" -type f -exec sed -i 's/print("Error/logger.error("/g' {} \;
````

## File: REQUIREMENTS.md
````markdown
# 📦 Guía Rápida: requirements.txt

## 🎯 ¿Qué es?

Un archivo que lista todas las **dependencias Python** de tu proyecto para instalarlas automáticamente.

---

## 📝 Contenido del archivo

```txt
# Dependencias Python
customtkinter>=5.2.0
psutil>=5.9.0
```

**Significado:**
- `customtkinter>=5.2.0` → Interfaz gráfica (versión 5.2.0 o superior)
- `psutil>=5.9.0` → Monitor de sistema (versión 5.9.0 o superior)

---

## 🚀 Cómo usar

### Instalar dependencias:

```bash
# En sistemas modernos (Ubuntu 23.04+, Debian 12+)
pip3 install --break-system-packages -r requirements.txt

# En sistemas antiguos
pip3 install -r requirements.txt

# O con sudo (global)
sudo pip3 install -r requirements.txt
```

---

## 🔧 Operadores de versión

| Operador | Significado | Ejemplo |
|----------|-------------|---------|
| `>=` | Versión mínima | `psutil>=5.9.0` |
| `==` | Versión exacta | `psutil==5.9.5` |
| `<=` | Versión máxima | `psutil<=6.0.0` |
| `~=` | Compatible | `psutil~=5.9.0` (5.9.x) |

---

## ✅ Buenas prácticas

### ✅ Hacer:
- Usar versiones mínimas (`>=`) en lugar de exactas
- Comentar dependencias opcionales
- Mantener el archivo actualizado

### ❌ Evitar:
- No especificar versiones (puede romper)
- Versiones exactas innecesarias (muy restrictivo)
- Incluir TODO con `pip freeze` (archivo enorme)

---

## 🧪 Verificar instalación

```bash
# Ver qué tienes instalado
pip3 list

# Ver versión específica
pip3 show customtkinter

# Comprobar problemas
pip3 check
```

---

## 📊 Dependencias del Sistema

**NOTA:** requirements.txt solo lista dependencias **Python**. 

Las dependencias del **sistema** (como `lm-sensors`) se instalan con:

```bash
# Ubuntu/Debian/Raspberry Pi
sudo apt-get install lm-sensors usbutils udisks2

# Fedora/RHEL
sudo dnf install lm-sensors usbutils udisks2
```

---

## 🎯 Resumen

**¿Qué es?** → Lista de dependencias Python  
**¿Para qué?** → Instalar todo automáticamente  
**¿Cómo usar?** → `pip3 install -r requirements.txt`  
**¿Dónde?** → Raíz del proyecto  

---

**Tip:** En sistemas modernos (Ubuntu 23.04+), usa `--break-system-packages` para evitar errores de PEP 668.
````

## File: setup.py
````python
"""
Setup script para System Dashboard
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="system-dashboard",
    version="1.0.0",
    author="Tu Nombre",
    author_email="tu@email.com",
    description="Sistema profesional de monitoreo del sistema con control de ventiladores",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tuusuario/system-dashboard",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "system-dashboard=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt"],
    },
)
````

## File: test_logging.py
````python
#!/usr/bin/env python3
"""
Script de prueba manual del sistema de logging
Ejecutar desde la raíz del proyecto: python3 test_logging.py
Ver logs en tiempo real con: tail -f data/logs/dashboard.log
"""
import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import get_logger

logger = get_logger("test")

def separador(titulo):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")

def ok(msg):
    print(f"  ✅ {msg}")

def info(msg):
    print(f"  ℹ️  {msg}")


# ============================================================
# TEST FILE_MANAGER
# ============================================================
def test_file_manager():
    separador("FILE MANAGER")
    from config.settings import STATE_FILE, CURVE_FILE
    from utils.file_manager import FileManager

    # --- Test 1: load_state cuando no existe el archivo ---
    print("\n[1] load_state con archivo inexistente:")
    backup = None
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            backup = f.read()
        os.remove(STATE_FILE)

    state = FileManager.load_state()
    ok(f"Retornó estado por defecto: {state}")
    info("Debe aparecer en log: [DEBUG] load_state: no existe, usando estado por defecto")

    # Restaurar
    if backup:
        with open(STATE_FILE, "w") as f:
            f.write(backup)

    # --- Test 2: load_state con JSON corrupto ---
    print("\n[2] load_state con JSON corrupto:")
    with open(STATE_FILE, "w") as f:
        f.write("{ esto no es json válido !!!}")

    state = FileManager.load_state()
    ok(f"Retornó estado por defecto: {state}")
    info("Debe aparecer en log: [ERROR] load_state: JSON corrupto")

    # Restaurar estado válido
    FileManager.write_state({"mode": "auto", "target_pwm": None})
    ok("Estado restaurado correctamente")

    # --- Test 3: load_curve con archivo inexistente ---
    print("\n[3] load_curve con archivo inexistente:")
    curve_backup = None
    if os.path.exists(CURVE_FILE):
        with open(CURVE_FILE) as f:
            curve_backup = f.read()
        os.remove(CURVE_FILE)

    curve = FileManager.load_curve()
    ok(f"Retornó curva por defecto con {len(curve)} puntos")
    info("Debe aparecer en log: [DEBUG] load_curve: no existe, usando curva por defecto")

    if curve_backup:
        with open(CURVE_FILE, "w") as f:
            f.write(curve_backup)

    # --- Test 4: load_curve con JSON corrupto ---
    print("\n[4] load_curve con JSON corrupto:")
    with open(CURVE_FILE, "w") as f:
        f.write("{ corrupto }")

    curve = FileManager.load_curve()
    ok(f"Retornó curva por defecto con {len(curve)} puntos")
    info("Debe aparecer en log: [ERROR] load_curve: JSON corrupto")

    # Restaurar curva válida
    if curve_backup:
        with open(CURVE_FILE, "w") as f:
            f.write(curve_backup)
    else:
        FileManager.save_curve([{"temp": 50, "pwm": 128}])

    ok("Curva restaurada correctamente")

    # --- Test 5: write_state correcto ---
    print("\n[5] write_state normal:")
    FileManager.write_state({"mode": "auto", "target_pwm": 128})
    ok("Estado guardado sin errores")

    # --- Test 6: save_curve correcta ---
    print("\n[6] save_curve normal:")
    FileManager.save_curve([{"temp": 50, "pwm": 100}, {"temp": 70, "pwm": 200}])
    ok("Curva guardada sin errores")
    info("Debe aparecer en log: [INFO] save_curve: curva guardada (2 puntos)")


# ============================================================
# TEST SYSTEM_UTILS
# ============================================================
def test_system_utils():
    separador("SYSTEM UTILS")
    from utils.system_utils import SystemUtils

    # --- Test 1: get_cpu_temp ---
    print("\n[1] get_cpu_temp:")
    temp = SystemUtils.get_cpu_temp()
    ok(f"Temperatura obtenida: {temp}°C")
    if temp == 0.0:
        info("Retornó 0.0 — revisa el log para ver qué método falló")
    else:
        info("Temperatura real leída correctamente")

    # --- Test 2: get_hostname ---
    print("\n[2] get_hostname:")
    hostname = SystemUtils.get_hostname()
    ok(f"Hostname: {hostname}")

    # --- Test 3: get_nvme_temp ---
    print("\n[3] get_nvme_temp:")
    nvme = SystemUtils.get_nvme_temp()
    ok(f"Temperatura NVMe: {nvme}°C")
    if nvme == 0.0:
        info("Retornó 0.0 — puede que no haya NVMe o falten permisos (normal)")
        info("Revisa el log: debe aparecer qué método falló (smartctl/sysfs)")

    # --- Test 4: list_usb_storage_devices ---
    print("\n[4] list_usb_storage_devices:")
    usb = SystemUtils.list_usb_storage_devices()
    ok(f"Dispositivos USB encontrados: {len(usb)}")
    for d in usb:
        info(f"  → {d.get('name')} ({d.get('dev')})")

    # --- Test 5: list_usb_other_devices ---
    print("\n[5] list_usb_other_devices:")
    otros = SystemUtils.list_usb_other_devices()
    ok(f"Otros dispositivos USB: {len(otros)}")

    # --- Test 6: get_interfaces_ips ---
    print("\n[6] get_interfaces_ips:")
    ips = SystemUtils.get_interfaces_ips()
    ok(f"Interfaces detectadas: {len(ips)}")
    for iface, ip in ips.items():
        info(f"  → {iface}: {ip}")

    # --- Test 7: run_script con script inexistente ---
    print("\n[7] run_script con script inexistente:")
    success, msg = SystemUtils.run_script("/ruta/que/no/existe.sh")
    ok(f"Retornó success={success}, msg='{msg}'")
    info("Debe aparecer en log: [ERROR] run_script: script no encontrado")

    # --- Test 8: run_script real (crea uno temporal) ---
    print("\n[8] run_script con script válido:")
    tmp_script = "/tmp/test_dashboard.sh"
    with open(tmp_script, "w") as f:
        f.write("#!/bin/bash\necho 'Script de prueba OK'\nexit 0\n")
    os.chmod(tmp_script, 0o755)

    success, msg = SystemUtils.run_script(tmp_script)
    ok(f"Retornó success={success}, msg='{msg}'")
    info("Debe aparecer en log: [INFO] Script ejecutado correctamente")
    os.remove(tmp_script)


# ============================================================
# TEST NETWORK_MONITOR
# ============================================================
def test_network_monitor():
    separador("NETWORK MONITOR (SPEEDTEST)")
    from core.network_monitor import NetworkMonitor

    monitor = NetworkMonitor()

    # --- Test 1: get_current_stats ---
    print("\n[1] get_current_stats:")
    stats = monitor.get_current_stats()
    ok(f"Interfaz: {stats['interface']}, ↓{stats['download_mb']:.3f} MB/s, ↑{stats['upload_mb']:.3f} MB/s")

    # --- Test 2: speedtest completo ---
    print("\n[2] Speedtest (puede tardar ~30-60s):")
    info("Iniciando speedtest... espera")
    monitor.run_speedtest()

    # Esperar resultado con timeout
    timeout = 90
    start = time.time()
    while time.time() - start < timeout:
        result = monitor.get_speedtest_result()
        status = result['status']

        if status == 'running':
            print(f"  ⏳ Ejecutando... ({int(time.time()-start)}s)", end='\r')
            time.sleep(2)
        elif status == 'done':
            print()
            ok(f"Ping: {result['ping']}ms | ↓{result['download']:.2f} MB/s | ↑{result['upload']:.2f} MB/s")
            info("Debe aparecer en log: [INFO] Speedtest completado con las métricas")
            break
        elif status == 'timeout':
            print()
            ok(f"Speedtest timeout (esperado si la conexión es lenta)")
            info("Debe aparecer en log: [WARNING] Speedtest timeout")
            break
        elif status == 'error':
            print()
            ok(f"Speedtest error (puede que speedtest-cli no esté instalado)")
            info("Debe aparecer en log: [ERROR] con el motivo del fallo")
            break
    else:
        print()
        info("Timeout de espera alcanzado en el script de prueba")

    # --- Test 3: speedtest con binario inexistente (simulado) ---
    print("\n[3] Verificar log de speedtest-cli no encontrado:")
    info("Para probar esto, renombra temporalmente speedtest-cli y ejecuta de nuevo")
    info("Debe aparecer en log: [ERROR] speedtest-cli no encontrado")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  TEST DE LOGGING - Dashboard v2.5.1")
    print("  Abre otra terminal y ejecuta:")
    print("  tail -f data/logs/dashboard.log")
    print("="*60)

    # Preguntar si hacer el speedtest (tarda mucho)
    hacer_speedtest = "--speedtest" in sys.argv or "-s" in sys.argv

    try:
        test_file_manager()
    except Exception as e:
        print(f"\n❌ Error en test_file_manager: {e}")

    try:
        test_system_utils()
    except Exception as e:
        print(f"\n❌ Error en test_system_utils: {e}")

    if hacer_speedtest:
        try:
            test_network_monitor()
        except Exception as e:
            print(f"\n❌ Error en test_network_monitor: {e}")
    else:
        separador("NETWORK MONITOR (SPEEDTEST)")
        print("\n  ⏭️  Saltado. Para incluir el speedtest ejecuta:")
        print("     python3 test_logging.py --speedtest")

    separador("RESULTADO FINAL")
    print("\n  Revisa data/logs/dashboard.log para verificar los mensajes.")
    print("  Todos los tests deberían mostrar ✅ sin excepciones no capturadas.\n")
````

## File: config/__init__.py
````python
"""
Paquete de configuración
"""
from .settings import (
    # Rutas
    PROJECT_ROOT,
    DATA_DIR,
    SCRIPTS_DIR,
    STATE_FILE,
    CURVE_FILE,
    # Pantalla
    DSI_WIDTH,
    DSI_HEIGHT,
    DSI_X,
    DSI_Y,
    # Actualización y gráficas
    UPDATE_MS,
    HISTORY,
    GRAPH_WIDTH,
    GRAPH_HEIGHT,
    # Umbrales
    CPU_WARN,
    CPU_CRIT,
    TEMP_WARN,
    TEMP_CRIT,
    RAM_WARN,
    RAM_CRIT,
    # Red
    NET_WARN,
    NET_CRIT,
    NET_INTERFACE,
    NET_MAX_MB,
    NET_MIN_SCALE,
    NET_MAX_SCALE,
    NET_IDLE_THRESHOLD,
    NET_IDLE_RESET_TIME,
    # Lanzadores
    LAUNCHERS,
    # Tema y estilos
    SELECTED_THEME,
    COLORS,
    FONT_FAMILY,
    FONT_SIZES,
)
````

## File: core/disk_monitor.py
````python
"""
Monitor de disco
"""
from collections import deque
from typing import Dict
from config.settings import HISTORY, UPDATE_MS, COLORS
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

        seconds = UPDATE_MS / 1000.0
        read_mb = (read_bytes / (1024 * 1024)) / seconds
        write_mb = (write_bytes / (1024 * 1024)) / seconds
        
        # Temperatura NVMe (NUEVO)
        nvme_temp = self.system_utils.get_nvme_temp()
        
        return {
            'disk_usage': disk_usage,
            'disk_read_mb': read_mb,
            'disk_write_mb': write_mb,
            'nvme_temp': nvme_temp  # NUEVO
        }
    
    def update_history(self, stats: Dict) -> None:
        """
        Actualiza historiales con estadísticas actuales
        
        Args:
            stats: Diccionario con estadísticas
        """
        self.usage_hist.append(stats['disk_usage'])
        self.read_hist.append(stats['disk_read_mb'])
        self.write_hist.append(stats['disk_write_mb'])
        self.nvme_temp_hist.append(stats['nvme_temp'])  # NUEVO
    
    def get_history(self) -> Dict:
        """
        Obtiene todos los historiales
        
        Returns:
            Diccionario con historiales
        """
        return {
            'disk_usage': list(self.usage_hist),
            'disk_read': list(self.read_hist),
            'disk_write': list(self.write_hist),
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
        
        if value >= crit:
            return COLORS['danger']
        elif value >= warn:
            return COLORS['warning']
        else:
            return COLORS['primary']
````

## File: core/fan_controller.py
````python
"""
Controlador de ventiladores
"""
from typing import List, Dict
from utils.file_manager import FileManager
from utils.logger import get_logger

logger = get_logger(__name__)


class FanController:
    """Controlador para gestión de ventiladores"""
    
    def __init__(self):
        self.file_manager = FileManager()
    
    def compute_pwm_from_curve(self, temp: float) -> int:
        """
        Calcula el PWM basado en la curva y la temperatura

        Args:
            temp: Temperatura actual en °C

        Returns:
            Valor PWM (0-255)
        """
        curve = self.file_manager.load_curve()
        
        if not curve:
            logger.warning("[FanController] compute_pwm_from_curve: curva vacía, retornando PWM 0")
            return 0
        
        if temp <= curve[0]["temp"]:
            return int(curve[0]["pwm"])
        
        if temp >= curve[-1]["temp"]:
            return int(curve[-1]["pwm"])
        
        for i in range(len(curve) - 1):
            t1, pwm1 = curve[i]["temp"], curve[i]["pwm"]
            t2, pwm2 = curve[i + 1]["temp"], curve[i + 1]["pwm"]
            
            if t1 <= temp <= t2:
                ratio = (temp - t1) / (t2 - t1)
                pwm = pwm1 + ratio * (pwm2 - pwm1)
                return int(pwm)
        
        return int(curve[-1]["pwm"])
    
    def get_pwm_for_mode(self, mode: str, temp: float, manual_pwm: int = 128) -> int:
        """
        Obtiene el PWM según el modo seleccionado

        Args:
            mode: Modo de operación (auto, manual, silent, normal, performance)
            temp: Temperatura actual
            manual_pwm: Valor PWM manual si mode='manual'

        Returns:
            Valor PWM calculado (0-255)
        """
        if mode == "manual":
            return max(0, min(255, manual_pwm))
        elif mode == "auto":
            return self.compute_pwm_from_curve(temp)
        elif mode == "silent":
            return 77
        elif mode == "normal":
            return 128
        elif mode == "performance":
            return 255
        else:
            logger.warning(f"[FanController] Modo desconocido '{mode}', usando curva auto")
            return self.compute_pwm_from_curve(temp)
    
    def update_fan_state(self, mode: str, temp: float, current_target: int = None,
                         manual_pwm: int = 128) -> Dict:
        """
        Actualiza el estado del ventilador

        Args:
            mode: Modo actual
            temp: Temperatura actual
            current_target: PWM objetivo actual
            manual_pwm: PWM manual configurado

        Returns:
            Diccionario con el nuevo estado
        """
        desired = self.get_pwm_for_mode(mode, temp, manual_pwm)
        desired = max(0, min(255, int(desired)))
        
        if desired != current_target:
            new_state = {"mode": mode, "target_pwm": desired}
            self.file_manager.write_state(new_state)
            logger.debug(f"[FanController] PWM actualizado: {current_target} → {desired} (modo={mode}, temp={temp:.1f}°C)")
            return new_state
        
        return {"mode": mode, "target_pwm": current_target}
    
    def add_curve_point(self, temp: int, pwm: int) -> List[Dict]:
        """
        Añade un punto a la curva

        Args:
            temp: Temperatura en °C
            pwm: Valor PWM (0-255)

        Returns:
            Curva actualizada
        """
        curve = self.file_manager.load_curve()
        pwm = max(0, min(255, pwm))
        
        found = False
        for point in curve:
            if point["temp"] == temp:
                logger.debug(f"[FanController] Punto actualizado en curva: {temp}°C → PWM {point['pwm']} → {pwm}")
                point["pwm"] = pwm
                found = True
                break
        
        if not found:
            logger.debug(f"[FanController] Nuevo punto añadido a curva: {temp}°C → PWM {pwm}")
            curve.append({"temp": temp, "pwm": pwm})
        
        curve = sorted(curve, key=lambda x: x["temp"])
        self.file_manager.save_curve(curve)
        
        return curve
    
    def remove_curve_point(self, temp: int) -> List[Dict]:
        """
        Elimina un punto de la curva

        Args:
            temp: Temperatura del punto a eliminar

        Returns:
            Curva actualizada
        """
        curve = self.file_manager.load_curve()
        original_len = len(curve)
        curve = [p for p in curve if p["temp"] != temp]
        
        if len(curve) < original_len:
            logger.debug(f"[FanController] Punto eliminado de curva: {temp}°C")
        else:
            logger.warning(f"[FanController] remove_curve_point: no se encontró punto en {temp}°C")
        
        if not curve:
            curve = [{"temp": 40, "pwm": 100}]
            logger.warning("[FanController] Curva quedó vacía, restaurado punto por defecto")
        
        self.file_manager.save_curve(curve)
        return curve
````

## File: core/service_monitor.py
````python
"""
Monitor de servicios systemd
"""
import subprocess
import re
from typing import List, Dict, Optional
from utils import DashboardLogger


class ServiceMonitor:
    """Monitor de servicios del sistema"""

    def __init__(self):
        """Inicializa el monitor de servicios"""
        self.sort_by = "name"  # name, state
        self.sort_reverse = False
        self.filter_type = "all"  # all, active, inactive, failed
        self.dashboard_logger = DashboardLogger()

    def get_services(self) -> List[Dict]:
        """
        Obtiene lista de servicios systemd

        Returns:
            Lista de diccionarios con información de servicios
        """
        services = []

        try:
            # Listar todos los servicios
            result = subprocess.run(
                ["systemctl", "list-units", "--type=service", "--all", "--no-pager"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return []

            # Parsear salida
            lines = result.stdout.strip().split('\n')

            for line in lines:
                # Saltar headers y footers
                if not line.strip() or line.startswith('UNIT') or line.startswith('●') or 'loaded units listed' in line:
                    continue

                # Parsear línea
                parts = line.split()
                if len(parts) < 4:
                    continue

                unit = parts[0]
                load = parts[1]
                active = parts[2]
                sub = parts[3]
                description = ' '.join(parts[4:]) if len(parts) > 4 else ''

                # Solo servicios .service
                if not unit.endswith('.service'):
                    continue

                # Extraer nombre sin .service
                name = unit.replace('.service', '')

                # Aplicar filtro
                if self.filter_type == "active" and active != "active":
                    continue
                elif self.filter_type == "inactive" and active != "inactive":
                    continue
                elif self.filter_type == "failed" and active != "failed":
                    continue

                services.append({
                    'name': name,
                    'unit': unit,
                    'load': load,
                    'active': active,
                    'sub': sub,
                    'description': description,
                    'enabled': self._check_enabled(unit)
                })

        except Exception as e:
            self.dashboard_logger.get_logger(__name__).error(f"[ServiceMonitor]Error getting services: {e}")
            return []

        # Ordenar
        if self.sort_by == "name":
            services.sort(key=lambda x: x['name'].lower(), reverse=self.sort_reverse)
        elif self.sort_by == "state":
            # Ordenar por estado: active > inactive > failed
            state_order = {'active': 0, 'inactive': 1, 'failed': 2}
            services.sort(
                key=lambda x: state_order.get(x['active'], 3),
                reverse=self.sort_reverse
            )

        return services

    def _check_enabled(self, unit: str) -> bool:
        """
        Verifica si un servicio está enabled

        Args:
            unit: Nombre del servicio (ej: nginx.service)

        Returns:
            True si está enabled
        """
        try:
            result = subprocess.run(
                ["systemctl", "is-enabled", unit],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0 and result.stdout.strip() == "enabled"
        except Exception:
            return False

    def start_service(self, name: str) -> tuple[bool, str]:
        """
        Inicia un servicio

        Args:
            name: Nombre del servicio

        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "start", f"{name}.service"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.dashboard_logger.get_logger(__name__).info(f"[ServiceMonitor] Servicio '{name}' iniciado correctamente")
                return True, f"Servicio '{name}' iniciado correctamente"
                
            else:
                self.dashboard_logger.get_logger(__name__).error(f"[ServiceMonitor] Error iniciando servicio '{name}': {result.stderr}")
                return False, f"Error: {result.stderr}"
        except Exception as e:
            self.dashboard_logger.get_logger(__name__).error(f"[ServiceMonitor] Error iniciando servicio '{name}': {e}")
            return False, f"Error: {str(e)}"

    def stop_service(self, name: str) -> tuple[bool, str]:
        """
        Detiene un servicio

        Args:
            name: Nombre del servicio

        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "stop", f"{name}.service"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.dashboard_logger.get_logger(__name__).info(f"[ServiceMonitor] Servicio '{name}' detenido correctamente")
                return True, f"Servicio '{name}' detenido correctamente"
            else:
                self.dashboard_logger.get_logger(__name__).error(f"[ServiceMonitor] Error deteniendo servicio '{name}': {result.stderr}")
                return False, f"Error: {result.stderr}"
        except Exception as e:
            self.dashboard_logger.get_logger(__name__).error(f"[ServiceMonitor] Error deteniendo servicio '{name}': {e}")
            return False, f"Error: {str(e)}"

    def restart_service(self, name: str) -> tuple[bool, str]:
        """
        Reinicia un servicio

        Args:
            name: Nombre del servicio

        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "restart", f"{name}.service"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.dashboard_logger.get_logger(__name__).info(f"[ServiceMonitor] Servicio '{name}' reiniciado correctamente")
                return True, f"Servicio '{name}' reiniciado correctamente"
            else:
                self.dashboard_logger.get_logger(__name__).error(f"[ServiceMonitor] Error reiniciando servicio '{name}': {result.stderr}")
                return False, f"Error: {result.stderr}"
        except Exception as e:
            self.dashboard_logger.get_logger(__name__).error(f"[ServiceMonitor] Error reiniciando servicio '{name}': {e}")
            return False, f"Error: {str(e)}"

    def enable_service(self, name: str) -> tuple[bool, str]:
        """
        Habilita autostart de un servicio

        Args:
            name: Nombre del servicio

        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "enable", f"{name}.service"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0: 
                self.dashboard_logger.get_logger(__name__).info(f"[ServiceMonitor] Autostart habilitado para '{name}'")
                return True, f"Autostart habilitado para '{name}'"
            else:
                self.dashboard_logger.get_logger(__name__).error(f"[ServiceMonitor] Error habilitando autostart para '{name}': {result.stderr}")
                return False, f"Error: {result.stderr}"
        except Exception as e:
            self.dashboard_logger.get_logger(__name__).error(f"[ServiceMonitor] Error habilitando autostart para '{name}': {e}")
            return False, f"Error: {str(e)}"

    def disable_service(self, name: str) -> tuple[bool, str]:
        """
        Deshabilita autostart de un servicio

        Args:
            name: Nombre del servicio

        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "disable", f"{name}.service"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.dashboard_logger.get_logger(__name__).info(f"[ServiceMonitor] Autostart deshabilitado para '{name}'")
                return True, f"Autostart deshabilitado para '{name}'"
            else:  
                self.dashboard_logger.get_logger(__name__).error(f"[ServiceMonitor] Error deshabilitando autostart para '{name}': {result.stderr}")
                return False, f"Error: {result.stderr}"
        except Exception as e:
            self.dashboard_logger.get_logger(__name__).error(f"[ServiceMonitor] Error deshabilitando autostart para '{name}': {e}")
            return False, f"Error: {str(e)}"

    def get_logs(self, name: str, lines: int = 50) -> str:
        """
        Obtiene logs de un servicio

        Args:
            name: Nombre del servicio
            lines: Número de líneas a obtener

        Returns:
            Logs del servicio
        """
        try:
            result = subprocess.run(
                ["journalctl", "-u", f"{name}.service", "-n", str(lines), "--no-pager"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                self.dashboard_logger.get_logger(__name__).info(f"[ServiceMonitor] Logs obtenidos para '{name}'")
                return result.stdout
            else:
                self.dashboard_logger.get_logger(__name__).error(f"[ServiceMonitor] Error obteniendo logs para '{name}': {result.stderr}")
                return f"Error obteniendo logs: {result.stderr}"
        except Exception as e:
            self.dashboard_logger.get_logger(__name__).error(f"[ServiceMonitor] Error obteniendo logs para '{name}': {e}")
            return f"Error: {str(e)}"

    def search_services(self, query: str) -> List[Dict]:
        """
        Busca servicios por nombre o descripción

        Args:
            query: Texto a buscar

        Returns:
            Lista de servicios que coinciden
        """
        query = query.lower()
        all_services = self.get_services()

        return [s for s in all_services 
                if query in s['name'].lower() or query in s['description'].lower()]

    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas de servicios

        Returns:
            Diccionario con estadísticas
        """
        services = self.get_services()

        total = len(services)
        active = len([s for s in services if s['active'] == 'active'])
        inactive = len([s for s in services if s['active'] == 'inactive'])
        failed = len([s for s in services if s['active'] == 'failed'])
        enabled = len([s for s in services if s['enabled']])

        return {
            'total': total,
            'active': active,
            'inactive': inactive,
            'failed': failed,
            'enabled': enabled
        }

    def set_sort(self, column: str, reverse: bool = False):
        """
        Configura el orden

        Args:
            column: Columna por la que ordenar (name, state)
            reverse: Si ordenar invertido
        """
        self.sort_by = column
        self.sort_reverse = reverse

    def set_filter(self, filter_type: str):
        """
        Configura el filtro

        Args:
            filter_type: Tipo de filtro (all, active, inactive, failed)
        """
        self.filter_type = filter_type

    def get_state_color(self, state: str) -> str:
        """
        Obtiene color según estado

        Args:
            state: Estado del servicio (active, inactive, failed)

        Returns:
            Nombre del color en COLORS
        """
        if state == "active":
            return "success"
        elif state == "failed":
            return "danger"
        else:
            return "text_dim"
````

## File: ui/widgets/__init__.py
````python
"""
Paquete de widgets personalizados
"""
from .graphs import GraphWidget, update_graph_lines, recolor_lines
from .dialogs import custom_msgbox, confirm_dialog, terminal_dialog

__all__ = ['GraphWidget', 'update_graph_lines', 'recolor_lines', 
           'custom_msgbox', 'confirm_dialog', 'terminal_dialog']
````

## File: utils/logger.py
````python
"""
Sistema de logging robusto para el dashboard
Funciona correctamente tanto desde terminal como desde auto-start

Ubicación: utils/logger.py
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
import os


class DashboardLogger:
    """Logger centralizado para el dashboard"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        """Configura el logger con rutas absolutas y rotación automática"""
        
        # 1. Obtener directorio del proyecto de forma absoluta
        if hasattr(sys, '_MEIPASS'):
            # Si está empaquetado con PyInstaller
            project_root = Path(sys._MEIPASS)
        else:
            # utils/logger.py -> utils/ -> project_root/
            project_root = Path(__file__).parent.parent.resolve()
        
        # 2. Crear directorio de logs
        log_dir = project_root / "data" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 3. Nombre fijo para que la rotación funcione
        # (Si el nombre cambia cada día, el sistema no puede detectar el tamaño del archivo previo)
        log_file = log_dir / "dashboard.log"
        
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 4. Configurar RotatingFileHandler
        # maxBytes: 2MB (2 * 1024 * 1024)
        # backupCount: 1 (mantiene el archivo actual y uno de respaldo .log.1)
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=2*1024*1024, 
            backupCount=1,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # 5. Handler para consola (solo si hay terminal)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.WARNING)
        
        # 6. Configurar root logger
        self.logger = logging.getLogger('Dashboard')
        self.logger.setLevel(logging.DEBUG)
        
        # Evitar duplicar handlers si se instancia varias veces
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            
            try:
                if sys.stdout and sys.stdout.isatty():
                    self.logger.addHandler(console_handler)
            except:
                pass
        
        # Log de confirmación
        self.logger.info("=" * 60)
        self.logger.info(f"Logger inicializado - Archivo: {log_file}")
        self.logger.info(f"Límite de tamaño: 2MB con rotación activa")
        self.logger.info("=" * 60)

    def get_logger(self, name: str):
        """Obtiene un sub-logger para un módulo específico (ej: Dashboard.Database)"""
        return logging.getLogger(f'Dashboard.{name}')


# Singleton global
_dashboard_logger = None

def get_logger(name: str):
    """
    Obtiene logger para un módulo
    
    Uso:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Mensaje")
        logger.warning("Advertencia")
        logger.error("Error")
        logger.debug("Debug")
    
    Args:
        name: Nombre del módulo (usa __name__)
        
    Returns:
        Logger configurado
    """
    global _dashboard_logger
    if _dashboard_logger is None:
        _dashboard_logger = DashboardLogger()
    return _dashboard_logger.get_logger(name)


def log_startup_info():
    """Log información de inicio del sistema"""
    logger = get_logger('startup')
    
    # Información del entorno
    logger.info(f"Python: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"CWD: {os.getcwd()}")
    logger.info(f"User: {os.getenv('USER', 'unknown')}")
    logger.info(f"HOME: {os.getenv('HOME', 'unknown')}")
    
    # Variables de entorno relevantes
    display = os.getenv('DISPLAY', 'not set')
    logger.info(f"DISPLAY: {display}")
    
    if display == 'not set':
        logger.warning("DISPLAY no configurado - posible problema de GUI")
````

## File: requirements.txt
````
# ============================================
# System Dashboard - Python Dependencies
# ============================================
#
# Instalación rápida (recomendada):
#   sudo ./install_system.sh
#
# O manualmente:
#   pip3 install --break-system-packages -r requirements.txt
#
# Versión mínima de Python: 3.8+
# ============================================

# === Dependencias Obligatorias ===

# Interfaz gráfica moderna con tema oscuro
customtkinter>=5.2.0

# Monitor del sistema (CPU, RAM, Disco, Red, Procesos)
psutil>=5.9.0

# Gráficas históricas (ventana Histórico Datos)
matplotlib>=3.5.0


# === Dependencias Opcionales ===

# Test de velocidad de internet (Monitor Red → Speedtest)
# Instalar también en sistema: sudo apt install speedtest-cli
# speedtest-cli>=2.1.3


# ============================================
# NOTA: Dependencias del Sistema (NO Python)
# ============================================
#
# El script install_system.sh las instala automáticamente.
# O manualmente con apt-get:
#
#   sudo apt-get install lm-sensors usbutils udisks2 smartmontools
#
# Descripción:
#   - lm-sensors:     Lectura de temperatura CPU (sensors)
#   - usbutils:       Comando lsusb (listar USB)
#   - udisks2:        Expulsar dispositivos USB de forma segura
#   - util-linux:     Comando lsblk (suele venir instalado)
#   - smartmontools:  Temperatura NVMe (smartctl)
#
# Opcional para speedtest (el script pregunta al instalarlo):
#   sudo apt-get install speedtest-cli
#
# ============================================
````

## File: THEMES_GUIDE.md
````markdown
# 🎨 Guía de Temas - System Dashboard

El dashboard incluye **15 temas profesionales** pre-configurados y la capacidad de crear temas personalizados.

---

## 🌈 Temas Disponibles

### 1. **Cyberpunk** (Original) ⚡
```
Colores: Cyan neón + Verde oscuro
Estilo: Futurista, neón brillante
Ideal para: Look cyberpunk clásico
```
**Paleta:**
- Primary: `#00ffff` (Cyan brillante)
- Secondary: `#14611E` (Verde oscuro)
- Success: `#1ae313` (Verde neón)
- Warning: `#ffaa00` (Naranja)
- Danger: `#ff3333` (Rojo)

---

### 2. **Matrix** 💚
```
Colores: Verde Matrix brillante
Estilo: Película Matrix
Ideal para: Fans de Matrix
```
**Paleta:**
- Primary: `#00ff00` (Verde Matrix)
- Secondary: `#0aff0a` (Verde brillante)
- Success: `#00ff00` (Verde puro)
- Warning: `#ccff00` (Verde-amarillo lima)
- Danger: `#ff0000` (Rojo)

**✨ Colores optimizados** para alto contraste.

---

### 3. **Sunset** 🌅
```
Colores: Naranja cálido + Púrpura
Estilo: Atardecer cálido
Ideal para: Ambiente acogedor
```
**Paleta:**
- Primary: `#ff6b35` (Naranja cálido)
- Secondary: `#f7931e` (Naranja dorado)
- Success: `#ffd23f` (Amarillo dorado)
- Warning: `#ffd23f` (Amarillo)
- Danger: `#d62828` (Rojo oscuro)

---

### 4. **Ocean** 🌊
```
Colores: Azul océano + Aqua
Estilo: Marino refrescante
Ideal para: Look fresco y limpio
```
**Paleta:**
- Primary: `#00d4ff` (Azul cielo)
- Secondary: `#48dbfb` (Azul claro)
- Success: `#1dd1a1` (Verde agua)
- Warning: `#feca57` (Amarillo suave)
- Danger: `#ee5a6f` (Rosa coral)

---

### 5. **Dracula** 🦇
```
Colores: Púrpura + Rosa pastel
Estilo: Elegante oscuro
Ideal para: Desarrolladores
```
**Paleta:**
- Primary: `#bd93f9` (Púrpura pastel)
- Secondary: `#ff79c6` (Rosa)
- Success: `#50fa7b` (Verde pastel)
- Warning: `#f1fa8c` (Amarillo pastel)
- Danger: `#ff5555` (Rojo pastel)

**Popular en editores de código.**

---

### 6. **Nord** ❄️
```
Colores: Azul hielo nórdico
Estilo: Minimalista frío
Ideal para: Estética nórdica
```
**Paleta:**
- Primary: `#88c0d0` (Azul hielo)
- Secondary: `#5e81ac` (Azul oscuro)
- Success: `#a3be8c` (Verde suave)
- Warning: `#ebcb8b` (Amarillo suave)
- Danger: `#bf616a` (Rojo suave)

---

### 7. **Tokyo Night** 🌃
```
Colores: Azul + Púrpura noche
Estilo: Noche de Tokio
Ideal para: Ambiente nocturno
```
**Paleta:**
- Primary: `#7aa2f7` (Azul brillante)
- Secondary: `#bb9af7` (Púrpura)
- Success: `#9ece6a` (Verde)
- Warning: `#e0af68` (Naranja suave)
- Danger: `#f7768e` (Rosa)

---

### 8. **Monokai** 🎨
```
Colores: Cyan + Verde lima
Estilo: IDE clásico
Ideal para: Programadores
```
**Paleta:**
- Primary: `#66d9ef` (Azul claro)
- Secondary: `#fd971f` (Naranja)
- Success: `#a6e22e` (Verde lima)
- Warning: `#e6db74` (Amarillo)
- Danger: `#f92672` (Rosa fucsia)

**Tema icónico de Sublime Text.**

---

### 9. **Gruvbox** 🏜️
```
Colores: Naranja + Beige retro
Estilo: Cálido vintage
Ideal para: Fans del retro
```
**Paleta:**
- Primary: `#fe8019` (Naranja)
- Secondary: `#d65d0e` (Naranja oscuro)
- Success: `#b8bb26` (Verde lima)
- Warning: `#fabd2f` (Amarillo)
- Danger: `#fb4934` (Rojo)

---

### 10. **Solarized Dark** ☀️
```
Colores: Azul + Cyan
Estilo: Elegante científico
Ideal para: Precisión visual
```
**Paleta:**
- Primary: `#268bd2` (Azul)
- Secondary: `#2aa198` (Cyan)
- Success: `#859900` (Verde oliva)
- Warning: `#b58900` (Amarillo oscuro)
- Danger: `#dc322f` (Rojo)

**Diseñado para reducir fatiga visual.**

---

### 11. **One Dark** 🌑
```
Colores: Azul claro + Cyan
Estilo: Moderno equilibrado
Ideal para: Uso prolongado
```
**Paleta:**
- Primary: `#61afef` (Azul claro)
- Secondary: `#56b6c2` (Cyan)
- Success: `#98c379` (Verde)
- Warning: `#e5c07b` (Amarillo)
- Danger: `#e06c75` (Rojo suave)

**Tema de Atom editor.**

---

### 12. **Synthwave 84** 🌆
```
Colores: Rosa + Verde neón
Estilo: Retro 80s
Ideal para: Nostalgia synthwave
```
**Paleta:**
- Primary: `#f92aad` (Rosa neón)
- Secondary: `#fe4450` (Rojo neón)
- Success: `#72f1b8` (Verde neón)
- Warning: `#fede5d` (Amarillo neón)
- Danger: `#fe4450` (Rojo neón)

**Inspirado en los 80s.**

---

### 13. **GitHub Dark** 🐙
```
Colores: Azul GitHub
Estilo: Profesional limpio
Ideal para: Desarrolladores
```
**Paleta:**
- Primary: `#58a6ff` (Azul GitHub)
- Secondary: `#1f6feb` (Azul oscuro)
- Success: `#3fb950` (Verde)
- Warning: `#d29922` (Amarillo)
- Danger: `#f85149` (Rojo)

---

### 14. **Material Dark** 📱
```
Colores: Azul Material Design
Estilo: Google Material
Ideal para: Estética moderna
```
**Paleta:**
- Primary: `#82aaff` (Azul material)
- Secondary: `#c792ea` (Púrpura)
- Success: `#c3e88d` (Verde claro)
- Warning: `#ffcb6b` (Amarillo)
- Danger: `#f07178` (Rojo suave)

---

### 15. **Ayu Dark** 🌙
```
Colores: Azul cielo minimalista
Estilo: Moderno limpio
Ideal para: Simplicidad
```
**Paleta:**
- Primary: `#59c2ff` (Azul cielo)
- Secondary: `#39bae6` (Azul claro)
- Success: `#aad94c` (Verde lima)
- Warning: `#ffb454` (Naranja)
- Danger: `#f07178` (Rosa)

---

## 🔄 Cambiar Tema

### **Desde la Interfaz:**
1. Menú principal → "Cambiar Tema"
2. Selecciona tu tema favorito
3. Clic en "Aplicar y Reiniciar"
4. ✨ Dashboard se reinicia automáticamente

### **Desde Código:**
Editar `data/theme_config.json`:
```json
{
  "selected_theme": "matrix"
}
```

---

## 🎨 Crear Tema Personalizado

### **Paso 1: Editar `config/themes.py`**

```python
THEMES = {
    # ... temas existentes ...
    
    "mi_tema": {
        "name": "Mi Tema Personalizado",
        "colors": {
            "primary": "#ff00ff",      # Color principal
            "secondary": "#00ffff",    # Color secundario
            "success": "#00ff00",      # Verde éxito
            "warning": "#ffff00",      # Amarillo advertencia
            "danger": "#ff0000",       # Rojo peligro
            "bg_dark": "#000000",      # Fondo oscuro
            "bg_medium": "#111111",    # Fondo medio
            "bg_light": "#222222",     # Fondo claro
            "text": "#ffffff",         # Texto
            "text_dim": "#aaaaaa",     # Texto tenue
            "border": "#ff00ff"        # Borde
        }
    }
}
```

### **Paso 2: Usar el Tema**

1. Reinicia el dashboard
2. "Cambiar Tema" → Aparecerá "Mi Tema Personalizado"
3. Selecciónalo y aplica

---

## 🎯 Guía de Colores

### **Colores Obligatorios:**
```python
"primary"    # Botones, sliders, elementos principales
"secondary"  # Títulos, elementos secundarios
"success"    # Indicadores positivos (<30% uso)
"warning"    # Indicadores medios (30-70% uso)
"danger"     # Indicadores altos (>70% uso)
"bg_dark"    # Fondo más oscuro
"bg_medium"  # Fondo medio
"bg_light"   # Fondo más claro
"text"       # Texto principal
"text_dim"   # Texto secundario/tenue
"border"     # Bordes de elementos
```

### **Dónde se Usa Cada Color:**

| Color | Uso |
|-------|-----|
| `primary` | Botones, sliders activos, bordes principales |
| `secondary` | Títulos de sección, hover de sliders/scrollbars |
| `success` | CPU/RAM <30%, mensajes de éxito |
| `warning` | CPU/RAM 30-70%, advertencias |
| `danger` | CPU/RAM >70%, errores, botón "Matar" |
| `bg_dark` | Fondo de cards, filas alternadas |
| `bg_medium` | Fondo principal de ventanas |
| `bg_light` | Fondo de sliders, elementos elevados |
| `text` | Texto principal |
| `text_dim` | Texto secundario (usuarios, paths) |
| `border` | Bordes de botones y elementos |

---

## 💡 Tips para Crear Temas

### **1. Contraste**
Asegura que `text` contraste bien con todos los fondos:
```python
# Bueno
"bg_dark": "#000000"
"text": "#ffffff"

# Malo (poco contraste)
"bg_dark": "#222222"
"text": "#333333"
```

### **2. Secondary Distintivo**
El color `secondary` debe ser diferente de los fondos:
```python
# ❌ Malo - secondary igual a bg_medium
"secondary": "#111111"
"bg_medium": "#111111"

# ✅ Bueno - secondary visible
"secondary": "#00ffff"
"bg_medium": "#111111"
```

### **3. Jerarquía de Fondos**
```python
bg_dark < bg_medium < bg_light
#000000   #111111     #222222
```

### **4. Paleta Armónica**
Usa una herramienta como:
- [Coolors.co](https://coolors.co)
- [Adobe Color](https://color.adobe.com)
- [Paletton](https://paletton.com)

---

## 🔍 Preview de Temas

Todos los temas han sido optimizados para:
- ✅ Alto contraste
- ✅ Legibilidad
- ✅ `secondary` distintivo
- ✅ Colores armónicos

**11 temas fueron corregidos** en v2.0 para tener `secondary` visible.

---

## 📊 Comparación de Temas

| Tema | Estilo | Colores Dominantes | Ideal Para |
|------|--------|-------------------|------------|
| Cyberpunk | Neón | Cyan + Verde | Original |
| Matrix | Película | Verde | Fans Matrix |
| Sunset | Cálido | Naranja + Púrpura | Acogedor |
| Ocean | Fresco | Azul + Aqua | Limpio |
| Dracula | Elegante | Púrpura + Rosa | Devs |
| Nord | Minimalista | Azul hielo | Nórdico |
| Tokyo Night | Nocturno | Azul + Púrpura | Noche |
| Monokai | IDE | Cyan + Verde | Código |
| Gruvbox | Retro | Naranja + Beige | Vintage |
| Solarized | Científico | Azul + Cyan | Precisión |
| One Dark | Moderno | Azul claro | Equilibrado |
| Synthwave | 80s | Rosa + Verde | Nostalgia |
| GitHub | Profesional | Azul GitHub | Devs |
| Material | Google | Azul material | Moderno |
| Ayu | Simple | Azul cielo | Minimalista |

---

## 🔄 Persistencia de Temas

El tema seleccionado se guarda en:
```
data/theme_config.json
```

**Se mantiene entre reinicios** del dashboard.

---

## 🆘 Troubleshooting

### **Tema no se aplica**
**Solución**: Usa "Aplicar y Reiniciar" (reinicia automáticamente)

### **Colores se ven mal**
**Causa**: Tema con contraste bajo  
**Solución**: Prueba otro tema o ajusta `text` y fondos

### **Secondary no se ve**
**Causa**: Color igual a fondo  
**Solución**: Ya corregido en v2.0. Actualiza.

---

**¡Personaliza tu dashboard!** 🎨✨
````

## File: config/themes.py
````python
"""
Sistema de temas personalizados
"""
import json
import os
from pathlib import Path
# ========================================
# TEMAS DISPONIBLES
# ========================================

THEMES = {
    "cyberpunk": {
        "name": "Cyberpunk (Original)",
        "colors": {
            "primary": "#00ffff",      # Cyan brillante
            "secondary": "#14611E",    # Verde oscuro ✓ OK
            "success": "#1ae313",      # Verde neón
            "warning": "#ffaa00",      # Naranja
            "danger": "#ff3333",       # Rojo
            "bg_dark": "#111111",      # Negro profundo
            "bg_medium": "#212121",    # Gris muy oscuro
            "bg_light": "#222222",     # Gris oscuro
            "text": "#ffffff",         # Blanco
            "text_dim": "#aaaaaa",     # Gris claro
            "border": "#00ffff"        # Cyan
        }
    },
    
    "matrix": {
        "name": "Matrix",
        "colors": {
            "primary": "#00ff00",      # Verde Matrix brillante
            "secondary": "#00ff88",    # Verde-cyan (bien diferente)
            "success": "#33ff33",      # Verde claro
            "warning": "#ffff00",      # Amarillo puro (muy diferente)
            "danger": "#ff0000",       # Rojo
            "bg_dark": "#000000",      # Negro puro
            "bg_medium": "#001a00",    # Negro verdoso sutil
            "bg_light": "#003300",     # Verde muy oscuro
            "text": "#00ff00",         # Verde brillante
            "text_dim": "#009900",     # Verde medio oscuro
            "border": "#00ff00"        # Verde brillante
        }
    },
    
    "sunset": {
        "name": "Sunset (Atardecer)",
        "colors": {
            "primary": "#ff6b35",      # Naranja cálido
            "secondary": "#f7931e",    # Naranja dorado ✓ CORREGIDO
            "success": "#ffd23f",      # Amarillo dorado
            "warning": "#ffd23f",      # Amarillo dorado
            "danger": "#d62828",       # Rojo oscuro
            "bg_dark": "#1a1423",      # Púrpura muy oscuro
            "bg_medium": "#2d1b3d",    # Púrpura oscuro
            "bg_light": "#3e2a47",     # Púrpura medio
            "text": "#f8f0e3",         # Beige claro
            "text_dim": "#c4b5a0",     # Beige oscuro
            "border": "#ff6b35"        # Naranja
        }
    },
    
    "ocean": {
        "name": "Ocean (Océano)",
        "colors": {
            "primary": "#00d4ff",      # Azul cielo
            "secondary": "#48dbfb",    # Azul claro ✓ CORREGIDO
            "success": "#1dd1a1",      # Verde agua
            "warning": "#feca57",      # Amarillo suave
            "danger": "#ee5a6f",       # Rosa coral
            "bg_dark": "#0c2233",      # Azul muy oscuro
            "bg_medium": "#163447",    # Azul oscuro
            "bg_light": "#1e4a5f",     # Azul medio
            "text": "#e0f7ff",         # Azul muy claro
            "text_dim": "#8899aa",     # Azul grisáceo
            "border": "#00d4ff"        # Azul cielo
        }
    },
    
    "dracula": {
        "name": "Dracula",
        "colors": {
            "primary": "#bd93f9",      # Púrpura pastel
            "secondary": "#ff79c6",    # Rosa ✓ CORREGIDO
            "success": "#50fa7b",      # Verde pastel
            "warning": "#f1fa8c",      # Amarillo pastel
            "danger": "#ff5555",       # Rojo pastel
            "bg_dark": "#1e1f29",      # Azul muy oscuro
            "bg_medium": "#282a36",    # Gris azulado
            "bg_light": "#44475a",     # Gris medio
            "text": "#f8f8f2",         # Blanco suave
            "text_dim": "#6272a4",     # Azul grisáceo
            "border": "#bd93f9"        # Púrpura
        }
    },
    
    "nord": {
        "name": "Nord (Nórdico)",
        "colors": {
            "primary": "#88c0d0",      # Azul hielo
            "secondary": "#5e81ac",    # Azul oscuro ✓ CORREGIDO
            "success": "#a3be8c",      # Verde suave
            "warning": "#ebcb8b",      # Amarillo suave
            "danger": "#bf616a",       # Rojo suave
            "bg_dark": "#1e2229",      # Negro azulado
            "bg_medium": "#2e3440",    # Gris polar
            "bg_light": "#3b4252",     # Gris claro
            "text": "#eceff4",         # Blanco nieve
            "text_dim": "#8899aa",     # Gris azulado
            "border": "#88c0d0"        # Azul hielo
        }
    },
    
    "tokyo_night": {
        "name": "Tokyo Night",
        "colors": {
            "primary": "#7aa2f7",      # Azul brillante
            "secondary": "#bb9af7",    # Púrpura ✓ CORREGIDO
            "success": "#9ece6a",      # Verde
            "warning": "#e0af68",      # Naranja suave
            "danger": "#f7768e",       # Rosa
            "bg_dark": "#16161e",      # Negro azulado
            "bg_medium": "#1a1b26",    # Azul noche
            "bg_light": "#24283b",     # Azul oscuro
            "text": "#c0caf5",         # Azul claro
            "text_dim": "#565f89",     # Azul oscuro
            "border": "#7aa2f7"        # Azul
        }
    },
    
    "monokai": {
        "name": "Monokai",
        "colors": {
            "primary": "#66d9ef",      # Azul claro
            "secondary": "#fd971f",    # Naranja ✓ CORREGIDO
            "success": "#a6e22e",      # Verde lima
            "warning": "#e6db74",      # Amarillo
            "danger": "#f92672",       # Rosa fucsia
            "bg_dark": "#1e1f1c",      # Negro verdoso
            "bg_medium": "#272822",    # Verde muy oscuro
            "bg_light": "#3e3d32",     # Verde grisáceo
            "text": "#f8f8f2",         # Blanco suave
            "text_dim": "#75715e",     # Gris verdoso
            "border": "#66d9ef"        # Azul claro
        }
    },
    
    "gruvbox": {
        "name": "Gruvbox",
        "colors": {
            "primary": "#fe8019",      # Naranja
            "secondary": "#d65d0e",    # Naranja oscuro ✓ CORREGIDO
            "success": "#b8bb26",      # Verde lima
            "warning": "#fabd2f",      # Amarillo
            "danger": "#fb4934",       # Rojo
            "bg_dark": "#1d2021",      # Negro marrón
            "bg_medium": "#282828",    # Gris oscuro
            "bg_light": "#3c3836",     # Gris medio
            "text": "#ebdbb2",         # Beige claro
            "text_dim": "#a89984",     # Beige oscuro
            "border": "#fe8019"        # Naranja
        }
    },
    
    "solarized_dark": {
        "name": "Solarized Dark",
        "colors": {
            "primary": "#268bd2",      # Azul
            "secondary": "#2aa198",    # Cyan ✓ CORREGIDO
            "success": "#859900",      # Verde oliva
            "warning": "#b58900",      # Amarillo oscuro
            "danger": "#dc322f",       # Rojo
            "bg_dark": "#002b36",      # Azul noche
            "bg_medium": "#073642",    # Azul oscuro
            "bg_light": "#586e75",     # Gris azulado
            "text": "#fdf6e3",         # Beige muy claro
            "text_dim": "#839496",     # Gris azulado
            "border": "#268bd2"        # Azul
        }
    },
    
    "one_dark": {
        "name": "One Dark",
        "colors": {
            "primary": "#61afef",      # Azul claro
            "secondary": "#56b6c2",    # Cyan ✓ CORREGIDO
            "success": "#98c379",      # Verde
            "warning": "#e5c07b",      # Amarillo
            "danger": "#e06c75",       # Rojo suave
            "bg_dark": "#1e2127",      # Negro azulado
            "bg_medium": "#282c34",    # Gris oscuro
            "bg_light": "#3e4451",     # Gris medio
            "text": "#abb2bf",         # Gris claro
            "text_dim": "#5c6370",     # Gris oscuro
            "border": "#61afef"        # Azul
        }
    },
    
    "synthwave": {
        "name": "Synthwave 84",
        "colors": {
            "primary": "#f92aad",      # Rosa neón
            "secondary": "#fe4450",    # Rojo neón ✓ CORREGIDO
            "success": "#72f1b8",      # Verde neón
            "warning": "#fede5d",      # Amarillo neón
            "danger": "#fe4450",       # Rojo neón
            "bg_dark": "#0e0b16",      # Negro púrpura
            "bg_medium": "#241734",    # Púrpura oscuro
            "bg_light": "#2d1b3d",     # Púrpura medio
            "text": "#ffffff",         # Blanco
            "text_dim": "#ff7edb",     # Rosa claro
            "border": "#f92aad"        # Rosa neón
        }
    },
    
    "github_dark": {
        "name": "GitHub Dark",
        "colors": {
            "primary": "#58a6ff",      # Azul GitHub
            "secondary": "#1f6feb",    # Azul oscuro ✓ CORREGIDO
            "success": "#3fb950",      # Verde
            "warning": "#d29922",      # Amarillo
            "danger": "#f85149",       # Rojo
            "bg_dark": "#0d1117",      # Negro
            "bg_medium": "#161b22",    # Gris muy oscuro
            "bg_light": "#21262d",     # Gris oscuro
            "text": "#c9d1d9",         # Gris claro
            "text_dim": "#8b949e",     # Gris medio
            "border": "#58a6ff"        # Azul
        }
    },
    
    "material": {
        "name": "Material Dark",
        "colors": {
            "primary": "#82aaff",      # Azul material
            "secondary": "#c792ea",    # Púrpura ✓ CORREGIDO
            "success": "#c3e88d",      # Verde claro
            "warning": "#ffcb6b",      # Amarillo
            "danger": "#f07178",       # Rojo suave
            "bg_dark": "#0f111a",      # Negro azulado
            "bg_medium": "#1e2029",    # Gris oscuro
            "bg_light": "#292d3e",     # Gris azulado
            "text": "#eeffff",         # Blanco azulado
            "text_dim": "#546e7a",     # Gris azulado
            "border": "#82aaff"        # Azul
        }
    },
    
    "ayu_dark": {
        "name": "Ayu Dark",
        "colors": {
            "primary": "#59c2ff",      # Azul cielo
            "secondary": "#39bae6",    # Azul claro ✓ CORREGIDO
            "success": "#aad94c",      # Verde lima
            "warning": "#ffb454",      # Naranja
            "danger": "#f07178",       # Rosa
            "bg_dark": "#0a0e14",      # Negro azulado
            "bg_medium": "#0d1017",    # Negro
            "bg_light": "#1c2128",     # Gris muy oscuro
            "text": "#b3b1ad",         # Gris claro
            "text_dim": "#626a73",     # Gris oscuro
            "border": "#59c2ff"        # Azul
        }
    }
}

# Tema por defecto
DEFAULT_THEME = "cyberpunk"

# ========================================
# FUNCIONES DE GESTIÓN DE TEMAS
# ========================================

def get_theme(theme_name: str) -> dict:
    """
    Obtiene un tema por su nombre
    
    Args:
        theme_name: Nombre del tema
        
    Returns:
        Diccionario con los colores del tema
    """
    return THEMES.get(theme_name, THEMES[DEFAULT_THEME])


def get_available_themes() -> list:
    """
    Obtiene lista de temas disponibles
    
    Returns:
        Lista de tuplas (id, nombre_descriptivo)
    """
    return [(key, theme["name"]) for key, theme in THEMES.items()]


def get_theme_colors(theme_name: str) -> dict:
    """
    Obtiene los colores de un tema
    
    Args:
        theme_name: Nombre del tema
        
    Returns:
        Diccionario de colores
    """
    theme = get_theme(theme_name)
    return theme["colors"]


# ========================================
# PREVIEW DE TEMAS (Para mostrar al usuario)
# ========================================

def get_theme_preview() -> str:
    """
    Genera un texto con preview de todos los temas
    
    Returns:
        String con la lista de temas y sus colores principales
    """
    preview = "TEMAS DISPONIBLES:\n\n"
    
    for theme_id, theme_data in THEMES.items():
        colors = theme_data["colors"]
        preview += f"• {theme_data['name']} ({theme_id})\n"
        preview += f"  Color principal: {colors['primary']}\n"
        preview += f"  Fondo: {colors['bg_dark']}\n"
        preview += f"  Texto: {colors['text']}\n\n"
    
    return preview


# ========================================
# CREAR TEMA PERSONALIZADO
# ========================================

def create_custom_theme(name: str, colors: dict) -> dict:
    """
    Crea un tema personalizado
    
    Args:
        name: Nombre descriptivo del tema
        colors: Diccionario con los colores personalizados
        
    Returns:
        Diccionario del tema creado
    """
    # Validar que tenga todos los colores necesarios
    required_keys = ["primary", "secondary", "success", "warning", "danger",
                     "bg_dark", "bg_medium", "bg_light", "text", "border"]
    
    for key in required_keys:
        if key not in colors:
            raise ValueError(f"Falta el color '{key}' en el tema personalizado")
    
    return {
        "name": name,
        "colors": colors
    }


# ========================================
# GUARDAR/CARGAR TEMA SELECCIONADO
# ========================================


THEME_CONFIG_FILE = Path(__file__).parent.parent / "data" / "theme_config.json"


def save_selected_theme(theme_name: str):
    """
    Guarda el tema seleccionado en archivo
    
    Args:
        theme_name: Nombre del tema a guardar
    """
    # Asegurar que el directorio existe
    THEME_CONFIG_FILE.parent.mkdir(exist_ok=True)
    
    config = {"selected_theme": theme_name}
    
    tmp_file = str(THEME_CONFIG_FILE) + ".tmp"
    with open(tmp_file, "w") as f:
        json.dump(config, f, indent=2)
    os.replace(tmp_file, THEME_CONFIG_FILE)


def load_selected_theme() -> str:
    """
    Carga el tema seleccionado desde archivo
    
    Returns:
        Nombre del tema seleccionado o DEFAULT_THEME
    """
    try:
        with open(THEME_CONFIG_FILE) as f:
            config = json.load(f)
            theme = config.get("selected_theme", DEFAULT_THEME)
            
            # Verificar que el tema existe
            if theme in THEMES:
                return theme
            else:
                return DEFAULT_THEME
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_THEME
````

## File: core/system_monitor.py
````python
"""
Monitor del sistema
"""
import psutil
from collections import deque
from typing import Dict, Tuple
from config.settings import HISTORY
from utils.system_utils import SystemUtils
from config.settings import UPDATE_MS
from config.settings import COLORS

class SystemMonitor:
    """Monitor centralizado de recursos del sistema"""
    
    def __init__(self):
        self.system_utils = SystemUtils()
        
        # Historiales
        self.cpu_hist = deque(maxlen=HISTORY)
        self.ram_hist = deque(maxlen=HISTORY)
        self.temp_hist = deque(maxlen=HISTORY)
        self.disk_hist = deque(maxlen=HISTORY)
        self.disk_write_hist = deque(maxlen=HISTORY)
        self.disk_read_hist = deque(maxlen=HISTORY)
        
        # Estado anterior para cálculos incrementales
        self.last_disk_io = psutil.disk_io_counters()
    
    def get_current_stats(self) -> Dict:
        """
        Obtiene estadísticas actuales del sistema
        
        Returns:
            Diccionario con todas las métricas actuales
        """
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        ram_used = psutil.virtual_memory().used
        temp = self.system_utils.get_cpu_temp()
        disk_usage = psutil.disk_usage('/').percent
        
        # Calcular I/O de disco
        disk_io = psutil.disk_io_counters()
        disk_read_bytes = max(0, disk_io.read_bytes - self.last_disk_io.read_bytes)
        disk_write_bytes = max(0, disk_io.write_bytes - self.last_disk_io.write_bytes)
        self.last_disk_io = disk_io
        
        # Convertir a MB/s

        seconds = UPDATE_MS / 1000.0
        disk_read_mb = (disk_read_bytes / (1024 * 1024)) / seconds
        disk_write_mb = (disk_write_bytes / (1024 * 1024)) / seconds
        
        return {
            'cpu': cpu,
            'ram': ram,
            'ram_used': ram_used,
            'temp': temp,
            'disk_usage': disk_usage,
            'disk_read_mb': disk_read_mb,
            'disk_write_mb': disk_write_mb
        }
    
    def update_history(self, stats: Dict) -> None:
        """
        Actualiza los historiales con las estadísticas actuales
        
        Args:
            stats: Diccionario con estadísticas actuales
        """
        self.cpu_hist.append(stats['cpu'])
        self.ram_hist.append(stats['ram'])
        self.temp_hist.append(stats['temp'])
        self.disk_hist.append(stats['disk_usage'])
        self.disk_read_hist.append(stats['disk_read_mb'])
        self.disk_write_hist.append(stats['disk_write_mb'])
    
    def get_history(self) -> Dict:
        """
        Obtiene todos los historiales
        
        Returns:
            Diccionario con todos los historiales
        """
        return {
            'cpu': list(self.cpu_hist),
            'ram': list(self.ram_hist),
            'temp': list(self.temp_hist),
            'disk': list(self.disk_hist),
            'disk_read': list(self.disk_read_hist),
            'disk_write': list(self.disk_write_hist)
        }
    
    @staticmethod
    def level_color(value: float, warn: float, crit: float) -> str:
        """
        Determina el color según el nivel de alerta
        
        Args:
            value: Valor actual
            warn: Umbral de advertencia
            crit: Umbral crítico
            
        Returns:
            Color en formato hex
        """
        
        if value >= crit:
            return COLORS['danger']
        elif value >= warn:
            return COLORS['warning']
        else:
            return COLORS['primary']
````

## File: core/update_monitor.py
````python
"""
Monitor de actualizaciones del sistema
"""
import subprocess
import time
from typing import Dict
from utils.logger import get_logger

logger = get_logger(__name__)


class UpdateMonitor:
    """Lógica para verificar actualizaciones del sistema con caché"""

    def __init__(self):
        # Inicializar con tiempo actual para que la caché sea válida desde el inicio
        # Solo ejecuta apt update real cuando: arranque (main.py) o usuario pulsa "Buscar"
        self.last_check_time = time.time()
        self.cached_result = {"pending": 0, "status": "Unknown", "message": "No comprobado"}
        self.check_interval = 43200  # 12 horas en segundos

    def check_updates(self, force=False) -> Dict:
        """
        Verifica actualizaciones pendientes con sistema de caché.

        Args:
            force: Si True, ignora el caché y ejecuta apt update real

        Returns:
            Diccionario con pending, status y message
        """
        current_time = time.time()

        # Devolver caché si no ha pasado el intervalo y no se fuerza
        if not force and (current_time - self.last_check_time) < self.check_interval:
            logger.debug("[UpdateMonitor] Devolviendo resultado en caché")
            return self.cached_result

        try:
            logger.info("[UpdateMonitor] Ejecutando búsqueda real de actualizaciones (apt update)...")

            result = subprocess.run(
                ["sudo", "apt", "update"],
                capture_output=True,
                timeout=20
            )
            if result.returncode != 0:
                logger.warning(f"[UpdateMonitor] apt update retornó código {result.returncode}")

            cmd = "apt-get -s upgrade | grep '^Inst ' | wc -l"
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            count = int(output) if output else 0

            if count > 0:
                logger.info(f"[UpdateMonitor] {count} paquetes pendientes de actualización")
            else:
                logger.debug("[UpdateMonitor] Sistema al día, sin actualizaciones pendientes")

            self.cached_result = {
                "pending": count,
                "status": "Ready" if count > 0 else "Updated",
                "message": f"{count} paquetes pendientes" if count > 0 else "Sistema al día"
            }
            self.last_check_time = current_time
            return self.cached_result

        except subprocess.TimeoutExpired:
            logger.error("[UpdateMonitor] check_updates: timeout ejecutando apt update (>20s)")
            return {"pending": 0, "status": "Error", "message": "Timeout ejecutando apt update"}
        except FileNotFoundError:
            logger.error("[UpdateMonitor] check_updates: apt no encontrado en el sistema")
            return {"pending": 0, "status": "Error", "message": "apt no encontrado"}
        except ValueError as e:
            logger.error(f"[UpdateMonitor] check_updates: error parseando resultado: {e}")
            return {"pending": 0, "status": "Error", "message": str(e)}
        except Exception as e:
            logger.error(f"[UpdateMonitor] check_updates: error inesperado: {e}")
            return {"pending": 0, "status": "Error", "message": str(e)}
````

## File: ui/windows/monitor.py
````python
"""
Ventana de monitoreo del sistema
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, 
                             DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS,
                             CPU_WARN, CPU_CRIT, TEMP_WARN, TEMP_CRIT,
                             RAM_WARN, RAM_CRIT)
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import GraphWidget
from core.system_monitor import SystemMonitor


class MonitorWindow(ctk.CTkToplevel):
    """Ventana de monitoreo del sistema"""
    
    def __init__(self, parent, system_monitor: SystemMonitor):
        super().__init__(parent)
        
        # Referencias
        self.system_monitor = system_monitor
        
        # Widgets para actualización
        self.widgets = {}
        self.graphs = {}
        
        # Configurar ventana
        self.title("Monitor del Sistema")
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
        
        # ── Header unificado ──────────────────────────────────────────────────
        self._header = make_window_header(
            main,
            title="MONITOR DEL SISTEMA",
            on_close=self.destroy,
        )
        
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
        
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Secciones de monitoreo
        self._create_cpu_section(inner)
        self._create_ram_section(inner)
        self._create_temp_section(inner)
        self._create_disk_usage_section(inner)
        self._create_disk_io_section(inner)
    
    def _create_metric_section(self, parent, title: str, metric_key: str,
                               unit: str, max_val: float = 100):
        """Crea una sección genérica para una métrica"""
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        frame.pack(fill="x", pady=10, padx=10)
        
        # Label del título
        label = ctk.CTkLabel(
            frame,
            text=title,
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        label.pack(anchor="w", pady=(5, 0), padx=10)
        
        # Valor actual
        value_label = ctk.CTkLabel(
            frame,
            text=f"0.0 {unit}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'])
        )
        value_label.pack(anchor="e", pady=(0, 5), padx=10)
        
        # Gráfica
        graph = GraphWidget(frame, width=DSI_WIDTH-80, height=100)
        graph.pack(pady=(0, 10))
        
        # Guardar referencias
        self.widgets[f"{metric_key}_label"] = label
        self.widgets[f"{metric_key}_value"] = value_label
        self.graphs[metric_key] = {
            'widget': graph,
            'max_val': max_val
        }
    
    def _create_cpu_section(self, parent):
        """Crea la sección de CPU"""
        self._create_metric_section(parent, "CPU %", "cpu", "%", 100)
    
    def _create_ram_section(self, parent):
        """Crea la sección de RAM"""
        self._create_metric_section(parent, "RAM %", "ram", "%", 100)
    
    def _create_temp_section(self, parent):
        """Crea la sección de temperatura"""
        self._create_metric_section(parent, "TEMPERATURA", "temp", "°C", 85)
    
    def _create_disk_usage_section(self, parent):
        """Crea la sección de uso de disco"""
        self._create_metric_section(parent, "DISCO %", "disk", "%", 100)
    
    def _create_disk_io_section(self, parent):
        """Crea la sección de I/O de disco"""
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        frame.pack(fill="x", pady=10, padx=10)
        
        # Título
        title = ctk.CTkLabel(
            frame,
            text="I/O DE DISCO",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        title.pack(anchor="w", pady=(5, 10), padx=10)
        
        # Escritura
        write_label = ctk.CTkLabel(
            frame,
            text="ESCRITURA",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        )
        write_label.pack(anchor="w", pady=(0, 0), padx=10)
        
        write_value = ctk.CTkLabel(
            frame,
            text="0.0 MB/s",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'])
        )
        write_value.pack(anchor="e", pady=(0, 5), padx=10)
        
        write_graph = GraphWidget(frame, width=DSI_WIDTH-80, height=80)
        write_graph.pack(pady=(0, 10))
        
        # Lectura
        read_label = ctk.CTkLabel(
            frame,
            text="LECTURA",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        )
        read_label.pack(anchor="w", pady=(0, 0), padx=10)
        
        read_value = ctk.CTkLabel(
            frame,
            text="0.0 MB/s",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'])
        )
        read_value.pack(anchor="e", pady=(0, 5), padx=10)
        
        read_graph = GraphWidget(frame, width=DSI_WIDTH-80, height=80)
        read_graph.pack(pady=(0, 10))
        
        # Guardar referencias
        self.widgets['disk_write_label'] = write_label
        self.widgets['disk_write_value'] = write_value
        self.widgets['disk_read_label'] = read_label
        self.widgets['disk_read_value'] = read_value
        
        self.graphs['disk_write'] = {
            'widget': write_graph,
            'max_val': 50
        }
        self.graphs['disk_read'] = {
            'widget': read_graph,
            'max_val': 50
        }
    
    def _update(self):
        """Actualiza los datos del sistema"""
        if not self.winfo_exists():
            return
        
        # Obtener estadísticas actuales
        stats = self.system_monitor.get_current_stats()
        self.system_monitor.update_history(stats)
        history = self.system_monitor.get_history()
        
        # Actualizar CPU
        self._update_metric(
            'cpu',
            stats['cpu'],
            history['cpu'],
            "%",
            CPU_WARN,
            CPU_CRIT
        )
        
        # Actualizar RAM
        self._update_metric(
            'ram',
            stats['ram'],
            history['ram'],
            "%",
            RAM_WARN,
            RAM_CRIT
        )
        
        # Actualizar Temperatura
        self._update_metric(
            'temp',
            stats['temp'],
            history['temp'],
            "°C",
            TEMP_WARN,
            TEMP_CRIT
        )
        
        # Actualizar Disco (uso)
        self._update_metric(
            'disk',
            stats['disk_usage'],
            history['disk'],
            "%",
            60,
            80
        )
        
        # Actualizar Disco I/O
        self._update_disk_io(
            'disk_write',
            stats['disk_write_mb'],
            history['disk_write']
        )
        
        self._update_disk_io(
            'disk_read',
            stats['disk_read_mb'],
            history['disk_read']
        )

        # Actualizar status en header
        cpu  = stats['cpu']
        ram  = stats['ram']
        temp = stats['temp']
        self._header.status_label.configure(
            text=f"CPU {cpu:.0f}%  ·  RAM {ram:.0f}%  ·  {temp:.0f}°C"
        )
        
        # Programar siguiente actualización
        self.after(UPDATE_MS, self._update)
    
    def _update_metric(self, key: str, value: float, history: list,
                      unit: str, warn: float, crit: float):
        """Actualiza una métrica genérica"""
        # Determinar color
        color = self.system_monitor.level_color(value, warn, crit)
        
        # Actualizar label
        value_widget = self.widgets[f"{key}_value"]
        value_widget.configure(
            text=f"{value:.1f} {unit}",
            text_color=color
        )
        
        # Actualizar label de título
        label_widget = self.widgets[f"{key}_label"]
        label_widget.configure(text_color=color)
        
        # Actualizar gráfica
        graph_info = self.graphs[key]
        graph_info['widget'].update(history, graph_info['max_val'], color)
    
    def _update_disk_io(self, key: str, value: float, history: list):
        """Actualiza métricas de I/O de disco"""
        # Determinar color (10 MB/s = warning, 50 MB/s = critical)
        color = self.system_monitor.level_color(value, 10, 50)
        
        # Actualizar valor
        value_widget = self.widgets[f"{key}_value"]
        value_widget.configure(
            text=f"{value:.1f} MB/s",
            text_color=color
        )
        
        # Actualizar label
        label_widget = self.widgets[f"{key}_label"]
        label_widget.configure(text_color=color)
        
        # Actualizar gráfica
        graph_info = self.graphs[key]
        graph_info['widget'].update(history, graph_info['max_val'], color)
````

## File: ui/windows/service.py
````python
"""
Ventana de monitor de servicios systemd
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import confirm_dialog, custom_msgbox
from core.service_monitor import ServiceMonitor


class ServiceWindow(ctk.CTkToplevel):
    """Ventana de monitor de servicios"""

    def __init__(self, parent, service_monitor: ServiceMonitor):
        super().__init__(parent)

        # Referencias
        self.service_monitor = service_monitor

        # Estado
        self.search_var = ctk.StringVar()
        self.filter_var = ctk.StringVar(value="all")
        self.update_paused = False
        self.update_job = None

        # Configurar ventana
        self.title("Monitor de Servicios")
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

        # ── Header unificado ──────────────────────────────────────────────────
        make_window_header(
            main,
            title="MONITOR DE SERVICIOS",
            on_close=self.destroy,
        )

        # Stats en línea propia debajo del header
        stats_bar = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'])
        stats_bar.pack(fill="x", padx=5, pady=(0, 4))
        self.stats_label = ctk.CTkLabel(
            stats_bar,
            text="Cargando...",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        self.stats_label.pack(pady=4, padx=10, anchor="w")

        # Controles (búsqueda y filtros)
        self._create_controls(main)

        # Encabezados de columnas
        self._create_column_headers(main)

        # Área de scroll para servicios
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Limitar altura
        max_height = DSI_HEIGHT - 300

        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
            height=max_height
        )
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")


        StyleManager.style_scrollbar_ctk(scrollbar)

        canvas.configure(yscrollcommand=scrollbar.set)

        # Frame interno para servicios
        self.service_frame = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=self.service_frame, anchor="nw", width=DSI_WIDTH-50)
        self.service_frame.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Botones inferiores
        bottom = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=10, padx=10)

        refresh_btn = make_futuristic_button(
            bottom,
            text="Refrescar",
            command=self._force_update,
            width=15,
            height=6
        )
        refresh_btn.pack(side="left", padx=5)



    def _create_controls(self, parent):
        """Crea controles de búsqueda y filtros"""
        controls = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        controls.pack(fill="x", padx=10, pady=5)

        # Búsqueda
        search_frame = ctk.CTkFrame(controls, fg_color=COLORS['bg_dark'])
        search_frame.pack(side="left", padx=10, pady=10)

        ctk.CTkLabel(
            search_frame,
            text="Buscar:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(0, 5))

        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            width=200,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        search_entry.pack(side="left")
        search_entry.bind("<KeyRelease>", lambda e: self._on_search_change())

        # Filtros
        filter_frame = ctk.CTkFrame(controls, fg_color=COLORS['bg_dark'])
        filter_frame.pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(
            filter_frame,
            text="Filtro:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(0, 5))

        for filter_type, label in [("all", "Todos"), ("active", "Activos"), 
                                   ("inactive", "Inactivos"), ("failed", "Fallidos")]:
            rb = ctk.CTkRadioButton(
                filter_frame,
                text=label,
                variable=self.filter_var,
                value=filter_type,
                command=self._on_filter_change,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=5)
            StyleManager.style_radiobutton_ctk(rb)

    def _create_column_headers(self, parent):
        """Crea encabezados de columnas"""
        headers = ctk.CTkFrame(parent, fg_color=COLORS['bg_light'])
        headers.pack(fill="x", padx=10, pady=(5, 0))

        headers.grid_columnconfigure(0, weight=2, minsize=150)  # Servicio
        headers.grid_columnconfigure(1, weight=1, minsize=100)  # Estado
        headers.grid_columnconfigure(2, weight=1, minsize=80)   # Autostart
        headers.grid_columnconfigure(3, weight=3, minsize=300)  # Acciones

        columns = [
            ("Servicio", "name"),
            ("Estado", "state"),
            ("Autostart", None),
            ("Acciones", None)
        ]

        for i, (label, sort_key) in enumerate(columns):
            if sort_key:
                btn = ctk.CTkButton(
                    headers,
                    text=label,
                    command=lambda k=sort_key: self._on_sort_change(k),
                    fg_color=COLORS['bg_medium'],
                    hover_color=COLORS['bg_dark'],
                    font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                    height=30
                )
            else:
                btn = ctk.CTkLabel(
                    headers,
                    text=label,
                    text_color=COLORS['text'],
                    font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
                )

            btn.grid(row=0, column=i, sticky="ew", padx=2, pady=5)

    def _on_sort_change(self, column: str):
        """Cambia el orden"""
        self.update_paused = True

        if self.service_monitor.sort_by == column:
            self.service_monitor.sort_reverse = not self.service_monitor.sort_reverse
        else:
            self.service_monitor.set_sort(column, reverse=False)

        self._update_now()
        self.after(2000, self._resume_updates)

    def _on_filter_change(self):
        """Cambia el filtro"""
        self.update_paused = True
        self.service_monitor.set_filter(self.filter_var.get())
        self._update_now()
        self.after(2000, self._resume_updates)

    def _on_search_change(self):
        """Callback cuando cambia la búsqueda"""
        self.update_paused = True

        if hasattr(self, '_search_timer'):
            self.after_cancel(self._search_timer)

        self._search_timer = self.after(500, self._do_search)

    def _do_search(self):
        """Ejecuta la búsqueda"""
        self._update_now()
        self.after(3000, self._resume_updates)

    def _update(self):
        """Actualiza la lista de servicios"""
        if not self.winfo_exists():
            return

        if self.update_paused:
            self.update_job = self.after(UPDATE_MS * 5, self._update)  # 10 segundos
            return

        self._update_now()
        self.update_job = self.after(UPDATE_MS * 5, self._update)  # 10 segundos

    def _update_now(self):
        """Actualiza inmediatamente"""
        if not self.winfo_exists():
            return

        # Actualizar estadísticas
        stats = self.service_monitor.get_stats()
        self.stats_label.configure(
            text=f"Total: {stats['total']} | "
                 f"Activos: {stats['active']} | "
                 f"Inactivos: {stats['inactive']} | "
                 f"Fallidos: {stats['failed']} | "
                 f"Autostart: {stats['enabled']}"
        )

        # Limpiar servicios anteriores
        for widget in self.service_frame.winfo_children():
            widget.destroy()

        # Obtener servicios
        search_query = self.search_var.get()
        if search_query:
            services = self.service_monitor.search_services(search_query)
        else:
            services = self.service_monitor.get_services()

        # Limitar a top 30
        services = services[:30]

        # Mostrar servicios
        for i, service in enumerate(services):
            self._create_service_row(service, i)

    def _create_service_row(self, service: dict, row: int):
        """Crea una fila para un servicio"""
        bg_color = COLORS['bg_dark'] if row % 2 == 0 else COLORS['bg_medium']
        row_frame = ctk.CTkFrame(self.service_frame, fg_color=bg_color)
        row_frame.pack(fill="x", pady=2)

        row_frame.grid_columnconfigure(0, weight=2, minsize=150)
        row_frame.grid_columnconfigure(1, weight=1, minsize=100)
        row_frame.grid_columnconfigure(2, weight=1, minsize=80)
        row_frame.grid_columnconfigure(3, weight=3, minsize=300)

        # Icono y nombre
        state_icon = "🟢" if service['active'] == 'active' else "🔴"
        state_color = COLORS[self.service_monitor.get_state_color(service['active'])]

        name_label = ctk.CTkLabel(
            row_frame,
            text=f"{state_icon} {service['name']}",
            text_color=state_color,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
        )
        name_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # Estado
        ctk.CTkLabel(
            row_frame,
            text=service['active'],
            text_color=state_color,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Autostart
        autostart_text = "✓" if service['enabled'] else "✗"
        autostart_color = COLORS['success'] if service['enabled'] else COLORS['text_dim']
        ctk.CTkLabel(
            row_frame,
            text=autostart_text,
            text_color=autostart_color,
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).grid(row=0, column=2, sticky="n", padx=5, pady=5)

        # Botones de acción
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=3, sticky="ew", padx=5, pady=3)

        # Start/Stop
        if service['active'] == 'active':
            stop_btn = ctk.CTkButton(
                actions_frame,
                text="⏸",
                command=lambda s=service: self._stop_service(s),
                fg_color=COLORS['warning'],
                hover_color=COLORS['danger'],
                width=40,
                height=25,
                font=(FONT_FAMILY, 14)
            )
            stop_btn.pack(side="left", padx=2)
        else:
            start_btn = ctk.CTkButton(
                actions_frame,
                text="▶",
                command=lambda s=service: self._start_service(s),
                fg_color=COLORS['success'],
                hover_color="#00aa00",
                width=40,
                height=25,
                font=(FONT_FAMILY, 14)
            )
            start_btn.pack(side="left", padx=2)

        # Restart
        restart_btn = ctk.CTkButton(
            actions_frame,
            text="🔄",
            command=lambda s=service: self._restart_service(s),
            fg_color=COLORS['primary'],
            width=40,
            height=25,
            font=(FONT_FAMILY, 12)
        )
        restart_btn.pack(side="left", padx=2)

        # Logs
        logs_btn = ctk.CTkButton(
            actions_frame,
            text="👁",
            command=lambda s=service: self._view_logs(s),
            fg_color=COLORS['bg_light'],
            width=40,
            height=25,
            font=(FONT_FAMILY, 12)
        )
        logs_btn.pack(side="left", padx=2)

        # Enable/Disable
        if service['enabled']:
            disable_btn = ctk.CTkButton(
                actions_frame,
                text="⚙",
                command=lambda s=service: self._disable_service(s),
                fg_color=COLORS['text_dim'],
                width=40,
                height=25,
                font=(FONT_FAMILY, 12)
            )
            disable_btn.pack(side="left", padx=2)
        else:
            enable_btn = ctk.CTkButton(
                actions_frame,
                text="⚙",
                command=lambda s=service: self._enable_service(s),
                fg_color=COLORS['secondary'],
                width=40,
                height=25,
                font=(FONT_FAMILY, 12)
            )
            enable_btn.pack(side="left", padx=2)

    def _start_service(self, service: dict):
        """Inicia un servicio"""
        def do_start():
            success, message = self.service_monitor.start_service(service['name'])
            custom_msgbox(self, message, "Iniciar Servicio")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Iniciar servicio '{service['name']}'?",
            title="⚠️ Confirmar",
            on_confirm=do_start,
            on_cancel=None
        )

    def _stop_service(self, service: dict):
        """Detiene un servicio"""
        def do_stop():
            success, message = self.service_monitor.stop_service(service['name'])
            custom_msgbox(self, message, "Detener Servicio")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Detener servicio '{service['name']}'?\n\n"
                 f"El servicio dejará de funcionar.",
            title="⚠️ Confirmar",
            on_confirm=do_stop,
            on_cancel=None
        )

    def _restart_service(self, service: dict):
        """Reinicia un servicio"""
        def do_restart():
            success, message = self.service_monitor.restart_service(service['name'])
            custom_msgbox(self, message, "Reiniciar Servicio")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Reiniciar servicio '{service['name']}'?",
            title="⚠️ Confirmar",
            on_confirm=do_restart,
            on_cancel=None
        )

    def _view_logs(self, service: dict):
        """Muestra logs de un servicio"""
        logs = self.service_monitor.get_logs(service['name'], lines=30)

        # Crear ventana de logs
        logs_window = ctk.CTkToplevel(self)
        logs_window.title(f"Logs: {service['name']}")
        logs_window.geometry("700x500")

        # Textbox con logs
        textbox = ctk.CTkTextbox(
            logs_window,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wrap="word"
        )
        textbox.pack(fill="both", expand=True, padx=10, pady=10)
        textbox.insert("1.0", logs)
        textbox.configure(state="disabled")

        # Botón cerrar
        close_btn = make_futuristic_button(
            logs_window,
            text="Cerrar",
            command=logs_window.destroy,
            width=15,
            height=6
        )
        close_btn.pack(pady=10)

    def _enable_service(self, service: dict):
        """Habilita autostart"""
        def do_enable():
            success, message = self.service_monitor.enable_service(service['name'])
            custom_msgbox(self, message, "Habilitar Autostart")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Habilitar autostart para '{service['name']}'?\n\n"
                 f"El servicio se iniciará automáticamente al arrancar.",
            title="⚠️ Confirmar",
            on_confirm=do_enable,
            on_cancel=None
        )

    def _disable_service(self, service: dict):
        """Deshabilita autostart"""
        def do_disable():
            success, message = self.service_monitor.disable_service(service['name'])
            custom_msgbox(self, message, "Deshabilitar Autostart")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Deshabilitar autostart para '{service['name']}'?\n\n"
                 f"El servicio NO se iniciará automáticamente al arrancar.",
            title="⚠️ Confirmar",
            on_confirm=do_disable,
            on_cancel=None
        )

    def _force_update(self):
        """Fuerza actualización inmediata"""
        self.update_paused = False
        self._update_now()

    def _resume_updates(self):
        """Reanuda actualizaciones"""
        self.update_paused = False
````

## File: ui/windows/usb.py
````python
"""
Ventana de monitoreo de dispositivos USB
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox
from utils.system_utils import SystemUtils
from utils.logger import get_logger

logger = get_logger(__name__)


class USBWindow(ctk.CTkToplevel):
    """Ventana de monitoreo de dispositivos USB"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.system_utils = SystemUtils()
        self.device_widgets = []
        
        self.title("Monitor USB")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        
        self._create_ui()
        self._refresh_devices()
    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── Header unificado ──────────────────────────────────────────────────
        make_window_header(
            main,
            title="DISPOSITIVOS USB",
            on_close=self.destroy,
        )
        # Botón Actualizar
        refresh_bar = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        refresh_bar.pack(fill="x", padx=10, pady=(0, 5))
        make_futuristic_button(
            refresh_bar,
            text="Actualizar",
            command=self._refresh_devices,
            width=15,
            height=5
        ).pack(side="right")
        
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=self.canvas.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.devices_frame = ctk.CTkFrame(self.canvas, fg_color=COLORS['bg_medium'])
        self.canvas.create_window(
            (0, 0),
            window=self.devices_frame,
            anchor="nw",
            width=DSI_WIDTH-50
        )
        
        self.devices_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
    
    def _refresh_devices(self):
        """Refresca la lista de dispositivos USB"""
        for widget in self.device_widgets:
            widget.destroy()
        self.device_widgets.clear()
        
        storage_devices = self.system_utils.list_usb_storage_devices()
        other_devices = self.system_utils.list_usb_other_devices()
        
        logger.debug(f"[USBWindow] Dispositivos detectados: {len(storage_devices)} almacenamiento, {len(other_devices)} otros")
        
        if storage_devices:
            self._create_storage_section(storage_devices)
        
        if other_devices:
            self._create_other_devices_section(other_devices)
        
        if not storage_devices and not other_devices:
            no_devices = ctk.CTkLabel(
                self.devices_frame,
                text="No se detectaron dispositivos USB",
                text_color=COLORS['warning'],
                font=(FONT_FAMILY, FONT_SIZES['medium']),
                justify="center"
            )
            no_devices.pack(pady=50)
            self.device_widgets.append(no_devices)
    
    def _create_storage_section(self, storage_devices: list):
        """Crea la sección de almacenamiento USB"""
        title = ctk.CTkLabel(
            self.devices_frame,
            text="ALMACENAMIENTO USB",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        title.pack(anchor="w", pady=(10, 10), padx=10)
        self.device_widgets.append(title)
        
        for idx, device in enumerate(storage_devices):
            self._create_storage_device_widget(device, idx)
    
    def _create_storage_device_widget(self, device: dict, index: int):
        """Crea widget para un dispositivo de almacenamiento"""
        device_frame = ctk.CTkFrame(
            self.devices_frame,
            fg_color=COLORS['bg_dark'],
            border_width=2,
            border_color=COLORS['success']
        )
        device_frame.pack(fill="x", pady=5, padx=10)
        self.device_widgets.append(device_frame)
        
        name = device.get('name', 'USB Disk')
        size = device.get('size', '?')
        dev_type = device.get('type', 'disk')
        
        header = ctk.CTkLabel(
            device_frame,
            text=f"💾 {name} ({dev_type}) - {size}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        )
        header.pack(anchor="w", padx=10, pady=(10, 5))
        
        dev_path = device.get('dev', '?')
        info = ctk.CTkLabel(
            device_frame,
            text=f"Dispositivo: {dev_path}",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        info.pack(anchor="w", padx=10, pady=(0, 5))
        
        eject_btn = make_futuristic_button(
            device_frame,
            text="Expulsar",
            command=lambda d=device: self._eject_device(d),
            width=15,
            height=4
        )
        eject_btn.pack(anchor="w", padx=20, pady=(5, 10))
        
        children = device.get('children', [])
        if children:
            for child in children:
                self._create_partition_widget(device_frame, child)
    
    def _create_partition_widget(self, parent, partition: dict):
        """Crea widget para una partición"""
        name = partition.get('name', '?')
        mount = partition.get('mount')
        size = partition.get('size', '?')
        
        part_text = f"  └─ Partición: {name} ({size})"
        if mount:
            part_text += f" | 📁 Montado en: {mount}"
        else:
            part_text += " | No montado"
        
        part_label = ctk.CTkLabel(
            parent,
            text=part_text,
            text_color=COLORS['primary'] if mount else COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wraplength=DSI_WIDTH - 80,
            anchor="w",
            justify="left"
        )
        part_label.pack(anchor="w", padx=30, pady=2)
    
    def _create_other_devices_section(self, other_devices: list):
        """Crea la sección de otros dispositivos USB"""
        title = ctk.CTkLabel(
            self.devices_frame,
            text="OTROS DISPOSITIVOS USB",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        title.pack(anchor="w", pady=(20, 10), padx=10)
        self.device_widgets.append(title)
        
        for idx, device_line in enumerate(other_devices):
            self._create_other_device_widget(device_line, idx)
    
    def _create_other_device_widget(self, device_line: str, index: int):
        """Crea widget para otro dispositivo USB"""
        device_info = self._parse_lsusb_line(device_line)
        
        device_frame = ctk.CTkFrame(
            self.devices_frame,
            fg_color=COLORS['bg_dark'],
            border_width=1,
            border_color=COLORS['primary']
        )
        device_frame.pack(fill="x", pady=3, padx=10)
        self.device_widgets.append(device_frame)
        
        inner = ctk.CTkFrame(device_frame, fg_color=COLORS['bg_dark'])
        inner.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            inner,
            text=f"#{index + 1}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            width=30
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            inner,
            text=device_info['bus'],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            inner,
            text=device_info['description'],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wraplength=DSI_WIDTH - 200,
            anchor="w",
            justify="left"
        ).pack(side="left", padx=5, fill="x", expand=True)
    
    def _parse_lsusb_line(self, line: str) -> dict:
        """Parsea una línea de lsusb"""
        parts = line.split()
        
        try:
            bus_idx = parts.index("Bus") + 1
            bus = f"Bus {parts[bus_idx]}"
            
            dev_idx = parts.index("Device") + 1
            device_num = parts[dev_idx].rstrip(':')
            bus += f" Dev {device_num}"
            
            id_idx = parts.index("ID") + 2
            description = " ".join(parts[id_idx:])
            
            if len(description) > 50:
                description = description[:47] + "..."
            
        except (ValueError, IndexError):
            bus = "Bus ?"
            description = line
        
        return {'bus': bus, 'description': description}
    
    def _eject_device(self, device: dict):
        """Expulsa un dispositivo USB"""
        device_name = device.get('name', 'dispositivo')
        
        logger.info(f"[USBWindow] Intentando expulsar: '{device_name}' ({device.get('dev', '?')})")
        
        success, message = self.system_utils.eject_usb_device(device)
        
        if success:
            logger.info(f"[USBWindow] Expulsión exitosa: '{device_name}'")
            custom_msgbox(
                self,
                f"✅ {device_name}\n\n{message}\n\nAhora puedes desconectar el dispositivo de forma segura.",
                "Expulsión Exitosa"
            )
            self._refresh_devices()
        else:
            logger.error(f"[USBWindow] Error expulsando '{device_name}': {message}")
            custom_msgbox(
                self,
                f"❌ Error al expulsar {device_name}:\n\n{message}",
                "Error"
            )
````

## File: utils/__init__.py
````python
"""
Paquete de utilidades
"""
from .file_manager import FileManager
from .system_utils import SystemUtils
from .logger import DashboardLogger

__all__ = ['FileManager', 'SystemUtils', 'DashboardLogger']
````

## File: utils/file_manager.py
````python
"""
Gestión de archivos JSON para estado y configuración
"""
import json
import os
from typing import Dict, List, Any
from config.settings import STATE_FILE, CURVE_FILE
from utils.logger import get_logger

logger = get_logger(__name__)


class FileManager:
    """Gestor centralizado de archivos JSON"""
    
    @staticmethod
    def write_state(data: Dict[str, Any]) -> None:
        """
        Escribe el estado de forma atómica usando archivo temporal
        
        Args:
            data: Diccionario con los datos a guardar
        """
        tmp = str(STATE_FILE) + ".tmp"
        try:
            with open(tmp, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, STATE_FILE)
        except OSError as e:
            logger.error(f"[FileManager] write_state: error escribiendo estado: {e}")
            raise
    
    @staticmethod
    def load_state() -> Dict[str, Any]:
        """
        Carga el estado guardado
        
        Returns:
            Diccionario con mode y target_pwm
        """
        default_state = {"mode": "auto", "target_pwm": None}
        
        try:
            with open(STATE_FILE) as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    logger.warning("[FileManager] load_state: contenido inválido, usando estado por defecto")
                    return default_state
                return {
                    "mode": data.get("mode", "auto"),
                    "target_pwm": data.get("target_pwm")
                }
        except FileNotFoundError:
            logger.debug(f"[FileManager] load_state: {STATE_FILE} no existe, usando estado por defecto")
            return default_state
        except json.JSONDecodeError as e:
            logger.error(f"[FileManager] load_state: JSON corrupto en {STATE_FILE}: {e} — usando estado por defecto")
            return default_state
    
    @staticmethod
    def load_curve() -> List[Dict[str, int]]:
        """
        Carga la curva de ventiladores
        
        Returns:
            Lista de puntos ordenados por temperatura
        """
        default_curve = [
            {"temp": 40, "pwm": 100},
            {"temp": 50, "pwm": 100},
            {"temp": 60, "pwm": 100},
            {"temp": 70, "pwm": 63},
            {"temp": 80, "pwm": 81}
        ]
        
        try:
            with open(CURVE_FILE) as f:
                data = json.load(f)
                pts = data.get("points", [])
                
                if not isinstance(pts, list):
                    logger.warning("[FileManager] load_curve: 'points' no es una lista, usando curva por defecto")
                    return default_curve
                
                sanitized = []
                for p in pts:
                    try:
                        temp = int(p.get("temp", 0))
                    except (ValueError, TypeError):
                        temp = 0
                    
                    try:
                        pwm = int(p.get("pwm", 0))
                    except (ValueError, TypeError):
                        pwm = 0
                    
                    pwm = max(0, min(255, pwm))
                    sanitized.append({"temp": temp, "pwm": pwm})
                
                if not sanitized:
                    logger.warning("[FileManager] load_curve: curva vacía tras sanear, usando curva por defecto")
                    return default_curve
                
                return sorted(sanitized, key=lambda x: x["temp"])
                
        except FileNotFoundError:
            logger.debug(f"[FileManager] load_curve: {CURVE_FILE} no existe, usando curva por defecto")
            return default_curve
        except json.JSONDecodeError as e:
            logger.error(f"[FileManager] load_curve: JSON corrupto en {CURVE_FILE}: {e} — usando curva por defecto")
            return default_curve
    
    @staticmethod
    def save_curve(points: List[Dict[str, int]]) -> None:
        """
        Guarda la curva de ventiladores
        
        Args:
            points: Lista de puntos {temp, pwm}
        """
        data = {"points": points}
        tmp = str(CURVE_FILE) + ".tmp"
        try:
            with open(tmp, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, CURVE_FILE)
            logger.info(f"[FileManager] save_curve: curva guardada ({len(points)} puntos)")
        except OSError as e:
            logger.error(f"[FileManager] save_curve: error guardando curva: {e}")
            raise
````

## File: core/data_logger.py
````python
"""
Sistema de logging de datos históricos
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict
from utils import DashboardLogger


class DataLogger:
    """Registra datos del sistema en base de datos SQLite"""

    def __init__(self, db_path: str = "data/history.db"):
        """
        Inicializa el logger

        Args:
            db_path: Ruta a la base de datos SQLite
        """
        # Crear directorio si no existe
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self._init_database()
        self.dashboard_logger = DashboardLogger()  # Logger para eventos y errores
        self.check_and_rotate_db(max_mb=5.0)  # Verificar tamaño al iniciar


    def _init_database(self):
        """Inicializa la base de datos con las tablas necesarias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabla principal de métricas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_percent REAL,
                ram_percent REAL,
                ram_used_gb REAL,
                temperature REAL,
                disk_used_percent REAL,
                disk_read_mb REAL,
                disk_write_mb REAL,
                net_download_mb REAL,
                net_upload_mb REAL,
                fan_pwm INTEGER,
                fan_mode TEXT,
                updates_available INTEGER 
            )
        ''')

        # Índice para búsquedas por timestamp
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON metrics(timestamp)
        ''')

        # Tabla de eventos (opcional, para alertas futuras)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                severity TEXT,
                message TEXT,
                data JSON
            )
        ''')

        conn.commit()
        conn.close()

    def log_metrics(self, metrics: Dict):
        """
        Guarda un conjunto de métricas

        Args:
            metrics: Diccionario con las métricas a guardar

        Ejemplo:
            metrics = {
                'cpu_percent': 45.2,
                'ram_percent': 62.3,
                'ram_used_gb': 5.2,
                'temperature': 58.5,
                'disk_used_percent': 75.0,
                'disk_read_mb': 120.5,
                'disk_write_mb': 45.2,
                'net_download_mb': 2.5,
                'net_upload_mb': 0.8,
                'fan_pwm': 128,
                'fan_mode': 'auto'
            }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO metrics (
                cpu_percent, ram_percent, ram_used_gb, temperature,
                disk_used_percent, disk_read_mb, disk_write_mb,
                net_download_mb, net_upload_mb, fan_pwm, fan_mode, updates_available
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics.get('cpu_percent'),
            metrics.get('ram_percent'),
            metrics.get('ram_used_gb'),
            metrics.get('temperature'),
            metrics.get('disk_used_percent'),
            metrics.get('disk_read_mb'),
            metrics.get('disk_write_mb'),
            metrics.get('net_download_mb'),
            metrics.get('net_upload_mb'),
            metrics.get('fan_pwm'),
            metrics.get('fan_mode'),
            metrics.get('updates_available'),
        ))

        conn.commit()
        conn.close()

    def log_event(self, event_type: str, severity: str, message: str, data: Dict = None):
        """
        Registra un evento

        Args:
            event_type: Tipo de evento (cpu_high, disk_full, etc)
            severity: Severidad (info, warning, critical)
            message: Mensaje descriptivo
            data: Datos adicionales (opcional)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO events (event_type, severity, message, data)
            VALUES (?, ?, ?, ?)
        ''', (event_type, severity, message, json.dumps(data) if data else None))

        conn.commit()
        conn.close()

    def get_metrics_count(self) -> int:
        """Obtiene el número total de registros"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM metrics')
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def get_db_size_mb(self) -> float:
        """Obtiene el tamaño de la base de datos en MB"""
        db_file = Path(self.db_path)
        if db_file.exists():
            return db_file.stat().st_size / (1024 * 1024)
        return 0.0

    def clean_old_data(self, days: int = 7):
        """
        Elimina datos más antiguos de X días

        Args:
            days: Número de días a mantener
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = datetime.now() - timedelta(days=days)

        cursor.execute('''
            DELETE FROM metrics 
            WHERE timestamp < ?
        ''', (cutoff_date,))

        # También limpiar eventos
        cursor.execute('''
            DELETE FROM events 
            WHERE timestamp < ?
        ''', (cutoff_date,))

        conn.commit()

        # Vacuum para recuperar espacio
        cursor.execute('VACUUM')

        conn.close()
    def check_and_rotate_db(self, max_mb: float = 5.0):
        """Si la DB supera el tamaño máximo, elimina datos antiguos de más de 30 días"""
        self.dashboard_logger.get_logger(__name__).info(f"[DataLogger]Verificando tamaño de la base de datos... Tamaño actual: {self.get_db_size_mb():.2f} MB")
        current_size = self.get_db_size_mb()
        if current_size > max_mb:
            # Limpia datos de más de 7 días para reducir tamaño
            self.dashboard_logger.get_logger(__name__).warning(f"[DataLogger]La base de datos ha superado el tamaño máximo de {max_mb} MB. Limpiando datos antiguos...")
            self.clean_old_data(days=7)
            self.dashboard_logger.get_logger(__name__).info(f"[DataLogger]Limpieza completada. Nuevo tamaño de la base de datos: {self.get_db_size_mb():.2f} MB")
````

## File: core/fan_auto_service.py
````python
"""
Servicio en segundo plano para modo AUTO de ventiladores
"""
import threading
import time
from typing import Optional
from core.fan_controller import FanController
from core.system_monitor import SystemMonitor
from utils import FileManager
from utils.logger import get_logger


logger = get_logger(__name__)


class FanAutoService:
    """
    Servicio que actualiza automáticamente el PWM en modo AUTO
    Se ejecuta en segundo plano independiente de la UI
    
    Características:
    - Singleton: Solo una instancia en toda la aplicación
    - Thread-safe: Seguro para concurrencia
    - Daemon: Se cierra automáticamente con el programa
    - Independiente de UI: Funciona con o sin ventanas abiertas
    """
    
    _instance: Optional['FanAutoService'] = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton: solo una instancia"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, fan_controller: FanController, 
                 system_monitor: SystemMonitor):
        """
        Inicializa el servicio (solo la primera vez)
        
        Args:
            fan_controller: Instancia del controlador de ventiladores
            system_monitor: Instancia del monitor del sistema
        """
        # Solo inicializar una vez (patrón singleton)
        if hasattr(self, '_initialized'):
            return
        
        self.fan_controller = fan_controller
        self.system_monitor = system_monitor
        self.file_manager = FileManager()
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._update_interval = 2.0  # segundos
        self._initialized = True
        self.start_cycle = True
    def start(self):
        """Inicia el servicio en segundo plano"""
        if self._running:
            logger.info("[FanAutoService] ya está corriendo")
            return
        
        self._running = True
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,  # Se cierra con el programa
            name="FanAutoService"
        )
        self._thread.start()
    
    def stop(self):
        """Detiene el servicio"""
        if not self._running:
            logger.warning("[FanAutoService] no está corriendo")
            return
        
        self._running = False
        
        if self._thread:
            self._thread.join(timeout=5)
    
    def _run(self):
        """Bucle principal del servicio (ejecuta en thread separado)"""
        while self._running:
            try:
                self._update_auto_mode()
            except Exception as e:
                logger.error(f"[FanAutoService] Error en actualización automática: {e}")
            
            # Dormir en intervalos pequeños para poder detener rápido
            for _ in range(int(self._update_interval * 10)):
                if not self._running:
                    break
                time.sleep(0.1)
    
    def _update_auto_mode(self):
        """Actualiza el PWM si está en modo auto"""
        
        try:
            state = self.file_manager.load_state()
        except Exception as e:
            logger.error(f"[FanAutoService] Error cargando estado: {e}")
            return
        
        # Solo actuar si está en modo auto
        if state.get("mode") != "auto":
            
            if self.start_cycle:
                logger.info("[FanAutoService] Modo no es auto, esperando para iniciar actualizaciones automáticas...")
                self.start_cycle = False
            return
        
        try:
            # Obtener temperatura actual
            stats = self.system_monitor.get_current_stats()
            temp = stats.get('temp', 50)
            
            # Calcular PWM según curva
            target_pwm = self.fan_controller.get_pwm_for_mode(
                mode="auto",
                temp=temp,
                manual_pwm=128  # No importa en auto
            )
            
            # Solo guardar si cambió (evitar writes innecesarios)
            current_pwm = state.get("target_pwm")
            if target_pwm != current_pwm:
                self.file_manager.write_state({
                    "mode": "auto",
                    "target_pwm": target_pwm
                })
        
        except Exception as e:
            logger.error(f"[FanAutoService] Error calculando o guardando PWM: {e}")
    
    def set_update_interval(self, seconds: float):
        """
        Cambia el intervalo de actualización
        
        Args:
            seconds: Segundos entre actualizaciones (mínimo 1.0)
        """
        self._update_interval = max(1.0, seconds)
    
    def is_running(self) -> bool:
        """
        Verifica si el servicio está corriendo
        
        Returns:
            True si está activo, False si no
        """
        logger.debug(f"[FanAutoService] is_running: {self._running}")
        return self._running
    
    def get_status(self) -> dict:
        """
        Obtiene el estado del servicio
        
        Returns:
            Diccionario con información del servicio
        """
        return {
            'running': self._running,
            'interval': self._update_interval,
            'thread_alive': self._thread.is_alive() if self._thread else False
        }
````

## File: core/process_monitor.py
````python
"""
Monitor de procesos del sistema
"""
import psutil
from typing import List, Dict
from datetime import datetime
from utils import DashboardLogger


class ProcessMonitor:
    """Monitor de procesos en tiempo real"""
    
    def __init__(self):
        """Inicializa el monitor de procesos"""
        self.sort_by = "cpu"  # cpu, memory, name, pid
        self.sort_reverse = True
        self.filter_type = "all"  # all, user, system
        self.dashboard_logger = DashboardLogger()
    
    def get_processes(self, limit: int = 20) -> List[Dict]:
        """
        Obtiene lista de procesos con su información
        
        Args:
            limit: Número máximo de procesos a retornar
            
        Returns:
            Lista de diccionarios con información de procesos
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'cmdline', 'exe']):
            try:
                pinfo = proc.info
                
                # Aplicar filtro
                if self.filter_type == "user":
                    # Solo procesos del usuario actual
                    if pinfo['username'] != psutil.Process().username():
                        continue
                elif self.filter_type == "system":
                    # Solo procesos del sistema (root, etc)
                    if pinfo['username'] == psutil.Process().username():
                        continue
                
                # Obtener descripción más detallada
                cmdline = pinfo['cmdline']
                exe = pinfo['exe']
                name = pinfo['name'] or 'N/A'
                
                # Crear descripción mejor
                if cmdline:
                    # Si hay cmdline, usar el primer argumento como descripción
                    display_name = ' '.join(cmdline[:2])  # Primeros 2 argumentos
                elif exe:
                    # Si no hay cmdline pero hay exe, usar el path
                    display_name = exe
                else:
                    display_name = name
                
                processes.append({
                    'pid': pinfo['pid'],
                    'name': name,
                    'display_name': display_name,  # Nueva columna descriptiva
                    'username': pinfo['username'] or 'N/A',
                    'cpu': pinfo['cpu_percent'] or 0.0,
                    'memory': pinfo['memory_percent'] or 0.0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Ordenar según criterio
        if self.sort_by == "cpu":
            processes.sort(key=lambda x: x['cpu'], reverse=self.sort_reverse)
        elif self.sort_by == "memory":
            processes.sort(key=lambda x: x['memory'], reverse=self.sort_reverse)
        elif self.sort_by == "name":
            processes.sort(key=lambda x: x['name'].lower(), reverse=self.sort_reverse)
        elif self.sort_by == "pid":
            processes.sort(key=lambda x: x['pid'], reverse=self.sort_reverse)
        
        return processes[:limit]
    
    def search_processes(self, query: str) -> List[Dict]:
        """
        Busca procesos por nombre o descripción
        
        Args:
            query: Texto a buscar en nombre de proceso
            
        Returns:
            Lista de procesos que coinciden
        """
        query = query.lower()
        all_processes = self.get_processes(limit=1000)  # Obtener todos
        
        return [p for p in all_processes 
                if query in p['name'].lower() or query in p.get('display_name', '').lower()]
    



    def kill_process(self, pid: int) -> tuple[bool, str]:
        """
        Mata un proceso por su PID
        
        Args:
            pid: ID del proceso
            
        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            proc = psutil.Process(pid)
            name = proc.name()

            # Obtener display_name igual que en get_processes
            try:
                cmdline = proc.cmdline()
                display_name = ' '.join(cmdline[:2]) if cmdline else name
            except (psutil.AccessDenied, psutil.ZombieProcess):
                display_name = name

            proc.terminate()  # Intenta cerrar limpiamente
            
            # Esperar un poco
            proc.wait(timeout=3)
            self.dashboard_logger.get_logger(__name__).info(f"[ProcessMonitor] Proceso '{display_name}' (PID {pid}) terminado correctamente")
            return True, f"Proceso '{display_name}' (PID {pid}) terminado correctamente"
        except psutil.NoSuchProcess:
            self.dashboard_logger.get_logger(__name__).error(f"[ProcessMonitor] Proceso con PID {pid} no existe")
            return False, f"Proceso con PID {pid} no existe"
        except psutil.AccessDenied:
            self.dashboard_logger.get_logger(__name__).error(f"[ProcessMonitor] Sin permisos para terminar proceso {pid}")
            return False, f"Sin permisos para terminar proceso {pid}"
        except psutil.TimeoutExpired:
            # Si no se cierra, forzar
            try:
                proc.kill()
                self.dashboard_logger.get_logger(__name__).info(f"[ProcessMonitor] Proceso '{display_name}' (PID {pid}) forzado a cerrar")
                return True, f"Proceso '{display_name}' (PID {pid}) forzado a cerrar"
            except Exception as e:
                self.dashboard_logger.get_logger(__name__).error(f"[ProcessMonitor] Error forzando cierre del proceso '{display_name}' (PID {pid}): {e}")
                return False, f"Error: {str(e)}"
        except Exception as e:
            self.dashboard_logger.get_logger(__name__).error(f"[ProcessMonitor] Error terminando proceso '{display_name}' (PID {pid}): {e}")
            return False, f"Error: {str(e)}"
    def get_system_stats(self) -> Dict:
        """
        Obtiene estadísticas generales del sistema
        
        Returns:
            Diccionario con estadísticas
        """
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # RAM
        mem = psutil.virtual_memory()
        mem_used_gb = mem.used / (1024**3)
        mem_total_gb = mem.total / (1024**3)
        mem_percent = mem.percent
        
        # Procesos
        total_processes = len(psutil.pids())
        
        # Uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_str = self._format_uptime(uptime.total_seconds())
        
        return {
            'cpu_percent': cpu_percent,
            'mem_used_gb': mem_used_gb,
            'mem_total_gb': mem_total_gb,
            'mem_percent': mem_percent,
            'total_processes': total_processes,
            'uptime': uptime_str
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """
        Formatea uptime en formato legible
        
        Args:
            seconds: Segundos de uptime
            
        Returns:
            String formateado
        """
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def set_sort(self, column: str, reverse: bool = True):
        """
        Configura el orden de procesos
        
        Args:
            column: Columna por la que ordenar (cpu, memory, name, pid)
            reverse: Si ordenar de mayor a menor
        """
        self.sort_by = column
        self.sort_reverse = reverse
    
    def set_filter(self, filter_type: str):
        """
        Configura el filtro de procesos
        
        Args:
            filter_type: Tipo de filtro (all, user, system)
        """
        self.filter_type = filter_type
    
    def get_process_color(self, value: float) -> str:
        """
        Obtiene color según porcentaje de uso
        
        Args:
            value: Porcentaje (0-100)
            
        Returns:
            Nombre del color en COLORS
        """
        if value >= 70:
            return "danger"
        elif value >= 30:
            return "warning"
        else:
            return "success"
````

## File: ui/widgets/dialogs.py
````python
"""
Diálogos y ventanas modales personalizadas
"""
import customtkinter as ctk
from ui.styles import make_futuristic_button
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES
import subprocess
import threading


def custom_msgbox(parent, text: str, title: str = "Info") -> None:
    """
    Muestra un cuadro de mensaje personalizado
    
    Args:
        parent: Ventana padre
        text: Texto del mensaje
        title: Título del diálogo
    """
    popup = ctk.CTkToplevel(parent)
    popup.overrideredirect(True)
    
    # Contenedor
    frame = ctk.CTkFrame(popup)
    frame.pack(fill="both", expand=True)
    
    # Título
    title_lbl = ctk.CTkLabel(
        frame, 
        text=title,
        text_color=COLORS['primary'],
        font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
    )
    title_lbl.pack(anchor="center", pady=(0, 10))
    
    # Texto
    text_lbl = ctk.CTkLabel(
        frame, 
        text=text,
        text_color=COLORS['text'],
        font=(FONT_FAMILY, FONT_SIZES['medium']),
        compound="left",
        wraplength=800
    )
    text_lbl.pack(anchor="center", pady=(0, 15))
    
    # Botón OK
    btn = make_futuristic_button(
        frame, 
        text="OK",
        command=popup.destroy,
        width=15, 
        height=6, 
        font_size=16
    )
    btn.pack()
    
    # Calcular tamaño
    popup.update_idletasks()
    
    w = popup.winfo_reqwidth()
    h = popup.winfo_reqheight()
    
    max_w = parent.winfo_screenwidth() - 40
    max_h = parent.winfo_screenheight() - 40
    
    w = min(w, max_w)
    h = min(h, max_h)
    
    # Centrar
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (w // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (h // 2)
    
    popup.geometry(f"{w}x{h}+{x}+{y}")
    
    popup.lift()
    popup.focus_force()
    popup.grab_set()


def confirm_dialog(parent, text: str, title: str = "Confirmar", 
                   on_confirm=None, on_cancel=None) -> None:
    """
    Muestra un diálogo de confirmación
    
    Args:
        parent: Ventana padre
        text: Texto del mensaje
        title: Título del diálogo
        on_confirm: Callback al confirmar
        on_cancel: Callback al cancelar
    """
    popup = ctk.CTkToplevel(parent)
    popup.overrideredirect(True)
    
    frame = ctk.CTkFrame(popup)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Título
    title_lbl = ctk.CTkLabel(
        frame, 
        text=title,
        text_color=COLORS['primary'],
        font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
    )
    title_lbl.pack(anchor="center", pady=(0, 10))
    
    # Texto
    text_lbl = ctk.CTkLabel(
        frame, 
        text=text,
        text_color=COLORS['text'],
        font=(FONT_FAMILY, FONT_SIZES['medium']),
        wraplength=600
    )
    text_lbl.pack(anchor="center", pady=(0, 20))
    
    # Botones
    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
    btn_frame.pack()
    
    def _on_confirm():
        popup.destroy()
        if on_confirm:
            on_confirm()
    
    def _on_cancel():
        popup.destroy()
        if on_cancel:
            on_cancel()
    
    btn_confirm = make_futuristic_button(
        btn_frame,
        text="Confirmar",
        command=_on_confirm,
        width=15,
        height=8,
        font_size=16
    )
    btn_confirm.pack(side="left", padx=5)
    
    btn_cancel = make_futuristic_button(
        btn_frame,
        text="Cancelar",
        command=_on_cancel,
        width=20,
        height=10,
        font_size=16
    )
    btn_cancel.pack(side="left", padx=5)
    
    # Centrar
    popup.update_idletasks()
    w = popup.winfo_reqwidth()
    h = popup.winfo_reqheight()
    
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (w // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (h // 2)
    
    popup.geometry(f"{w}x{h}+{x}+{y}")
    
    popup.lift()
    popup.focus_force()
    popup.grab_set()
def terminal_dialog(parent, script_path, title="Consola de Sistema", on_close=None):
    popup = ctk.CTkToplevel(parent)
    popup.overrideredirect(True)
    popup.configure(fg_color=COLORS['bg_dark'])
    
    # Tamaño para pantalla 800x480
    w, h = 720, 400
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (w // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (h // 2)
    popup.geometry(f"{w}x{h}+{x}+{y}")

    frame = ctk.CTkFrame(popup, fg_color=COLORS['bg_dark'], border_width=2, border_color=COLORS['primary'])
    frame.pack(fill="both", expand=True, padx=2, pady=2)

    ctk.CTkLabel(frame, text=title, font=(FONT_FAMILY, 18, "bold"), text_color=COLORS['secondary']).pack(pady=5)
    def _on_close():
        popup.destroy()
        if on_close:
            on_close()
    console = ctk.CTkTextbox(frame, fg_color="black", text_color="#00FF00", font=("Courier New", 12))
    console.pack(fill="both", expand=True, padx=10, pady=5)

    btn_close = ctk.CTkButton(frame, text="Cerrar", command=_on_close, state="disabled")
    btn_close.pack(pady=10)

    def run_command():
        process = subprocess.Popen(["bash", script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            popup.after(0, lambda l=line: console.insert("end", l))
            popup.after(0, lambda: console.see("end"))
        process.wait()
        popup.after(0, lambda: btn_close.configure(state="normal"))

    threading.Thread(target=run_command, daemon=True).start()
    popup.grab_set()
````

## File: ui/windows/disk.py
````python
"""
Ventana de monitoreo de disco
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH,
                             DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS)
from ui.styles import StyleManager, make_futuristic_button, make_window_header
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
        
        # ── Header unificado ──────────────────────────────────────────────────
        self._header = make_window_header(
            main,
            title="MONITOR DE DISCO",
            on_close=self.destroy,
        )
        
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
        
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Secciones
        self._create_usage_section(inner)
        self._create_disk_io_section(inner)
        self._create_nvme_temp_section(inner)
        
    def _create_metric_section(self, parent, title: str, metric_key: str,
                               unit: str, max_val: float = 100):
        """Crea una sección genérica para una métrica"""
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        frame.pack(fill="x", pady=10, padx=10)
        
        # Label del título
        label = ctk.CTkLabel(
            frame,
            text=title,
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        label.pack(anchor="w", pady=(5, 0), padx=10)
        
        # Valor actual
        value_label = ctk.CTkLabel(
            frame,
            text=f"0.0 {unit}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'])
        )
        value_label.pack(anchor="e", pady=(0, 5), padx=10)
        
        # Gráfica
        graph = GraphWidget(frame, width=DSI_WIDTH-80, height=100)
        graph.pack(pady=(0, 10))
        
        # Guardar referencias
        self.widgets[f"{metric_key}_label"] = label
        self.widgets[f"{metric_key}_value"] = value_label
        self.graphs[metric_key] = {
            'widget': graph,
            'max_val': max_val
        }    

    def _create_usage_section(self, parent):
        """Crea la sección de uso de disco"""
        self._create_metric_section(parent, "DISCO %", "disk", "%", 100)

    def _create_disk_io_section(self, parent):
        """Crea la sección de I/O de disco"""
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        frame.pack(fill="x", pady=10, padx=10)
        
        # Título
        title = ctk.CTkLabel(
            frame,
            text="I/O DE DISCO",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        title.pack(anchor="w", pady=(5, 10), padx=10)
        
        # Escritura
        write_label = ctk.CTkLabel(
            frame,
            text="ESCRITURA",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        )
        write_label.pack(anchor="w", pady=(0, 0), padx=10)
        
        write_value = ctk.CTkLabel(
            frame,
            text="0.0 MB/s",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'])
        )
        write_value.pack(anchor="e", pady=(0, 5), padx=10)
        
        write_graph = GraphWidget(frame, width=DSI_WIDTH-80, height=80)
        write_graph.pack(pady=(0, 10))
        
        # Lectura
        read_label = ctk.CTkLabel(
            frame,
            text="LECTURA",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        )
        read_label.pack(anchor="w", pady=(0, 0), padx=10)
        
        read_value = ctk.CTkLabel(
            frame,
            text="0.0 MB/s",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'])
        )
        read_value.pack(anchor="e", pady=(0, 5), padx=10)
        
        read_graph = GraphWidget(frame, width=DSI_WIDTH-80, height=80)
        read_graph.pack(pady=(0, 10))
        
        # Guardar referencias
        self.widgets['disk_write_label'] = write_label
        self.widgets['disk_write_value'] = write_value
        self.widgets['disk_read_label'] = read_label
        self.widgets['disk_read_value'] = read_value
        
        self.graphs['disk_write'] = {
            'widget': write_graph,
            'max_val': 50
        }
        self.graphs['disk_read'] = {
            'widget': read_graph,
            'max_val': 50
        }
    
    def _create_nvme_temp_section(self, parent):
        """Crea la sección de temperatura NVMe"""
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
            'max_val': 85
        }

    def _update(self):
        """Actualiza los datos del disco"""
        if not self.winfo_exists():
            return
        
        # Obtener estadísticas actuales
        stats = self.disk_monitor.get_current_stats()
        self.disk_monitor.update_history(stats)
        history = self.disk_monitor.get_history()
        
        # Actualizar Disco (uso)
        self._update_metric(
            'disk',
            stats['disk_usage'],
            history['disk_usage'],
            "%",
            60,
            80
        )
        
        # Actualizar Disco I/O
        self._update_disk_io(
            'disk_write',
            stats['disk_write_mb'],
            history['disk_write']
        )
        
        self._update_disk_io(
            'disk_read',
            stats['disk_read_mb'],
            history['disk_read']
        )
        
        # Temperatura NVMe
        self._update_metric(
            'nvme_temp',
            stats['nvme_temp'],
            history['nvme_temp'],
            "°C",
            60,
            70
        )

        # Actualizar status en header
        disk  = stats['disk_usage']
        nvme  = stats['nvme_temp']
        self._header.status_label.configure(
            text=f"Uso {disk:.0f}%  ·  NVMe {nvme:.0f}°C"
        )
        
        # Programar siguiente actualización
        self.after(UPDATE_MS, self._update)

    def _update_metric(self, key, value, history, unit, warn, crit):
        """Actualiza una métrica genérica"""
        color = self.disk_monitor.level_color(value, warn, crit)
        
        self.widgets[f"{key}_value"].configure(
            text=f"{value:.1f} {unit}",
            text_color=color
        )
        self.widgets[f"{key}_label"].configure(text_color=color)
        
        graph_info = self.graphs[key]
        graph_info['widget'].update(history, graph_info['max_val'], color)
        
    def _update_disk_io(self, key: str, value: float, history: list):
        """Actualiza métricas de I/O de disco"""
        color = self.disk_monitor.level_color(value, 10, 50)
        
        self.widgets[f"{key}_value"].configure(
            text=f"{value:.1f} MB/s",
            text_color=color
        )
        self.widgets[f"{key}_label"].configure(text_color=color)
        
        graph_info = self.graphs[key]
        graph_info['widget'].update(history, graph_info['max_val'], color)
````

## File: ui/windows/process_window.py
````python
"""
Ventana de monitor de procesos
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import confirm_dialog, custom_msgbox
from core.process_monitor import ProcessMonitor


class ProcessWindow(ctk.CTkToplevel):
    """Ventana de monitor de procesos"""
    
    def __init__(self, parent, process_monitor: ProcessMonitor):
        super().__init__(parent)
        
        # Referencias
        self.process_monitor = process_monitor
        
        # Estado
        self.search_var = ctk.StringVar()
        self.filter_var = ctk.StringVar(value="all")
        self.process_labels = []  # Lista de labels de procesos
        self.update_paused = False  # Flag para pausar actualización
        self.update_job = None  # ID del trabajo de actualización
        
        # Configurar ventana
        self.title("Monitor de Procesos")
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
        
        # ── Header unificado ──────────────────────────────────────────────────
        make_window_header(
            main,
            title="MONITOR DE PROCESOS",
            on_close=self.destroy,
        )

        # Stats en línea propia debajo del header
        stats_bar = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'])
        stats_bar.pack(fill="x", padx=5, pady=(0, 4))
        self.stats_label = ctk.CTkLabel(
            stats_bar,
            text="Cargando...",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        self.stats_label.pack(pady=4, padx=10, anchor="w")
        
        # Controles (búsqueda y filtros)
        self._create_controls(main)
        
        # Encabezados de columnas
        self._create_column_headers(main)
        
        # Área de scroll para procesos (con altura limitada)
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Limitar altura del canvas para que el botón cerrar sea visible
        max_height = DSI_HEIGHT - 300  # Dejar espacio para header, controles y botón
        
        # Canvas y scrollbar
        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
            height=max_height  # Altura máxima
        )
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")
        
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno para procesos
        self.process_frame = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=self.process_frame, anchor="nw", width=DSI_WIDTH-50)
        self.process_frame.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Botón cerrar
        bottom = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=5, padx=10)
        
    
    
    def _create_controls(self, parent):
        """Crea controles de búsqueda y filtros"""
        controls = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        controls.pack(fill="x", padx=10, pady=5)
        
        # Búsqueda
        search_frame = ctk.CTkFrame(controls, fg_color=COLORS['bg_dark'])
        search_frame.pack(side="left", padx=10, pady=10)
        
        ctk.CTkLabel(
            search_frame,
            text="Buscar:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(0, 5))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            width=200,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        search_entry.pack(side="left")
        search_entry.bind("<KeyRelease>", lambda e: self._on_search_change())
        
        # Filtros
        filter_frame = ctk.CTkFrame(controls, fg_color=COLORS['bg_dark'])
        filter_frame.pack(side="left", padx=20, pady=10)
        
        ctk.CTkLabel(
            filter_frame,
            text="Filtro:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(0, 5))
        
        for filter_type, label in [("all", "Todos"), ("user", "Usuario"), ("system", "Sistema")]:
            rb = ctk.CTkRadioButton(
                filter_frame,
                text=label,
                variable=self.filter_var,
                value=filter_type,
                command=self._on_filter_change,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=5)
            from ui.styles import StyleManager
            StyleManager.style_radiobutton_ctk(rb)
    
    def _create_column_headers(self, parent):
        """Crea encabezados de columnas ordenables"""
        headers = ctk.CTkFrame(parent, fg_color=COLORS['bg_light'])
        headers.pack(fill="x", padx=10, pady=(5, 0))
        
        # Configurar grid
        headers.grid_columnconfigure(0, weight=1, minsize=20)   # PID
        headers.grid_columnconfigure(1, weight=4, minsize=200)  # Nombre
        headers.grid_columnconfigure(2, weight=2, minsize=100)  # Usuario
        headers.grid_columnconfigure(3, weight=1, minsize=80)   # CPU
        headers.grid_columnconfigure(4, weight=1, minsize=80)   # RAM
        headers.grid_columnconfigure(5, weight=1, minsize=100)  # Acción
        
        # Crear headers
        columns = [
            ("PID", "pid"),
            ("Proceso", "name"),
            ("Usuario", "username"),
            ("CPU%", "cpu"),
            ("RAM%", "memory"),
            ("Acción", None)
        ]
        
        for i, (label, sort_key) in enumerate(columns):
            if sort_key:
                btn = ctk.CTkButton(
                    headers,
                    text=label,
                    command=lambda k=sort_key: self._on_sort_change(k),
                    fg_color=COLORS['bg_medium'],
                    hover_color=COLORS['bg_dark'],
                    font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                    width=50,
                    height=30
                )
            else:
                btn = ctk.CTkLabel(
                    headers,
                    text=label,
                    text_color=COLORS['text'],
                    font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
                )
            
            btn.grid(row=0, column=i, sticky="n", padx=2, pady=5)
    
    def _on_sort_change(self, column: str):
        """Cambia el orden de procesos"""
        # Pausar actualización automática temporalmente
        self.update_paused = True
        
        # Si ya estaba ordenado por esta columna, invertir
        if self.process_monitor.sort_by == column:
            self.process_monitor.sort_reverse = not self.process_monitor.sort_reverse
        else:
            self.process_monitor.set_sort(column, reverse=True)
        
        # Actualizar inmediatamente
        self._update_now()
        
        # Reanudar actualización después de 2 segundos
        self.after(2000, self._resume_updates)
    
    def _on_filter_change(self):
        """Cambia el filtro de procesos"""
        # Pausar actualización automática temporalmente
        self.update_paused = True
        
        self.process_monitor.set_filter(self.filter_var.get())
        
        # Actualizar inmediatamente
        self._update_now()
        
        # Reanudar actualización después de 2 segundos
        self.after(2000, self._resume_updates)
    
    def _update_now(self):
        """Actualiza inmediatamente sin programar siguiente"""
        if not self.winfo_exists():
            return
        
        # Cancelar actualización programada si existe
        if self.update_job:
            self.after_cancel(self.update_job)
            self.update_job = None
        
        # Actualizar estadísticas del sistema
        stats = self.process_monitor.get_system_stats()
        self.stats_label.configure(
            text=f"Procesos: {stats['total_processes']} | "
                 f"CPU: {stats['cpu_percent']:.1f}% | "
                 f"RAM: {stats['mem_used_gb']:.1f}/{stats['mem_total_gb']:.1f} GB ({stats['mem_percent']:.1f}%) | "
                 f"Uptime: {stats['uptime']}"
        )
        
        # Limpiar procesos anteriores
        for widget in self.process_frame.winfo_children():
            widget.destroy()
        self.process_labels = []
        
        # Obtener procesos
        search_query = self.search_var.get()
        if search_query:
            processes = self.process_monitor.search_processes(search_query)
        else:
            processes = self.process_monitor.get_processes(limit=20)
        
        # Mostrar procesos
        for i, proc in enumerate(processes):
            self._create_process_row(proc, i)
    
    def _resume_updates(self):
        """Reanuda las actualizaciones automáticas"""
        self.update_paused = False
    
    def _on_search_change(self):
        """Callback cuando cambia la búsqueda"""
        # Pausar actualización automática temporalmente
        self.update_paused = True
        
        # Cancelar timer anterior si existe
        if hasattr(self, '_search_timer'):
            self.after_cancel(self._search_timer)
        
        # Actualizar después de 500ms (debounce)
        self._search_timer = self.after(500, self._do_search)
    
    def _do_search(self):
        """Ejecuta la búsqueda"""
        self._update_now()
        # Reanudar actualización después de 3 segundos
        self.after(3000, self._resume_updates)
    
    def _update(self):
        """Actualiza la lista de procesos"""
        if not self.winfo_exists():
            return
        
        # Si está pausada, reprogramar y salir
        if self.update_paused:
            self.update_job = self.after(UPDATE_MS * 2, self._update)
            return
        
        # Actualizar estadísticas del sistema
        stats = self.process_monitor.get_system_stats()
        self.stats_label.configure(
            text=f"Procesos: {stats['total_processes']} | "
                 f"CPU: {stats['cpu_percent']:.1f}% | "
                 f"RAM: {stats['mem_used_gb']:.1f}/{stats['mem_total_gb']:.1f} GB ({stats['mem_percent']:.1f}%) | "
                 f"Uptime: {stats['uptime']}"
        )
        
        # Limpiar procesos anteriores
        for widget in self.process_frame.winfo_children():
            widget.destroy()
        self.process_labels = []
        
        # Obtener procesos
        search_query = self.search_var.get()
        if search_query:
            processes = self.process_monitor.search_processes(search_query)
        else:
            processes = self.process_monitor.get_processes(limit=20)
        
        # Mostrar procesos
        for i, proc in enumerate(processes):
            self._create_process_row(proc, i)
        
        # Programar siguiente actualización
        self.update_job = self.after(UPDATE_MS * 2, self._update)  # Cada 4 segundos
    
    def _create_process_row(self, proc: dict, row: int):
        """Crea una fila para un proceso"""
        # Frame de la fila (sin altura fija, se adapta al contenido)
        bg_color = COLORS['bg_dark'] if row % 2 == 0 else COLORS['bg_medium']
        row_frame = ctk.CTkFrame(self.process_frame, fg_color=bg_color)
        row_frame.pack(fill="x", pady=2, padx=10)  # Más padding vertical
        
        # Configurar grid igual que headers
        row_frame.grid_columnconfigure(0, weight=1, minsize=70)
        row_frame.grid_columnconfigure(1, weight=3, minsize=300)
        row_frame.grid_columnconfigure(2, weight=2, minsize=100)
        row_frame.grid_columnconfigure(3, weight=1, minsize=80)
        row_frame.grid_columnconfigure(4, weight=1, minsize=80)
        row_frame.grid_columnconfigure(5, weight=1, minsize=100)
        
        # Colores según uso
        cpu_color = COLORS[self.process_monitor.get_process_color(proc['cpu'])]
        mem_color = COLORS[self.process_monitor.get_process_color(proc['memory'])]
        
        # PID
        ctk.CTkLabel(
            row_frame,
            text=str(proc['pid']),
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            anchor="center"
        ).grid(row=0, column=0, sticky="n", padx=5, pady=5)  # nw = arriba izquierda
        
        # Nombre (mostrar display_name que es más descriptivo)
        name_text = proc.get('display_name', proc['name'])
        name_label = ctk.CTkLabel(
            row_frame,
            text=name_text,  # Sin truncar
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wraplength=250,  # Ajustar texto en 350px de ancho
            justify="left",
            anchor="center"
        )
        name_label.grid(row=0, column=1, sticky="n", padx=5, pady=5)  # nw = arriba izquierda
        
        # Usuario
        ctk.CTkLabel(
            row_frame,
            text=proc['username'][:15],
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            anchor="center"
        ).grid(row=0, column=2, sticky="n", padx=5, pady=5)  # nw = arriba izquierda
        
        # CPU
        ctk.CTkLabel(
            row_frame,
            text=f"{proc['cpu']:.1f}%",
            text_color=cpu_color,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
        ).grid(row=0, column=3, sticky="n", padx=5, pady=5)  # ne = arriba derecha
        
        # RAM
        ctk.CTkLabel(
            row_frame,
            text=f"{proc['memory']:.1f}%",
            text_color=mem_color,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
        ).grid(row=0, column=4, sticky="n", padx=5, pady=5)  # ne = arriba derecha
        
        # Botón matar
        kill_btn = ctk.CTkButton(
            row_frame,
            text="Matar",
            command=lambda p=proc: self._kill_process(p),
            fg_color=COLORS['danger'],
            hover_color="#cc0000",
            width=70,
            height=25,
            font=(FONT_FAMILY, 9)
        )
        kill_btn.grid(row=0, column=5, padx=5, pady=5)  # centrado
    
    def _kill_process(self, proc: dict):
        """Mata un proceso con confirmación"""
        def do_kill():
            success, message = self.process_monitor.kill_process(proc['pid'])
            
            if success:
                title = "Proceso Terminado"
            else:
                title = "Error"
            
            custom_msgbox(self, message, title)
            self._update()  # Actualizar lista
        
        # Confirmar
        confirm_dialog(
            parent=self,
            text=f"¿Matar proceso '{proc['name']}'?\n\nPID: {proc['pid']}\nCPU: {proc['cpu']:.1f}%",
            title="⚠️ Confirmar",
            on_confirm=do_kill,
            on_cancel=None
        )
````

## File: ui/windows/theme_selector.py
````python
"""
Ventana de selección de temas
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
from config.themes import get_available_themes, get_theme, save_selected_theme, load_selected_theme
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox, confirm_dialog
import sys
import os

class ThemeSelector(ctk.CTkToplevel):
    """Ventana de selección de temas"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configurar ventana
        self.title("Selector de Temas")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        
        # Tema actualmente seleccionado
        self.current_theme = load_selected_theme()
        self.selected_theme_var = ctk.StringVar(value=self.current_theme)
        
        # Crear interfaz
        self._create_ui()
    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        # Frame principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── Header unificado ──────────────────────────────────────────────────
        make_window_header(
            main,
            title="SELECTOR DE TEMAS",
            on_close=self.destroy,
            status_text="Elige un tema y reinicia el dashboard para aplicarlo",
        )
        
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
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Crear tarjetas de temas
        self._create_theme_cards(inner)
        
        # Botones inferiores
        self._create_bottom_buttons(main)
    
    def _create_theme_cards(self, parent):
        """Crea las tarjetas de cada tema"""
        themes = get_available_themes()
        
        for theme_id, theme_name in themes:
            theme_data = get_theme(theme_id)
            colors = theme_data["colors"]
            
            # Frame de la tarjeta
            is_current = (theme_id == self.current_theme)
            border_color = COLORS['success'] if is_current else COLORS['primary']
            border_width = 3 if is_current else 2
            
            card = ctk.CTkFrame(
                parent,
                fg_color=COLORS['bg_dark'],
                border_width=border_width,
                border_color=border_color
            )
            card.pack(fill="x", pady=8, padx=10)
            
            # Radiobutton para seleccionar
            radio = ctk.CTkRadioButton(
                card,
                text=theme_name,
                variable=self.selected_theme_var,
                value=theme_id,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
                command=lambda: self._on_theme_change()
            )
            radio.pack(anchor="w", padx=15, pady=(10, 5))
            StyleManager.style_radiobutton_ctk(radio)
            
            # Indicador de tema actual
            if is_current:
                current_label = ctk.CTkLabel(
                    card,
                    text="✓ TEMA ACTUAL",
                    text_color=COLORS['success'],
                    font=(FONT_FAMILY, 10, "bold")
                )
                current_label.pack(anchor="w", padx=15, pady=(0, 5))
            
            # Frame de preview de colores
            preview_frame = ctk.CTkFrame(card, fg_color=COLORS['bg_medium'])
            preview_frame.pack(fill="x", padx=15, pady=(5, 10))
            
            # Mostrar colores principales
            color_samples = [
                ("Principal", colors['primary']),
                ("Secundario", colors['secondary']),
                ("Éxito", colors['success']),
                ("Advertencia", colors['warning']),
                ("Peligro", colors['danger']),
                ("Fondo oscuro", colors['bg_dark']),
                ("Fondo medio", colors['bg_medium']),
                ("Fondo claro", colors['bg_light']),
                ("Texto", colors['text']),
                ("Bordes", colors['border'])
            ]
            
            for i, (label, color) in enumerate(color_samples):
                color_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
                color_frame.grid(row=0, column=i, padx=5, pady=5)
                
                # Cuadrado de color
                color_box = ctk.CTkFrame(
                    color_frame,
                    width=40,
                    height=40,
                    fg_color=color,
                    border_width=1,
                    border_color=COLORS['text']
                )
                color_box.pack()
                color_box.pack_propagate(False)
                
                # Label
                color_label = ctk.CTkLabel(
                    color_frame,
                    text=label,
                    text_color=COLORS['text'],
                    font=(FONT_FAMILY, 9)
                )
                color_label.pack(pady=(2, 0))
    
    def _create_bottom_buttons(self, parent):
        """Crea los botones inferiores"""
        bottom = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=10, padx=10)
        
        # Botón aplicar
        apply_btn = make_futuristic_button(
            bottom,
            text="Aplicar y Reiniciar",
            command=self._apply_theme,
            width=20,
            height=6
        )
        apply_btn.pack(side="right", padx=5)
    
    def _on_theme_change(self):
        """Callback cuando se selecciona un tema"""
        # Simplemente actualiza la variable, no aplica aún
        pass
    
    def _apply_theme(self):
        """Aplica el tema seleccionado y reinicia la aplicación"""
        selected = self.selected_theme_var.get()
        
        if selected == self.current_theme:
            custom_msgbox(
                self,
                "Este tema ya está activo.\nNo es necesario reiniciar.",
                "Tema Actual"
            )
            return
        
        # Guardar tema seleccionado
        save_selected_theme(selected)
        
        # Mostrar confirmación y reiniciar
        theme_name = get_theme(selected)["name"]
        

        
        def do_restart():
            """Reinicia la aplicación"""
            
            
            # Cerrar ventana de temas
            self.destroy()
            
            # Obtener el script principal
            python = sys.executable
            script = os.path.abspath(sys.argv[0])
            
            # Cerrar aplicación actual
            self.master.quit()
            self.master.destroy()
            
            # Reiniciar con os.execv (reemplaza el proceso actual)
            os.execv(python, [python, script] + sys.argv[1:])
        
        # Confirmar antes de reiniciar
        confirm_dialog(
            parent=self,
            text=f"Tema '{theme_name}' guardado.\n\n¿Reiniciar ahora para aplicar los cambios?",
            title="🔄 Aplicar Tema",
            on_confirm=do_restart,
            on_cancel=self.destroy
        )
````

## File: ui/windows/update.py
````python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, SCRIPTS_DIR
from ui.styles import make_futuristic_button
from ui.widgets.dialogs import terminal_dialog
from utils import SystemUtils


class UpdatesWindow(ctk.CTkToplevel):
    """Ventana de control de actualizaciones del sistema"""
    
    def __init__(self, parent, update_monitor):
        super().__init__(parent)
        self.system_utils = SystemUtils()
        self.monitor = update_monitor
        self._polling = False

        # Configuración de ventana (Estilo DSI)
        self.title("Actualizaciones del Sistema")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        
        self._create_ui()
        self._refresh_status(force=False)

    def _create_ui(self):
        # Frame Principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Icono
        self.status_icon = ctk.CTkLabel(main, text="󰚰", font=(FONT_FAMILY, 60))
        self.status_icon.pack(pady=(10, 5))
        
        # Labels
        self.status_label = ctk.CTkLabel(
            main, text="Verificando...", 
            font=(FONT_FAMILY, FONT_SIZES['xxlarge'], "bold")
        )
        self.status_label.pack()
        
        self.info_label = ctk.CTkLabel(
            main, text="Estado de los paquetes",
            text_color=COLORS['text_dim'], font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        self.info_label.pack(pady=5)
        
        # Frame para botones
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=(10, 20))
        
        # 1. Botón Buscar (Manual)
        self.search_btn = make_futuristic_button(
            btn_frame, text="🔍 Buscar", 
            command=lambda: self._refresh_status(force=True), width=12
        )
        self.search_btn.pack(side="left", padx=5, expand=True)

        # 2. Botón Instalar
        self.update_btn = make_futuristic_button(
            btn_frame, text="󰚰 Instalar", 
            command=self._execute_update_script, width=12
        )
        self.update_btn.pack(side="left", padx=5, expand=True)
        self.update_btn.configure(state="disabled")
        
        # 3. Botón Cerrar
        close_btn = make_futuristic_button(
            btn_frame, text="Cerrar", 
            command=self.destroy, width=12
        )
        close_btn.pack(side="left", padx=5, expand=True)

    def _refresh_status(self, force=False):
        """Consulta el estado de actualizaciones"""
        if force:
            self._polling = False  # Cancelar polling si el usuario busca manualmente
            self.status_label.configure(text="Buscando...", text_color=COLORS['warning'])
            self.update_idletasks()

        res = self.monitor.check_updates(force=force)

        # Si el thread de arranque aún no ha terminado, mostrar estado de espera
        if res['status'] == "Unknown":
            self.status_label.configure(text="Comprobando...", text_color=COLORS['text_dim'])
            self.info_label.configure(text="Verificación inicial en curso")
            self.status_icon.configure(text_color=COLORS['text_dim'])
            self.update_btn.configure(state="disabled")
            # Reintentar cada 2 segundos hasta tener resultado real
            if not self._polling:
                self._polling = True
                self._poll_until_ready()
            return

        self._polling = False
        color = COLORS['success'] if res['pending'] == 0 else COLORS['warning']
        self.status_label.configure(text=res['status'], text_color=color)
        self.info_label.configure(text=res['message'])
        self.status_icon.configure(text_color=color)
        self.update_btn.configure(state="normal" if res['pending'] > 0 else "disabled")

    def _poll_until_ready(self):
        """Reintenta _refresh_status cada 2s mientras el resultado sea Unknown"""
        if not self._polling:
            return
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return

        res = self.monitor.check_updates(force=False)
        if res['status'] != "Unknown":
            self._refresh_status(force=False)
        else:
            self.after(2000, self._poll_until_ready)

    def _execute_update_script(self):
        """Lanza el script de terminal y refresca al terminar"""
        script_path = str(SCRIPTS_DIR / "update.sh")
        
        def al_terminar_actualizacion():
            self._refresh_status(force=True)
        
        terminal_dialog(
            self, 
            script_path, 
            "CONSOLA DE ACTUALIZACIÓN",
            on_close=al_terminar_actualizacion
        )
````

## File: ui/styles.py
````python
"""
Estilos y temas para la interfaz
"""
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES


class StyleManager:
    """Gestor centralizado de estilos"""
    
    @staticmethod
    def style_radiobutton_tk(rb: tk.Radiobutton, 
                            fg: str = None, 
                            bg: str = None, 
                            hover_fg: str = None) -> None:
        """
        Aplica estilo a radiobutton de tkinter
        
        Args:
            rb: Widget radiobutton
            fg: Color de texto
            bg: Color de fondo
            hover_fg: Color al pasar el mouse
        """
        fg = fg or COLORS['primary']
        bg = bg or COLORS['bg_dark']
        hover_fg = hover_fg or COLORS['success']
        
        rb.config(
            fg=fg, 
            bg=bg, 
            selectcolor=bg, 
            activeforeground=fg, 
            activebackground=bg,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), 
            indicatoron=True
        )
        
        def on_enter(e): 
            rb.config(fg=hover_fg)
        
        def on_leave(e): 
            rb.config(fg=fg)
        
        rb.bind("<Enter>", on_enter)
        rb.bind("<Leave>", on_leave)
    
    @staticmethod
    def style_radiobutton_ctk(rb: ctk.CTkRadioButton) -> None:
        """
        Aplica estilo a radiobutton de customtkinter
        
        Args:
            rb: Widget radiobutton
        """
        rb.configure(
            radiobutton_width=25,
            radiobutton_height=25,
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            fg_color=COLORS['primary'],
        )
    
    @staticmethod
    def style_slider(slider: tk.Scale, color: str = None) -> None:
        """
        Aplica estilo a slider de tkinter
        
        Args:
            slider: Widget slider
            color: Color personalizado
        """
        color = color or COLORS['primary']
        slider.config(
            troughcolor=COLORS['secondary'], 
            sliderrelief="flat", 
            bd=0,
            highlightthickness=0, 
            fg=color, 
            bg=COLORS['bg_dark'], 
            activebackground=color
        )
    
    @staticmethod
    def style_slider_ctk(slider: ctk.CTkSlider, color: str = None) -> None:
        """
        Aplica estilo a slider de customtkinter
        
        Args:
            slider: Widget slider
            color: Color personalizado
        """
        color = color or COLORS['primary']  # ✓ Usar tema
        slider.configure(
            fg_color=COLORS['bg_light'],
            progress_color=color,
            button_color=color,
            button_hover_color=COLORS['secondary'],
            height=30
        )
    
    @staticmethod
    def style_scrollbar(sb: tk.Scrollbar, color: str = None) -> None:
        """
        Aplica estilo a scrollbar de tkinter
        
        Args:
            sb: Widget scrollbar
            color: Color personalizado
        """
        color = color or COLORS['bg_dark']
        sb.config(
            troughcolor=COLORS['secondary'], 
            bg=color, 
            activebackground=color,
            highlightthickness=0, 
            relief="flat"
        )
    
    @staticmethod
    def style_scrollbar_ctk(sb: ctk.CTkScrollbar, color: str = None) -> None:
        """
        Aplica estilo a scrollbar de customtkinter
        
        Args:
            sb: Widget scrollbar
            color: Color personalizado
        """
        color = color or COLORS['primary']  # ✓ Usar tema
        sb.configure(
            bg_color=COLORS['bg_medium'],
            button_color=color,
            button_hover_color=COLORS['secondary']
        )
    
    @staticmethod
    def style_ctk_scrollbar(scrollable_frame: ctk.CTkScrollableFrame, 
                           color: str = None) -> None:
        """
        Aplica estilo a scrollable frame de customtkinter
        
        Args:
            scrollable_frame: Widget scrollable frame
            color: Color personalizado
        """
        color = color or COLORS['primary']  # ✓ Usar tema
        scrollable_frame.configure(
            scrollbar_fg_color=COLORS['bg_medium'],
            scrollbar_button_color=color,
            scrollbar_button_hover_color=COLORS['secondary']
        )


def make_futuristic_button(parent, text: str, command=None, 
                          width: int = None, height: int = None, 
                          font_size: int = None, state: str = "normal") -> ctk.CTkButton:
    """
    Crea un botón con estilo futurista
    
    Args:
        parent: Widget padre
        text: Texto del botón
        command: Función a ejecutar al hacer clic
        width: Ancho en unidades
        height: Alto en unidades
        font_size: Tamaño de fuente
        
    Returns:
        Widget CTkButton configurado
    """
    width = width or 20
    height = height or 10
    font_size = font_size or FONT_SIZES['large']
    
    btn = ctk.CTkButton(
        parent, 
        text=text, 
        command=command,
        fg_color=COLORS['bg_dark'], 
        hover_color=COLORS['bg_light'],
        border_width=3, 
        border_color=COLORS['border'],
        width=width * 8, 
        height=height * 8,
        font=(FONT_FAMILY, font_size, "bold"), 
        corner_radius=10,
        state=state
    )
    
    def on_enter(e): 
        btn.configure(fg_color=COLORS['bg_light'])
    
    def on_leave(e): 
        btn.configure(fg_color=COLORS['bg_dark'])
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn


def make_window_header(parent, title: str, on_close, status_text: str = None) -> ctk.CTkFrame:
    """
    Crea una barra de cabecera unificada para ventanas de monitoreo.

    Layout (altura fija 48px):
    ┌─────────────────────────────────────────────────────────┐
    │  ● TÍTULO DE VENTANA      status_text opcional   [✕]   │
    └─────────────────────────────────────────────────────────┘

    El indicador ● usa COLORS['secondary'] para identificar
    visualmente que es una ventana hija del dashboard.

    Args:
        parent:      Widget padre (normalmente el frame main de la ventana).
        title:       Texto del título en mayúsculas (ej. "MONITOR DEL SISTEMA").
        on_close:    Callable ejecutado al pulsar el botón ✕.
        status_text: Texto informativo opcional a la derecha del título
                     (ej. "CPU 12% · RAM 45% · 52°C"). Si es None no se muestra.

    Returns:
        CTkFrame de cabecera ya empaquetado con pack(fill="x").
        Guarda referencia al label de estado en frame.status_label
        para que la ventana pueda actualizarlo dinámicamente.
    """
    # ── Contenedor ───────────────────────────────────────────────────────────
    header = ctk.CTkFrame(
        parent,
        fg_color=COLORS['bg_dark'],
        height=56,
        corner_radius=8,
    )
    header.pack(fill="x", padx=5, pady=(5, 0))
    header.pack_propagate(False)  # Altura fija

    # Separador inferior (línea decorativa)
    separator = ctk.CTkFrame(
        parent,
        fg_color=COLORS['border'],
        height=1,
        corner_radius=0,
    )
    separator.pack(fill="x", padx=5, pady=(0, 4))

    # ── Indicador de color (pastilla izquierda) ───────────────────────────
    dot = ctk.CTkLabel(
        header,
        text="●",
        text_color=COLORS['secondary'],
        font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
        width=28,
    )
    dot.pack(side="left", padx=(10, 2))

    # ── Título ────────────────────────────────────────────────────────────
    title_lbl = ctk.CTkLabel(
        header,
        text=title,
        text_color=COLORS['secondary'],
        font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
        anchor="w",
    )
    title_lbl.pack(side="left", padx=(0, 10))

    # ── Botón cerrar (derecha) ────────────────────────────────────────────
    close_btn = ctk.CTkButton(
        header,
        text="✕",
        command=on_close,
        width=52,
        height=42,
        fg_color=COLORS['bg_medium'],
        hover_color=COLORS['danger'],
        border_width=1,
        border_color=COLORS['border'],
        font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
        corner_radius=6,
    )
    close_btn.pack(side="right", padx=(0, 8))

    # ── Status label (derecha del título, izquierda del botón) ───────────
    status_lbl = ctk.CTkLabel(
        header,
        text=status_text or "",
        text_color=COLORS['text_dim'],
        font=(FONT_FAMILY, FONT_SIZES['small']),
        anchor="e",
    )
    status_lbl.pack(side="right", padx=(0, 12), expand=True, fill="x")

    # Referencia pública para actualizaciones dinámicas
    header.status_label = status_lbl

    return header
````

## File: utils/system_utils.py
````python
"""
Utilidades para obtener información del sistema
"""
import re
import socket
import psutil
import subprocess
import glob
from typing import Tuple, Dict, Optional, Any
from collections import namedtuple
from config.settings import UPDATE_MS
import json
from utils.logger import get_logger

logger = get_logger(__name__)


class SystemUtils:
    """Utilidades para interactuar con el sistema"""
    
    # Variable de clase para mantener estado de red entre llamadas
    _last_net_io = {}
    
    @staticmethod
    def get_cpu_temp() -> float:
        """
        Obtiene la temperatura de la CPU
        
        Returns:
            Temperatura en grados Celsius
        """
        # Método 1: vcgencmd (Raspberry Pi - método oficial)
        try:
            out = subprocess.check_output(
                ["vcgencmd", "measure_temp"],
                universal_newlines=True,
                timeout=2
            )
            temp_str = out.replace("temp=", "").replace("'C", "").strip()
            return float(temp_str)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        except ValueError as e:
            logger.warning(f"[SystemUtils] get_cpu_temp: formato inesperado de vcgencmd: {e}")
        
        # Método 2: sensors (Linux genérico)
        try:
            out = subprocess.check_output(["sensors"], universal_newlines=True, timeout=2)
            for line in out.split('\n'):
                if 'Package id 0:' in line or 'Tdie:' in line or 'CPU:' in line:
                    m = re.search(r'[\+\-](\d+\.\d+).C', line)
                    if m:
                        return float(m.group(1))
                        
            for line in out.split('\n'):
                if 'temp' in line.lower():
                    m = re.search(r'[\+\-](\d+\.\d+).C', line)
                    if m:
                        return float(m.group(1))
        except subprocess.TimeoutExpired:
            logger.warning("[SystemUtils] get_cpu_temp: timeout leyendo sensors")
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Método 3: Fallback - leer de thermal_zone
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                val = f.read().strip()
                return float(val) / 1000.0
        except FileNotFoundError:
            logger.warning("[SystemUtils] get_cpu_temp: no se encontró thermal_zone0, retornando 0.0")
        except ValueError as e:
            logger.error(f"[SystemUtils] get_cpu_temp: error leyendo thermal_zone0: {e}")
        
        return 0.0
    
    @staticmethod
    def get_hostname() -> str:
        """
        Obtiene el nombre del host
        
        Returns:
            Nombre del host o "unknown"
        """
        try:
            return socket.gethostname()
        except Exception as e:
            logger.warning(f"[SystemUtils] get_hostname: {e}")
            return "unknown"
    
    @staticmethod
    def get_net_io(interface: Optional[str] = None) -> Tuple[str, Any]:
        """
        Obtiene estadísticas de red con auto-detección de interfaz activa
        
        Args:
            interface: Nombre de la interfaz o None para auto-detección
            
        Returns:
            Tupla (nombre_interfaz, estadísticas)
        """
        if not SystemUtils._last_net_io:
            SystemUtils._last_net_io = psutil.net_io_counters(pernic=True)
        
        stats = psutil.net_io_counters(pernic=True)
        
        if interface and interface in stats:
            SystemUtils._last_net_io = stats
            return interface, stats[interface]
        
        best_name = None
        best_speed = -1
        
        for name in stats:
            if name not in SystemUtils._last_net_io:
                continue
            
            curr = stats[name]
            prev = SystemUtils._last_net_io[name]
            
            speed = (
                (curr.bytes_recv - prev.bytes_recv) +
                (curr.bytes_sent - prev.bytes_sent)
            )
            
            if speed < 0 or speed > 500 * 1024 * 1024:
                continue
            
            if speed > best_speed:
                best_speed = speed
                best_name = name
        
        SystemUtils._last_net_io = stats
        
        if best_name:
            return best_name, stats[best_name]
        
        for iface, s in stats.items():
            if iface.startswith(('eth', 'enp', 'wlan', 'wlp', 'tun')):
                if s.bytes_sent > 0 or s.bytes_recv > 0:
                    return iface, s
        
        if stats:
            first = list(stats.items())[0]
            return first[0], first[1]
        
        EmptyStats = namedtuple('EmptyStats', 
            ['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv',
             'errin', 'errout', 'dropin', 'dropout'])
        return "none", EmptyStats(0, 0, 0, 0, 0, 0, 0, 0)
    
    @staticmethod
    def safe_net_speed(current: Any, previous: Optional[Any]) -> Tuple[float, float]:
        """
        Calcula velocidad de red de forma segura
        
        Args:
            current: Estadísticas actuales
            previous: Estadísticas anteriores
            
        Returns:
            Tupla (download_mb, upload_mb)
        """
        if previous is None:
            return 0.0, 0.0
        
        try:
            dl_bytes = max(0, current.bytes_recv - previous.bytes_recv)
            ul_bytes = max(0, current.bytes_sent - previous.bytes_sent)
            
            seconds = UPDATE_MS / 1000.0
            
            dl_mb = (dl_bytes / (1024 * 1024)) / seconds
            ul_mb = (ul_bytes / (1024 * 1024)) / seconds
            
            return dl_mb, ul_mb
        except (AttributeError, TypeError) as e:
            logger.warning(f"[SystemUtils] safe_net_speed: error calculando velocidad de red: {e}")
            return 0.0, 0.0
    
    @staticmethod
    def list_usb_storage_devices() -> list:
        """
        Lista dispositivos USB de almacenamiento (discos)
        
        Returns:
            Lista de diccionarios con información de almacenamiento USB
        """
        storage_devices = []
        
        try:
            result = subprocess.run(
                ['lsblk', '-o', 'NAME,MODEL,TRAN,MOUNTPOINT,SIZE,TYPE', '-J'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                for block in data.get('blockdevices', []):
                    if block.get('tran') == 'usb':
                        dev = {
                            'name': block.get('model', 'USB Disk').strip(),
                            'type': block.get('type', 'disk'),
                            'mount': block.get('mountpoint'),
                            'dev': '/dev/' + block.get('name', ''),
                            'size': block.get('size', ''),
                            'children': []
                        }
                        
                        for child in block.get('children', []):
                            child_dev = {
                                'name': child.get('name', ''),
                                'type': child.get('type', 'part'),
                                'mount': child.get('mountpoint'),
                                'dev': '/dev/' + child.get('name', ''),
                                'size': child.get('size', '')
                            }
                            dev['children'].append(child_dev)
                        
                        storage_devices.append(dev)
            else:
                logger.warning(f"[SystemUtils] list_usb_storage_devices: lsblk retornó código {result.returncode}")
        
        except subprocess.TimeoutExpired:
            logger.error("[SystemUtils] list_usb_storage_devices: timeout ejecutando lsblk")
        except FileNotFoundError:
            logger.error("[SystemUtils] list_usb_storage_devices: lsblk no encontrado")
        except json.JSONDecodeError as e:
            logger.error(f"[SystemUtils] list_usb_storage_devices: error parseando JSON de lsblk: {e}")
        
        return storage_devices
    
    @staticmethod
    def list_usb_other_devices() -> list:
        """
        Lista otros dispositivos USB (no almacenamiento)
        
        Returns:
            Lista de strings con información de dispositivos USB
        """
        try:
            result = subprocess.run(
                ['lsusb'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                devices = [line for line in result.stdout.strip().split('\n') if line]
                return devices
            else:
                logger.warning(f"[SystemUtils] list_usb_other_devices: lsusb retornó código {result.returncode}")
            
        except subprocess.TimeoutExpired:
            logger.error("[SystemUtils] list_usb_other_devices: timeout ejecutando lsusb")
        except FileNotFoundError:
            logger.error("[SystemUtils] list_usb_other_devices: lsusb no encontrado")
        
        return []
    
    @staticmethod
    def list_usb_devices() -> list:
        """
        Lista TODOS los dispositivos USB (mantener para compatibilidad)
        
        Returns:
            Lista de strings con lsusb
        """
        return SystemUtils.list_usb_other_devices()
    
    @staticmethod
    def eject_usb_device(device: dict) -> Tuple[bool, str]:
        """
        Expulsa un dispositivo USB de forma segura
        
        Args:
            device: Diccionario con información del dispositivo
                   (debe tener 'children' con particiones)
        
        Returns:
            Tupla (success: bool, message: str)
        """
        device_name = device.get('name', 'desconocido')
        
        try:
            unmounted = []
            for partition in device.get('children', []):
                if partition.get('mount'):
                    result = subprocess.run(
                        ['udisksctl', 'unmount', '-b', partition['dev']],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        unmounted.append(partition['name'])
                        logger.info(f"[SystemUtils] Partición {partition['name']} desmontada correctamente")
                    else:
                        logger.error(f"[SystemUtils] Error desmontando {partition['name']}: {result.stderr}")
                        return (False, f"Error desmontando {partition['name']}: {result.stderr}")
            
            if unmounted:
                logger.info(f"[SystemUtils] Dispositivo '{device_name}' expulsado: {', '.join(unmounted)}")
                return (True, f"Desmontado correctamente: {', '.join(unmounted)}")
            else:
                logger.info(f"[SystemUtils] Dispositivo '{device_name}': no había particiones montadas")
                return (True, "No había particiones montadas")
        
        except subprocess.TimeoutExpired:
            logger.error(f"[SystemUtils] eject_usb_device: timeout desmontando '{device_name}'")
            return (False, "Timeout al desmontar el dispositivo")
        except FileNotFoundError:
            logger.error("[SystemUtils] eject_usb_device: udisksctl no encontrado")
            return (False, "udisksctl no encontrado. Instala: sudo apt-get install udisks2")
        except Exception as e:
            logger.error(f"[SystemUtils] eject_usb_device: error inesperado con '{device_name}': {e}")
            return (False, f"Error: {str(e)}")
    
    @staticmethod
    def run_script(script_path: str) -> Tuple[bool, str]:
        """
        Ejecuta un script de sistema
        
        Args:
            script_path: Ruta al script
            
        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            result = subprocess.run(
                ["bash", script_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"[SystemUtils] Script ejecutado correctamente: {script_path}")
                return True, "Script ejecutado exitosamente"
            else:
                logger.error(f"[SystemUtils] Script falló ({script_path}): {result.stderr}")
                return False, f"Error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            logger.error(f"[SystemUtils] run_script: timeout ejecutando {script_path}")
            return False, "Timeout: El script tardó demasiado"
        except FileNotFoundError:
            logger.error(f"[SystemUtils] run_script: script no encontrado: {script_path}")
            return False, f"Script no encontrado: {script_path}"
        except Exception as e:
            logger.error(f"[SystemUtils] run_script: error inesperado ({script_path}): {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def get_interfaces_ips() -> Dict[str, str]:
        """
        Obtiene las IPs de todas las interfaces de red
        
        Returns:
            Diccionario {interfaz: IP}
        """
        result = {}
        try:
            addrs = psutil.net_if_addrs()
            for iface, addr_list in addrs.items():
                for addr in addr_list:
                    if addr.family == socket.AF_INET:
                        result[iface] = addr.address
                        break
        except Exception as e:
            logger.warning(f"[SystemUtils] get_interfaces_ips: {e}")
        
        return result
    
    @staticmethod
    def get_nvme_temp() -> float:
        """
        Obtiene la temperatura del disco NVMe
        
        Returns:
            Temperatura en °C o 0.0 si no se puede leer
        """
        # Método 1: smartctl
        try:
            result = subprocess.run(
                ["sudo", "smartctl", "-a", "/dev/nvme0"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Temperature:' in line or 'Temperature Sensor' in line:
                        match = re.search(r'(\d+)\s*Celsius', line)
                        if match:
                            return float(match.group(1))
            else:
                logger.debug(f"[SystemUtils] get_nvme_temp: smartctl retornó código {result.returncode}")
        except subprocess.TimeoutExpired:
            logger.warning("[SystemUtils] get_nvme_temp: timeout ejecutando smartctl")
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Método 2: sysfs
        try:
            temp_files = [
                "/sys/class/hwmon/hwmon*/temp1_input",
                "/sys/block/nvme0n1/device/hwmon/hwmon*/temp1_input"
            ]
            
            for pattern in temp_files:
                for temp_file in glob.glob(pattern):
                    with open(temp_file, 'r') as f:
                        temp_millis = int(f.read().strip())
                        return temp_millis / 1000.0
        except FileNotFoundError:
            logger.debug("[SystemUtils] get_nvme_temp: archivos sysfs no encontrados")
        except ValueError as e:
            logger.warning(f"[SystemUtils] get_nvme_temp: error leyendo sysfs: {e}")
        except PermissionError:
            logger.warning("[SystemUtils] get_nvme_temp: sin permisos para leer sysfs")
        
        return 0.0
````

## File: QUICKSTART.md
````markdown
# 🚀 Inicio Rápido - Dashboard v2.5.1

---

## ⚡ Instalación (2 Comandos)

```bash
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard
chmod +x install_system.sh
sudo ./install_system.sh
python3 main.py
```

El script instala automáticamente las dependencias del sistema y Python, y pregunta si quieres configurar sensores y speedtest.

---

## 🔁 Alternativa con Entorno Virtual

Si prefieres aislar las dependencias:

```bash
chmod +x install.sh
./install.sh
source venv/bin/activate
python3 main.py
```

> Recuerda activar el entorno (`source venv/bin/activate`) cada vez que quieras ejecutar el dashboard.

---

## 📋 Requisitos Mínimos

- ✅ Raspberry Pi 3/4/5
- ✅ Raspberry Pi OS (cualquier versión)
- ✅ Python 3.8+
- ✅ Conexión a internet (para instalación)

---

## 🎯 Menú Principal (13 botones)

```
┌───────────────────────────────────┐
│  Control        │  Monitor         │
│  Ventiladores   │  Placa           │
├─────────────────┼──────────────────┤
│  Monitor        │  Monitor         │
│  Red            │  USB             │
├─────────────────┼──────────────────┤
│  Monitor        │  Lanzadores      │
│  Disco          │                  │
├─────────────────┼──────────────────┤
│  Monitor        │  Monitor         │
│  Procesos       │  Servicios       │
├─────────────────┼──────────────────┤
│  Histórico      │  Actualizaciones │
│  Datos          │                  │
├─────────────────┼──────────────────┤
│  Cambiar Tema   │  Reiniciar       │
├─────────────────┼──────────────────┤
│  Salir          │                  │
└─────────────────┴──────────────────┘
```

---

## 🖥️ Las 13 Ventanas

**1. Monitor Placa** — CPU, RAM y temperatura en tiempo real con gráficas

**2. Monitor Red** — Download/Upload en vivo, speedtest, lista de IPs

**3. Monitor USB** — Dispositivos conectados, expulsión segura

**4. Monitor Disco** — Espacio, temperatura NVMe, velocidad I/O

**5. Monitor Procesos** — Top 20 procesos, búsqueda, matar procesos

**6. Monitor Servicios** — Start/Stop/Restart systemd, ver logs

**7. Histórico Datos** — Gráficas CPU/RAM/Temp en 24h, 7d, 30d, exportar CSV

**8. Control Ventiladores** — Modo Auto/Manual/Silent/Normal/Performance, curvas PWM

**9. Lanzadores** — Scripts personalizados con terminal en vivo

**10. Actualizaciones** — Estado de paquetes, instalar con terminal integrada

**11. Cambiar Tema** — 15 temas (Cyberpunk, Matrix, Dracula, Nord...)

**12. Reiniciar** — Reinicia el dashboard aplicando cambios de código

**13. Salir** — Salir de la app o apagar el sistema

---

## 🔧 Configuración Básica

### Ajustar posición en pantalla DSI (`config/settings.py`):
```python
DSI_X = 0     # Posición horizontal
DSI_Y = 0     # Posición vertical
```

### Añadir scripts en Lanzadores:
```python
LAUNCHERS = [
    {"label": "Mi Script", "script": str(SCRIPTS_DIR / "mi_script.sh")},
]
```

---

## 📋 Ver Logs del Sistema

```bash
# En tiempo real
tail -f data/logs/dashboard.log

# Solo errores
grep ERROR data/logs/dashboard.log
```

---

## ❓ Problemas Comunes

| Problema | Solución |
|----------|----------|
| No arranca | `pip3 install --break-system-packages -r requirements.txt` |
| Temperatura 0 | `sudo sensors-detect --auto` |
| NVMe temp 0 | `sudo apt install smartmontools` |
| Speedtest falla | `sudo apt install speedtest-cli` |
| USB no expulsa | `sudo apt install udisks2` |
| Ver qué falla | `grep ERROR data/logs/dashboard.log` |

---

## 🆕 Novedades v2.5.1

✅ **Logging completo** — Todos los módulos loguean eventos y errores  
✅ **Ventana Actualizaciones** — Terminal integrada para instalar paquetes  
✅ **Caché de actualizaciones** — `apt update` solo al arranque y al pedir  
✅ **Fix arranque** — Servicio de datos ya no se detiene a los 3 segundos  
✅ **Terminal de apagado** — Visualiza el proceso de shutdown  

---

## 📚 Más Información

**[README.md](README.md)** — Documentación completa  
**[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** — Instalación detallada  
**[INDEX.md](INDEX.md)** — Índice de toda la documentación

---

**Dashboard v2.5.1** 🚀✨
````

## File: config/settings.py
````python
"""
Configuración centralizada del sistema de monitoreo
"""
from pathlib import Path
from config.themes import load_selected_theme, get_theme_colors
# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Asegurar que los directorios existan
DATA_DIR.mkdir(exist_ok=True)
SCRIPTS_DIR.mkdir(exist_ok=True)

# Archivos de estado
STATE_FILE = DATA_DIR / "fan_state.json"
CURVE_FILE = DATA_DIR / "fan_curve.json"

# Configuración de pantalla DSI
DSI_WIDTH = 800
DSI_HEIGHT = 480
DSI_X = 1124
DSI_Y = 1080

# Configuración de actualización
UPDATE_MS = 2000
HISTORY = 60
GRAPH_WIDTH = 800
GRAPH_HEIGHT = 20

# Umbrales de advertencia y críticos
CPU_WARN = 60
CPU_CRIT = 85
TEMP_WARN = 60
TEMP_CRIT = 75
RAM_WARN = 65
RAM_CRIT = 85

# Configuración de red
NET_WARN = 2.0  # MB/s
NET_CRIT = 6.0
NET_INTERFACE = None  # None = auto | "eth0" | "wlan0"
NET_MAX_MB = 10.0
NET_MIN_SCALE = 0.5
NET_MAX_SCALE = 200.0
NET_IDLE_THRESHOLD = 0.2
NET_IDLE_RESET_TIME = 15  # segundos

# Lanzadores de scripts
LAUNCHERS = [
    {
        "label": "󰣳 󰌘 Montar NAS",
        "script": str(SCRIPTS_DIR / "montarnas.sh")
    },
    {
        "label": "󰣳 󰌙 Desmontar NAS",
        "script": str(SCRIPTS_DIR / "desmontarnas.sh")
    },
    {
        "label": "󰚰  Update System",
        "script": str(SCRIPTS_DIR / "update.sh")
    },
    {
        "label": "󰌘  Conectar VPN",
        "script": str(SCRIPTS_DIR / "conectar_vpn.sh")
    },
    {
        "label": "󰌙  Desconectar VPN",
        "script": str(SCRIPTS_DIR / "desconectar_vpn.sh")
    },
    {
        "label": "󱓞  Iniciar fase1",
        "script": str(SCRIPTS_DIR / "fase1.sh")
    },
    {
        "label": "󰅙  Shutdown",
        "script": str(SCRIPTS_DIR / "apagado.sh")
    }
]

# ========================================
# SISTEMA DE TEMAS
# ========================================

# Importar sistema de temas


# Cargar tema seleccionado
SELECTED_THEME = load_selected_theme()

# Obtener colores del tema
COLORS = get_theme_colors(SELECTED_THEME)

# Fuente
FONT_FAMILY = "FiraMono Nerd Font"
FONT_SIZES = {
    "small": 14,
    "medium": 18,
    "large": 20,
    "xlarge": 24,
    "xxlarge": 30
}
````

## File: core/network_monitor.py
````python
"""
Monitor de red
"""
import json
import threading
import subprocess
from collections import deque
from typing import Dict, Optional
from config.settings import (HISTORY, NET_MIN_SCALE, NET_MAX_SCALE, 
                             NET_IDLE_THRESHOLD, NET_IDLE_RESET_TIME, NET_MAX_MB, COLORS, NET_WARN, NET_CRIT)
from utils.system_utils import SystemUtils
from utils.logger import get_logger

logger = get_logger(__name__)


class NetworkMonitor:
    """Monitor de red con gestión de estadísticas y speedtest"""
    
    def __init__(self):
        self.system_utils = SystemUtils()
        
        # Historiales
        self.download_hist = deque(maxlen=HISTORY)
        self.upload_hist = deque(maxlen=HISTORY)
        
        # Estado
        self.last_net_io = {}
        self.last_used_iface = None
        self.dynamic_max = NET_MAX_MB
        self.idle_counter = 0
        
        # Speedtest
        self.speedtest_result = {
            "status": "idle",
            "ping": 0,
            "download": 0.0,
            "upload": 0.0
        }
    
    def get_current_stats(self, interface: Optional[str] = None) -> Dict:
        """
        Obtiene estadísticas actuales de red
        
        Args:
            interface: Interfaz de red específica o None para auto-detección
            
        Returns:
            Diccionario con estadísticas de red
        """
        iface, stats = self.system_utils.get_net_io(interface)
        
        prev = self.last_net_io.get(iface)
        dl, ul = self.system_utils.safe_net_speed(stats, prev)
        
        self.last_net_io[iface] = stats
        self.last_used_iface = iface
        
        return {
            'interface': iface,
            'download_mb': dl,
            'upload_mb': ul
        }
    
    def update_history(self, stats: Dict) -> None:
        """
        Actualiza historiales de red
        
        Args:
            stats: Estadísticas actuales
        """
        self.download_hist.append(stats['download_mb'])
        self.upload_hist.append(stats['upload_mb'])
    
    def adaptive_scale(self, current_max: float, recent_data: list) -> float:
        """
        Ajusta dinámicamente la escala del gráfico
        
        Args:
            current_max: Máximo actual
            recent_data: Datos recientes
            
        Returns:
            Nuevo máximo escalado
        """
        if not recent_data:
            return current_max
        
        peak = max(recent_data) if recent_data else 0
        
        if peak < NET_IDLE_THRESHOLD:
            self.idle_counter += 1
            if self.idle_counter >= NET_IDLE_RESET_TIME:
                self.idle_counter = 0
                return NET_MAX_MB
        else:
            self.idle_counter = 0
        
        if peak > current_max * 0.8:
            new_max = peak * 1.2
        elif peak < current_max * 0.3:
            new_max = max(peak * 1.5, NET_MIN_SCALE)
        else:
            new_max = current_max
        
        return max(NET_MIN_SCALE, min(NET_MAX_SCALE, new_max))
    
    def update_dynamic_scale(self) -> None:
        """Actualiza la escala dinámica basada en el historial"""
        all_data = list(self.download_hist) + list(self.upload_hist)
        self.dynamic_max = self.adaptive_scale(self.dynamic_max, all_data)
    
    def get_history(self) -> Dict:
        """
        Obtiene historiales de red
        
        Returns:
            Diccionario con historiales
        """
        return {
            'download': list(self.download_hist),
            'upload': list(self.upload_hist),
            'dynamic_max': self.dynamic_max
        }
    
    def run_speedtest(self) -> None:
        """Ejecuta speedtest (Ookla CLI) en un thread separado"""
        def _run():
            logger.info("[NetworkMonitor] Iniciando speedtest...")
            self.speedtest_result["status"] = "running"
            try:
                result = subprocess.run(
                    ["speedtest", "--format=json", "--accept-license", "--accept-gdpr"],
                    capture_output=True,
                    text=True,
                    timeout=90
                )

                if result.returncode == 0:
                    data = json.loads(result.stdout)

                    # El nuevo CLI devuelve bytes/s → convertir a MB/s
                    ping     = data["ping"]["latency"]
                    download = data["download"]["bandwidth"] / 1_000_000
                    upload   = data["upload"]["bandwidth"]   / 1_000_000

                    self.speedtest_result.update({
                        "status":   "done",
                        "ping":     round(ping, 1),
                        "download": round(download, 2),
                        "upload":   round(upload, 2),
                    })
                    logger.info(
                        f"[NetworkMonitor] Speedtest completado — "
                        f"Ping: {ping:.1f}ms, ↓{download:.2f} MB/s, ↑{upload:.2f} MB/s"
                    )
                else:
                    logger.error(
                        f"[NetworkMonitor] speedtest retornó código {result.returncode}: {result.stderr}"
                    )
                    self.speedtest_result["status"] = "error"

            except subprocess.TimeoutExpired:
                logger.warning("[NetworkMonitor] Speedtest timeout (>90s)")
                self.speedtest_result["status"] = "timeout"
            except FileNotFoundError:
                logger.error(
                    "[NetworkMonitor] speedtest no encontrado. "
                    "Instala el CLI oficial de Ookla: https://www.speedtest.net/apps/cli"
                )
                self.speedtest_result["status"] = "error"
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"[NetworkMonitor] Error parseando resultado de speedtest: {e}")
                self.speedtest_result["status"] = "error"
            except Exception as e:
                logger.error(f"[NetworkMonitor] Error inesperado en speedtest: {e}")
                self.speedtest_result["status"] = "error"

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
    
    def get_speedtest_result(self) -> Dict:
        """
        Obtiene el resultado del speedtest
        
        Returns:
            Diccionario con resultados
        """
        return self.speedtest_result.copy()
    
    def reset_speedtest(self) -> None:
        """Resetea el estado del speedtest"""
        self.speedtest_result = {
            "status": "idle",
            "ping": 0,
            "download": 0.0,
            "upload": 0.0
        }
    
    @staticmethod
    def net_color(value: float) -> str:
        """
        Determina el color según el tráfico de red
        
        Args:
            value: Velocidad en MB/s
            
        Returns:
            Color en formato hex
        """
        if value >= NET_CRIT:
            return COLORS['danger']
        elif value >= NET_WARN:
            return COLORS['warning']
        else:
            return COLORS['primary']
````

## File: ui/windows/network.py
````python
"""
Ventana de monitoreo de red
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH,
                             DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, NET_INTERFACE)
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import GraphWidget
from core.network_monitor import NetworkMonitor
from utils.system_utils import SystemUtils


class NetworkWindow(ctk.CTkToplevel):
    """Ventana de monitoreo de red"""
    
    def __init__(self, parent, network_monitor: NetworkMonitor):
        super().__init__(parent)
        
        # Referencias
        self.network_monitor = network_monitor
        
        # Widgets para actualización
        self.widgets = {}
        self.graphs = {}
        
        # Configurar ventana
        self.title("Monitor de Red")
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
        
        # ── Header unificado ──────────────────────────────────────────────────
        # El status mostrará interfaz activa + velocidades en tiempo real
        self._header = make_window_header(
            main,
            title="MONITOR DE RED",
            on_close=self.destroy,
            status_text="Detectando interfaz...",
        )
        
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

        StyleManager.style_scrollbar_ctk(scrollbar)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Secciones
        self._create_interfaces_section(inner)
        self._create_download_section(inner)
        self._create_upload_section(inner)
        self._create_speedtest_section(inner)
        

    
    def _create_interfaces_section(self, parent):
        """Crea la sección de interfaces e IPs"""
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        frame.pack(fill="x", pady=10, padx=10)
        
        # Título
        title = ctk.CTkLabel(
            frame,
            text="INTERFACES Y IPs",
            text_color=COLORS['success'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        title.pack(anchor="w", pady=(10, 10), padx=10)
        
        # Contenedor para las interfaces
        self.interfaces_container = ctk.CTkFrame(frame, fg_color=COLORS['bg_dark'])
        self.interfaces_container.pack(fill="x", padx=10, pady=(0, 10))
        
        # Obtener y mostrar interfaces
        self._update_interfaces()
    
    def _update_interfaces(self):
        """Actualiza la lista de interfaces e IPs"""
        # Limpiar widgets anteriores
        for widget in self.interfaces_container.winfo_children():
            widget.destroy()
        
        # Obtener IPs
        interfaces = SystemUtils.get_interfaces_ips()
        
        if not interfaces:
            no_iface = ctk.CTkLabel(
                self.interfaces_container,
                text="No se detectaron interfaces",
                text_color=COLORS['warning'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            no_iface.pack(pady=5)
            return
        
        # Mostrar cada interfaz
        for iface, ip in sorted(interfaces.items()):
            if iface.startswith('tun'):
                text_color = COLORS['success']
                icon = "🔒"
            elif iface.startswith(('eth', 'enp')):
                text_color = COLORS['primary']
                icon = "🌐"
            elif iface.startswith(('wlan', 'wlp')):
                text_color = COLORS['warning']
                icon = "\uf0eb"  # icono wifi Nerd Font — extraer del repomix con repr()
            else:
                text_color = COLORS['text']
                icon = "•"
            
            iface_label = ctk.CTkLabel(
                self.interfaces_container,
                text=f"{icon} {iface}: {ip}",
                text_color=text_color,
                font=(FONT_FAMILY, FONT_SIZES['medium']),
                anchor="w"
            )
            iface_label.pack(anchor="w", pady=2, padx=10)
    
    def _create_download_section(self, parent):
        """Crea la sección de descarga"""
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        frame.pack(fill="x", pady=10, padx=10)
        
        label = ctk.CTkLabel(
            frame,
            text="DESCARGA",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        label.pack(anchor="w", pady=(5, 0), padx=10)
        
        value_label = ctk.CTkLabel(
            frame,
            text="0.00 MB/s | Escala: 10.00",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        value_label.pack(anchor="e", pady=(0, 5), padx=10)
        
        graph = GraphWidget(frame, width=DSI_WIDTH-80, height=120)
        graph.pack(pady=(0, 10))
        
        self.widgets['download_label'] = label
        self.widgets['download_value'] = value_label
        self.graphs['download'] = graph
    
    def _create_upload_section(self, parent):
        """Crea la sección de subida"""
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        frame.pack(fill="x", pady=10, padx=10)
        
        label = ctk.CTkLabel(
            frame,
            text="SUBIDA",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        label.pack(anchor="w", pady=(5, 0), padx=10)
        
        value_label = ctk.CTkLabel(
            frame,
            text="0.00 MB/s | Escala: 10.00",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        value_label.pack(anchor="e", pady=(0, 5), padx=10)
        
        graph = GraphWidget(frame, width=DSI_WIDTH-80, height=120)
        graph.pack(pady=(0, 10))
        
        self.widgets['upload_label'] = label
        self.widgets['upload_value'] = value_label
        self.graphs['upload'] = graph
    
    def _create_speedtest_section(self, parent):
        """Crea la sección de speedtest"""
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        frame.pack(fill="x", pady=10, padx=10)
        
        title = ctk.CTkLabel(
            frame,
            text="SPEEDTEST",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        title.pack(anchor="w", pady=(5, 10), padx=10)
        
        self.speedtest_result = ctk.CTkLabel(
            frame,
            text="Haz clic en 'Ejecutar Test' para comenzar",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            justify="left"
        )
        self.speedtest_result.pack(pady=(0, 10), padx=10)
        
        btn_frame = ctk.CTkFrame(frame, fg_color=COLORS['bg_dark'])
        btn_frame.pack(pady=(0, 10))
        
        self.speedtest_btn = make_futuristic_button(
            btn_frame,
            text="Ejecutar Test",
            command=self._run_speedtest,
            width=20,
            height=6
        )
        self.speedtest_btn.pack()
    
    def _run_speedtest(self):
        """Ejecuta el speedtest"""
        result = self.network_monitor.get_speedtest_result()
        if result['status'] == 'running':
            return
        
        self.network_monitor.reset_speedtest()
        self.network_monitor.run_speedtest()
        
        self.speedtest_btn.configure(state="disabled")
        self.speedtest_result.configure(
            text="Ejecutando test...",
            text_color=COLORS['warning']
        )
    
    def _update(self):
        """Actualiza los datos de red"""
        if not self.winfo_exists():
            return
        
        # Obtener estadísticas
        stats = self.network_monitor.get_current_stats(NET_INTERFACE)
        self.network_monitor.update_history(stats)
        self.network_monitor.update_dynamic_scale()
        
        history = self.network_monitor.get_history()
        
        # Actualizar status del header con interfaz activa + velocidades
        dl = stats['download_mb']
        ul = stats['upload_mb']
        iface = stats['interface']
        self._header.status_label.configure(
            text=f"{iface}  ·  ↓{dl:.2f}  ↑{ul:.2f} MB/s"
        )
        
        # Actualizar descarga
        dl_color = self.network_monitor.net_color(stats['download_mb'])
        self.widgets['download_label'].configure(text_color=dl_color)
        self.widgets['download_value'].configure(
            text=f"{stats['download_mb']:.2f} MB/s | Escala: {history['dynamic_max']:.2f}",
            text_color=dl_color
        )
        self.graphs['download'].update(
            history['download'],
            history['dynamic_max'],
            dl_color
        )
        
        # Actualizar subida
        ul_color = self.network_monitor.net_color(stats['upload_mb'])
        self.widgets['upload_label'].configure(text_color=ul_color)
        self.widgets['upload_value'].configure(
            text=f"{stats['upload_mb']:.2f} MB/s | Escala: {history['dynamic_max']:.2f}",
            text_color=ul_color
        )
        self.graphs['upload'].update(
            history['upload'],
            history['dynamic_max'],
            ul_color
        )
        
        # Actualizar speedtest
        self._update_speedtest()
        
        # Actualizar interfaces cada 5 ciclos
        if not hasattr(self, '_interface_update_counter'):
            self._interface_update_counter = 0
        
        self._interface_update_counter += 1
        if self._interface_update_counter >= 5:
            self._update_interfaces()
            self._interface_update_counter = 0
        
        # Programar siguiente actualización
        self.after(UPDATE_MS, self._update)
    
    def _update_speedtest(self):
        """Actualiza el resultado del speedtest"""
        result = self.network_monitor.get_speedtest_result()
        status = result['status']
        
        if status == 'idle':
            self.speedtest_result.configure(
                text="Haz clic en 'Ejecutar Test' para comenzar",
                text_color=COLORS['text']
            )
            self.speedtest_btn.configure(state="normal")
        
        elif status == 'running':
            self.speedtest_result.configure(
                text="Ejecutando test de velocidad...",
                text_color=COLORS['warning']
            )
            self.speedtest_btn.configure(state="disabled")
        
        elif status == 'done':
            ping     = result['ping']
            download = result['download']
            upload   = result['upload']
            
            self.speedtest_result.configure(
                text=f"Ping: {ping} ms\n↓ {download:.2f} MB/s\n↑ {upload:.2f} MB/s",
                text_color=COLORS['success']
            )
            self.speedtest_btn.configure(state="normal")
        
        elif status == 'timeout':
            self.speedtest_result.configure(
                text="Timeout: El test tardó demasiado",
                text_color=COLORS['danger']
            )
            self.speedtest_btn.configure(state="normal")
        
        elif status == 'error':
            self.speedtest_result.configure(
                text="Error ejecutando el test\nVerifica que speedtest-cli esté instalado",
                text_color=COLORS['danger']
            )
            self.speedtest_btn.configure(state="normal")
````

## File: INDEX.md
````markdown
# 📚 Índice de Documentación - System Dashboard v2.7

Guía completa de toda la documentación del proyecto actualizada.

---

## 🚀 Documentos Esenciales

### **Para Empezar:**
1. **[README.md](README.md)** ⭐  
   Documentación completa del proyecto v2.7. **Empieza aquí.**

2. **[QUICKSTART.md](QUICKSTART.md)** ⚡  
   Instalación y ejecución en 5 minutos.

---

## 📖 Guías por Tema

### 🎨 **Personalización**

**[THEMES_GUIDE.md](THEMES_GUIDE.md)**  
- Lista completa de 15 temas
- Cómo crear temas personalizados
- Paletas de colores de cada tema
- Cambiar tema desde código

---

### 🔧 **Instalación**

**[INSTALL_GUIDE.md](INSTALL_GUIDE.md)**  
- Instalación en Raspberry Pi OS
- Instalación en Kali Linux
- Instalación en otros Linux
- Solución de problemas comunes
- Métodos: venv, sin venv, script automático

---

### ⚙️ **Características Avanzadas**

**[PROCESS_MONITOR_GUIDE.md](PROCESS_MONITOR_GUIDE.md)**  
- Monitor de procesos completo
- Búsqueda y filtrado
- Terminación de procesos
- Personalización de columnas

**[SERVICE_MONITOR_GUIDE.md](SERVICE_MONITOR_GUIDE.md)**  
- Monitor de servicios systemd
- Start/Stop/Restart servicios
- Enable/Disable autostart
- Ver logs en tiempo real
- Implementación paso a paso

**[HISTORICO_DATOS_GUIDE.md](HISTORICO_DATOS_GUIDE.md)**  
- Sistema de histórico completo
- Base de datos SQLite
- Visualización con matplotlib
- Recolección automática
- Exportación CSV
- Implementación paso a paso

**[FAN_CONTROL_GUIDE.md](FAN_CONTROL_GUIDE.md)** (si existe)  
- Configuración de ventiladores PWM
- Crear curvas personalizadas
- Modos de operación
- Servicio background

**[NETWORK_GUIDE.md](NETWORK_GUIDE.md)** (si existe)  
- Monitor de tráfico de red
- Speedtest integrado (CLI oficial Ookla)
- Auto-detección de interfaz
- Lista de IPs

---

### 🏗️ **Arquitectura**

**[ARCHITECTURE.md](ARCHITECTURE.md)** (si existe)  
- Estructura del proyecto
- Patrones de diseño
- Flujo de datos
- Cómo extender funcionalidad

---

### 🤝 **Integración**

**[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)**  
- Integrar con fase1.py (OLED)
- Compartir estado de ventiladores
- API de archivos JSON
- Sincronización entre procesos

---

### 💡 **Ideas y Expansión**

**[IDEAS_EXPANSION.md](IDEAS_EXPANSION.md)**  
- ✅ Funcionalidades implementadas (12 áreas)
- 🔄 En evaluación (Alertas, GPU)
- 💭 Ideas futuras (Automatización, API REST)
- Roadmap v2.8 y v3.0

---

## 📋 Archivos de Soporte

### **Configuración:**
- `requirements.txt` - Dependencias Python
- `install.sh` - Script de instalación automática
- `config/settings.py` - Configuración global
- `config/themes.py` - Definición de 15 temas

### **Scripts:**
- `main.py` - Punto de entrada
- `scripts/` - Scripts personalizados

### **Compatibilidad:**
- `COMPATIBILIDAD.md` - Sistemas soportados
- `REQUIREMENTS.md` - Requisitos detallados

---

## 🗂️ Estructura de Documentos v2.7

```
📚 Documentación/
├── README.md                    ⭐ Documento principal v2.7
├── QUICKSTART.md                ⚡ Inicio rápido
├── INDEX.md                     📑 Este archivo
├── INSTALL_GUIDE.md             🔧 Instalación
├── THEMES_GUIDE.md              🎨 Guía de temas
├── PROCESS_MONITOR_GUIDE.md     ⚙️ Monitor de procesos
├── SERVICE_MONITOR_GUIDE.md     🔧 Monitor de servicios
├── HISTORICO_DATOS_GUIDE.md     📊 Histórico de datos
├── INTEGRATION_GUIDE.md         🤝 Integración
├── IDEAS_EXPANSION.md           💡 Ideas futuras
├── COMPATIBILIDAD.md            🌐 Compatibilidad
└── REQUIREMENTS.md              📋 Requisitos
```

---

## 🎯 Flujo de Lectura Recomendado

### **Usuario Nuevo:**
1. README.md - Leer sección "Características"
2. QUICKSTART.md - Instalar y ejecutar
3. THEMES_GUIDE.md - Personalizar colores
4. Explorar las 10 ventanas del dashboard 🎉

### **Usuario Avanzado:**
1. README.md completo
2. PROCESS_MONITOR_GUIDE.md - Gestión avanzada
3. SERVICE_MONITOR_GUIDE.md - Control de servicios
4. HISTORICO_DATOS_GUIDE.md - Análisis de datos
5. Personalizar configuración

### **Desarrollador:**
1. ARCHITECTURE.md - Estructura del proyecto
2. README.md sección "Arquitectura"
3. Código fuente en `core/` y `ui/`
4. IDEAS_EXPANSION.md - Ver qué se puede añadir
5. Implementar nuevas funciones

---

## 🔍 Buscar por Tema

### **¿Cómo hacer X?**
- **Cambiar tema** → THEMES_GUIDE.md
- **Instalar** → QUICKSTART.md o INSTALL_GUIDE.md
- **Ver procesos** → PROCESS_MONITOR_GUIDE.md
- **Gestionar servicios** → SERVICE_MONITOR_GUIDE.md
- **Ver histórico** → HISTORICO_DATOS_GUIDE.md
- **Configurar ventiladores** → FAN_CONTROL_GUIDE.md
- **Integrar con OLED** → INTEGRATION_GUIDE.md
- **Añadir funciones** → ARCHITECTURE.md + IDEAS_EXPANSION.md

### **¿Tengo un problema?**
- **No arranca** → QUICKSTART.md sección "Problemas Comunes"
- **Ventiladores no funcionan** → FAN_CONTROL_GUIDE.md
- **Temperatura no se lee** → INSTALL_GUIDE.md
- **Speedtest falla** → NETWORK_GUIDE.md
- **Base de datos crece** → HISTORICO_DATOS_GUIDE.md
- **Servicios no se gestionan** → SERVICE_MONITOR_GUIDE.md
- **Otro problema** → README.md sección "Troubleshooting"

---

## 📊 Estadísticas del Proyecto v2.7

- **Archivos Python**: 42+
- **Líneas de código**: ~13,000
- **Ventanas**: 10 ventanas funcionales
- **Temas**: 15 temas pre-configurados
- **Documentos**: 12 guías
- **Servicios background**: 3 (FanAuto + DataCollection + Cleanup)

---

## 🆕 Novedades en v2.7

### **Funcionalidades Nuevas:**
- ✅ **Header unificado** (`make_window_header`) en las 10 ventanas
- ✅ **Botón ✕ táctil** (52×42px) en todas las ventanas
- ✅ **Status en tiempo real** en el header de cada ventana
- ✅ **Speedtest** migrado al CLI oficial de Ookla (JSON, MB/s)

### **Fixes:**
- ✅ Botón Cerrar duplicado en Monitor de Red
- ✅ Import `make_window_header` en ThemeSelector
- ✅ Stats label de Servicios y Procesos en línea propia

---

## 📧 Ayuda Adicional

**¿No encuentras lo que buscas?**

1. Busca en README.md (Ctrl+F)
2. Revisa los ejemplos en las guías
3. Abre un Issue en GitHub
4. Revisa el código fuente (está comentado)

---

## 🔗 Enlaces Rápidos

| Tema | Documento |
|------|-----------|
| **Inicio Rápido** | [QUICKSTART.md](QUICKSTART.md) |
| **Características** | [README.md](README.md) |
| **Instalación** | [INSTALL_GUIDE.md](INSTALL_GUIDE.md) |
| **Temas** | [THEMES_GUIDE.md](THEMES_GUIDE.md) |
| **Procesos** | [PROCESS_MONITOR_GUIDE.md](PROCESS_MONITOR_GUIDE.md) |
| **Servicios** | [SERVICE_MONITOR_GUIDE.md](SERVICE_MONITOR_GUIDE.md) |
| **Histórico** | [HISTORICO_DATOS_GUIDE.md](HISTORICO_DATOS_GUIDE.md) |
| **Ideas Futuras** | [IDEAS_EXPANSION.md](IDEAS_EXPANSION.md) |

---

**Versión actual**: v2.7 — **Última actualización**: 2026-02-22
````

## File: core/data_analyzer.py
````python
"""
Análisis de datos históricos
"""
import sqlite3
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from config.settings import DATA_DIR
from utils.logger import get_logger

logger = get_logger(__name__)


class DataAnalyzer:
    """Analiza datos históricos de la base de datos"""

    def __init__(self, db_path: str = f"{DATA_DIR}/history.db"):
        self.db_path = db_path

    # ─────────────────────────────────────────────
    # Métodos basados en horas (uso existente)
    # ─────────────────────────────────────────────

    def get_data_range(self, hours: int = 24) -> List[Dict]:
        """
        Obtiene datos de las últimas X horas

        Args:
            hours: Número de horas hacia atrás

        Returns:
            Lista de diccionarios con los datos
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cutoff_time = datetime.now() - timedelta(hours=hours)

            cursor.execute('''
                SELECT * FROM metrics
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
            ''', (cutoff_time,))

            rows = cursor.fetchall()
            conn.close()

            logger.debug(f"[DataAnalyzer] get_data_range: {len(rows)} registros obtenidos (últimas {hours}h)")
            return [dict(row) for row in rows]

        except sqlite3.OperationalError as e:
            logger.error(f"[DataAnalyzer] get_data_range: error de base de datos: {e}")
            return []
        except Exception as e:
            logger.error(f"[DataAnalyzer] get_data_range: error inesperado: {e}")
            return []

    def get_stats(self, hours: int = 24) -> Dict:
        """
        Obtiene estadísticas de las últimas X horas

        Args:
            hours: Número de horas hacia atrás

        Returns:
            Diccionario con estadísticas
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return self._get_stats_between(cutoff_time, datetime.now())

    def get_graph_data(self, metric: str, hours: int = 24) -> Tuple[List, List]:
        """
        Obtiene datos para gráficas (últimas X horas)

        Args:
            metric: Métrica a obtener (cpu_percent, ram_percent, temperature, etc)
            hours: Número de horas hacia atrás

        Returns:
            Tupla (timestamps, values)
        """
        try:
            data = self.get_data_range(hours)
            return self._extract_metric(data, metric)
        except Exception as e:
            logger.error(f"[DataAnalyzer] get_graph_data: error obteniendo datos de '{metric}': {e}")
            return [], []

    def export_to_csv(self, output_path: str, hours: int = 24):
        """
        Exporta datos a CSV (últimas X horas)

        Args:
            output_path: Ruta del archivo CSV a crear
            hours: Número de horas a exportar
        """
        data = self.get_data_range(hours)
        self._write_csv(output_path, data)

    # ─────────────────────────────────────────────
    # Métodos basados en rango personalizado
    # ─────────────────────────────────────────────

    def get_data_range_between(self, start: datetime, end: datetime) -> List[Dict]:
        """
        Obtiene datos entre dos fechas exactas.

        Args:
            start: Fecha/hora de inicio
            end:   Fecha/hora de fin

        Returns:
            Lista de diccionarios con los datos
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM metrics
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp ASC
            ''', (start, end))

            rows = cursor.fetchall()
            conn.close()

            logger.debug(
                f"[DataAnalyzer] get_data_range_between: {len(rows)} registros "
                f"({start.strftime('%Y-%m-%d %H:%M')} → {end.strftime('%Y-%m-%d %H:%M')})"
            )
            return [dict(row) for row in rows]

        except sqlite3.OperationalError as e:
            logger.error(f"[DataAnalyzer] get_data_range_between: error de base de datos: {e}")
            return []
        except Exception as e:
            logger.error(f"[DataAnalyzer] get_data_range_between: error inesperado: {e}")
            return []

    def get_stats_between(self, start: datetime, end: datetime) -> Dict:
        """
        Obtiene estadísticas entre dos fechas exactas.

        Args:
            start: Fecha/hora de inicio
            end:   Fecha/hora de fin

        Returns:
            Diccionario con estadísticas (mismo formato que get_stats)
        """
        return self._get_stats_between(start, end)

    def get_graph_data_between(self, metric: str, start: datetime, end: datetime) -> Tuple[List, List]:
        """
        Obtiene datos para gráficas entre dos fechas exactas.

        Args:
            metric: Métrica a obtener
            start:  Fecha/hora de inicio
            end:    Fecha/hora de fin

        Returns:
            Tupla (timestamps, values)
        """
        try:
            data = self.get_data_range_between(start, end)
            return self._extract_metric(data, metric)
        except Exception as e:
            logger.error(f"[DataAnalyzer] get_graph_data_between: error obteniendo datos de '{metric}': {e}")
            return [], []

    def export_to_csv_between(self, output_path: str, start: datetime, end: datetime):
        """
        Exporta datos a CSV entre dos fechas exactas.

        Args:
            output_path: Ruta del archivo CSV
            start:       Fecha/hora de inicio
            end:         Fecha/hora de fin
        """
        data = self.get_data_range_between(start, end)
        self._write_csv(output_path, data)

    # ─────────────────────────────────────────────
    # Detección de anomalías (sin cambios)
    # ─────────────────────────────────────────────

    def detect_anomalies(self, hours: int = 24) -> List[Dict]:
        """
        Detecta anomalías en los datos

        Args:
            hours: Número de horas hacia atrás

        Returns:
            Lista de anomalías detectadas
        """
        anomalies = []
        stats = self.get_stats(hours)

        if not stats:
            return anomalies

        if stats.get('cpu_avg', 0) > 80:
            anomalies.append({
                'type': 'cpu_high',
                'severity': 'warning',
                'message': f"CPU promedio alta: {stats['cpu_avg']:.1f}%"
            })
            logger.warning(f"[DataAnalyzer] Anomalía detectada: CPU promedio {stats['cpu_avg']:.1f}%")

        if stats.get('temp_max', 0) > 80:
            anomalies.append({
                'type': 'temp_high',
                'severity': 'critical',
                'message': f"Temperatura máxima: {stats['temp_max']:.1f}°C"
            })
            logger.warning(f"[DataAnalyzer] Anomalía detectada: temperatura máxima {stats['temp_max']:.1f}°C")

        if stats.get('ram_avg', 0) > 85:
            anomalies.append({
                'type': 'ram_high',
                'severity': 'warning',
                'message': f"RAM promedio alta: {stats['ram_avg']:.1f}%"
            })
            logger.warning(f"[DataAnalyzer] Anomalía detectada: RAM promedio {stats['ram_avg']:.1f}%")

        return anomalies

    # ─────────────────────────────────────────────
    # Métodos privados compartidos
    # ─────────────────────────────────────────────

    def _get_stats_between(self, start: datetime, end: datetime) -> Dict:
        """Lógica común de estadísticas para cualquier rango start→end."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT 
                    AVG(cpu_percent) as cpu_avg,
                    MAX(cpu_percent) as cpu_max,
                    MIN(cpu_percent) as cpu_min,
                    AVG(ram_percent) as ram_avg,
                    MAX(ram_percent) as ram_max,
                    MIN(ram_percent) as ram_min,
                    AVG(temperature) as temp_avg,
                    MAX(temperature) as temp_max,
                    MIN(temperature) as temp_min,
                    AVG(net_download_mb) as down_avg,
                    MAX(net_download_mb) as down_max,
                    MIN(net_download_mb) as down_min,
                    AVG(net_upload_mb) as up_avg,
                    MAX(net_upload_mb) as up_max,
                    MIN(net_upload_mb) as up_min,
                    AVG(disk_read_mb) as disk_read_avg,
                    MAX(disk_read_mb) as disk_read_max,
                    MIN(disk_read_mb) as disk_read_min,
                    AVG(disk_write_mb) as disk_write_avg,
                    MAX(disk_write_mb) as disk_write_max,
                    MIN(disk_write_mb) as disk_write_min,
                    AVG(fan_pwm) as pwm_avg,
                    MAX(fan_pwm) as pwm_max,
                    MIN(fan_pwm) as pwm_min,
                    MAX(updates_available) as updates_available_max,
                    MIN(updates_available) as updates_available_min,
                    AVG(updates_available) as updates_available_avg,
                    COUNT(*) as total_samples
                FROM metrics
                WHERE timestamp >= ? AND timestamp <= ?
            ''', (start, end))

            row = cursor.fetchone()
            conn.close()

            if row and row[24]:
                logger.debug(f"[DataAnalyzer] _get_stats_between: {row[24]} muestras")
                return {
                    'cpu_avg': round(row[0], 1) if row[0] else 0,
                    'cpu_max': round(row[1], 1) if row[1] else 0,
                    'cpu_min': round(row[2], 1) if row[2] else 0,
                    'ram_avg': round(row[3], 1) if row[3] else 0,
                    'ram_max': round(row[4], 1) if row[4] else 0,
                    'ram_min': round(row[5], 1) if row[5] else 0,
                    'temp_avg': round(row[6], 1) if row[6] else 0,
                    'temp_max': round(row[7], 1) if row[7] else 0,
                    'temp_min': round(row[8], 1) if row[8] else 0,
                    'down_avg': round(row[9], 2) if row[9] else 0,
                    'down_max': round(row[10], 2) if row[10] else 0,
                    'down_min': round(row[11], 2) if row[11] else 0,
                    'up_avg': round(row[12], 2) if row[12] else 0,
                    'up_max': round(row[13], 2) if row[13] else 0,
                    'up_min': round(row[14], 2) if row[14] else 0,
                    'disk_read_avg': round(row[15], 2) if row[15] else 0,
                    'disk_read_max': round(row[16], 2) if row[16] else 0,
                    'disk_read_min': round(row[17], 2) if row[17] else 0,
                    'disk_write_avg': round(row[18], 2) if row[18] else 0,
                    'disk_write_max': round(row[19], 2) if row[19] else 0,
                    'disk_write_min': round(row[20], 2) if row[20] else 0,
                    'pwm_avg': round(row[21], 0) if row[21] else 0,
                    'pwm_max': round(row[22], 0) if row[22] else 0,
                    'pwm_min': round(row[23], 0) if row[23] else 0,
                    'updates_available_max': row[24] if row[24] else 0,
                    'updates_available_min': row[25] if row[25] else 0,
                    'updates_available_avg': row[26] if row[26] else 0,
                    'total_samples': row[27]
                }

            logger.debug(f"[DataAnalyzer] _get_stats_between: sin datos en el rango")
            return {}

        except sqlite3.OperationalError as e:
            logger.error(f"[DataAnalyzer] _get_stats_between: error de base de datos: {e}")
            return {}
        except Exception as e:
            logger.error(f"[DataAnalyzer] _get_stats_between: error inesperado: {e}")
            return {}

    def _extract_metric(self, data: List[Dict], metric: str) -> Tuple[List, List]:
        """Extrae timestamps y valores de una métrica de una lista de registros."""
        timestamps = []
        values = []
        for entry in data:
            ts = datetime.fromisoformat(entry['timestamp'])
            timestamps.append(ts)
            values.append(entry.get(metric, 0))
        return timestamps, values

    def _write_csv(self, output_path: str, data: List[Dict]):
        """Escribe una lista de registros a CSV."""
        try:
            if not data:
                logger.warning(f"[DataAnalyzer] _write_csv: sin datos para exportar")
                return

            with open(output_path, 'w', newline='') as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in data:
                    writer.writerow(row)

            logger.info(f"[DataAnalyzer] _write_csv: {len(data)} registros exportados a {output_path}")

        except OSError as e:
            logger.error(f"[DataAnalyzer] _write_csv: error escribiendo {output_path}: {e}")
        except Exception as e:
            logger.error(f"[DataAnalyzer] _write_csv: error inesperado: {e}")
````

## File: ui/windows/__init__.py
````python
"""
Paquete de ventanas secundarias
"""
from .fan_control import FanControlWindow
from .monitor import MonitorWindow
from .network import NetworkWindow
from .usb import USBWindow
from .launchers import LaunchersWindow
from .disk import DiskWindow
from .process_window import ProcessWindow
from .service import ServiceWindow
from .update import UpdatesWindow
from .history import HistoryWindow
from .theme_selector import ThemeSelector

__all__ = [
    'FanControlWindow',
    'MonitorWindow', 
    'NetworkWindow',
    'USBWindow',
    'LaunchersWindow',
    'DiskWindow',
    'ProcessWindow',
    'ServiceWindow',
    'UpdatesWindow',
    'HistoryWindow',
    'ThemeSelector'
]
````

## File: IDEAS_EXPANSION.md
````markdown
# 💡 Ideas de Expansión - Dashboard v2.7

Roadmap de funcionalidades y estado real de implementación.

---

## ✅ Implementado

### **1. Monitor de Procesos en Tiempo Real**
**Implementado en v2.0**
- ✅ Lista en tiempo real (Top 20) con PID, comando, usuario, CPU%, RAM%
- ✅ Búsqueda por nombre o comando
- ✅ Filtros: Todos / Usuario / Sistema
- ✅ Ordenar por PID, Nombre, CPU%, RAM%
- ✅ Matar procesos con confirmación
- ✅ Colores dinámicos según uso
- ✅ Pausa inteligente durante interacciones
- ✅ Estadísticas: procesos totales, CPU, RAM, uptime

---

### **2. Monitor de Servicios systemd**
**Implementado en v2.5**
- ✅ Lista completa de servicios systemd
- ✅ Estados: active, inactive, failed con iconos
- ✅ Start/Stop/Restart con confirmación
- ✅ Ver logs en tiempo real (últimas 50 líneas)
- ✅ Enable/Disable autostart
- ✅ Búsqueda y filtros (Todos / Activos / Inactivos / Fallidos)
- ✅ Estadísticas: total, activos, fallidos, enabled

---

### **3. Histórico de Datos**
**Implementado en v2.5 — ampliado en v2.5.1**
- ✅ Base de datos SQLite (~5MB/10k registros)
- ✅ Recolección automática cada 5 minutos en background
- ✅ Métricas guardadas: CPU, RAM, Temp, Disco I/O, Red, PWM, actualizaciones
- ✅ **8 gráficas**: CPU, RAM, Temperatura, Red Download, Red Upload, Disk Read, Disk Write, PWM
- ✅ Periodos: 24h, 7d, 30d
- ✅ Estadísticas completas: promedios, mínimos, máximos de todas las métricas
- ✅ Detección de anomalías automática
- ✅ Exportación a CSV
- ✅ Exportación de gráficas como imagen PNG
- ✅ Limpieza de datos antiguos configurable
- ✅ **Zoom, pan y navegación** sobre las gráficas (toolbar matplotlib)
- ✅ Registro de eventos críticos en BD separada

---

### **4. Sistema de Temas**
**Implementado en v2.0**
- ✅ 15 temas pre-configurados
- ✅ Cambio con un clic y reinicio automático
- ✅ Preview visual antes de aplicar
- ✅ Persistencia entre reinicios
- ✅ Todos los componentes usan colores del tema (sliders, scrollbars, radiobuttons)

---

### **5. Reinicio y Apagado**
**Implementado en v2.5**
- ✅ Botón Reiniciar con confirmación (aplica cambios de código)
- ✅ Botón Salir con opción de apagar el sistema
- ✅ Terminal de apagado (visualiza apagado.sh en vivo)

---

### **6. Actualizaciones del Sistema**
**Implementado en v2.5.1**
- ✅ Verificación al arranque en background (no bloquea la UI)
- ✅ Sistema de caché 12h (no repite apt update innecesariamente)
- ✅ Ventana dedicada con estado visual
- ✅ Instalación con terminal integrada en vivo
- ✅ Botón Buscar para forzar comprobación manual
- ✅ Refresco automático del estado tras instalar

---

### **7. Sistema de Logging Completo**
**Implementado en v2.5.1**
- ✅ Cobertura 100% en módulos core y UI
- ✅ Niveles diferenciados: DEBUG, INFO, WARNING, ERROR
- ✅ Rotación automática 2MB con backup
- ✅ Archivo fijo `data/logs/dashboard.log`

---

### **8. Lanzadores de Scripts**
**Implementado desde v1.0 — mejorado en v2.5.1**
- ✅ Scripts personalizados configurables en `settings.py`
- ✅ Terminal integrada que muestra el output en vivo
- ✅ Confirmación previa a ejecución
- ✅ Layout en grid configurable

---

### **9. Servicio de Limpieza Automática**
**Implementado en v2.6**
- ✅ `CleanupService` en `core/` — singleton, daemon thread
- ✅ Limpieza automática de CSV exportados (máx. 10)
- ✅ Limpieza automática de PNG exportados (máx. 10)
- ✅ Limpieza periódica de BD SQLite (registros >30 días, cada 24h)
- ✅ `force_cleanup()` para limpieza manual desde la UI
- ✅ Inyección de dependencias en `HistoryWindow`
- ✅ Botón "Limpiar Antiguos" delega en el servicio
- ✅ Red de seguridad por tamaño en `DataLogger` (>5MB → limpia a 7 días)

---

### **10. Notificaciones Visuales en el Menú**
**Implementado en v2.6**
- ✅ Badge en "Actualizaciones" con paquetes pendientes (naranja)
- ✅ Badge en "Monitor Servicios" con servicios fallidos (rojo)
- ✅ Badge en "Control Ventiladores" y "Monitor Placa" con temperatura (naranja >60°C, rojo >70°C)
- ✅ Badge en "Monitor Placa" con CPU (naranja >75%, rojo >90%)
- ✅ Badge en "Monitor Placa" con RAM (naranja >75%, rojo >90%)
- ✅ Badge en "Monitor Disco" con uso de disco (naranja >80%, rojo >90%)
- ✅ Texto dinámico en badge (valor real: temperatura en °C, porcentaje)
- ✅ Color de texto adaptativo (negro sobre amarillo, blanco sobre rojo)

---

### **11. Header Unificado y Mejoras UI**
**Implementado en v2.7**
- ✅ `make_window_header()` en `ui/styles.py` — componente reutilizable
- ✅ Header consistente en las 10 ventanas (título + status + botón ✕)
- ✅ Botón ✕ táctil (52×42px) apto para pantalla táctil DSI
- ✅ Status en tiempo real en el header: CPU/RAM/Temp en Monitor, Disco/NVMe en Disco, interfaz/velocidades en Red
- ✅ Stats label en línea propia para Servicios y Procesos (texto largo)
- ✅ Eliminados todos los botones "Cerrar" inferiores redundantes
- ✅ Separador decorativo bajo el header en todas las ventanas

---

### **12. Speedtest CLI Oficial de Ookla**
**Implementado en v2.7**
- ✅ Migrado de `speedtest-cli` a `speedtest` (CLI oficial de Ookla)
- ✅ Salida en JSON — más robusto que parsear texto
- ✅ Conversión correcta bytes/s → MB/s
- ✅ Timeout ampliado a 90s
- ✅ Captura de errores JSON y KeyError

---

## 🔄 En Evaluación

### **Monitor de Contenedores Docker**
**Prioridad**: Descartado — usuario no usa Docker  

---

### **Alertas Externas**
**Prioridad**: Baja  
**Complejidad**: Media

- Notificaciones por Telegram o webhook
- Alertas por temperatura alta sostenida, CPU, disco lleno, servicios caídos
- Configurable por umbral y duración

---

### **Monitor de GPU**
**Prioridad**: Muy baja (Raspberry Pi sin GPU dedicada)  
**Complejidad**: Media

---

## 🚀 Ideas Futuras (Backlog)

**Automatización**: cron visual, profiles de ventiladores por hora, auto-reinicio de servicios caídos

**Red avanzada**: monitor de dispositivos en red (nmap), Pi-hole stats, VPN panel

**Backup**: programar backups, estado con progreso, sincronización cloud

**Seguridad**: intentos de login fallidos, logs de seguridad, firewall status

**API REST**: endpoints para métricas, histórico y control de servicios

**UI**: grid de 2 columnas en ventanas de monitoreo (mejor aprovechamiento de 800×480)

---

## 🎯 Roadmap

### **v2.5.1** ✅ — 2026-02-20
- ✅ Logging completo en todos los módulos
- ✅ Ventana Actualizaciones con caché y terminal
- ✅ 8 gráficas en Histórico (Red, Disco, PWM añadidas)
- ✅ Zoom y navegación en gráficas
- ✅ Fix bug atexit en DataCollectionService
- ✅ Paso correcto de dependencias (update_monitor inyectado)

### **v2.6** ✅ — 2026-02-22
- ✅ Badges de notificación visual en menú principal (6 badges, 5 botones)
- ✅ CleanupService — limpieza automática background de CSV, PNG y BD
- ✅ Fan control: entries con placeholder en lugar de sliders
- ✅ Inyección de dependencias profesional (CleanupService → HistoryWindow)

### **v2.7** ✅ ACTUAL — 2026-02-22
- ✅ `make_window_header()` — header unificado y consistente en 10 ventanas
- ✅ Botón ✕ táctil (52×42px) en todas las ventanas
- ✅ Status en tiempo real en el header de cada ventana
- ✅ Migración a speedtest CLI oficial de Ookla (JSON, MB/s)
- ✅ Fix botón Cerrar duplicado en Monitor de Red
- ✅ Fix import `make_window_header` en ThemeSelector

### **v2.8** (Próximo)
- [ ] Grid de 2 columnas en ventanas de monitoreo (mejor uso del espacio 800×480)
- [ ] Mejoras UI adicionales

### **v3.0** (Futuro)
- [ ] Alertas externas (Telegram/webhook)
- [ ] API REST básica

---

## 📈 Cobertura actual

| Área | Estado |
|------|--------|
| Monitoreo básico (CPU, RAM, Temp, Disco, Red) | ✅ 100% |
| Control avanzado (Ventiladores, Procesos, Servicios) | ✅ 100% |
| Histórico y análisis | ✅ 100% |
| Actualizaciones del sistema | ✅ 100% |
| Logging y observabilidad | ✅ 100% |
| Notificaciones visuales internas | ✅ 100% |
| Consistencia visual UI | ✅ 100% |
| Alertas externas | ⏳ 0% |
| Automatización | ⏳ 0% |

---

**Versión actual**: v2.7 — **Última actualización**: 2026-02-22
````

## File: core/__init__.py
````python
"""
Paquete core con lógica de negocio
"""
from .fan_controller import FanController
from .system_monitor import SystemMonitor
from .network_monitor import NetworkMonitor
from .fan_auto_service import FanAutoService
from .disk_monitor import DiskMonitor
from .process_monitor import ProcessMonitor
from .service_monitor import ServiceMonitor
from .update_monitor import UpdateMonitor
from .cleanup_service import CleanupService

__all__ = [
    'FanController',
    'SystemMonitor',
    'NetworkMonitor',
    'FanAutoService',
    'DiskMonitor',
    'ProcessMonitor',
    'ServiceMonitor',
    'UpdateMonitor',
    'CleanupService',
]
````

## File: core/data_collection_service.py
````python
"""
Servicio de recolección automática de datos
"""
import threading
import time
from datetime import datetime
from core.data_logger import DataLogger
from utils.file_manager import FileManager

from utils.logger import get_logger

logger = get_logger(__name__)


class DataCollectionService:
    """Servicio que recolecta métricas cada X minutos"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """Implementa singleton thread-safe"""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, system_monitor, fan_controller, network_monitor,
                 disk_monitor, update_monitor, interval_minutes: int = 5):
        # Evitar re-inicialización del singleton
        if hasattr(self, '_initialized'):
            return

        self.system_monitor = system_monitor
        self.fan_controller = FileManager()
        self.network_monitor = network_monitor
        self.disk_monitor = disk_monitor
        self.update_monitor = update_monitor
        self.interval_minutes = interval_minutes

        self.logger = DataLogger()
        self.running = False
        self.thread = None


        self._initialized = True

        # ELIMINADO: atexit.register(self.stop)
        # El registro del cleanup se hace en main.py junto con fan_service.stop()
        # para evitar que se dispare durante os.execv() en el reinicio

    def start(self):
        """Inicia el servicio de recolección"""
        if self.running:
            logger.info("[DataCollection] Servicio ya está corriendo")
            return

        self.running = True
        self.thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.thread.start()
        logger.info(f"[DataCollection] Servicio iniciado (cada {self.interval_minutes} min)")

    def stop(self):
        """Detiene el servicio"""
        if not self.running:
            return

        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("[DataCollection] Servicio detenido")

    def _collection_loop(self):
        """Bucle principal de recolección"""
        while self.running:
            try:
                self._collect_and_save()
            except Exception as e:
                logger.error(f"[DataCollection] Error en recolección: {e}")
            time.sleep(self.interval_minutes * 60)

    def _collect_and_save(self):
        """Recolecta métricas y las guarda"""
        system_stats = self.system_monitor.get_current_stats()
        network_stats = self.network_monitor.get_current_stats()
        disk_stats = self.disk_monitor.get_current_stats()
        update_stats = self.update_monitor.check_updates()
        fan_state = self.fan_controller.load_state()

        metrics = {
            'cpu_percent': system_stats.get('cpu', 0),
            'ram_percent': system_stats.get('ram', 0),
            'ram_used_gb': "{:.2f}".format(system_stats.get('ram_used', 0) / (1024 ** 3)),
            'temperature': system_stats.get('temp', 0),
            'disk_used_percent': disk_stats.get('disk_usage', 0),
            'disk_read_mb': "{:.2f}".format(disk_stats.get('disk_read_mb', 0)),
            'disk_write_mb': "{:.2f}".format(disk_stats.get('disk_write_mb', 0)),
            'net_download_mb': "{:.2f}".format(network_stats.get('download_mb', 0)),
            'net_upload_mb': "{:.2f}".format(network_stats.get('upload_mb', 0)),
            'fan_pwm': fan_state.get('target_pwm', 0),
            'fan_mode': fan_state.get('mode', 'unknown'),
            'updates_available': update_stats.get('pending', 0),
        }

        self.logger.log_metrics(metrics)

        if metrics['temperature'] > 80:
            self.logger.log_event(
                'temp_high', 'critical',
                f"Temperatura alta detectada: {metrics['temperature']:.1f}°C",
                {'temperature': metrics['temperature']}
            )

        if metrics['cpu_percent'] > 90:
            self.logger.log_event(
                'cpu_high', 'warning',
                f"CPU alta detectada: {metrics['cpu_percent']:.1f}%",
                {'cpu': metrics['cpu_percent']}
            )

        logger.info(f"[DataCollection] Métricas guardadas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def force_collection(self):
        """Fuerza una recolección inmediata (útil para testing)"""
        self._collect_and_save()
````

## File: ui/windows/launchers.py
````python
"""
Ventana de lanzadores de scripts
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, LAUNCHERS
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import confirm_dialog, terminal_dialog
from utils.system_utils import SystemUtils
from utils.logger import get_logger

logger = get_logger(__name__)


class LaunchersWindow(ctk.CTkToplevel):
    """Ventana de lanzadores de scripts del sistema"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.system_utils = SystemUtils()
        
        self.title("Lanzadores")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        
        self._create_ui()
    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── Header unificado ──────────────────────────────────────────────────
        make_window_header(
            main,
            title="LANZADORES",
            on_close=self.destroy,
        )
        
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
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
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        self._create_launcher_buttons(inner)
        
    
    def _create_launcher_buttons(self, parent):
        """Crea los botones de lanzadores en layout grid"""
        if not LAUNCHERS:
            no_launchers = ctk.CTkLabel(
                parent,
                text="No hay lanzadores configurados\n\nEdita config/settings.py para añadir scripts",
                text_color=COLORS['warning'],
                font=(FONT_FAMILY, FONT_SIZES['medium']),
                justify="center"
            )
            no_launchers.pack(pady=50)
            return
        
        columns = 2
        
        for i, launcher in enumerate(LAUNCHERS):
            label = launcher.get("label", "Script")
            script_path = launcher.get("script", "")
            
            row = i // columns
            col = i % columns
            
            launcher_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
            launcher_frame.grid(row=row, column=col, sticky="nsew")
            
            btn = make_futuristic_button(
                launcher_frame,
                text=label,
                command=lambda s=script_path, l=label: self._run_script(s, l),
                width=40,
                height=15,
                font_size=FONT_SIZES['large']
            )
            btn.pack(pady=(10, 5), padx=10)
            
            path_label = ctk.CTkLabel(
                launcher_frame,
                text=script_path,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small']),
                wraplength=300
            )
            path_label.pack(pady=(0, 10), padx=10)
        
        for c in range(columns):
            parent.grid_columnconfigure(c, weight=1)
    
    def _run_script(self, script_path: str, label: str):
        """Ejecuta un script usando la terminal integrada tras confirmar"""

        def do_execute():
            logger.info(f"[LaunchersWindow] Ejecutando script: '{label}' → {script_path}")
            terminal_dialog(
                parent=self,
                script_path=script_path,
                title=f"EJECUTANDO: {label.upper()}"
            )

        confirm_dialog(
            parent=self,
            text=f"¿Deseas iniciar el proceso '{label}'?\n\nArchivo: {script_path}",
            title="⚠️ Lanzador de Sistema",
            on_confirm=do_execute
        )
````

## File: ui/windows/fan_control.py
````python
"""
Ventana de control de ventiladores
"""
import tkinter as tk
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, 
                             DSI_HEIGHT, DSI_X, DSI_Y)
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox
from core.fan_controller import FanController
from core.system_monitor import SystemMonitor
from utils.file_manager import FileManager


class FanControlWindow(ctk.CTkToplevel):
    """Ventana de control de ventiladores y curvas PWM"""
    
    def __init__(self, parent, fan_controller: FanController, 
                 system_monitor: SystemMonitor):
        super().__init__(parent)
        
        # Referencias
        self.fan_controller = fan_controller
        self.system_monitor = system_monitor
        self.file_manager = FileManager()
        
        # Variables de estado
        self.mode_var = tk.StringVar()
        self.manual_pwm_var = tk.IntVar(value=128)
        self.curve_vars = []

        # Variables para entries de nuevo punto (con placeholder)
        self._PLACEHOLDER_TEMP = "0-100"
        self._PLACEHOLDER_PWM  = "0-255"
        self.new_temp_var = tk.StringVar(value=self._PLACEHOLDER_TEMP)
        self.new_pwm_var  = tk.StringVar(value=self._PLACEHOLDER_PWM)
        
        # Cargar estado inicial
        self._load_initial_state()
        
        # Configurar ventana
        self.title("Control de Ventiladores")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.focus_force()
        self.lift()
        self.after(100, lambda: self.grab_set())
        
        # Crear interfaz
        self._create_ui()
        
        # Iniciar bucle de actualización del slider/valor
        self._update_pwm_display()
    
    def _load_initial_state(self):
        """Carga el estado inicial desde archivo"""
        state = self.file_manager.load_state()
        self.mode_var.set(state.get("mode", "auto"))
        
        target = state.get("target_pwm")
        if target is not None:
            self.manual_pwm_var.set(target)
    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        # Frame principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── Header unificado ──────────────────────────────────────────────────
        self._header = make_window_header(
            main,
            title="CONTROL DE VENTILADORES",
            on_close=self.destroy,
        )
        
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
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>", 
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Secciones
        self._create_mode_section(inner)
        self._create_manual_pwm_section(inner)
        self._create_curve_section(inner)
        self._create_bottom_buttons(main)
    
    def _create_mode_section(self, parent):
        """Crea la sección de selección de modo"""
        mode_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        mode_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(
            mode_frame,
            text="MODO DE OPERACIÓN",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        modes_container = ctk.CTkFrame(mode_frame, fg_color=COLORS['bg_medium'])
        modes_container.pack(fill="x", pady=5)
        
        modes = [
            ("Auto", "auto"),
            ("Silent", "silent"),
            ("Normal", "normal"),
            ("Performance", "performance"),
            ("Manual", "manual")
        ]
        
        for text, value in modes:
            rb = ctk.CTkRadioButton(
                modes_container,
                text=text,
                variable=self.mode_var,
                value=value,
                command=lambda v=value: self._on_mode_change(v),
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=8)
            StyleManager.style_radiobutton_ctk(rb)
    
    def _create_manual_pwm_section(self, parent):
        """Crea la sección de PWM manual"""
        manual_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        manual_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(
            manual_frame,
            text="PWM MANUAL (0-255)",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.pwm_value_label = ctk.CTkLabel(
            manual_frame,
            text=f"Valor: {self.manual_pwm_var.get()} ({int(self.manual_pwm_var.get()/255*100)}%)",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        self.pwm_value_label.pack(anchor="w", pady=(0, 10))
        
        slider = ctk.CTkSlider(
            manual_frame,
            from_=0,
            to=255,
            variable=self.manual_pwm_var,
            command=self._on_pwm_change,
            width=DSI_WIDTH - 100
        )
        slider.pack(fill="x", pady=5)
        StyleManager.style_slider_ctk(slider)
    
    def _create_curve_section(self, parent):
        """Crea la sección de curva temperatura-PWM"""
        curve_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        curve_frame.pack(fill="x", pady=5, padx=10)

        ctk.CTkLabel(
            curve_frame,
            text="CURVA TEMPERATURA-PWM",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        # Lista de puntos actuales
        self.points_frame = ctk.CTkFrame(curve_frame, fg_color=COLORS['bg_dark'])
        self.points_frame.pack(fill="x", pady=5, padx=5)
        self._refresh_curve_points()
        
        # Sección añadir punto con ENTRIES
        add_section = ctk.CTkFrame(curve_frame, fg_color=COLORS['bg_dark'])
        add_section.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(
            add_section,
            text="AÑADIR NUEVO PUNTO",
            text_color=COLORS['success'],
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
        ).pack(anchor="w", padx=5, pady=5)

        # Fila con los dos entries en línea
        entries_row = ctk.CTkFrame(add_section, fg_color=COLORS['bg_dark'])
        entries_row.pack(fill="x", padx=5, pady=5)

        # — Temperatura —
        temp_col = ctk.CTkFrame(entries_row, fg_color=COLORS['bg_dark'])
        temp_col.pack(side="top", padx=(0, 20))

        ctk.CTkLabel(
            temp_col,
            text="Temperatura (°C)",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(anchor="n")

        self._entry_temp = ctk.CTkEntry(
            temp_col,
            textvariable=self.new_temp_var,
            width=120,
            height=36,
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            text_color=COLORS['text_dim'],      # color placeholder
            fg_color=COLORS['bg_medium'],
            border_color=COLORS['primary']
        )
        self._entry_temp.pack(pady=4)
        self._entry_temp.bind("<FocusIn>",  lambda e: self._entry_focus_in(self._entry_temp, self.new_temp_var, self._PLACEHOLDER_TEMP))
        self._entry_temp.bind("<FocusOut>", lambda e: self._entry_focus_out(self._entry_temp, self.new_temp_var, self._PLACEHOLDER_TEMP))

        # — PWM —
        pwm_col = ctk.CTkFrame(entries_row, fg_color=COLORS['bg_dark'])
        pwm_col.pack(side="top", padx=(0, 20))

        ctk.CTkLabel(
            pwm_col,
            text="PWM (0-255)",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(anchor="n")

        self._entry_pwm = ctk.CTkEntry(
            pwm_col,
            textvariable=self.new_pwm_var,
            width=120,
            height=36,
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            text_color=COLORS['text_dim'],      # color placeholder
            fg_color=COLORS['bg_medium'],
            border_color=COLORS['primary']
        )
        self._entry_pwm.pack(pady=4)
        self._entry_pwm.bind("<FocusIn>",  lambda e: self._entry_focus_in(self._entry_pwm, self.new_pwm_var, self._PLACEHOLDER_PWM))
        self._entry_pwm.bind("<FocusOut>", lambda e: self._entry_focus_out(self._entry_pwm, self.new_pwm_var, self._PLACEHOLDER_PWM))

        # Botón añadir
        make_futuristic_button(
            add_section,
            text="✓ Añadir Punto a la Curva",
            command=self._add_curve_point_from_entries,
            width=25,
            height=6,
            font_size=16
        ).pack(pady=10)

    # ── Helpers de placeholder ──────────────────────────────────────────────

    def _entry_focus_in(self, entry: ctk.CTkEntry, var: tk.StringVar, placeholder: str):
        """Borra el placeholder al enfocar y cambia color a texto normal"""
        if var.get() == placeholder:
            var.set("")
            entry.configure(text_color=COLORS['text'])

    def _entry_focus_out(self, entry: ctk.CTkEntry, var: tk.StringVar, placeholder: str):
        """Restaura el placeholder si el campo queda vacío"""
        if var.get().strip() == "":
            var.set(placeholder)
            entry.configure(text_color=COLORS['text_dim'])

    # ── Lógica de añadir punto ──────────────────────────────────────────────

    def _add_curve_point_from_entries(self):
        """Valida los entries y añade el punto a la curva"""
        temp_raw = self.new_temp_var.get().strip()
        pwm_raw  = self.new_pwm_var.get().strip()

        # Validar que no son placeholders ni vacíos
        if temp_raw in ("", self._PLACEHOLDER_TEMP) or pwm_raw in ("", self._PLACEHOLDER_PWM):
            custom_msgbox(self, "Introduce un valor en ambos campos.", "Error")
            return

        try:
            temp = int(temp_raw)
            pwm  = int(pwm_raw)
        except ValueError:
            custom_msgbox(self, "Los valores deben ser números enteros.", "Error")
            return

        if not (0 <= temp <= 100):
            custom_msgbox(self, "La temperatura debe estar entre 0 y 100 °C.", "Error")
            return
        if not (0 <= pwm <= 255):
            custom_msgbox(self, "El PWM debe estar entre 0 y 255.", "Error")
            return

        # Añadir punto
        self.fan_controller.add_curve_point(temp, pwm)

        # Resetear entries a placeholder
        self.new_temp_var.set(self._PLACEHOLDER_TEMP)
        self.new_pwm_var.set(self._PLACEHOLDER_PWM)
        self._entry_temp.configure(text_color=COLORS['text_dim'])
        self._entry_pwm.configure(text_color=COLORS['text_dim'])

        # Refrescar lista y confirmar
        self._refresh_curve_points()
        custom_msgbox(self, f"✓ Punto añadido:\n{temp}°C → PWM {pwm}", "Éxito")

    # ── Curva ───────────────────────────────────────────────────────────────

    def _refresh_curve_points(self):
        """Refresca la lista de puntos de la curva"""
        for widget in self.points_frame.winfo_children():
            widget.destroy()
        
        curve = self.file_manager.load_curve()
        
        if not curve:
            ctk.CTkLabel(
                self.points_frame,
                text="No hay puntos en la curva",
                text_color=COLORS['warning'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            ).pack(pady=10)
            return
        
        for point in curve:
            temp = point['temp']
            pwm  = point['pwm']
            
            point_frame = ctk.CTkFrame(self.points_frame, fg_color=COLORS['bg_medium'])
            point_frame.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(
                point_frame,
                text=f"{temp}°C → PWM {pwm}",
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            ).pack(side="left", padx=10)
            
            make_futuristic_button(
                point_frame,
                text="Eliminar",
                command=lambda t=temp: self._remove_curve_point(t),
                width=10,
                height=3,
                font_size=12
            ).pack(side="right", padx=5)

    def _remove_curve_point(self, temp: int):
        """Elimina un punto de la curva"""
        self.fan_controller.remove_curve_point(temp)
        self._refresh_curve_points()

    # ── Botones inferiores ──────────────────────────────────────────────────

    def _create_bottom_buttons(self, parent):
        """Crea los botones inferiores"""
        bottom = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=10, padx=10)
        

        
        make_futuristic_button(
            bottom,
            text="Refrescar Curva",
            command=self._refresh_curve_points,
            width=15,
            height=6
        ).pack(side="left", padx=5)

    # ── Callbacks modo / PWM ────────────────────────────────────────────────

    def _on_mode_change(self, mode: str):
        """Callback cuando cambia el modo"""
        temp = self.system_monitor.get_current_stats()['temp']
        target_pwm = self.fan_controller.get_pwm_for_mode(
            mode=mode,
            temp=temp,
            manual_pwm=self.manual_pwm_var.get()
        )
        percent = int(target_pwm / 255 * 100)
        self.manual_pwm_var.set(target_pwm)
        self.pwm_value_label.configure(text=f"Valor: {target_pwm} ({percent}%)")
        self.file_manager.write_state({"mode": mode, "target_pwm": target_pwm})
    
    def _on_pwm_change(self, value):
        """Callback cuando cambia el PWM manual"""
        pwm = int(float(value))
        percent = int(pwm / 255 * 100)
        self.pwm_value_label.configure(text=f"Valor: {pwm} ({percent}%)")
        if self.mode_var.get() == "manual":
            self.file_manager.write_state({"mode": "manual", "target_pwm": pwm})
    
    def _update_pwm_display(self):
        """Actualiza el slider y valor para reflejar el PWM activo"""
        if not self.winfo_exists():
            return
        
        mode = self.mode_var.get()
        if mode != "manual":
            temp = self.system_monitor.get_current_stats()['temp']
            target_pwm = self.fan_controller.get_pwm_for_mode(
                mode=mode,
                temp=temp,
                manual_pwm=self.manual_pwm_var.get()
            )
            percent = int(target_pwm / 255 * 100)
            self.manual_pwm_var.set(target_pwm)
            self.pwm_value_label.configure(text=f"Valor: {target_pwm} ({percent}%)")
        
        self.after(2000, self._update_pwm_display)
````

## File: README.md
````markdown
# 🖥️ Sistema de Monitoreo y Control - Dashboard v2.7

Sistema completo de monitoreo y control para Raspberry Pi con interfaz gráfica DSI, control de ventiladores PWM, temas personalizables, histórico de datos, gestión avanzada del sistema, logging completo y UI táctil unificada.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)
[![Version](https://img.shields.io/badge/Version-2.7-orange.svg)]()

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
- **Tráfico en tiempo real**: Download/Upload con gráficas en MB/s
- **Auto-detección**: Interfaz activa (eth0, wlan0, tun0)
- **Lista de IPs**: Todas las interfaces con iconos por tipo
- **Speedtest integrado**: CLI oficial de Ookla, resultados en MB/s

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
- **8 gráficas**: CPU, RAM, Temperatura, Red ↓/↑, Disco R/W, PWM
- **Periodos**: 24 horas, 7 días, 30 días
- **Estadísticas**: Promedios, mínimos, máximos
- **Detección de anomalías**: Alertas automáticas
- **Exportación CSV**: Para análisis externo

### 󱇰 **Monitor USB**
- **Detección automática**: Dispositivos conectados
- **Separación inteligente**: Mouse/teclado vs almacenamiento
- **Expulsión segura**: Unmount + eject con confirmación

###  **Monitor de Disco**
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

### 🎨 **15 Temas Personalizables**
- **Cambio con un clic**: Reinicio automático
- **Paletas completas**: Cyberpunk, Matrix, Dracula, Nord, Tokyo Night, etc.
- **Preview en vivo**: Ve los colores antes de aplicar

### **Reinicio y Apagado**
- **Botón Reiniciar**: Reinicia el dashboard aplicando cambios de código
- **Botón Salir**: Salir de la app o apagar el sistema
- **Terminal de apagado**: Visualiza `apagado.sh` en tiempo real
- **Con confirmación**: Evita acciones accidentales

### 🔔 **Badges de Notificación Visual**
- **6 badges** en el menú principal con alertas en tiempo real
- **Temperatura**: naranja >60°C, rojo >70°C (Control Ventiladores + Monitor Placa)
- **CPU y RAM**: naranja >75%, rojo >90% (Monitor Placa)
- **Disco**: naranja >80%, rojo >90% (Monitor Disco)
- **Servicios fallidos**: rojo con contador (Monitor Servicios)
- **Actualizaciones pendientes**: naranja con contador (Actualizaciones)
- Texto dinámico: muestra el valor real (temperatura en °C, porcentaje)

### 🧹 **Limpieza Automática**
- **CleanupService**: servicio background singleton
- Limpia CSV exportados (máx. 10), PNG exportados (máx. 10)
- Limpia BD SQLite: registros >30 días cada 24h
- Red de seguridad: si BD supera 5MB limpia a 7 días al arrancar
- Botón "Limpiar Antiguos" fuerza limpieza manual completa

### 📋 **Sistema de Logging Completo**
- **Cobertura total**: Todos los módulos core y UI
- **Niveles diferenciados**: DEBUG, INFO, WARNING, ERROR
- **Rotación automática**: 2MB máximo con backup
- **Ubicación**: `data/logs/dashboard.log`

### 👆 **UI Táctil Unificada** *(nuevo en v2.7)*
- **Header consistente** en todas las ventanas: título + status en tiempo real + botón ✕
- **Botón ✕ táctil** (52×42px) optimizado para pantalla DSI 4,5"
- **Status dinámico** en el header: CPU/RAM/Temp, Disco/NVMe, interfaz/velocidades
- Sin botones "Cerrar" redundantes — un solo punto de cierre por ventana

---

## 📦 Instalación

###  **Requisitos del Sistema**
- **Hardware**: Raspberry Pi 3/4/5
- **OS**: Raspberry Pi OS (Bullseye/Bookworm) o Kali Linux
- **Pantalla**: Touchscreen DSI 4,5" (800x480) o HDMI
- **Python**: 3.8 o superior

### ⚡ **Instalación Recomendada**

```bash
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard
chmod +x install_system.sh
sudo ./install_system.sh
python3 main.py
```

El script `install_system.sh` instala automáticamente:
- Dependencias del sistema (`lm-sensors`, `usbutils`, `udisks2`, `smartmontools`)
- Dependencias Python con `--break-system-packages`
- Ofrece configurar sensores de temperatura

### 🛠️ **Instalación Manual**

```bash
# 1. Dependencias del sistema
sudo apt-get update
sudo apt-get install -y lm-sensors usbutils udisks2 smartmontools

# 2. Speedtest CLI oficial de Ookla
sudo apt install speedtest
speedtest --accept-license --accept-gdpr

# 3. Detectar sensores
sudo sensors-detect --auto

# 4. Dependencias Python
pip3 install --break-system-packages -r requirements.txt

# 5. Ejecutar
python3 main.py
```

###  **Alternativa con Entorno Virtual**

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
│   ├── network_monitor.py          # Red, speedtest CLI Ookla, interfaces
│   ├── disk_monitor.py             # Disco, NVMe, I/O
│   ├── process_monitor.py          # Gestión de procesos
│   ├── service_monitor.py          # Servicios systemd
│   ├── update_monitor.py           # Actualizaciones con caché 12h
│   ├── data_logger.py              # SQLite logging
│   ├── data_analyzer.py            # Análisis histórico
│   ├── data_collection_service.py  # Recolección automática (singleton)
│   ├── cleanup_service.py          # Limpieza automática background (singleton)
│   └── __init__.py
├── ui/
│   ├── main_window.py              # Ventana principal (13 botones + badges)
│   ├── styles.py                   # Estilos, botones y make_window_header()
│   ├── widgets/
│   │   ├── graphs.py               # Gráficas personalizadas
│   │   └── dialogs.py              # custom_msgbox, confirm_dialog, terminal_dialog
│   └── windows/
│       ├── monitor.py              # Monitor placa (CPU/RAM/Temp)
│       ├── network.py              # Monitor red + speedtest
│       ├── disk.py                 # Monitor disco + NVMe
│       ├── usb.py                  # Monitor USB
│       ├── process_window.py       # Monitor procesos
│       ├── service.py              # Monitor servicios systemd
│       ├── history.py              # Histórico de datos
│       ├── update.py               # Actualizaciones
│       ├── fan_control.py          # Control ventiladores
│       ├── launchers.py            # Lanzadores de scripts
│       ├── theme_selector.py       # Selector de temas
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
├── main.py
└── requirements.txt
```

---

##  Configuración

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
- **Threads background**: 4 (main + FanAuto + DataCollection + Cleanup)
- **Log**: máx. 2MB con rotación automática

---

##  Troubleshooting

| Problema | Solución |
|----------|----------|
| No arranca | `pip3 install --break-system-packages -r requirements.txt` |
| Temperatura 0 | `sudo sensors-detect --auto && sudo systemctl restart lm-sensors` |
| NVMe temp 0 | `sudo apt install smartmontools` |
| Ventiladores no responden | `sudo python3 main.py` |
| Speedtest falla (403) | `sudo apt remove speedtest-cli && sudo apt install speedtest` |
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
| Versión | 2.7 |
| Archivos Python | 41 |
| Líneas de código | ~12,500 |
| Ventanas | 13 |
| Temas | 15 |
| Servicios background | 3 (FanAuto + DataCollection + Cleanup) |
| Cobertura logging | 100% módulos core y UI |

---

## Changelog

### **v2.7** - 2026-02-22 ⭐ ACTUAL
- ✅ **NUEVO**: `make_window_header()` — header unificado y consistente en las 10 ventanas de monitoreo
- ✅ **NUEVO**: Botón ✕ táctil (52×42px) en todas las ventanas, optimizado para pantalla DSI
- ✅ **NUEVO**: Status en tiempo real en el header (CPU/RAM/Temp, Disco/NVMe, interfaz/velocidades)
- ✅ **NUEVO**: Speedtest migrado al CLI oficial de Ookla (JSON, MB/s correcto)
- ✅ **FIX**: Botón Cerrar duplicado eliminado en Monitor de Red
- ✅ **FIX**: Import `make_window_header` en ThemeSelector
- ✅ **FIX**: Stats label de Servicios y Procesos en línea propia (sin superposición)

### **v2.6** - 2026-02-22
- ✅ **NUEVO**: 6 badges de notificación visual en menú principal
- ✅ **NUEVO**: `CleanupService` — limpieza automática background de CSV, PNG y BD
- ✅ **NUEVO**: Fan control con entries (placeholder) en lugar de sliders
- ✅ **MEJORA**: Botón "Limpiar Antiguos" delega en CleanupService (inyección de dependencias)
- ✅ **MEJORA**: Badges con texto dinámico y color adaptativo

### **v2.5.1** - 2026-02-19
- ✅ **NUEVO**: Sistema de logging completo en todos los módulos core y UI
- ✅ **NUEVO**: Ventana Actualizaciones con terminal integrada y caché 12h
- ✅ **NUEVO**: Comprobación de actualizaciones al arranque en background
- ✅ **FIX**: Bug `atexit` en `DataCollectionService` (se detenía a los 3s del arranque)
- ✅ **MEJORA**: `update_monitor` con caché 12h y parámetro `force`

### **v2.5** - 2026-02-17
- ✅ Monitor de Servicios systemd, Histórico de Datos SQLite, Botón Reiniciar
- ✅ Recolección automática background, Exportación CSV, Detección de anomalías

### **v2.0** - 2026-02-16
- ✅ Monitor de Procesos, 15 temas

### **v1.0** - 2025-01
- ✅ Release inicial, 8 ventanas, control ventiladores, tema Cyberpunk

---

## Licencia

MIT License

---

## Agradecimientos

**CustomTkinter** · **psutil** · **matplotlib** · **Raspberry Pi Foundation**

---

**Dashboard v2.7: Profesional, Táctil, Completo y Auto-mantenido**
````

## File: ui/windows/history.py
````python
"""
Ventana de histórico de datos
"""
import customtkinter as ctk
from datetime import datetime, timedelta
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, DATA_DIR
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox , confirm_dialog
from core.data_analyzer import DataAnalyzer
from core.data_logger import DataLogger
from core.cleanup_service import CleanupService
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from utils.logger import get_logger
import os

logger = get_logger(__name__)

_DATE_FMT = "%Y-%m-%d %H:%M"


class HistoryWindow(ctk.CTkToplevel):
    """Ventana de visualización de histórico"""

    def __init__(self, parent, cleanup_service: CleanupService):
        super().__init__(parent)

        # Referencias
        self.analyzer         = DataAnalyzer()
        self.logger           = DataLogger()
        self.cleanup_service  = cleanup_service

        # Estado de periodo
        self.period_var = ctk.StringVar(value="24h")
        self.period_start = ctk.StringVar(value="YYYY-MM-DD HH:MM")
        self.period_end   = ctk.StringVar(value="YYYY-MM-DD HH:MM")

        # Estado de rango personalizado
        self._using_custom_range = False
        self._custom_start: datetime = None
        self._custom_end:   datetime = None

        # Configurar ventana
        self.title("Histórico de Datos")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        # Crear interfaz
        self._create_ui()

        # Cargar datos iniciales
        self._update_data()

    # ─────────────────────────────────────────────
    # Construcción de la UI
    # ─────────────────────────────────────────────

    def _create_ui(self):
        self._main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        self._main.pack(fill="both", expand=True, padx=5, pady=5) 
        # ── Header unificado ──────────────────────────────────────────────────
        self._header = make_window_header(
            self._main,
            title="HISTÓRICO DE DATOS",
            on_close=self.destroy,
        )
        # toolbar_container vive en el header para los botones de gráfica
        self.toolbar_container = ctk.CTkFrame(self._header, fg_color="transparent")
        self.toolbar_container.pack(side="left", padx=(10, 0))
        self._create_period_controls(self._main)
        self._create_range_panel(self._main)   # fila oculta de OptionMenus

        scroll_container = ctk.CTkFrame(self._main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas_tk = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
            height=DSI_HEIGHT - 300
        )
        canvas_tk.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas_tk.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")

        StyleManager.style_scrollbar_ctk(scrollbar)

        canvas_tk.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas_tk, fg_color=COLORS['bg_medium'])
        canvas_tk.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH - 50)
        inner.bind("<Configure>",
                   lambda e: canvas_tk.configure(scrollregion=canvas_tk.bbox("all")))

        self._create_graphs_area(inner)
        self._create_stats_area(inner)
        self._create_buttons(self._main)


    def _create_period_controls(self, parent):
        """Fila 1: radio buttons 24h/7d/30d + botón para abrir/cerrar el panel de rango."""
        self._controls_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        self._controls_frame.pack(fill="x", padx=10, pady=(5, 0))

        ctk.CTkLabel(
            self._controls_frame,
            text="Periodo:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        ).pack(side="left", padx=10)

        for period, label in [("24h", "24 horas"), ("7d", "7 días"), ("30d", "30 días")]:
            rb = ctk.CTkRadioButton(
                self._controls_frame,
                text=label,
                variable=self.period_var,
                value=period,
                command=self._on_period_radio,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=10)
            StyleManager.style_radiobutton_ctk(rb)

        # Botón toggle del panel de rango
        self._toggle_btn = make_futuristic_button(
            self._controls_frame,
            text="󰙹 Rango",
            command=self._toggle_range_panel,
            height=6,
            width=13
        )
        self._toggle_btn.pack(side="right", padx=10)

    def _create_range_panel(self, parent):
        """
        Fila 2 (oculta por defecto): selectores día/mes/año/hora/min
        para inicio y fin del rango. Sin teclado — todo por OptionMenu.
        """
        self._range_panel = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        # No se hace pack aquí → empieza oculto
        ctk.CTkLabel(
            self._range_panel,
            text="desde:",
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(10, 2))

        self.date_start = ctk.CTkEntry(
            self._range_panel,
            textvariable=self.period_start,
            text_color=COLORS['text_dim'],
            width=300,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        # Limpiar al hacer foco si tiene el texto de ejemplo
        self.date_start.bind("<FocusIn>",  lambda e: self._entry_focus_in(self.date_start, self.period_start))
        self.date_start.bind("<FocusOut>", lambda e: self._entry_focus_out(self.date_start, self.period_start))
        self.date_start.pack(side="left", padx=(0, 4))
                # Entradas de fecha en la fila de controles (derecha)
        ctk.CTkLabel(
            self._range_panel,
            text="hasta:",
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(0, 2))

        self.date_end = ctk.CTkEntry(
            self._range_panel,
            textvariable=self.period_end,
            text_color=COLORS['text_dim'],
            width=300,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        self.date_end.bind("<FocusIn>",  lambda e: self._entry_focus_in(self.date_end, self.period_end))
        self.date_end.bind("<FocusOut>", lambda e: self._entry_focus_out(self.date_end, self.period_end))
        self.date_end.pack(side="left", padx=(0, 4))


        # ── BOTÓN APLICAR ─────────────────────────────────────────
        self._apply_btn = make_futuristic_button(
            self._controls_frame,
            text="✓Aplicar",
            command=self._apply_custom_range,
            height=6,
            width=12,
            state="disabled"  # solo se habilita al abrir el panel, para evitar confusión
        )
        self._apply_btn.pack(side="right", padx=(10, 5))

    def _create_graphs_area(self, parent):
        graphs_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        graphs_frame.pack(fill="both", expand=True, padx=(0, 10), pady=(0, 10))

        self.fig = Figure(figsize=(9, 20), facecolor=COLORS['bg_medium'])
        self.fig.set_tight_layout(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=graphs_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=0)

        # Toolbar invisible — sus métodos se invocan desde botones propios
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.pack_forget()

        for text, cmd, w in [
            ("🏠 Inicio",  self.toolbar.home,          12),
            ("🔍 Zoom",    self.toolbar.zoom,           12),
            ("🖐️ Mover",  self.toolbar.pan,            12),
            (" Guardar",  self._export_figure_image,   12),
        ]:
            make_futuristic_button(
                self.toolbar_container, text=text, command=cmd, height=6, width=w
            ).pack(side="left", padx=5)

        self.canvas.mpl_connect('button_press_event',   self._on_click)
        self.canvas.mpl_connect('button_release_event', self._on_release)
        self.canvas.mpl_connect('motion_notify_event',  self._on_motion)

    def _create_stats_area(self, parent):
        stats_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        stats_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            stats_frame,
            text="Estadísticas:",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).pack(pady=(10, 5))

        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="Cargando...",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            justify="left"
        )
        self.stats_label.pack(pady=(0, 10), padx=20)

    def _create_buttons(self, parent):
        buttons = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        buttons.pack(fill="x", pady=10, padx=10)

        for text, cmd, side, w in [
            ("Actualizar",       self._update_data,    "left",  18),
            ("Exportar CSV",     self._export_csv,     "left",  18),
            ("Limpiar Antiguos", self._clean_old_data, "left",  18),
        ]:
            make_futuristic_button(
                buttons, text=text, command=cmd, width=w, height=6
            ).pack(side=side, padx=5)

    # ─────────────────────────────────────────────
    # Control del panel de rango
    # ─────────────────────────────────────────────

    def _toggle_range_panel(self):
        """Muestra u oculta la fila de OptionMenus de rango personalizado."""
        if self._range_panel.winfo_ismapped():
            self._range_panel.pack_forget()
            self._toggle_btn.configure(text="󰙹 Rango")
            self._apply_btn.configure(state="disabled")
        else:
            # Insertar después del frame de controles de periodo
            self._range_panel.pack(
                fill="x", padx=10, pady=(10, 5),
                after=self._controls_frame
            )
            self._toggle_btn.configure(text="✕ Cerrar")
            self._apply_btn.configure(state="normal")


    # ─────────────────────────────────────────────
    # Lógica de actualización
    # ─────────────────────────────────────────────

    _PLACEHOLDER = "YYYY-MM-DD HH:MM"

    def _entry_focus_in(self, entry: ctk.CTkEntry, var: ctk.StringVar):
        """Al enfocar: si tiene el texto de ejemplo, lo borra y pone color normal."""
        if var.get() == self._PLACEHOLDER:
            var.set("")
            entry.configure(text_color=COLORS['text'])

    def _entry_focus_out(self, entry: ctk.CTkEntry, var: ctk.StringVar):
        """Al perder foco: si quedó vacío, restaura el texto de ejemplo en gris."""
        if var.get().strip() == "":
            var.set(self._PLACEHOLDER)
            entry.configure(text_color=COLORS['text_dim'])

    def _on_period_radio(self):
        """Al pulsar radio button fijo: desactiva modo custom y actualiza."""
        self._using_custom_range = False
        self._update_data()

    def _apply_custom_range(self):
        """Lee los OptionMenus y aplica el rango sin necesidad de teclado."""
        _PH = self._PLACEHOLDER
        start_dt_text = self.period_start.get().strip()
        end_dt_text   = self.period_end.get().strip()
        if start_dt_text == _PH: start_dt_text = ""
        if end_dt_text   == _PH: end_dt_text   = ""
        try:
            start_dt = datetime.strptime(start_dt_text, _DATE_FMT)
        except ValueError as e:
            custom_msgbox(self, f"Fecha de inicio inválida:\n{e}", "❌ Error")
            return

        try:
            end_dt = datetime.strptime(end_dt_text, _DATE_FMT)
        except ValueError as e:
            custom_msgbox(self, f"Fecha de fin inválida:\n{e}", "❌ Error")
            return

        if end_dt <= start_dt:
            custom_msgbox(self, "La fecha de fin debe ser\nposterior a la de inicio.", "⚠️ Rango inválido")
            return

        if (end_dt - start_dt).days > 90:
            custom_msgbox(self, "El rango no puede superar 90 días.", "⚠️ Rango demasiado amplio")
            return

        self._using_custom_range = True
        self._custom_start = start_dt
        self._custom_end   = end_dt

        logger.info(
            f"[HistoryWindow] Rango aplicado: "
            f"{start_dt.strftime('%Y-%m-%d %H:%M')} → {end_dt.strftime('%Y-%m-%d %H:%M')}"
        )
        self._update_data()

    def _update_data(self):
        """Actualiza estadísticas y gráficas según el modo activo."""
        if self._using_custom_range:
            start = self._custom_start
            end   = self._custom_end
            stats = self.analyzer.get_stats_between(start, end)
            rango_label = f"{start.strftime('%Y-%m-%d %H:%M')} → {end.strftime('%Y-%m-%d %H:%M')}"
            hours = None  # no se usa en modo custom
        else:
            period = self.period_var.get()
            hours  = {"24h": 24, "7d": 24 * 7, "30d": 24 * 30}[period]
            stats  = self.analyzer.get_stats(hours)
            rango_label = period

        total_records = self.logger.get_metrics_count()
        db_size       = self.logger.get_db_size_mb()

        stats_text = (
            f"• CPU promedio: {stats.get('cpu_avg', 0):.1f}%  "
            f"(min: {stats.get('cpu_min', 0):.1f}%, max: {stats.get('cpu_max', 0):.1f}%)\n"
            f"• RAM promedio: {stats.get('ram_avg', 0):.1f}%  "
            f"(min: {stats.get('ram_min', 0):.1f}%, max: {stats.get('ram_max', 0):.1f}%)\n"
            f"• Temp promedio: {stats.get('temp_avg', 0):.1f}°C  "
            f"(min: {stats.get('temp_min', 0):.1f}°C, max: {stats.get('temp_max', 0):.1f}°C)\n"
            f"• Red Down: {stats.get('down_avg', 0):.2f} MB/s  "
            f"(min: {stats.get('down_min', 0):.2f}, max: {stats.get('down_max', 0):.2f})\n"
            f"• Red Up: {stats.get('up_avg', 0):.2f} MB/s  "
            f"(min: {stats.get('up_min', 0):.2f}, max: {stats.get('up_max', 0):.2f})\n"
            f"• Disk Read: {stats.get('disk_read_avg', 0):.2f} MB/s  "
            f"(min: {stats.get('disk_read_min', 0):.2f}, max: {stats.get('disk_read_max', 0):.2f})\n"
            f"• Disk Write: {stats.get('disk_write_avg', 0):.2f} MB/s  "
            f"(min: {stats.get('disk_write_min', 0):.2f}, max: {stats.get('disk_write_max', 0):.2f})\n"
            f"• PWM promedio: {stats.get('pwm_avg', 0):.0f}  "
            f"(min: {stats.get('pwm_min', 0):.0f}, max: {stats.get('pwm_max', 0):.0f})\n"
            f"• Actualizaciones disponibles promedio: {stats.get('updates_available_avg', 0):.2f}\n"
            f"• Actualizaciones disponibles (min: {stats.get('updates_available_min', 0)})\n"
            f"• Actualizaciones disponibles (max: {stats.get('updates_available_max', 0)})\n"
            f"• Muestras: {stats.get('total_samples', 0)} en {rango_label}\n"
            f"• Total registros: {total_records}  |  DB: {db_size:.2f} MB"
        )
        self.stats_label.configure(text=stats_text)

        if self._using_custom_range:
            self._update_graphs_between(self._custom_start, self._custom_end)
        else:
            self._update_graphs(hours)

    # ─────────────────────────────────────────────
    # Gráficas
    # ─────────────────────────────────────────────

    _METRICS = [
        ('cpu_percent',     'CPU %',           'primary'),
        ('ram_percent',     'RAM %',           'secondary'),
        ('temperature',     'Temp °C',         'danger'),
        ('net_download_mb', 'Red Down MB/s',   'primary'),
        ('net_upload_mb',   'Red Up MB/s',     'secondary'),
        ('disk_read_mb',    'Disk Read MB/s',  'primary'),
        ('disk_write_mb',   'Disk Write MB/s', 'secondary'),
        ('fan_pwm',         'PWM',             'warning'),
    ]

    def _update_graphs(self, hours: int):
        self.fig.clear()
        axes = [self.fig.add_subplot(8, 1, i) for i in range(1, 9)]
        for (metric, ylabel, color_key), ax in zip(self._METRICS, axes):
            ts, vals = self.analyzer.get_graph_data(metric, hours)
            self._draw_metric(ax, ts, vals, ylabel, COLORS[color_key])
        self.fig.tight_layout()
        self.canvas.draw()

    def _update_graphs_between(self, start: datetime, end: datetime):
        self.fig.clear()
        axes = [self.fig.add_subplot(8, 1, i) for i in range(1, 9)]
        for (metric, ylabel, color_key), ax in zip(self._METRICS, axes):
            ts, vals = self.analyzer.get_graph_data_between(metric, start, end)
            self._draw_metric(ax, ts, vals, ylabel, COLORS[color_key])
        self.fig.tight_layout()
        self.canvas.draw()

    def _draw_metric(self, ax, timestamps, values, ylabel: str, color: str):
        ax.set_facecolor(COLORS['bg_dark'])
        ax.tick_params(colors=COLORS['text'])
        ax.set_ylabel(ylabel, color=COLORS['text'])
        ax.set_xlabel('Tiempo', color=COLORS['text'])
        ax.grid(True, alpha=0.2)
        if timestamps:
            ax.plot(timestamps, values, color=color, linewidth=1.5)

    # ─────────────────────────────────────────────
    # Exportación
    # ─────────────────────────────────────────────

    def _export_csv(self):
        if self._using_custom_range:
            start = self._custom_start
            end   = self._custom_end
            label = f"custom_{start.strftime('%Y%m%d%H%M')}_{end.strftime('%Y%m%d%H%M')}"
            path  = f"{DATA_DIR}/history_{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            try:
                self.analyzer.export_to_csv_between(path, start, end)
                custom_msgbox(self, f"Datos exportados a:\n{path}", "✅ Exportado")
            except Exception as e:
                custom_msgbox(self, f"Error al exportar:\n{e}", "❌ Error")
        else:
            period = self.period_var.get()
            hours  = {"24h": 24, "7d": 24 * 7, "30d": 24 * 30}[period]
            path   = f"{DATA_DIR}/history_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            try:
                self.analyzer.export_to_csv(path, hours)
                custom_msgbox(self, f"Datos exportados a:\n{path}", "✅ Exportado")
            except Exception as e:
                custom_msgbox(self, f"Error al exportar:\n{e}", "❌ Error")

    def _clean_old_data(self):
        """Fuerza un ciclo de limpieza completo a través de CleanupService."""
        status = self.cleanup_service.get_status()

        def do_clean():
            try:
                result = self.cleanup_service.force_cleanup()
                msg = (
                    f"Limpieza completada:\n\n"
                    f"• CSV eliminados: {result['deleted_csv']}\n"
                    f"• PNG eliminados: {result['deleted_png']}\n"
                    f"• BD limpiada: {'Sí' if result['db_ok'] else 'No'}"
                )
                custom_msgbox(self, msg, "✅ Limpiado")
                logger.info(f"[HistoryWindow] Limpieza manual completada: {result}")
                self._update_data()
            except Exception as e:
                logger.error(f"[HistoryWindow] Error en limpieza manual: {e}")
                custom_msgbox(self, f"Error al limpiar:\n{e}", "❌ Error")

        confirm_dialog(
            parent=self,
            text=(
                f"¿Forzar limpieza ahora?\n\n"
                f"• CSV actuales: {status['csv_count']} (límite: {status['max_csv']})\n"
                f"• PNG actuales: {status['png_count']} (límite: {status['max_png']})\n"
                f"• BD: registros >'{status['db_days']}' días\n\n"
                f"Esto liberará espacio en disco."
            ),
            title="⚠️ Confirmar Limpieza",
            on_confirm=do_clean,
            on_cancel=None
        )

    def _export_figure_image(self):
        
        try:
            save_dir = os.path.join(os.getcwd(), "data/screenshots")
            os.makedirs(save_dir, exist_ok=True)
            filepath = os.path.join(
                save_dir,
                f"graficas_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.png"
            )
            self.fig.savefig(
                filepath, dpi=150,
                facecolor=self.fig.get_facecolor(),
                bbox_inches='tight'
            )
            logger.info(f"[HistoryWindow] Figura guardada: {filepath}")
            custom_msgbox(self, f"Imagen guardada en:\n\n{filepath}", "✅ Captura Guardada")
        except Exception as e:
            logger.error(f"[HistoryWindow] Error guardando imagen: {e}")
            custom_msgbox(self, f"Error al guardar la imagen: {e}", "❌ Error")

    # ─────────────────────────────────────────────
    # Eventos matplotlib
    # ─────────────────────────────────────────────

    def _on_click(self, event):
        if event.inaxes:
            logger.debug(f"Click en gráfica: x={event.xdata}, y={event.ydata}")

    def _on_release(self, event):
        pass

    def _on_motion(self, event):
        pass
````

## File: main.py
````python
#!/usr/bin/env python3
"""
Sistema de Monitoreo y Control
Punto de entrada principal
"""
import sys
import os
import atexit
import threading
import customtkinter as ctk
from config import DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from core import SystemMonitor, FanController, NetworkMonitor, FanAutoService, DiskMonitor, ProcessMonitor, ServiceMonitor, UpdateMonitor, CleanupService
from core.data_collection_service import DataCollectionService
from core.data_logger import DataLogger
from ui.main_window import MainWindow
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Función principal"""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    root = ctk.CTk()
    root.title("Sistema de Monitoreo")
    
    root.withdraw()
    root.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
    root.configure(bg="#111111")
    root.update_idletasks()
    root.overrideredirect(True)
    root.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
    root.update_idletasks()
    root.deiconify()
    root.lift()
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))
    
    # Inicializar monitores
    system_monitor = SystemMonitor()
    fan_controller = FanController()
    network_monitor = NetworkMonitor()
    disk_monitor = DiskMonitor()
    process_monitor = ProcessMonitor()
    service_monitor = ServiceMonitor()
    update_monitor = UpdateMonitor()

    # Comprobación inicial de actualizaciones en background
    # No bloquea el arranque y llena el caché para toda la sesión
    threading.Thread(
        target=lambda: update_monitor.check_updates(force=True),
        daemon=True,
        name="UpdateCheck-Startup"
    ).start()

    # Iniciar servicio de recolección de datos
    data_service = DataCollectionService(
        system_monitor=system_monitor,
        fan_controller=fan_controller,
        network_monitor=network_monitor,
        disk_monitor=disk_monitor,
        update_monitor=update_monitor,
        interval_minutes=5
    )
    data_service.start()
    
    # Iniciar servicio de limpieza automática
    cleanup_service = CleanupService(
        data_logger=DataLogger(),
        max_csv=10,
        max_png=10,
        db_days=30,
        interval_hours=24,
    )
    cleanup_service.start()

    # Iniciar servicio de ventiladores AUTO
    fan_service = FanAutoService(fan_controller, system_monitor)
    fan_service.start()
    
    # Cleanup centralizado — ambos servicios aquí, ninguno en atexit interno
    def cleanup():
        """Limpieza al cerrar la aplicación"""
        fan_service.stop()
        data_service.stop()
        cleanup_service.stop()
    
    atexit.register(cleanup)
    
    # Crear interfaz
    app = MainWindow(
        root,
        system_monitor=system_monitor,
        fan_controller=fan_controller,
        network_monitor=network_monitor,
        disk_monitor=disk_monitor,
        update_interval=UPDATE_MS,
        process_monitor=process_monitor,
        service_monitor=service_monitor,
        update_monitor=update_monitor,
        cleanup_service=cleanup_service
    )

    try:
        root.mainloop()
    finally:
        cleanup()


if __name__ == "__main__":
    main()
````

## File: ui/main_window.py
````python
"""
Ventana principal del sistema de monitoreo
"""
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_X, DSI_Y, SCRIPTS_DIR
from ui.styles import StyleManager, make_futuristic_button
from ui.windows import FanControlWindow, MonitorWindow, NetworkWindow, USBWindow, ProcessWindow, ServiceWindow, HistoryWindow, LaunchersWindow, ThemeSelector, DiskWindow, UpdatesWindow
from ui.widgets import confirm_dialog, terminal_dialog
from utils.system_utils import SystemUtils
from utils.logger import get_logger
import sys
import os
logger = get_logger(__name__)


class MainWindow:
    """Ventana principal del dashboard"""
    
    def __init__(self, root, system_monitor, fan_controller, network_monitor,
                 disk_monitor, process_monitor, service_monitor, update_monitor, cleanup_service,
                 update_interval=2000):
        self.root = root
        self.system_monitor = system_monitor
        self.fan_controller = fan_controller
        self.network_monitor = network_monitor
        self.disk_monitor = disk_monitor
        self.process_monitor = process_monitor
        self.service_monitor = service_monitor
        self.update_monitor = update_monitor
        self.cleanup_service = cleanup_service
        
        self.update_interval = update_interval
        self.system_utils = SystemUtils()
        
        # Referencias a badges (canvas item ids)
        self._badges = {}  # key -> (canvas, oval_id, text_id)

        # Referencias a ventanas secundarias
        self.fan_window = None
        self.monitor_window = None
        self.network_window = None
        self.usb_window = None
        self.launchers_window = None
        self.disk_window = None
        self.process_window = None
        self.service_window = None
        self.history_window = None
        self.update_window = None

        logger.info(f"[MainWindow] Dashboard iniciado en {self.system_utils.get_hostname()}")

        self._create_ui()
        self._start_update_loop()
    
    def _create_ui(self):
        """Crea la interfaz principal"""
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS['bg_medium'])
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        title = ctk.CTkLabel(
            main_frame,
            text="SISTEMA DE MONITOREO",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xxlarge'], "bold")
        )
        title.pack(pady=(20, 10))
        
        hostname = self.system_utils.get_hostname()
        info_label = ctk.CTkLabel(
            main_frame,
            text=f"Host: {hostname}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'])
        )
        info_label.pack(pady=5)
        
        menu_container = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_medium'])
        menu_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.menu_canvas = ctk.CTkCanvas(
            menu_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0
        )
        self.menu_canvas.pack(side="left", fill="both", expand=True)
        
        menu_scrollbar = ctk.CTkScrollbar(
            menu_container,
            orientation="vertical",
            command=self.menu_canvas.yview,
            width=30
        )
        menu_scrollbar.pack(side="right", fill="y")
        

        StyleManager.style_scrollbar_ctk(menu_scrollbar)
        
        self.menu_canvas.configure(yscrollcommand=menu_scrollbar.set)
        
        self.menu_inner = ctk.CTkFrame(self.menu_canvas, fg_color=COLORS['bg_medium'])
        self.menu_canvas.create_window(
            (0, 0),
            window=self.menu_inner,
            anchor="nw",
            width=DSI_WIDTH - 50
        )
        
        self.menu_inner.bind(
            "<Configure>",
            lambda e: self.menu_canvas.configure(
                scrollregion=self.menu_canvas.bbox("all")
            )
        )
        
        self._create_menu_buttons()
    
    def _create_menu_buttons(self):
        """Crea los botones del menú principal"""
        buttons_config = [
            ("󰈐  Control Ventiladores", self.open_fan_control,     ["temp_fan"]),
            ("󰚗  Monitor Placa",         self.open_monitor_window,  ["temp_monitor", "cpu", "ram"]),
            ("  Monitor Red",               self.open_network_window,  []),
            ("󱇰 Monitor USB",            self.open_usb_window,      []),
            ("  Monitor Disco",             self.open_disk_window,     ["disk"]),
            ("󱓞  Lanzadores",            self.open_launchers,       []),
            ("⚙️ Monitor Procesos",     self.open_process_window,  []),
            ("⚙️ Monitor Servicios",    self.open_service_window,  ["services"]),
            ("󱘿  Histórico Datos",       self.open_history_window,  []),
            ("󰆧  Actualizaciones",       self.open_update_window,   ["updates"]),
            ("󰔎  Cambiar Tema",          self.open_theme_selector,  []),
            ("  Reiniciar",                 self.restart_application,  []),
            ("󰿅  Salir",                 self.exit_application,     []),
        ]
        
        columns = 2
        
        for i, (text, command, badge_keys) in enumerate(buttons_config):
            row = i // columns
            col = i % columns
            
            btn = make_futuristic_button(
                self.menu_inner,
                text,
                command=command,
                font_size=FONT_SIZES['large'],
                width=30,
                height=15
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Múltiples badges por botón, colocados de derecha a izquierda
            for j, key in enumerate(badge_keys):
                self._create_badge(btn, key, offset_index=j)
        
        for c in range(columns):
            self.menu_inner.grid_columnconfigure(c, weight=1)

    # ── Badges ────────────────────────────────────────────────────────────────

    def _create_badge(self, btn, key, offset_index=0):
        """Crea un badge circular en la esquina superior-derecha del botón.
        offset_index separa horizontalmente múltiples badges en el mismo botón."""
        BADGE_SIZE = 36
        x_offset = -6 - offset_index * (BADGE_SIZE + 4)
        badge_canvas = tk.Canvas(
            btn,
            width=BADGE_SIZE,
            height=BADGE_SIZE,
            bg=COLORS['bg_dark'],
            highlightthickness=0,
            bd=0
        )
        badge_canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)

        oval = badge_canvas.create_oval(
            1, 1, BADGE_SIZE - 1, BADGE_SIZE - 1,
            fill=COLORS['danger'],
            outline=""
        )
        txt = badge_canvas.create_text(
            BADGE_SIZE // 2, BADGE_SIZE // 2,
            text="0",
            fill="white",
            font=(FONT_FAMILY, 13, "bold")
        )

        self._badges[key] = (badge_canvas, oval, txt, x_offset)
        badge_canvas.place_forget()

    # Umbrales de temperatura
    _TEMP_WARN = 60   # °C — badge naranja
    _TEMP_CRIT = 70   # °C — badge rojo

    # Umbrales CPU / RAM (%)
    _CPU_WARN  = 75
    _CPU_CRIT  = 90
    _RAM_WARN  = 75
    _RAM_CRIT  = 90

    # Umbrales disco (%)
    _DISK_WARN = 80
    _DISK_CRIT = 90

    def _update_badge(self, key, value, color=None):
        """Actualiza el valor y visibilidad de un badge."""
        if key not in self._badges:
            return
        canvas, oval, txt, x_offset = self._badges[key]
        if value > 0:
            display = str(value) if value < 100 else "99+"
            canvas.itemconfigure(txt, text=display)
            if color is None:
                color = COLORS['danger'] if key == "services" else COLORS.get('warning', '#ffaa00')
            canvas.itemconfigure(oval, fill=color)
            txt_color = "black" if color == COLORS.get('warning', '#ffaa00') else "white"
            canvas.itemconfigure(txt, fill=txt_color)
            canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)
        else:
            canvas.place_forget()
    
    # ── Apertura de ventanas ──────────────────────────────────────────────────

    def open_fan_control(self):
        """Abre la ventana de control de ventiladores"""
        if self.fan_window is None or not self.fan_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Control Ventiladores")
            self.fan_window = FanControlWindow(self.root, self.fan_controller, self.system_monitor)
        else:
            self.fan_window.lift()
    
    def open_monitor_window(self):
        """Abre la ventana de monitoreo del sistema"""
        if self.monitor_window is None or not self.monitor_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Placa")
            self.monitor_window = MonitorWindow(self.root, self.system_monitor)
        else:
            self.monitor_window.lift()
    
    def open_network_window(self):
        """Abre la ventana de monitoreo de red"""
        if self.network_window is None or not self.network_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Red")
            self.network_window = NetworkWindow(self.root, self.network_monitor)
        else:
            self.network_window.lift()
    
    def open_usb_window(self):
        """Abre la ventana de monitoreo USB"""
        if self.usb_window is None or not self.usb_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor USB")
            self.usb_window = USBWindow(self.root)
        else:
            self.usb_window.lift()
    
    def open_process_window(self):
        """Abre el monitor de procesos"""
        if self.process_window is None or not self.process_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Procesos")
            self.process_window = ProcessWindow(self.root, self.process_monitor)
        else:
            self.process_window.lift()
    
    def open_service_window(self):
        """Abre el monitor de servicios"""
        if self.service_window is None or not self.service_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Servicios")
            self.service_window = ServiceWindow(self.root, self.service_monitor)
        else:
            self.service_window.lift()
    
    def open_history_window(self):
        """Abre la ventana de histórico"""
        if self.history_window is None or not self.history_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Histórico Datos")
            self.history_window = HistoryWindow(self.root, self.cleanup_service)
        else:
            self.history_window.lift()
    
    def open_launchers(self):
        """Abre la ventana de lanzadores"""
        if self.launchers_window is None or not self.launchers_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Lanzadores")
            self.launchers_window = LaunchersWindow(self.root)
        else:
            self.launchers_window.lift()
    
    def open_theme_selector(self):
        """Abre el selector de temas"""
        logger.debug("[MainWindow] Abriendo: Cambiar Tema")
        theme_window = ThemeSelector(self.root)
        theme_window.lift()
    
    def open_disk_window(self):
        """Abre la ventana de monitor de disco"""
        if self.disk_window is None or not self.disk_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Disco")
            self.disk_window = DiskWindow(self.root, self.disk_monitor)
        else:
            self.disk_window.lift()
    
    def open_update_window(self):
        """Abre la ventana de actualizaciones"""
        if self.update_window is None or not self.update_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Actualizaciones")
            self.update_window = UpdatesWindow(self.root, self.update_monitor)
        else:
            self.update_window.lift()
    
    # ── Salir / Reiniciar ─────────────────────────────────────────────────────

    def exit_application(self):
        """Cierra la aplicación con opciones de salida o apagado"""
        selection_window = ctk.CTkToplevel(self.root)
        selection_window.title("Opciones de Salida")
        selection_window.configure(fg_color=COLORS['bg_medium'])
        selection_window.geometry("450x280")
        selection_window.resizable(False, False)
        selection_window.overrideredirect(True)
        
        selection_window.update_idletasks()
        x = DSI_X + (450 // 2) - 40
        y = DSI_Y + (280 // 2) - 40
        selection_window.geometry(f"450x280+{x}+{y}")
        
        selection_window.transient(self.root)
        selection_window.focus_force()
        selection_window.grab_set()
        
        main_frame = ctk.CTkFrame(selection_window, fg_color=COLORS['bg_medium'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="⚠️ ¿Qué deseas hacer?",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold")
        )
        title_label.pack(pady=(10, 20))
        
        selection_var = ctk.StringVar(value="exit")
        
        options_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_dark'])
        options_frame.pack(fill="x", pady=10, padx=20)
        
        exit_radio = ctk.CTkRadioButton(
            options_frame,
            text="  Salir de la aplicación",
            variable=selection_var,
            value="exit",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        exit_radio.pack(anchor="w", padx=20, pady=12)
        
        shutdown_radio = ctk.CTkRadioButton(
            options_frame,
            text="󰐥  Apagar el sistema",
            variable=selection_var,
            value="shutdown",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        shutdown_radio.pack(anchor="w", padx=20, pady=12)
        

        StyleManager.style_radiobutton_ctk(exit_radio)
        StyleManager.style_radiobutton_ctk(shutdown_radio)
        
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        def on_confirm():
            selected = selection_var.get()
            selection_window.destroy()
            
            if selected == "exit":
                def do_exit():
                    logger.info("[MainWindow] Cerrando dashboard por solicitud del usuario")
                    self.root.quit()
                    self.root.destroy()
                
                confirm_dialog(
                    parent=self.root,
                    text="¿Confirmar salir de la aplicación?",
                    title=" Confirmar Salida",
                    on_confirm=do_exit,
                    on_cancel=None
                )
            
            else:  # shutdown
                def do_shutdown():
                    logger.info("[MainWindow] Iniciando apagado del sistema")
                    shutdown_script = str(SCRIPTS_DIR / "apagado.sh")
                    terminal_dialog(
                        parent=self.root,
                        script_path=shutdown_script,
                        title="󰐥  APAGANDO SISTEMA..."
                    )
                
                confirm_dialog(
                    parent=self.root,
                    text="⚠️ ¿Confirmar APAGAR el sistema?\n\nEsta acción apagará completamente el equipo.",
                    title=" Confirmar Apagado",
                    on_confirm=do_shutdown,
                    on_cancel=None
                )
        
        def on_cancel():
            logger.debug("[MainWindow] Diálogo de salida cancelado")
            selection_window.destroy()
        
        confirm_btn = make_futuristic_button(
            buttons_frame,
            text="Continuar",
            command=on_confirm,
            width=18,
            height=6
        )
        confirm_btn.pack(side="right", padx=5)
        
        cancel_btn = make_futuristic_button(
            buttons_frame,
            text="Cancelar",
            command=on_cancel,
            width=18,
            height=6
        )
        cancel_btn.pack(side="right", padx=5)
        
        selection_window.bind("<Escape>", lambda e: on_cancel())
    
    def restart_application(self):
        """Reinicia la aplicación"""
        def do_restart():

            logger.info("[MainWindow] Reiniciando dashboard")
            self.root.quit()
            self.root.destroy()
            os.execv(sys.executable, [sys.executable, os.path.abspath(sys.argv[0])] + sys.argv[1:])
        
        confirm_dialog(
            parent=self.root,
            text="¿Reiniciar el dashboard?\n\nSe aplicarán los cambios realizados.",
            title=" Reiniciar Dashboard",
            on_confirm=do_restart,
            on_cancel=None
        )
    
    # ── Loop de actualización ─────────────────────────────────────────────────

    def _start_update_loop(self):
        """Inicia el bucle de actualización"""
        self._update()
    
    def _update(self):
        """Actualiza los datos del sistema y los badges"""
        try:
            pending = self.update_monitor.cached_result.get('pending', 0)
            self._update_badge("updates", pending)
        except Exception:
            pass

        try:
            stats = self.service_monitor.get_stats()
            failed = stats.get('failed', 0)
            self._update_badge("services", failed)
        except Exception:
            pass

        try:
            sys_stats = self.system_monitor.get_current_stats()

            # Temperatura
            temp = sys_stats['temp']
            if temp >= self._TEMP_CRIT:
                temp_color = COLORS['danger']
                show_temp = True
            elif temp >= self._TEMP_WARN:
                temp_color = COLORS.get('warning', '#ffaa00')
                show_temp = True
            else:
                show_temp = False
            if show_temp:
                self._update_badge_temp("temp_fan",     int(temp), temp_color)
                self._update_badge_temp("temp_monitor", int(temp), temp_color)
            else:
                self._update_badge("temp_fan",     0)
                self._update_badge("temp_monitor", 0)

            # CPU
            cpu = sys_stats['cpu']
            if cpu >= self._CPU_CRIT:
                self._update_badge("cpu", int(cpu), COLORS['danger'])
            elif cpu >= self._CPU_WARN:
                self._update_badge("cpu", int(cpu), COLORS.get('warning', '#ffaa00'))
            else:
                self._update_badge("cpu", 0)

            # RAM
            ram = sys_stats['ram']
            if ram >= self._RAM_CRIT:
                self._update_badge("ram", int(ram), COLORS['danger'])
            elif ram >= self._RAM_WARN:
                self._update_badge("ram", int(ram), COLORS.get('warning', '#ffaa00'))
            else:
                self._update_badge("ram", 0)

            # Disco
            disk = sys_stats['disk_usage']
            if disk >= self._DISK_CRIT:
                self._update_badge("disk", int(disk), COLORS['danger'])
            elif disk >= self._DISK_WARN:
                self._update_badge("disk", int(disk), COLORS.get('warning', '#ffaa00'))
            else:
                self._update_badge("disk", 0)

        except Exception:
            pass

        self.root.after(self.update_interval, self._update)

    def _update_badge_temp(self, key, temp, color):
        """Muestra la temperatura en el badge con el color indicado."""
        if key not in self._badges:
            return
        canvas, oval, txt, x_offset = self._badges[key]
        canvas.itemconfigure(txt, text=f"{temp}°")
        canvas.itemconfigure(oval, fill=color)
        txt_color = "black" if color == COLORS.get('warning', '#ffaa00') else "white"
        canvas.itemconfigure(txt, fill=txt_color)
        canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)
````
