#!/usr/bin/env python3
"""
Sistema de Monitoreo y Control
Punto de entrada principal
"""
import sys
import os
import atexit
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from config.settings import DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from core import SystemMonitor, FanController, NetworkMonitor, FanAutoService, DiskMonitor, ProcessMonitor, ServiceMonitor, UpdateMonitor
from core.data_collection_service import DataCollectionService
from ui.main_window import MainWindow


def main():
    """Función principal"""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    root = ctk.CTk()
    root.title("Sistema de Monitoreo")
    
    root.withdraw()
    root.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
    root.configure(bg="#111111")
    root.update_idletasks()
    root.overrideredirect(True)
    root.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
    root.update_idletasks()
    root.deiconify()
    root.lift()
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))
    
    # Inicializar monitores
    system_monitor = SystemMonitor()
    fan_controller = FanController()
    network_monitor = NetworkMonitor()
    disk_monitor = DiskMonitor()
    process_monitor = ProcessMonitor()
    service_monitor = ServiceMonitor()
    update_monitor = UpdateMonitor()

    # Comprobación inicial de actualizaciones en background
    # No bloquea el arranque y llena el caché para toda la sesión
    threading.Thread(
        target=lambda: update_monitor.check_updates(force=True),
        daemon=True,
        name="UpdateCheck-Startup"
    ).start()

    # Iniciar servicio de recolección de datos
    data_service = DataCollectionService(
        system_monitor=system_monitor,
        fan_controller=fan_controller,
        network_monitor=network_monitor,
        disk_monitor=disk_monitor,
        update_monitor=update_monitor,
        interval_minutes=5
    )
    data_service.start()
    
    # Iniciar servicio de ventiladores AUTO
    fan_service = FanAutoService(fan_controller, system_monitor)
    fan_service.start()
    
    # Cleanup centralizado — ambos servicios aquí, ninguno en atexit interno
    def cleanup():
        """Limpieza al cerrar la aplicación"""
        fan_service.stop()
        data_service.stop()
    
    atexit.register(cleanup)
    
    # Crear interfaz
    app = MainWindow(
        root,
        system_monitor=system_monitor,
        fan_controller=fan_controller,
        network_monitor=network_monitor,
        disk_monitor=disk_monitor,
        update_interval=UPDATE_MS,
        process_monitor=process_monitor,
        service_monitor=service_monitor,
        update_monitor=update_monitor
    )

    try:
        root.mainloop()
    finally:
        cleanup()


if __name__ == "__main__":
    main()
