"""
Ventana de histórico de datos
"""
import customtkinter as ctk
from datetime import datetime, timedelta
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, DATA_DIR
from ui.styles import make_futuristic_button
from ui.widgets import custom_msgbox
from core.data_analyzer import DataAnalyzer
from core.data_logger import DataLogger
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


class HistoryWindow(ctk.CTkToplevel):
    """Ventana de visualización de histórico"""

    def __init__(self, parent):
        super().__init__(parent)

        # Referencias
        self.analyzer = DataAnalyzer()
        self.logger = DataLogger()

        # Estado
        self.period_var = ctk.StringVar(value="24h")

        # Configurar ventana
        self.title("Histórico de Datos")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        # Crear interfaz
        self._create_ui()

        # Cargar datos iniciales
        self._update_data()

    def _create_ui(self):
        """Crea la interfaz"""
        # Frame principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        # Título
        self._create_header(main)

        # Controles de periodo
        self._create_period_controls(main)
        # Área de scroll
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Limitar altura
        max_height = DSI_HEIGHT - 300

        # Canvas y scrollbar
        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
            height=max_height
        )
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")
        
        from ui.styles import StyleManager
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Área de gráficas
        self._create_graphs_area(inner)

        # Estadísticas
        self._create_stats_area(inner)

        # Botones inferiores
        self._create_buttons(main)

    def _create_header(self, parent):
        """Crea el encabezado"""
        header = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        header.pack(fill="x", padx=10, pady=(10, 5))

        title = ctk.CTkLabel(
            header,
            text="HISTÓRICO DE DATOS",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold")
        )
        title.pack(pady=10)

    def _create_period_controls(self, parent):
        """Crea controles de periodo"""
        controls = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        controls.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            controls,
            text="Periodo:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        ).pack(side="left", padx=10)

        for period, label in [("24h", "24 horas"), ("7d", "7 días"), ("30d", "30 días")]:
            rb = ctk.CTkRadioButton(
                controls,
                text=label,
                variable=self.period_var,
                value=period,
                command=self._update_data,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=10)
            from ui.styles import StyleManager
            StyleManager.style_radiobutton_ctk(rb)

    def _create_graphs_area(self, parent):
        """Crea área de gráficas"""
        graphs_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        graphs_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Figura de matplotlib
        self.fig = Figure(figsize=(10, 20), facecolor=COLORS['bg_medium'])

        # Canvas para incrustar en tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=graphs_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        # AÑADIR: Toolbar de navegación
        toolbar_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        toolbar_frame.pack(fill="x", pady=(5, 0))

        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

        # Estilizar toolbar
        self.toolbar.config(background=COLORS['bg_dark'])
        for widget in self.toolbar.winfo_children():
            if hasattr(widget, 'config'):
                widget.config(bg=COLORS['primary'], highlightcolor=COLORS['text'])

    def _create_stats_area(self, parent):
        """Crea área de estadísticas"""
        stats_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        stats_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            stats_frame,
            text="Estadísticas:",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).pack(pady=(10, 5))

        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="Cargando...",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            justify="left"
        )
        self.stats_label.pack(pady=(0, 10), padx=20)

    def _create_buttons(self, parent):
        """Crea botones inferiores"""
        buttons = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        buttons.pack(fill="x", pady=10, padx=10)
        
        update_btn = make_futuristic_button(
            buttons,
            text="Actualizar",
            command=self._update_data,
            width=18,
            height=6
        )
        update_btn.pack(side="left", padx=5)

        export_btn = make_futuristic_button(
            buttons,
            text="Exportar CSV",
            command=self._export_csv,
            width=18,
            height=6
        )
        export_btn.pack(side="left", padx=5)

        clean_btn = make_futuristic_button(
            buttons,
            text="Limpiar Antiguos",
            command=self._clean_old_data,
            width=18,
            height=6
        )
        clean_btn.pack(side="left", padx=5)

        close_btn = make_futuristic_button(
            buttons,
            text="Cerrar",
            command=self.destroy,
            width=15,
            height=6
        )
        close_btn.pack(side="right", padx=5)

    def _update_data(self):
        """Actualiza datos y gráficas"""
        # Obtener horas según periodo
        period = self.period_var.get()
        if period == "24h":
            hours = 24
        elif period == "7d":
            hours = 24 * 7
        else:  # 30d
            hours = 24 * 30

        # Obtener estadísticas
        stats = self.analyzer.get_stats(hours)

        # Actualizar label de estadísticas
        total_records = self.logger.get_metrics_count()
        db_size = self.logger.get_db_size_mb()

        stats_text = f"""• CPU promedio: {stats.get('cpu_avg', 0):.1f}%  (min: {stats.get('cpu_min', 0):.1f}%, max: {stats.get('cpu_max', 0):.1f}%)
• RAM promedio: {stats.get('ram_avg', 0):.1f}%  (min: {stats.get('ram_min', 0):.1f}%, max: {stats.get('ram_max', 0):.1f}%)
• Temp promedio: {stats.get('temp_avg', 0):.1f}°C  (min: {stats.get('temp_min', 0):.1f}°C, max: {stats.get('temp_max', 0):.1f}°C)
• Red Down promedio: {stats.get('down_avg', 0):.2f} MB/s (min: {stats.get('down_min', 0):.2f} MB/s, max: {stats.get('down_max', 0):.2f} MB/s)
• Red Up promedio: {stats.get('up_avg', 0):.2f} MB/s (min: {stats.get('up_min', 0):.2f} MB/s, max: {stats.get('up_max', 0):.2f} MB/s)
• Disk Read promedio: {stats.get('disk_read_avg', 0):.2f} MB/s (min: {stats.get('disk_read_min', 0):.2f} MB/s, max: {stats.get('disk_read_max', 0):.2f} MB/s)
• Disk Write promedio: {stats.get('disk_write_avg', 0):.2f} MB/s (min: {stats.get('disk_write_min', 0):.2f} MB/s, max: {stats.get('disk_write_max', 0):.2f} MB/s)
• PWM promedio: {stats.get('pwm_avg', 0):.0f} (min: {stats.get('pwm_min', 0):.0f}, max: {stats.get('pwm_max', 0):.0f})
• Muestras: {stats.get('total_samples', 0)} en {period}
• Total registros: {total_records}  |  DB: {db_size:.2f} MB"""

        self.stats_label.configure(text=stats_text)

        # Actualizar gráficas
        self._update_graphs(hours)

    def _update_graphs(self, hours: int):
        """Actualiza las gráficas"""
        # Limpiar figura
        self.fig.clear()

        # Crear 8 subplots
        ax1 = self.fig.add_subplot(8, 1, 1)  # CPU
        ax2 = self.fig.add_subplot(8, 1, 2)  # RAM
        ax3 = self.fig.add_subplot(8, 1, 3)  # Temperatura
        ax4 = self.fig.add_subplot(8, 1, 4)  # Red Download
        ax5 = self.fig.add_subplot(8, 1, 5)  # Red Upload
        ax6 = self.fig.add_subplot(8, 1, 6)  # Disk Read
        ax7 = self.fig.add_subplot(8, 1, 7)  # Disk Write
        ax8 = self.fig.add_subplot(8, 1, 8)  # PWM
        
        # Habilitar interactividad
        """self.canvas.mpl_connect('button_press_event', self._on_click)
        self.canvas.mpl_connect('button_release_event', self._on_release)
        self.canvas.mpl_connect('motion_notify_event', self._on_motion)
                """
        # Obtener datos
        ts_cpu, vals_cpu = self.analyzer.get_graph_data('cpu_percent', hours)
        ts_ram, vals_ram = self.analyzer.get_graph_data('ram_percent', hours)
        ts_temp, vals_temp = self.analyzer.get_graph_data('temperature', hours)
        ts_down, vals_down = self.analyzer.get_graph_data('net_download_mb', hours)
        ts_up, vals_up = self.analyzer.get_graph_data('net_upload_mb', hours)
        ts_disk_read, vals_disk_read = self.analyzer.get_graph_data('disk_read_mb', hours)
        ts_disk_write, vals_disk_write = self.analyzer.get_graph_data('disk_write_mb', hours)
        ts_pwm, vals_pwm = self.analyzer.get_graph_data('fan_pwm', hours)

        # Gráfica CPU
        if ts_cpu:
            ax1.plot(ts_cpu, vals_cpu, color=COLORS['primary'], linewidth=1.5)
            ax1.set_ylabel('CPU %', color=COLORS['text'])
            ax1.set_xlabel('Tiempo', color=COLORS['text'])
            ax1.set_facecolor(COLORS['bg_dark'])
            ax1.tick_params(colors=COLORS['text'])
            ax1.grid(True, alpha=0.2)

        # Gráfica RAM
        if ts_ram:
            ax2.plot(ts_ram, vals_ram, color=COLORS['secondary'], linewidth=1.5)
            ax2.set_ylabel('RAM %', color=COLORS['text'])
            ax2.set_xlabel('Tiempo', color=COLORS['text'])
            ax2.set_facecolor(COLORS['bg_dark'])
            ax2.tick_params(colors=COLORS['text'])
            ax2.grid(True, alpha=0.2)

        # Gráfica Temperatura
        if ts_temp:
            ax3.plot(ts_temp, vals_temp, color=COLORS['danger'], linewidth=1.5)
            ax3.set_ylabel('Temp °C', color=COLORS['text'])
            ax3.set_xlabel('Tiempo', color=COLORS['text'])
            ax3.set_facecolor(COLORS['bg_dark'])
            ax3.tick_params(colors=COLORS['text'])
            ax3.grid(True, alpha=0.2)

        # Gráfica Red Download
        if ts_down:
            ax4.plot(ts_down, vals_down, color=COLORS['primary'], linewidth=1.5)
            ax4.set_ylabel('Red Down MB/s', color=COLORS['text'])
            ax4.set_xlabel('Tiempo', color=COLORS['text'])
            ax4.set_facecolor(COLORS['bg_dark'])
            ax4.tick_params(colors=COLORS['text'])
            ax4.grid(True, alpha=0.2)
            
        # Gráfica Red Upload
        if ts_up:
            ax5.plot(ts_up, vals_up, color=COLORS["secondary"], linewidth=1.5)
            ax5.set_ylabel('Red Up MB/s', color=COLORS['text'])
            ax5.set_xlabel('Tiempo', color=COLORS['text'])
            ax5.set_facecolor(COLORS['bg_dark'])
            ax5.tick_params(colors=COLORS['text'])
            ax5.grid(True, alpha=0.2)
        
        # Gráfica Disk Read
        if ts_disk_read:
            ax6.plot(ts_disk_read, vals_disk_read, color=COLORS["primary"], linewidth=1.5)
            ax6.set_ylabel('Disk Read MB/s', color=COLORS['text'])
            ax6.set_xlabel('Tiempo', color=COLORS['text'])
            ax6.set_facecolor(COLORS['bg_dark'])
            ax6.tick_params(colors=COLORS['text'])
            ax6.grid(True, alpha=0.2)
            
        # Gráfica Disk Write
        if ts_disk_write:
            ax7.plot(ts_disk_write, vals_disk_write, color=COLORS["secondary"], linewidth=1.5)
            ax7.set_ylabel('Disk Write MB/s', color=COLORS['text'])
            ax7.set_xlabel('Tiempo', color=COLORS['text'])
            ax7.set_facecolor(COLORS['bg_dark'])
            ax7.tick_params(colors=COLORS['text'])
            ax7.grid(True, alpha=0.2)
        
        # Gráfica PWM
        if ts_pwm:
            ax8.plot(ts_pwm, vals_pwm, color=COLORS["warning"], linewidth=1.5)
            ax8.set_ylabel('PWM', color=COLORS['text'])
            ax8.set_xlabel('Tiempo', color=COLORS['text'])
            ax8.set_facecolor(COLORS['bg_dark'])
            ax8.tick_params(colors=COLORS['text'])
            ax8.grid(True, alpha=0.2)

        # Ajustar layout
        self.fig.tight_layout()

        # Redibujar
        self.canvas.draw()

    def _export_csv(self):
        """Exporta datos a CSV"""
        period = self.period_var.get()
        hours = 24 if period == "24h" else (24 * 7 if period == "7d" else 24 * 30)

        output_path = f"{DATA_DIR}/history_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        try:
            self.analyzer.export_to_csv(output_path, hours)
            custom_msgbox(self, f"Datos exportados a:\n{output_path}", "✅ Exportado")
        except Exception as e:
            custom_msgbox(self, f"Error al exportar:\n{str(e)}", "❌ Error")

    def _clean_old_data(self):
        """Limpia datos antiguos"""
        from ui.widgets import confirm_dialog

        def do_clean():
            try:
                self.logger.clean_old_data(days=90)
                custom_msgbox(self, "Datos antiguos eliminados\n(mayores a 90 días)", "✅ Limpiado")
                self._update_data()
            except Exception as e:
                custom_msgbox(self, f"Error al limpiar:\n{str(e)}", "❌ Error")

        confirm_dialog(
            parent=self,
            text="¿Eliminar datos mayores a 90 días?\n\nEsto liberará espacio en disco.",
            title="⚠️ Confirmar",
            on_confirm=do_clean,
            on_cancel=None
        )