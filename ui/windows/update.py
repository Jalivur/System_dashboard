import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, SCRIPTS_DIR
from ui.styles import make_futuristic_button
from ui.widgets.dialogs import terminal_dialog
from utils import SystemUtils


class UpdatesWindow(ctk.CTkToplevel):
    """Ventana de control de actualizaciones del sistema"""
    
    def __init__(self, parent, update_monitor):
        super().__init__(parent)
        self.system_utils = SystemUtils()
        self.monitor = update_monitor
        self._polling = False

        # Configuración de ventana (Estilo DSI)
        self.title("Actualizaciones del Sistema")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        
        self._create_ui()
        self._refresh_status(force=False)

    def _create_ui(self):
        # Frame Principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Icono
        self.status_icon = ctk.CTkLabel(main, text="󰚰", font=(FONT_FAMILY, 60))
        self.status_icon.pack(pady=(10, 5))
        
        # Labels
        self.status_label = ctk.CTkLabel(
            main, text="Verificando...", 
            font=(FONT_FAMILY, FONT_SIZES['xxlarge'], "bold")
        )
        self.status_label.pack()
        
        self.info_label = ctk.CTkLabel(
            main, text="Estado de los paquetes",
            text_color=COLORS['text_dim'], font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        self.info_label.pack(pady=5)
        
        # Frame para botones
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=(10, 20))
        
        # 1. Botón Buscar (Manual)
        self.search_btn = make_futuristic_button(
            btn_frame, text="🔍 Buscar", 
            command=lambda: self._refresh_status(force=True), width=12
        )
        self.search_btn.pack(side="left", padx=5, expand=True)

        # 2. Botón Instalar
        self.update_btn = make_futuristic_button(
            btn_frame, text="󰚰 Instalar", 
            command=self._execute_update_script, width=12
        )
        self.update_btn.pack(side="left", padx=5, expand=True)
        self.update_btn.configure(state="disabled")
        
        # 3. Botón Cerrar
        close_btn = make_futuristic_button(
            btn_frame, text="Cerrar", 
            command=self.destroy, width=12
        )
        close_btn.pack(side="left", padx=5, expand=True)

    def _refresh_status(self, force=False):
        """Consulta el estado de actualizaciones"""
        if force:
            self._polling = False  # Cancelar polling si el usuario busca manualmente
            self.status_label.configure(text="Buscando...", text_color=COLORS['warning'])
            self.update_idletasks()

        res = self.monitor.check_updates(force=force)

        # Si el thread de arranque aún no ha terminado, mostrar estado de espera
        if res['status'] == "Unknown":
            self.status_label.configure(text="Comprobando...", text_color=COLORS['text_dim'])
            self.info_label.configure(text="Verificación inicial en curso")
            self.status_icon.configure(text_color=COLORS['text_dim'])
            self.update_btn.configure(state="disabled")
            # Reintentar cada 2 segundos hasta tener resultado real
            if not self._polling:
                self._polling = True
                self._poll_until_ready()
            return

        self._polling = False
        color = COLORS['success'] if res['pending'] == 0 else COLORS['warning']
        self.status_label.configure(text=res['status'], text_color=color)
        self.info_label.configure(text=res['message'])
        self.status_icon.configure(text_color=color)
        self.update_btn.configure(state="normal" if res['pending'] > 0 else "disabled")

    def _poll_until_ready(self):
        """Reintenta _refresh_status cada 2s mientras el resultado sea Unknown"""
        if not self._polling:
            return
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return

        res = self.monitor.check_updates(force=False)
        if res['status'] != "Unknown":
            self._refresh_status(force=False)
        else:
            self.after(2000, self._poll_until_ready)

    def _execute_update_script(self):
        """Lanza el script de terminal y refresca al terminar"""
        script_path = str(SCRIPTS_DIR / "update.sh")
        
        def al_terminar_actualizacion():
            self._refresh_status(force=True)
        
        terminal_dialog(
            self, 
            script_path, 
            "CONSOLA DE ACTUALIZACIÓN",
            on_close=al_terminar_actualizacion
        )
