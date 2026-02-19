import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, SCRIPTS_DIR
from ui.styles import make_futuristic_button
from ui.widgets.dialogs import terminal_dialog
from core import UpdateMonitor
from utils import SystemUtils

class UpdatesWindow(ctk.CTkToplevel):
    """Ventana de control de actualizaciones del sistema"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.system_utils = SystemUtils()
        self.monitor = UpdateMonitor()
        
        # Configuración de ventana (Estilo DSI)
        self.title("Actualizaciones del Sistema")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        
        self._create_ui()
        self._refresh_status()

    def _create_ui(self):
        # Frame Principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Icono y Título
        self.status_icon = ctk.CTkLabel(main, text="󰚰", font=(FONT_FAMILY, 80))
        self.status_icon.pack(pady=(20, 10))
        
        self.status_label = ctk.CTkLabel(
            main, text="Verificando...", 
            font=(FONT_FAMILY, FONT_SIZES['xxlarge'], "bold")
        )
        self.status_label.pack()
        
        self.info_label = ctk.CTkLabel(
            main, text="Buscando actualizaciones pendientes",
            text_color=COLORS['text_dim'], font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        self.info_label.pack(pady=10)
        
        # Botones
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=20)
        
        self.update_btn = make_futuristic_button(
            btn_frame, text="Actualizar Ahora", 
            command=self._run_update, width=25
        )
        self.update_btn.pack(side="left", padx=10, expand=True)
        self.update_btn.configure(state="disabled") # Deshabilitado hasta que termine el check
        
        close_btn = make_futuristic_button(
            btn_frame, text="Cerrar", 
            command=self.destroy, width=15
        )
        close_btn.pack(side="right", padx=10, expand=True)

    def _refresh_status(self):
        """Consulta el estado de actualizaciones"""
        res = self.monitor.check_updates()
        color = COLORS['success'] if res['pending'] == 0 else COLORS['warning']
        
        self.status_label.configure(text=res['status'], text_color=color)
        self.info_label.configure(text=res['message'])
        self.status_icon.configure(text_color=color)
        
        if res['pending'] > 0:
            self.update_btn.configure(state="normal")

    def _run_update(self):
            script_path = str(SCRIPTS_DIR / "update.sh")
            terminal_dialog(self.master, script_path, "CONSOLA DE ACTUALIZACIÓN")
            self.destroy()