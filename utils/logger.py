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