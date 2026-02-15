"""
Utilidades para obtener información del sistema
"""
import re
import socket
import psutil
import subprocess
from typing import Tuple, Dict, Optional, Any


class SystemUtils:
    """Utilidades para interactuar con el sistema"""
    
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
            # Formato: temp=45.0'C
            temp_str = out.replace("temp=", "").replace("'C", "").strip()
            return float(temp_str)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, 
                FileNotFoundError, ValueError):
            pass
        
        # Método 2: sensors (Linux genérico)
        try:
            out = subprocess.check_output(["sensors"], universal_newlines=True, timeout=2)
            for line in out.split('\n'):
                if 'Package id 0:' in line or 'Tdie:' in line or 'CPU:' in line:
                    m = re.search(r'[\+\-](\d+\.\d+).C', line)
                    if m:
                        return float(m.group(1))
                        
            # Intentar CPU temp genérico
            for line in out.split('\n'):
                if 'temp' in line.lower():
                    m = re.search(r'[\+\-](\d+\.\d+).C', line)
                    if m:
                        return float(m.group(1))
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Método 3: Fallback - leer de thermal_zone
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                val = f.read().strip()
                return float(val) / 1000.0
        except (FileNotFoundError, ValueError):
            pass
        
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
        except Exception:
            return "unknown"
    
    @staticmethod
    def get_net_io(interface: Optional[str] = None) -> Tuple[str, Any]:
        """
        Obtiene estadísticas de red
        
        Args:
            interface: Nombre de la interfaz o None para auto-detección
            
        Returns:
            Tupla (nombre_interfaz, estadísticas)
        """
        net = psutil.net_io_counters(pernic=True)
        
        if interface and interface in net:
            return interface, net[interface]
        
        # Auto-detectar interfaz activa
        for iface, stats in net.items():
            if iface.startswith(('eth', 'enp', 'wlan', 'wlp')):
                if stats.bytes_sent > 0 or stats.bytes_recv > 0:
                    return iface, stats
        
        # Fallback a la primera disponible
        if net:
            first = list(net.items())[0]
            return first[0], first[1]
        
        # Crear stats vacío si no hay interfaces
        from collections import namedtuple
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
            
            # Convertir a MB/s (asumiendo UPDATE_MS = 2000ms)
            from config.settings import UPDATE_MS
            seconds = UPDATE_MS / 1000.0
            
            dl_mb = (dl_bytes / (1024 * 1024)) / seconds
            ul_mb = (ul_bytes / (1024 * 1024)) / seconds
            
            return dl_mb, ul_mb
        except (AttributeError, TypeError):
            return 0.0, 0.0
    
    @staticmethod
    def list_usb_storage_devices() -> list:
        """
        Lista dispositivos USB de almacenamiento (discos)
        
        Returns:
            Lista de diccionarios con información de almacenamiento USB:
            [
                {
                    'name': 'SanDisk Ultra',
                    'type': 'disk',
                    'mount': None,
                    'dev': '/dev/sda',
                    'size': '32G',
                    'children': [
                        {
                            'name': 'sda1',
                            'type': 'part',
                            'mount': '/media/usb',
                            'dev': '/dev/sda1',
                            'size': '32G'
                        }
                    ]
                }
            ]
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
                import json
                data = json.loads(result.stdout)
                
                for block in data.get('blockdevices', []):
                    # Solo dispositivos USB
                    if block.get('tran') == 'usb':
                        dev = {
                            'name': block.get('model', 'USB Disk').strip(),
                            'type': block.get('type', 'disk'),
                            'mount': block.get('mountpoint'),
                            'dev': '/dev/' + block.get('name', ''),
                            'size': block.get('size', ''),
                            'children': []
                        }
                        
                        # Procesar particiones hijas
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
        
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
        
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
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
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
        try:
            # Desmontar todas las particiones montadas
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
                    else:
                        return (False, f"Error desmontando {partition['name']}: {result.stderr}")
            
            if unmounted:
                return (True, f"Desmontado correctamente: {', '.join(unmounted)}")
            else:
                return (True, "No había particiones montadas")
        
        except subprocess.TimeoutExpired:
            return (False, "Timeout al desmontar el dispositivo")
        except FileNotFoundError:
            return (False, "udisksctl no encontrado. Instala: sudo apt-get install udisks2")
        except Exception as e:
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
                return True, f"Script ejecutado exitosamente"
            else:
                return False, f"Error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Timeout: El script tardó demasiado"
        except FileNotFoundError:
            return False, f"Script no encontrado: {script_path}"
        except Exception as e:
            return False, f"Error: {str(e)}"
