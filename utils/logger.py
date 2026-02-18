"""
Sistema de logging centralizado
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

class DashboardLogger:
    """Logger centralizado para el dashboard"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        """Configura el logger"""
        # Crear directorio de logs
        log_dir = Path("data/logs")
        log_dir.mkdir(exist_ok=True)

        # Nombre del archivo con fecha
        log_file = log_dir / f"dashboard_{datetime.now().strftime('%Y%m%d')}.log"

        # Configurar formato
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler para archivo
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        # Handler para consola (solo WARNING y superior)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.WARNING)

        # Configurar root logger
        self.logger = logging.getLogger('Dashboard')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self, name: str):
        """Obtiene logger para un módulo"""
        return logging.getLogger(f'Dashboard.{name}')

# Singleton global
_dashboard_logger = DashboardLogger()

def get_logger(name: str):
    """
    Obtiene logger para un módulo

    Uso:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Mensaje")
    """
    return _dashboard_logger.get_logger(name)