import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, SCRIPTS_DIR
from ui.styles import make_futuristic_button
from ui.widgets.dialogs import terminal_dialog, confirm_dialog
from core import UpdateMonitor
from utils import SystemUtils

class UpdatesWindow(ctk.CTkToplevel):
    """Ventana de control de actualizaciones del sistema"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.system_utils = SystemUtils()

        
        # Configuración de ventana (Estilo DSI)
        self.title("Actualizaciones del Sistema")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        
        # Creamos la interfaz primero
        self._create_ui()
        # Importante: Asegúrate de que UpdateMonitor esté bien inicializado
        self.monitor = UpdateMonitor()
        # Cargamos el estado inicial sin forzar apt update
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

        # 2. Botón Instalar (Aquí estaba el error de nombre)
        self.update_btn = make_futuristic_button(
            btn_frame, text="󰚰 Instalar", 
            command=self._execute_update_script, width=12
        )
        self.update_btn.pack(side="left", padx=5, expand=True)
        self.update_btn.configure(state="disabled")  # Deshabilitado por defecto
        
        # 3. Botón Cerrar
        close_btn = make_futuristic_button(
            btn_frame, text="Cerrar", 
            command=self.destroy, width=12
        )
        close_btn.pack(side="left", padx=5, expand=True)

    def _refresh_status(self, force=False):
        """Consulta el estado de actualizaciones"""
        if force:
            self.status_label.configure(text="Buscando...", text_color=COLORS['warning'])
            self.update_idletasks()

        # Llamada al core
        res = self.monitor.check_updates(force=force)
        
        color = COLORS['success'] if res['pending'] == 0 else COLORS['warning']
        
        self.status_label.configure(text=res['status'], text_color=color)
        self.info_label.configure(text=res['message'])
        self.status_icon.configure(text_color=color)
        
        if res['pending'] > 0:
            self.update_btn.configure(state="normal")
        else:
            self.update_btn.configure(state="disabled")

    def _execute_update_script(self):
        """Lanza el script de terminal y refresca al terminar"""
        script_path = str(SCRIPTS_DIR / "update.sh")
        
        # Definimos qué hacer cuando la terminal se cierre
        def al_terminar_actualizacion():
            # Forzamos una búsqueda real para confirmar que ya no hay paquetes
            self._refresh_status(force=True)
            # Opcional: podrías mostrar un mensaje de "Actualización completada"
        
        # Lanzamos el diálogo. 
        # Si tu terminal_dialog permite un callback al cerrar, lo usamos:
        terminal_dialog(
            self, 
            script_path, 
            "CONSOLA DE ACTUALIZACIÓN",
            on_close=al_terminar_actualizacion
        )
