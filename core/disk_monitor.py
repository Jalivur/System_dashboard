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
        from config.settings import COLORS
        
        if value >= crit:
            return COLORS['danger']
        elif value >= warn:
            return COLORS['warning']
        else:
            return COLORS['primary']