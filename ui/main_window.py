"""
Ventana principal del sistema de monitoreo
"""
import customtkinter as ctk
from typing import Optional
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, SCRIPTS_DIR
from ui.styles import make_futuristic_button
import customtkinter as ctk
from ui.widgets import confirm_dialog, custom_msgbox
from utils.system_utils import SystemUtils
import subprocess

class MainWindow:
    """Ventana principal del dashboard"""
    
    def __init__(self, root, system_monitor, fan_controller, network_monitor, disk_monitor, process_monitor, service_monitor, update_monitor, update_interval=2000,):
        """
        Inicializa la ventana principal
        
        Args:
            root: Ventana raíz de CTk
            system_monitor: Instancia de SystemMonitor
            fan_controller: Instancia de FanController
            network_monitor: Instancia de NetworkMonitor
            disk_monitor: Instancia de DiskMonitor
            process_monitor: Instancia de ProcessMonitor
            service_monitor: Instancia de ServiceMonitor
            update_interval: Intervalo de actualización en ms
        """
        self.root = root
        self.system_monitor = system_monitor
        self.fan_controller = fan_controller
        self.network_monitor = network_monitor
        self.disk_monitor = disk_monitor
        self.process_monitor= process_monitor
        self.service_monitor = service_monitor
        self.update_monitor = update_monitor
        
        self.update_interval = update_interval
        self.system_utils = SystemUtils()
        
        # Referencias a ventanas secundarias
        self.fan_window = None
        self.monitor_window = None
        self.network_window = None
        self.usb_window = None
        self.launchers_window = None
        self.disk_window = None
        self.process_window = None
        self.service_window = None
        self.history_window = None
        self.update_window = None
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
        title.pack(pady=(20, 10))
        
        # Información del sistema
        hostname = self.system_utils.get_hostname()
        info_label = ctk.CTkLabel(
            main_frame,
            text=f"Host: {hostname}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'])
        )
        info_label.pack(pady=5)
        
        # Contenedor de menú con scroll
        menu_container = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_medium'])
        menu_container.pack(fill="both", expand=True, padx=5, pady=5)
        
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
            width=DSI_WIDTH - 50
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
            ("󰈐  Control Ventiladores", self.open_fan_control),
            ("󰚗  Monitor Placa", self.open_monitor_window),
            ("  Monitor Red", self.open_network_window),
            ("󱇰 Monitor USB", self.open_usb_window),
            ("  Monitor Disco", self.open_disk_window),  
            ("󱓞  Lanzadores", self.open_launchers),
            ("⚙️ Monitor Procesos", self.open_process_window),
            ("⚙️ Monitor Servicios", self.open_service_window),
            ("󱘿  Histórico Datos", self.open_history_window),
            ("󰆧  Actualizaciones", self.open_update_window),
            ("󰔎  Cambiar Tema", self.open_theme_selector),
            ("  Reiniciar", self.restart_application),  # NUEVO
            ("󰿅  Salir", self.exit_application),  # NUEVO
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
    # Método:
    def open_process_window(self):
        if self.process_window is None or not self.process_window.winfo_exists():
            from ui.windows.process_window import ProcessWindow
            self.process_window = ProcessWindow(self.root, self.process_monitor)
        else:
            self.process_window.lift()
    
    def open_service_window(self):
        """Abre el monitor de servicios"""
        if self.service_window is None or not self.service_window.winfo_exists():
            from ui.windows.service import ServiceWindow
            self.service_window = ServiceWindow(
                self.root,
                self.service_monitor
            )
        else:
            self.service_window.lift()
            
    def open_history_window(self):
        """Abre la ventana de histórico"""
        if self.history_window is None or not self.history_window.winfo_exists():
            from ui.windows.history import HistoryWindow
            self.history_window = HistoryWindow(self.root)
        else:
            self.history_window.lift()
            
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
        
    def open_disk_window(self):
        """Abre la ventana de monitor de disco"""
        if self.disk_window is None or not self.disk_window.winfo_exists():
            from ui.windows.disk import DiskWindow
            self.disk_window = DiskWindow(
                self.root,
                self.disk_monitor
            )
        else:
            self.disk_window.lift()
    def open_update_window(self):
        """Abre la ventana de monitor de actualizaciones"""
        if self.update_window is None or not self.update_window.winfo_exists():
            from ui.windows.update import UpdatesWindow
            self.update_window = UpdatesWindow(
                self.root,
            )
        else:
            self.update_window.lift()
            
    def exit_application(self):
        """Cierra la aplicación con opciones de salida o apagado"""

        # Crear ventana de selección
        selection_window = ctk.CTkToplevel(self.root)
        selection_window.title("Opciones de Salida")
        selection_window.configure(fg_color=COLORS['bg_medium'])
        selection_window.geometry("450x280")
        selection_window.resizable(False, False)
        selection_window.overrideredirect(True)
        
        
        # Centrar en pantalla
        selection_window.update_idletasks()
        x = DSI_X + (450 // 2) - 40
        y = DSI_Y + (280 // 2) - 40
        selection_window.geometry(f"450x280+{x}+{y}")
        
        # Hacer modal
        selection_window.transient(self.root)
        selection_window.focus_force()
        selection_window.grab_set()
        
        # Frame principal
        main_frame = ctk.CTkFrame(selection_window, fg_color=COLORS['bg_medium'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="⚠️ ¿Qué deseas hacer?",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Variable para la selección
        selection_var = ctk.StringVar(value="exit")
        
        # Frame de opciones
        options_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_dark'])
        options_frame.pack(fill="x", pady=10, padx=20)
        
        # Opción 1: Salir de la aplicación
        exit_radio = ctk.CTkRadioButton(
            options_frame,
            text="  Salir de la aplicación",
            variable=selection_var,
            value="exit",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        exit_radio.pack(anchor="w", padx=20, pady=12)
        
        # Opción 2: Apagar el sistema
        shutdown_radio = ctk.CTkRadioButton(
            options_frame,
            text="󰐥  Apagar el sistema",
            variable=selection_var,
            value="shutdown",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        shutdown_radio.pack(anchor="w", padx=20, pady=12)
        
        # Estilizar radio buttons
        from ui.styles import StyleManager
        StyleManager.style_radiobutton_ctk(exit_radio)
        StyleManager.style_radiobutton_ctk(shutdown_radio)
        
        # Frame de botones
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        def on_confirm():
            """Ejecuta la acción seleccionada con confirmación"""
            selected = selection_var.get()
            selection_window.destroy()
            
            if selected == "exit":
                # Salir de la aplicación
                def do_exit():
                    """Cierra todo"""
                    self.root.quit()
                    self.root.destroy()
                
                confirm_dialog(
                    parent=self.root,
                    text="¿Confirmar salir de la aplicación?",
                    title="⚠️ Confirmar Salida",
                    on_confirm=do_exit,
                    on_cancel=None
                )
                
            else:  # shutdown
                # Apagar el sistema
                def do_shutdown():
                    """Ejecuta script de apagado"""
                    shutdown_script = str(SCRIPTS_DIR / "apagado.sh")
                    
                    try:
                        # Ejecutar script
                        result = subprocess.run(
                            ["bash", shutdown_script],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        
                        if result.returncode == 0:
                            # Cerrar aplicación después de lanzar shutdown
                            self.root.quit()
                            self.root.destroy()
                        else:
                            custom_msgbox(
                                self.root,
                                f"Error al ejecutar apagado:\n{result.stderr}",
                                "❌ Error"
                            )
                    except subprocess.TimeoutExpired:
                        custom_msgbox(
                            self.root,
                            "Timeout al ejecutar script de apagado",
                            "❌ Error"
                        )
                    except Exception as e:
                        custom_msgbox(
                            self.root,
                            f"Error: {str(e)}",
                            "❌ Error"
                        )
                
                confirm_dialog(
                    parent=self.root,
                    text="⚠️ ¿Confirmar APAGAR el sistema?\n\nEsta acción apagará completamente el equipo.",
                    title="🔴 Confirmar Apagado",
                    on_confirm=do_shutdown,
                    on_cancel=None
                )
        
        def on_cancel():
            """Cancela y cierra ventana de selección"""
            selection_window.destroy()
        
        # Botón Confirmar
        confirm_btn = make_futuristic_button(
            buttons_frame,
            text="Continuar",
            command=on_confirm,
            width=18,
            height=6
        )
        confirm_btn.pack(side="right", padx=5)
        
        # Botón Cancelar
        cancel_btn = make_futuristic_button(
            buttons_frame,
            text="Cancelar",
            command=on_cancel,
            width=18,
            height=6
        )
        cancel_btn.pack(side="right", padx=5)
        
        # Bind ESC para cancelar
        selection_window.bind("<Escape>", lambda e: on_cancel())
    
    
    def restart_application(self):
        """Reinicia la aplicación"""
        from ui.widgets import confirm_dialog
        
        def do_restart():
            """Reinicia el dashboard"""
            import sys
            import os
            
            # Obtener el script principal
            python = sys.executable
            script = os.path.abspath(sys.argv[0])
            
            # Cerrar aplicación actual
            self.root.quit()
            self.root.destroy()
            
            # Reiniciar con os.execv (reemplaza el proceso actual)
            os.execv(python, [python, script] + sys.argv[1:])
        
        # Confirmar antes de reiniciar
        confirm_dialog(
            parent=self.root,
            text="¿Reiniciar el dashboard?\n\nSe aplicarán los cambios realizados.",
            title="🔄 Reiniciar Dashboard",
            on_confirm=do_restart,
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
