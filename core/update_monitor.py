import subprocess
import time
from typing import Dict
from utils.logger import get_logger

logger = get_logger(__name__)

class UpdateMonitor:
    def __init__(self):
        self.last_check_time = 0
        self.cached_result = {"pending": 0, "status": "Unknown", "message": "No comprobado"}
        self.check_interval = 43200  # 12 horas en segundos

    def check_updates(self, force=False) -> Dict:
        """Verifica actualizaciones con sistema de caché"""
        current_time = time.time()
        
        # Si no se fuerza y no ha pasado el tiempo, devolvemos el caché
        if not force and (current_time - self.last_check_time) < self.check_interval:
            return self.cached_result

        try:
            logger.info("[UpdateMonitor] Ejecutando búsqueda real de actualizaciones (apt update)...")
            result = subprocess.run(["sudo", "apt", "update"], capture_output=True, timeout=20)
            
            # Contar paquetes
            cmd = "apt-get -s upgrade | grep '^Inst ' | wc -l"
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            count = int(output) if output else 0

            self.cached_result = {
                "pending": count,
                "status": "Ready" if count > 0 else "Updated",
                "message": f"{count} paquetes pendientes" if count > 0 else "Sistema al día"
            }
            self.last_check_time = current_time
            return self.cached_result

        except Exception as e:
            logger.error(f"[UpdateMonitor] Error en check_updates: {e}")
            return self.cached_result