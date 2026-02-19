import subprocess
from typing import Dict

class UpdateMonitor:
    """Lógica para verificar actualizaciones del sistema"""
    
    def check_updates(self) -> Dict:
        """Verifica actualizaciones pendientes en sistemas Debian/Ubuntu"""
        try:
            # Actualizar lista de paquetes (Silencioso)
            subprocess.run(["sudo", "apt", "update"], capture_output=True, timeout=15)
            
            # Contar paquetes que se pueden actualizar
            cmd = "apt-get -s upgrade | grep '^Inst ' | wc -l"
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            count = int(output) if output else 0
            
            return {
                "pending": count,
                "status": "Ready" if count > 0 else "Updated",
                "message": f"{count} paquetes pendientes" if count > 0 else "Sistema al día"
            }
        except Exception as e:
            return {"pending": 0, "status": "Error", "message": str(e)}