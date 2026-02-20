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