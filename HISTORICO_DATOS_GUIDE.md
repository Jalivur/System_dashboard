# 📊 Guía Paso a Paso: Implementar Histórico de Datos

Esta guía te enseñará a crear un sistema completo de histórico de datos para guardar y visualizar métricas del sistema a lo largo del tiempo.

---

## 📋 Índice de Pasos

1. [Crear base de datos SQLite](#paso-1-crear-base-de-datos-sqlite)
2. [Crear DataLogger para guardar métricas](#paso-2-crear-datalogger)
3. [Crear DataAnalyzer para consultas](#paso-3-crear-dataanalyzer)
4. [Crear servicio de recolección automática](#paso-4-crear-servicio-de-recolección)
5. [Crear ventana de visualización](#paso-5-crear-ventana-de-visualización)
6. [Integrar en el menú principal](#paso-6-integrar-en-menú)
7. [Añadir exportación a CSV](#paso-7-exportación-a-csv)

---

## 🎯 Objetivo Final

Crear un sistema que:
- ✅ Guarde métricas cada 5 minutos automáticamente
- ✅ Almacene: CPU, RAM, Temperatura, Red, Disco, PWM
- ✅ Visualice gráficas de 24h, 7 días, 30 días
- ✅ Detecte patrones y anomalías
- ✅ Exporte a CSV
- ✅ Base de datos SQLite ligera

**Vista previa:**
```
┌────────────────────────────────────────────────┐
│          HISTÓRICO DE DATOS                    │
│  Periodo: ⦿ 24h  ○ 7 días  ○ 30 días         │
├────────────────────────────────────────────────┤
│  [Gráfica CPU %] ─────────────────────────    │
│                                                │
│  [Gráfica RAM %] ─────────────────────────    │
│                                                │
│  [Gráfica Temp °C] ───────────────────────    │
│                                                │
│  Estadísticas:                                │
│  • CPU promedio: 35.2%                        │
│  • RAM promedio: 45.8%                        │
│  • Temp máxima: 65°C                          │
│  • Datos almacenados: 8,640 registros        │
├────────────────────────────────────────────────┤
│  [Exportar CSV]  [Limpiar]  [Cerrar]          │
└────────────────────────────────────────────────┘
```

---

## Paso 1: Crear base de datos SQLite

### 1.1 Crear estructura de la base de datos

Crear archivo `core/data_logger.py`:

```python
"""
Sistema de logging de datos históricos
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


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
                fan_mode TEXT
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
                net_download_mb, net_upload_mb, fan_pwm, fan_mode
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            metrics.get('fan_mode')
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
    
    def clean_old_data(self, days: int = 90):
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
```

---

## Paso 2: Crear DataAnalyzer

Crear archivo `core/data_analyzer.py`:

```python
"""
Análisis de datos históricos
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class DataAnalyzer:
    """Analiza datos históricos de la base de datos"""
    
    def __init__(self, db_path: str = "data/history.db"):
        """
        Inicializa el analizador
        
        Args:
            db_path: Ruta a la base de datos
        """
        self.db_path = db_path
    
    def get_data_range(self, hours: int = 24) -> List[Dict]:
        """
        Obtiene datos de las últimas X horas
        
        Args:
            hours: Número de horas hacia atrás
            
        Returns:
            Lista de diccionarios con los datos
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para obtener dict
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT * FROM metrics
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        ''', (cutoff_time,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_stats(self, hours: int = 24) -> Dict:
        """
        Obtiene estadísticas de las últimas X horas
        
        Args:
            hours: Número de horas hacia atrás
            
        Returns:
            Diccionario con estadísticas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
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
                AVG(fan_pwm) as pwm_avg,
                COUNT(*) as total_samples
            FROM metrics
            WHERE timestamp >= ?
        ''', (cutoff_time,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
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
                'pwm_avg': round(row[9], 0) if row[9] else 0,
                'total_samples': row[10]
            }
        
        return {}
    
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
        
        # CPU muy alta de forma sostenida
        if stats.get('cpu_avg', 0) > 80:
            anomalies.append({
                'type': 'cpu_high',
                'severity': 'warning',
                'message': f"CPU promedio alta: {stats['cpu_avg']:.1f}%"
            })
        
        # Temperatura muy alta
        if stats.get('temp_max', 0) > 80:
            anomalies.append({
                'type': 'temp_high',
                'severity': 'critical',
                'message': f"Temperatura máxima: {stats['temp_max']:.1f}°C"
            })
        
        # RAM muy alta
        if stats.get('ram_avg', 0) > 85:
            anomalies.append({
                'type': 'ram_high',
                'severity': 'warning',
                'message': f"RAM promedio alta: {stats['ram_avg']:.1f}%"
            })
        
        return anomalies
    
    def get_graph_data(self, metric: str, hours: int = 24) -> Tuple[List, List]:
        """
        Obtiene datos para gráficas
        
        Args:
            metric: Métrica a obtener (cpu_percent, ram_percent, temperature, etc)
            hours: Número de horas hacia atrás
            
        Returns:
            Tupla (timestamps, values)
        """
        data = self.get_data_range(hours)
        
        timestamps = []
        values = []
        
        for entry in data:
            # Convertir timestamp string a datetime
            ts = datetime.fromisoformat(entry['timestamp'])
            timestamps.append(ts)
            values.append(entry.get(metric, 0))
        
        return timestamps, values
    
    def export_to_csv(self, output_path: str, hours: int = 24):
        """
        Exporta datos a CSV
        
        Args:
            output_path: Ruta del archivo CSV a crear
            hours: Número de horas a exportar
        """
        import csv
        
        data = self.get_data_range(hours)
        
        if not data:
            return
        
        with open(output_path, 'w', newline='') as csvfile:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in data:
                writer.writerow(row)
```

---

## Paso 3: Crear servicio de recolección

Crear archivo `core/data_collection_service.py`:

```python
"""
Servicio de recolección automática de datos
"""
import threading
import time
import atexit
from datetime import datetime
from core.data_logger import DataLogger


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
                 disk_monitor, interval_minutes: int = 5):
        """
        Inicializa el servicio
        
        Args:
            system_monitor: Instancia de SystemMonitor
            fan_controller: Instancia de FanController
            network_monitor: Instancia de NetworkMonitor
            disk_monitor: Instancia de DiskMonitor
            interval_minutes: Intervalo de recolección en minutos
        """
        # Evitar re-inicialización del singleton
        if hasattr(self, '_initialized'):
            return
        
        self.system_monitor = system_monitor
        self.fan_controller = fan_controller
        self.network_monitor = network_monitor
        self.disk_monitor = disk_monitor
        self.interval_minutes = interval_minutes
        
        self.logger = DataLogger()
        self.running = False
        self.thread = None
        
        self._initialized = True
        
        # Registrar cleanup al salir
        atexit.register(self.stop)
    
    def start(self):
        """Inicia el servicio de recolección"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.thread.start()
        print(f"[DataCollection] Servicio iniciado (cada {self.interval_minutes} min)")
    
    def stop(self):
        """Detiene el servicio"""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("[DataCollection] Servicio detenido")
    
    def _collection_loop(self):
        """Bucle principal de recolección"""
        while self.running:
            try:
                self._collect_and_save()
            except Exception as e:
                print(f"[DataCollection] Error: {e}")
            
            # Dormir por el intervalo especificado
            time.sleep(self.interval_minutes * 60)
    
    def _collect_and_save(self):
        """Recolecta métricas y las guarda"""
        # Obtener métricas de cada monitor
        system_stats = self.system_monitor.get_current_stats()
        network_stats = self.network_monitor.get_current_stats()
        disk_stats = self.disk_monitor.get_current_stats()
        
        # Obtener estado del ventilador
        fan_state = self.fan_controller.get_current_state()
        
        # Construir diccionario de métricas
        metrics = {
            'cpu_percent': system_stats.get('cpu', 0),
            'ram_percent': system_stats.get('ram_percent', 0),
            'ram_used_gb': system_stats.get('ram_used', 0) / 1024,  # MB a GB
            'temperature': system_stats.get('temp', 0),
            'disk_used_percent': disk_stats.get('percent', 0),
            'disk_read_mb': disk_stats.get('read_speed', 0),
            'disk_write_mb': disk_stats.get('write_speed', 0),
            'net_download_mb': network_stats.get('download', 0),
            'net_upload_mb': network_stats.get('upload', 0),
            'fan_pwm': fan_state.get('current_pwm', 0),
            'fan_mode': fan_state.get('mode', 'unknown')
        }
        
        # Guardar en base de datos
        self.logger.log_metrics(metrics)
        
        # Detectar y registrar eventos críticos
        if metrics['temperature'] > 80:
            self.logger.log_event(
                'temp_high',
                'critical',
                f"Temperatura alta detectada: {metrics['temperature']:.1f}°C",
                {'temperature': metrics['temperature']}
            )
        
        if metrics['cpu_percent'] > 90:
            self.logger.log_event(
                'cpu_high',
                'warning',
                f"CPU alta detectada: {metrics['cpu_percent']:.1f}%",
                {'cpu': metrics['cpu_percent']}
            )
        
        print(f"[DataCollection] Métricas guardadas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def force_collection(self):
        """Fuerza una recolección inmediata (útil para testing)"""
        self._collect_and_save()
```

---

## Paso 4: Crear ventana de visualización

Crear archivo `ui/windows/history.py`:

```python
"""
Ventana de histórico de datos
"""
import customtkinter as ctk
from datetime import datetime, timedelta
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
from ui.styles import make_futuristic_button
from ui.widgets import custom_msgbox
from core.data_analyzer import DataAnalyzer
from core.data_logger import DataLogger
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class HistoryWindow(ctk.CTkToplevel):
    """Ventana de visualización de histórico"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Referencias
        self.analyzer = DataAnalyzer()
        self.logger = DataLogger()
        
        # Estado
        self.period_var = ctk.StringVar(value="24h")
        
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
    
    def _create_ui(self):
        """Crea la interfaz"""
        # Frame principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Título
        self._create_header(main)
        
        # Controles de periodo
        self._create_period_controls(main)
        
        # Área de gráficas
        self._create_graphs_area(main)
        
        # Estadísticas
        self._create_stats_area(main)
        
        # Botones inferiores
        self._create_buttons(main)
    
    def _create_header(self, parent):
        """Crea el encabezado"""
        header = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        header.pack(fill="x", padx=10, pady=(10, 5))
        
        title = ctk.CTkLabel(
            header,
            text="HISTÓRICO DE DATOS",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold")
        )
        title.pack(pady=10)
    
    def _create_period_controls(self, parent):
        """Crea controles de periodo"""
        controls = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        controls.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            controls,
            text="Periodo:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        ).pack(side="left", padx=10)
        
        for period, label in [("24h", "24 horas"), ("7d", "7 días"), ("30d", "30 días")]:
            rb = ctk.CTkRadioButton(
                controls,
                text=label,
                variable=self.period_var,
                value=period,
                command=self._update_data,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=10)
            from ui.styles import StyleManager
            StyleManager.style_radiobutton_ctk(rb)
    
    def _create_graphs_area(self, parent):
        """Crea área de gráficas"""
        graphs_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        graphs_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Figura de matplotlib
        self.fig = Figure(figsize=(7, 5), facecolor=COLORS['bg_medium'])
        
        # Canvas para incrustar en tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=graphs_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _create_stats_area(self, parent):
        """Crea área de estadísticas"""
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
        """Crea botones inferiores"""
        buttons = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        buttons.pack(fill="x", pady=10, padx=10)
        
        export_btn = make_futuristic_button(
            buttons,
            text="Exportar CSV",
            command=self._export_csv,
            width=18,
            height=6
        )
        export_btn.pack(side="left", padx=5)
        
        clean_btn = make_futuristic_button(
            buttons,
            text="Limpiar Antiguos",
            command=self._clean_old_data,
            width=18,
            height=6
        )
        clean_btn.pack(side="left", padx=5)
        
        close_btn = make_futuristic_button(
            buttons,
            text="Cerrar",
            command=self.destroy,
            width=15,
            height=6
        )
        close_btn.pack(side="right", padx=5)
    
    def _update_data(self):
        """Actualiza datos y gráficas"""
        # Obtener horas según periodo
        period = self.period_var.get()
        if period == "24h":
            hours = 24
        elif period == "7d":
            hours = 24 * 7
        else:  # 30d
            hours = 24 * 30
        
        # Obtener estadísticas
        stats = self.analyzer.get_stats(hours)
        
        # Actualizar label de estadísticas
        total_records = self.logger.get_metrics_count()
        db_size = self.logger.get_db_size_mb()
        
        stats_text = f"""• CPU promedio: {stats.get('cpu_avg', 0):.1f}%  (min: {stats.get('cpu_min', 0):.1f}%, max: {stats.get('cpu_max', 0):.1f}%)
• RAM promedio: {stats.get('ram_avg', 0):.1f}%  (min: {stats.get('ram_min', 0):.1f}%, max: {stats.get('ram_max', 0):.1f}%)
• Temp promedio: {stats.get('temp_avg', 0):.1f}°C  (min: {stats.get('temp_min', 0):.1f}°C, max: {stats.get('temp_max', 0):.1f}°C)
• PWM promedio: {stats.get('pwm_avg', 0):.0f}
• Muestras: {stats.get('total_samples', 0)} en {period}
• Total registros: {total_records}  |  DB: {db_size:.2f} MB"""
        
        self.stats_label.configure(text=stats_text)
        
        # Actualizar gráficas
        self._update_graphs(hours)
    
    def _update_graphs(self, hours: int):
        """Actualiza las gráficas"""
        # Limpiar figura
        self.fig.clear()
        
        # Crear 3 subplots
        ax1 = self.fig.add_subplot(3, 1, 1)
        ax2 = self.fig.add_subplot(3, 1, 2)
        ax3 = self.fig.add_subplot(3, 1, 3)
        
        # Obtener datos
        ts_cpu, vals_cpu = self.analyzer.get_graph_data('cpu_percent', hours)
        ts_ram, vals_ram = self.analyzer.get_graph_data('ram_percent', hours)
        ts_temp, vals_temp = self.analyzer.get_graph_data('temperature', hours)
        
        # Gráfica CPU
        if ts_cpu:
            ax1.plot(ts_cpu, vals_cpu, color=COLORS['primary'], linewidth=1.5)
            ax1.set_ylabel('CPU %', color=COLORS['text'])
            ax1.set_facecolor(COLORS['bg_dark'])
            ax1.tick_params(colors=COLORS['text'])
            ax1.grid(True, alpha=0.2)
        
        # Gráfica RAM
        if ts_ram:
            ax2.plot(ts_ram, vals_ram, color=COLORS['success'], linewidth=1.5)
            ax2.set_ylabel('RAM %', color=COLORS['text'])
            ax2.set_facecolor(COLORS['bg_dark'])
            ax2.tick_params(colors=COLORS['text'])
            ax2.grid(True, alpha=0.2)
        
        # Gráfica Temperatura
        if ts_temp:
            ax3.plot(ts_temp, vals_temp, color=COLORS['danger'], linewidth=1.5)
            ax3.set_ylabel('Temp °C', color=COLORS['text'])
            ax3.set_xlabel('Tiempo', color=COLORS['text'])
            ax3.set_facecolor(COLORS['bg_dark'])
            ax3.tick_params(colors=COLORS['text'])
            ax3.grid(True, alpha=0.2)
        
        # Ajustar layout
        self.fig.tight_layout()
        
        # Redibujar
        self.canvas.draw()
    
    def _export_csv(self):
        """Exporta datos a CSV"""
        period = self.period_var.get()
        hours = 24 if period == "24h" else (24 * 7 if period == "7d" else 24 * 30)
        
        output_path = f"/mnt/user-data/outputs/history_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            self.analyzer.export_to_csv(output_path, hours)
            custom_msgbox(self, f"Datos exportados a:\n{output_path}", "✅ Exportado")
        except Exception as e:
            custom_msgbox(self, f"Error al exportar:\n{str(e)}", "❌ Error")
    
    def _clean_old_data(self):
        """Limpia datos antiguos"""
        from ui.widgets import confirm_dialog
        
        def do_clean():
            try:
                self.logger.clean_old_data(days=90)
                custom_msgbox(self, "Datos antiguos eliminados\n(mayores a 90 días)", "✅ Limpiado")
                self._update_data()
            except Exception as e:
                custom_msgbox(self, f"Error al limpiar:\n{str(e)}", "❌ Error")
        
        confirm_dialog(
            parent=self,
            text="¿Eliminar datos mayores a 90 días?\n\nEsto liberará espacio en disco.",
            title="⚠️ Confirmar",
            on_confirm=do_clean,
            on_cancel=None
        )
```

---

## Paso 5: Integrar en main.py

### 5.1 Actualizar imports en `main.py`:

```python
from core import (SystemMonitor, FanController, NetworkMonitor, 
                  FanAutoService, DiskMonitor, ProcessMonitor)
from core.data_collection_service import DataCollectionService  # ← NUEVO
```

### 5.2 Iniciar servicio después de crear monitores:

```python
# ... después de crear todos los monitores ...

# Iniciar servicio de recolección de datos (cada 5 minutos)
data_service = DataCollectionService(
    system_monitor=system_monitor,
    fan_controller=fan_controller,
    network_monitor=network_monitor,
    disk_monitor=disk_monitor,
    interval_minutes=5  # Recolectar cada 5 minutos
)
data_service.start()
```

---

## Paso 6: Añadir botón al menú

### 6.1 Actualizar `ui/main_window.py`:

**En `__init__` añadir:**
```python
self.history_window = None
```

**En `buttons_config` añadir:**
```python
("Histórico Datos", self.open_history_window),
```

**Añadir método:**
```python
def open_history_window(self):
    """Abre la ventana de histórico"""
    if self.history_window is None or not self.history_window.winfo_exists():
        from ui.windows.history import HistoryWindow
        self.history_window = HistoryWindow(self.root)
    else:
        self.history_window.lift()
```

---

## Paso 7: Probar el sistema

### 7.1 Ejecutar dashboard

```bash
python3 main.py
```

### 7.2 Verificar que se crean datos

```bash
# Ver base de datos
ls -lh data/history.db

# Consultar registros
sqlite3 data/history.db "SELECT COUNT(*) FROM metrics;"

# Ver últimos 5 registros
sqlite3 data/history.db "SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 5;"
```

### 7.3 Forzar recolección (testing)

Añadir en `main.py` después de iniciar el servicio:

```python
# Testing: Forzar primera recolección
data_service.force_collection()
```

---

## 📊 Funcionalidades Implementadas

✅ **Base de datos SQLite** - Ligera y eficiente  
✅ **Recolección automática** - Cada 5 minutos en background  
✅ **Métricas guardadas**: CPU, RAM, Temp, Disco, Red, PWM  
✅ **Visualización gráfica** - 3 gráficas (CPU, RAM, Temp)  
✅ **Periodos**: 24h, 7 días, 30 días  
✅ **Estadísticas** - Promedios, min, max  
✅ **Detección de anomalías** - Alertas automáticas  
✅ **Exportación CSV** - Para análisis externo  
✅ **Limpieza automática** - Elimina datos >90 días  

---

## 🔧 Personalización

### **Cambiar intervalo de recolección:**
```python
# En main.py
data_service = DataCollectionService(
    ...,
    interval_minutes=10  # Cada 10 minutos
)
```

### **Añadir más métricas:**
Editar `DataCollectionService._collect_and_save()` y añadir campos a la tabla `metrics`.

### **Cambiar retención de datos:**
```python
# En HistoryWindow._clean_old_data()
self.logger.clean_old_data(days=30)  # Mantener solo 30 días
```

---

## 🎯 Resultado Final

Un sistema completo de histórico que:
- 📊 Recolecta datos automáticamente
- 💾 Los almacena en SQLite
- 📈 Los visualiza en gráficas
- 📉 Detecta anomalías
- 📤 Exporta a CSV
- 🧹 Limpia datos antiguos

---

**¡Sistema de histórico completo implementado!** 📊✨
