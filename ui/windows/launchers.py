"""
Ventana de lanzadores de scripts
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, LAUNCHERS
from ui.styles import make_futuristic_button, StyleManager
from ui.widgets import custom_msgbox, confirm_dialog
from utils.system_utils import SystemUtils


class LaunchersWindow(ctk.CTkToplevel):
    """Ventana de lanzadores de scripts del sistema"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Referencias
        self.system_utils = SystemUtils()
        
        # Configurar ventana
        self.title("Lanzadores")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        
        # Crear interfaz
        self._create_ui()
    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        # Frame principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Título
        title = ctk.CTkLabel(
            main,
            text="LANZADORES",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold")
        )
        title.pack(pady=(10, 20))
        
        # Área de scroll
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Canvas y scrollbar
        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno para botones
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Crear botones de lanzadores
        self._create_launcher_buttons(inner)
        
        # Botón cerrar
        bottom = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=10, padx=10)
        
        close_btn = make_futuristic_button(
            bottom,
            text="Cerrar",
            command=self.destroy,
            width=15,
            height=6
        )
        close_btn.pack(side="right", padx=5)
    
    def _create_launcher_buttons(self, parent):
        """Crea los botones de lanzadores"""
        if not LAUNCHERS:
            # Mensaje si no hay lanzadores configurados
            no_launchers = ctk.CTkLabel(
                parent,
                text="No hay lanzadores configurados\n\nEdita config/settings.py para añadir scripts",
                text_color=COLORS['warning'],
                font=(FONT_FAMILY, FONT_SIZES['medium']),
                justify="center"
            )
            no_launchers.pack(pady=50)
            return
        
        # Crear botón para cada lanzador
        for launcher in LAUNCHERS:
            label = launcher.get("label", "Script")
            script_path = launcher.get("script", "")
            
            # Frame del launcher
            launcher_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
            launcher_frame.pack(fill="x", pady=10, padx=20)
            
            # Botón
            btn = make_futuristic_button(
                launcher_frame,
                text=label,
                command=lambda s=script_path, l=label: self._run_script(s, l),
                width=80,
                height=10,
                font_size=FONT_SIZES['large']
            )
            btn.pack(fill="x")
            
            # Path del script (información adicional)
            path_label = ctk.CTkLabel(
                launcher_frame,
                text=f"Script: {script_path}",
                text_color=COLORS['text'],
                font=(FONT_FAMILY, 10),
                anchor="w"
            )
            path_label.pack(anchor="w", padx=10, pady=(5, 0))
    
    def _run_script(self, script_path: str, label: str):
        """
        Ejecuta un script (con confirmación previa)
        
        Args:
            script_path: Ruta al script
            label: Nombre del lanzador para mostrar en mensajes
        """
        def do_execute():
            """Ejecuta el script después de confirmar"""
            # Mostrar mensaje de ejecución
            executing_msg = f"Ejecutando '{label}'...\n\nEsto puede tardar unos segundos."
            custom_msgbox(self, executing_msg, "Ejecutando")
            
            # Ejecutar script en background
            self.after(100, lambda: self._execute_and_show_result(script_path, label))
        
        # Mostrar diálogo de confirmación usando el sistema existente
        confirm_dialog(
            parent=self,
            text=f"¿Ejecutar '{label}'?\n\n{script_path}",
            title="⚠️ Confirmar Ejecución",
            on_confirm=do_execute,
            on_cancel=None
        )
    
    def _execute_and_show_result(self, script_path: str, label: str):
        """Ejecuta el script y muestra el resultado"""
        success, message = self.system_utils.run_script(script_path)
        
        if success:
            title = "Éxito"
            msg = f"'{label}' se ejecutó correctamente.\n\n{message}"
        else:
            title = "Error"
            msg = f"Error al ejecutar '{label}':\n\n{message}"
        
        custom_msgbox(self, msg, title)
