#!/usr/bin/env python3
"""
Sistema de Monitoreo y Control
Punto de entrada principal
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from config.settings import DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from core import SystemMonitor, FanController, NetworkMonitor
from ui.main_window import MainWindow


def main():
    """Función principal"""
    # Configurar modo de apariencia
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    # Crear ventana principal
    root = ctk.CTk()
    root.title("Sistema de Monitoreo")
    root.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
    root.configure(bg="#111111")
	
	# SIN BORDES Y PANTALLA COMPLETA (COMO ORIGINAL)
    root.overrideredirect(True)        # Sin bordes de ventana
    root.attributes('-fullscreen', True)  # Pantalla completa
	
    
    # Inicializar monitores
    system_monitor = SystemMonitor()
    fan_controller = FanController()
    network_monitor = NetworkMonitor()
    
    # Crear interfaz
    app = MainWindow(
        root,
        system_monitor=system_monitor,
        fan_controller=fan_controller,
        network_monitor=network_monitor,
        update_interval=UPDATE_MS
    )
    
    # Iniciar bucle principal
    root.mainloop()


if __name__ == "__main__":
    main()
