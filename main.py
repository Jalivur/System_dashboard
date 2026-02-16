#!/usr/bin/env python3
"""
Sistema de Monitoreo y Control
Punto de entrada principal
"""
import sys
import os
import atexit

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from config.settings import DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from core import SystemMonitor, FanController, NetworkMonitor, FanAutoService, DiskMonitor, ProcessMonitor
from ui.main_window import MainWindow


def main():
    """Función principal"""
    # Configurar modo de apariencia
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    # Crear ventana principal
    root = ctk.CTk()
    root.title("Sistema de Monitoreo")
    
    # IMPORTANTE: Configurar posición ANTES de mostrar
    root.withdraw()  # Ocultar temporalmente
    
    # Configurar geometría
    root.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
    root.configure(bg="#111111")
    
    # Forzar procesamiento de geometría
    root.update_idletasks()
    
    # Sin bordes
    root.overrideredirect(True)
    
    # Reconfirmar posición después de overrideredirect
    root.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
    
    # Procesar cambios
    root.update_idletasks()
    
    # Mostrar ventana en posición correcta
    root.deiconify()
    
    # Asegurar que está en primer plano
    root.lift()
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))
    
    # Inicializar monitores
    system_monitor = SystemMonitor()
    fan_controller = FanController()
    network_monitor = NetworkMonitor()
    disk_monitor = DiskMonitor()
    process_monitor = ProcessMonitor()
    
    # Iniciar servicio de ventiladores AUTO (background)
    fan_service = FanAutoService(fan_controller, system_monitor)
    fan_service.start()
    
    # Asegurar que el servicio se detiene al cerrar
    def cleanup():
        """Limpieza al cerrar la aplicación"""
        fan_service.stop()
    
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
    )
    
    # Iniciar bucle principal
    try:
        root.mainloop()
    finally:
        cleanup()


if __name__ == "__main__":
    main()
