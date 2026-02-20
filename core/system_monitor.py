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
