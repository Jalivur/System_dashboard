"""
Paquete de ventanas secundarias
"""
from .fan_control import FanControlWindow
from .monitor import MonitorWindow
from .network import NetworkWindow
from .usb import USBWindow
from .launchers import LaunchersWindow
from .disk import DiskWindow
from .process_window import ProcessWindow

__all__ = [
    'FanControlWindow',
    'MonitorWindow', 
    'NetworkWindow',
    'USBWindow',
    'LaunchersWindow',
    'DiskWindow',
    'ProcessWindow',
]
