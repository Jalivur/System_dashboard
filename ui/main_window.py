"""
Ventana principal del sistema de monitoreo
"""
import customtkinter as ctk
from typing import Optional
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH
from ui.styles import make_futuristic_button
from utils.system_utils import SystemUtils


class MainWindow:
    """Ventana principal del dashboard"""
    
    def __init__(self, root, system_monitor, fan_controller, network_monitor, 
                 update_interval=2000):
        """
        Inicializa la ventana principal
        
        Args:
            root: Ventana raíz de CTk
            system_monitor: Instancia de SystemMonitor
            fan_controller: Instancia de FanController
            network_monitor: Instancia de NetworkMonitor
            update_interval: Intervalo de actualización en ms
        """
        self.root = root
        self.system_monitor = system_monitor
        self.fan_controller = fan_controller
        self.network_monitor = network_monitor
        self.update_interval = update_interval
        self.system_utils = SystemUtils()
        
        # Referencias a ventanas secundarias
        self.fan_window = None
        self.monitor_window = None
        self.network_window = None
        self.usb_window = None
        self.launchers_window = None
        
        # Crear interfaz
        self._create_ui()
        
        # Iniciar actualización
        self._start_update_loop()
    
    def _create_ui(self):
        """Crea la interfaz principal"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS['bg_medium'])
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Título
        title = ctk.CTkLabel(
            main_frame,
            text="SISTEMA DE MONITOREO",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xxlarge'], "bold")
        )
        title.pack(pady=20)
        
        # Información del sistema
        hostname = self.system_utils.get_hostname()
        info_label = ctk.CTkLabel(
            main_frame,
            text=f"Host: {hostname}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        info_label.pack(pady=5)
        
        # Contenedor de menú con scroll
        menu_container = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_medium'])
        menu_container.pack(fill="both", expand=True, padx=5, pady=10)
        
        # Canvas para scroll
        self.menu_canvas = ctk.CTkCanvas(
            menu_container, 
            bg=COLORS['bg_medium'], 
            highlightthickness=0
        )
        self.menu_canvas.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        menu_scrollbar = ctk.CTkScrollbar(
            menu_container, 
            orientation="vertical", 
            command=self.menu_canvas.yview,
            width=30
        )
        menu_scrollbar.pack(side="right", fill="y")
        
        from ui.styles import StyleManager
        StyleManager.style_scrollbar_ctk(menu_scrollbar)
        
        self.menu_canvas.configure(yscrollcommand=menu_scrollbar.set)
        
        # Frame interno para botones
        self.menu_inner = ctk.CTkFrame(self.menu_canvas, fg_color=COLORS['bg_medium'])
        self.menu_canvas.create_window(
            (0, 0), 
            window=self.menu_inner, 
            anchor="nw",
            width=DSI_WIDTH - 60
        )
        
        # Configurar scroll
        self.menu_inner.bind(
            "<Configure>",
            lambda e: self.menu_canvas.configure(
                scrollregion=self.menu_canvas.bbox("all")
            )
        )
        
        # Crear botones del menú
        self._create_menu_buttons()
    
    def _create_menu_buttons(self):
        """Crea los botones del menú principal"""
        buttons_config = [
            ("Control Ventiladores", self.open_fan_control),
            ("Monitor Placa", self.open_monitor_window),
            ("Monitor Red", self.open_network_window),
            ("Monitor USB", self.open_usb_window),
            ("Lanzadores", self.open_launchers),
            ("🎨 Cambiar Tema", self.open_theme_selector),
            ("❌ Salir", self.exit_application),  # NUEVO
        ]
        
        columns = 2
        
        for i, (text, command) in enumerate(buttons_config):
            row = i // columns
            col = i % columns
            
            btn = make_futuristic_button(
                self.menu_inner,
                text,
                command=command,
                font_size=FONT_SIZES['large'],
                width=30,
                height=15
            )
            
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Configurar columnas con peso igual
        for c in range(columns):
            self.menu_inner.grid_columnconfigure(c, weight=1)
    
    def open_fan_control(self):
        """Abre la ventana de control de ventiladores"""
        if self.fan_window is None or not self.fan_window.winfo_exists():
            from ui.windows.fan_control import FanControlWindow
            self.fan_window = FanControlWindow(
                self.root, 
                self.fan_controller,
                self.system_monitor
            )
        else:
            self.fan_window.lift()
    
    def open_monitor_window(self):
        """Abre la ventana de monitoreo del sistema"""
        if self.monitor_window is None or not self.monitor_window.winfo_exists():
            from ui.windows.monitor import MonitorWindow
            self.monitor_window = MonitorWindow(
                self.root,
                self.system_monitor
            )
        else:
            self.monitor_window.lift()
    
    def open_network_window(self):
        """Abre la ventana de monitoreo de red"""
        if self.network_window is None or not self.network_window.winfo_exists():
            from ui.windows.network import NetworkWindow
            self.network_window = NetworkWindow(
                self.root,
                self.network_monitor
            )
        else:
            self.network_window.lift()
    
    def open_usb_window(self):
        """Abre la ventana de monitoreo USB"""
        if self.usb_window is None or not self.usb_window.winfo_exists():
            from ui.windows.usb import USBWindow
            self.usb_window = USBWindow(self.root)
        else:
            self.usb_window.lift()
    
    def open_launchers(self):
        """Abre la ventana de lanzadores"""
        if self.launchers_window is None or not self.launchers_window.winfo_exists():
            from ui.windows.launchers import LaunchersWindow
            self.launchers_window = LaunchersWindow(self.root)
        else:
            self.launchers_window.lift()
    
    def open_theme_selector(self):
        """Abre el selector de temas"""
        from ui.windows.theme_selector import ThemeSelector
        theme_window = ThemeSelector(self.root)
        theme_window.lift()
    
    def exit_application(self):
        """Cierra la aplicación completamente"""
        from ui.widgets import confirm_dialog
        
        def do_exit():
            """Cierra todo"""
            self.root.quit()
            self.root.destroy()
        
        # Usar confirm_dialog existente
        confirm_dialog(
            parent=self.root,
            text="¿Seguro que quieres salir?",
            title="⚠️ Confirmar Salida",
            on_confirm=do_exit,
            on_cancel=None
            
        )
    
    def _start_update_loop(self):
        """Inicia el bucle de actualización"""
        self._update()
    
    def _update(self):
        """Actualiza los datos del sistema"""
        # Las ventanas secundarias se actualizan en sus propias clases
        # Aquí solo programamos la siguiente actualización
        self.root.after(self.update_interval, self._update)
