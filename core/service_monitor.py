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