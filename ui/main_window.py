"""
Ventana principal del sistema de monitoreo
"""
import customtkinter as ctk
from typing import Optional
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, SCRIPTS_DIR
from ui.styles import make_futuristic_button
from ui.widgets import confirm_dialog, custom_msgbox
from utils.system_utils import SystemUtils
from utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow:
    """Ventana principal del dashboard"""
    
    def __init__(self, root, system_monitor, fan_controller, network_monitor,
                 disk_monitor, process_monitor, service_monitor, update_monitor,
                 update_interval=2000):
        self.root = root
        self.system_monitor = system_monitor
        self.fan_controller = fan_controller
        self.network_monitor = network_monitor
        self.disk_monitor = disk_monitor
        self.process_monitor = process_monitor
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

        logger.info(f"[MainWindow] Dashboard iniciado en {self.system_utils.get_hostname()}")

        self._create_ui()
        self._start_update_loop()
    
    def _create_ui(self):
        """Crea la interfaz principal"""
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS['bg_medium'])
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        title = ctk.CTkLabel(
            main_frame,
            text="SISTEMA DE MONITOREO",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xxlarge'], "bold")
        )
        title.pack(pady=(20, 10))
        
        hostname = self.system_utils.get_hostname()
        info_label = ctk.CTkLabel(
            main_frame,
            text=f"Host: {hostname}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'])
        )
        info_label.pack(pady=5)
        
        menu_container = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_medium'])
        menu_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.menu_canvas = ctk.CTkCanvas(
            menu_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0
        )
        self.menu_canvas.pack(side="left", fill="both", expand=True)
        
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
        
        self.menu_inner = ctk.CTkFrame(self.menu_canvas, fg_color=COLORS['bg_medium'])
        self.menu_canvas.create_window(
            (0, 0),
            window=self.menu_inner,
            anchor="nw",
            width=DSI_WIDTH - 50
        )
        
        self.menu_inner.bind(
            "<Configure>",
            lambda e: self.menu_canvas.configure(
                scrollregion=self.menu_canvas.bbox("all")
            )
        )
        
        self._create_menu_buttons()
    
    def _create_menu_buttons(self):
        """Crea los botones del menú principal"""
        buttons_config = [
            ("󰈐  Control Ventiladores", self.open_fan_control),
            ("󰚗  Monitor Placa",         self.open_monitor_window),
            ("  Monitor Red",           self.open_network_window),
            ("󱇰 Monitor USB",            self.open_usb_window),
            ("  Monitor Disco",         self.open_disk_window),
            ("󱓞  Lanzadores",            self.open_launchers),
            ("⚙️ Monitor Procesos",      self.open_process_window),
            ("⚙️ Monitor Servicios",     self.open_service_window),
            ("󱘿  Histórico Datos",       self.open_history_window),
            ("󰆧  Actualizaciones",       self.open_update_window),
            ("󰔎  Cambiar Tema",          self.open_theme_selector),
            ("  Reiniciar",            self.restart_application),
            ("󰿅  Salir",                self.exit_application),
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
        
        for c in range(columns):
            self.menu_inner.grid_columnconfigure(c, weight=1)
    
    # ── Apertura de ventanas ──────────────────────────────────────────────────

    def open_fan_control(self):
        """Abre la ventana de control de ventiladores"""
        if self.fan_window is None or not self.fan_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Control Ventiladores")
            from ui.windows.fan_control import FanControlWindow
            self.fan_window = FanControlWindow(self.root, self.fan_controller, self.system_monitor)
        else:
            self.fan_window.lift()
    
    def open_monitor_window(self):
        """Abre la ventana de monitoreo del sistema"""
        if self.monitor_window is None or not self.monitor_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Placa")
            from ui.windows.monitor import MonitorWindow
            self.monitor_window = MonitorWindow(self.root, self.system_monitor)
        else:
            self.monitor_window.lift()
    
    def open_network_window(self):
        """Abre la ventana de monitoreo de red"""
        if self.network_window is None or not self.network_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Red")
            from ui.windows.network import NetworkWindow
            self.network_window = NetworkWindow(self.root, self.network_monitor)
        else:
            self.network_window.lift()
    
    def open_usb_window(self):
        """Abre la ventana de monitoreo USB"""
        if self.usb_window is None or not self.usb_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor USB")
            from ui.windows.usb import USBWindow
            self.usb_window = USBWindow(self.root)
        else:
            self.usb_window.lift()
    
    def open_process_window(self):
        """Abre el monitor de procesos"""
        if self.process_window is None or not self.process_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Procesos")
            from ui.windows.process_window import ProcessWindow
            self.process_window = ProcessWindow(self.root, self.process_monitor)
        else:
            self.process_window.lift()
    
    def open_service_window(self):
        """Abre el monitor de servicios"""
        if self.service_window is None or not self.service_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Servicios")
            from ui.windows.service import ServiceWindow
            self.service_window = ServiceWindow(self.root, self.service_monitor)
        else:
            self.service_window.lift()
    
    def open_history_window(self):
        """Abre la ventana de histórico"""
        if self.history_window is None or not self.history_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Histórico Datos")
            from ui.windows.history import HistoryWindow
            self.history_window = HistoryWindow(self.root)
        else:
            self.history_window.lift()
    
    def open_launchers(self):
        """Abre la ventana de lanzadores"""
        if self.launchers_window is None or not self.launchers_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Lanzadores")
            from ui.windows.launchers import LaunchersWindow
            self.launchers_window = LaunchersWindow(self.root)
        else:
            self.launchers_window.lift()
    
    def open_theme_selector(self):
        """Abre el selector de temas"""
        logger.debug("[MainWindow] Abriendo: Cambiar Tema")
        from ui.windows.theme_selector import ThemeSelector
        theme_window = ThemeSelector(self.root)
        theme_window.lift()
    
    def open_disk_window(self):
        """Abre la ventana de monitor de disco"""
        if self.disk_window is None or not self.disk_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Disco")
            from ui.windows.disk import DiskWindow
            self.disk_window = DiskWindow(self.root, self.disk_monitor)
        else:
            self.disk_window.lift()
    
    def open_update_window(self):
        """Abre la ventana de actualizaciones"""
        if self.update_window is None or not self.update_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Actualizaciones")
            from ui.windows.update import UpdatesWindow
            self.update_window = UpdatesWindow(self.root, self.update_monitor)
        else:
            self.update_window.lift()
    
    # ── Salir / Reiniciar ─────────────────────────────────────────────────────

    def exit_application(self):
        """Cierra la aplicación con opciones de salida o apagado"""
        selection_window = ctk.CTkToplevel(self.root)
        selection_window.title("Opciones de Salida")
        selection_window.configure(fg_color=COLORS['bg_medium'])
        selection_window.geometry("450x280")
        selection_window.resizable(False, False)
        selection_window.overrideredirect(True)
        
        selection_window.update_idletasks()
        x = DSI_X + (450 // 2) - 40
        y = DSI_Y + (280 // 2) - 40
        selection_window.geometry(f"450x280+{x}+{y}")
        
        selection_window.transient(self.root)
        selection_window.focus_force()
        selection_window.grab_set()
        
        main_frame = ctk.CTkFrame(selection_window, fg_color=COLORS['bg_medium'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="⚠️ ¿Qué deseas hacer?",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold")
        )
        title_label.pack(pady=(10, 20))
        
        selection_var = ctk.StringVar(value="exit")
        
        options_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_dark'])
        options_frame.pack(fill="x", pady=10, padx=20)
        
        exit_radio = ctk.CTkRadioButton(
            options_frame,
            text="  Salir de la aplicación",
            variable=selection_var,
            value="exit",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        exit_radio.pack(anchor="w", padx=20, pady=12)
        
        shutdown_radio = ctk.CTkRadioButton(
            options_frame,
            text="󰐥  Apagar el sistema",
            variable=selection_var,
            value="shutdown",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        shutdown_radio.pack(anchor="w", padx=20, pady=12)
        
        from ui.styles import StyleManager
        StyleManager.style_radiobutton_ctk(exit_radio)
        StyleManager.style_radiobutton_ctk(shutdown_radio)
        
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        def on_confirm():
            selected = selection_var.get()
            selection_window.destroy()
            
            if selected == "exit":
                def do_exit():
                    logger.info("[MainWindow] Cerrando dashboard por solicitud del usuario")
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
                def do_shutdown():
                    logger.info("[MainWindow] Iniciando apagado del sistema")
                    from ui.widgets.dialogs import terminal_dialog
                    shutdown_script = str(SCRIPTS_DIR / "apagado.sh")
                    terminal_dialog(
                        parent=self.root,
                        script_path=shutdown_script,
                        title="󰐥  APAGANDO SISTEMA..."
                    )
                
                confirm_dialog(
                    parent=self.root,
                    text="⚠️ ¿Confirmar APAGAR el sistema?\n\nEsta acción apagará completamente el equipo.",
                    title="🔴 Confirmar Apagado",
                    on_confirm=do_shutdown,
                    on_cancel=None
                )
        
        def on_cancel():
            logger.debug("[MainWindow] Diálogo de salida cancelado")
            selection_window.destroy()
        
        confirm_btn = make_futuristic_button(
            buttons_frame,
            text="Continuar",
            command=on_confirm,
            width=18,
            height=6
        )
        confirm_btn.pack(side="right", padx=5)
        
        cancel_btn = make_futuristic_button(
            buttons_frame,
            text="Cancelar",
            command=on_cancel,
            width=18,
            height=6
        )
        cancel_btn.pack(side="right", padx=5)
        
        selection_window.bind("<Escape>", lambda e: on_cancel())
    
    def restart_application(self):
        """Reinicia la aplicación"""
        from ui.widgets import confirm_dialog
        
        def do_restart():
            import sys
            import os
            logger.info("[MainWindow] Reiniciando dashboard")
            self.root.quit()
            self.root.destroy()
            os.execv(sys.executable, [sys.executable, os.path.abspath(sys.argv[0])] + sys.argv[1:])
        
        confirm_dialog(
            parent=self.root,
            text="¿Reiniciar el dashboard?\n\nSe aplicarán los cambios realizados.",
            title="🔄 Reiniciar Dashboard",
            on_confirm=do_restart,
            on_cancel=None
        )
    
    # ── Loop de actualización ─────────────────────────────────────────────────

    def _start_update_loop(self):
        """Inicia el bucle de actualización"""
        self._update()
    
    def _update(self):
        """Actualiza los datos del sistema"""
        self.root.after(self.update_interval, self._update)
