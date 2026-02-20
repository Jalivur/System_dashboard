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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from utils.logger import get_logger

logger = get_logger(__name__)


class HistoryWindow(ctk.CTkToplevel):
    """Ventana de visualización de histórico"""

    def __init__(self, parent):
        super().__init__(parent)

        # Referencias
        self.analyzer = DataAnalyzer()
        self.logger   = DataLogger()

        # Estado de periodo
        self.period_var = ctk.StringVar(value="24h")

        # Estado de rango personalizado
        self._using_custom_range = False
        self._custom_start: datetime = None
        self._custom_end:   datetime = None

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

    # ─────────────────────────────────────────────
    # Construcción de la UI
    # ─────────────────────────────────────────────

    def _create_ui(self):
        self._main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        self._main.pack(fill="both", expand=True, padx=5, pady=5)

        self._create_header(self._main)
        self._create_period_controls(self._main)
        self._create_range_panel(self._main)   # fila oculta de OptionMenus

        scroll_container = ctk.CTkFrame(self._main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas_tk = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
            height=DSI_HEIGHT - 300
        )
        canvas_tk.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas_tk.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")

        from ui.styles import StyleManager
        StyleManager.style_scrollbar_ctk(scrollbar)

        canvas_tk.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas_tk, fg_color=COLORS['bg_medium'])
        canvas_tk.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH - 50)
        inner.bind("<Configure>",
                   lambda e: canvas_tk.configure(scrollregion=canvas_tk.bbox("all")))

        self._create_graphs_area(inner)
        self._create_stats_area(inner)
        self._create_buttons(self._main)

    def _create_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        header.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            header,
            text="HISTÓRICO DE DATOS",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold")
        ).pack(pady=10)

        self.toolbar_container = ctk.CTkFrame(header, fg_color=COLORS['bg_dark'])
        self.toolbar_container.pack(side="top", padx=10)

    def _create_period_controls(self, parent):
        """Fila 1: radio buttons 24h/7d/30d + botón para abrir/cerrar el panel de rango."""
        self._controls_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        self._controls_frame.pack(fill="x", padx=10, pady=(5, 0))

        ctk.CTkLabel(
            self._controls_frame,
            text="Periodo:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        ).pack(side="left", padx=10)

        for period, label in [("24h", "24 horas"), ("7d", "7 días"), ("30d", "30 días")]:
            rb = ctk.CTkRadioButton(
                self._controls_frame,
                text=label,
                variable=self.period_var,
                value=period,
                command=self._on_period_radio,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=10)
            from ui.styles import StyleManager
            StyleManager.style_radiobutton_ctk(rb)

        # Botón toggle del panel de rango
        self._toggle_btn = make_futuristic_button(
            self._controls_frame,
            text="󰙹 Rango",
            command=self._toggle_range_panel,
            height=6,
            width=13
        )
        self._toggle_btn.pack(side="right", padx=10)

    def _create_range_panel(self, parent):
        """
        Fila 2 (oculta por defecto): selectores día/mes/año/hora/min
        para inicio y fin del rango. Sin teclado — todo por OptionMenu.
        """
        self._range_panel = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        # No se hace pack aquí → empieza oculto

        font_s = (FONT_FAMILY, FONT_SIZES['small'])
        now = datetime.now()

        # Listas de opciones
        años  = [str(y) for y in range(now.year - 2, now.year + 1)]
        meses = [f"{m:02d}" for m in range(1, 13)]
        dias  = [f"{d:02d}" for d in range(1, 32)]
        horas = [f"{h:02d}" for h in range(0, 24)]
        mins  = [f"{m:02d}" for m in range(0, 60, 5)]   # saltos de 5 min

        # Valores por defecto: inicio = hace 24h, fin = ahora
        start_def = now - timedelta(hours=24)
        s_min_def = f"{(start_def.minute // 5) * 5:02d}"
        e_min_def = f"{(now.minute // 5) * 5:02d}"

        def make_om(parent_frame, values, default):
            """Crea un CTkOptionMenu pequeño y devuelve (widget, StringVar)."""
            var = ctk.StringVar(value=default)
            om = ctk.CTkOptionMenu(
                parent_frame,
                variable=var,
                values=values,
                width=58,
                height=28,
                font=font_s,
                fg_color=COLORS['bg_medium'],
                button_color=COLORS['bg_light'],
                button_hover_color=COLORS['bg_dark'],
                dropdown_fg_color=COLORS['bg_dark'],
                text_color=COLORS['text'],
                dropdown_text_color=COLORS['text'],
            )
            return om, var

        # ── INICIO ───────────────────────────────────────────────
        ctk.CTkLabel(
            self._range_panel,
            text="Desde:",
            text_color=COLORS['secondary'],
            font=font_s
        ).pack(side="left", padx=(10, 4))

        self._s_day,  self._sv_s_day  = make_om(self._range_panel, dias,  f"{start_def.day:02d}")
        self._s_mon,  self._sv_s_mon  = make_om(self._range_panel, meses, f"{start_def.month:02d}")
        self._s_year, self._sv_s_year = make_om(self._range_panel, años,  str(start_def.year))

        # Separador visual entre fecha y hora
        self._s_hour, self._sv_s_hour = make_om(self._range_panel, horas, f"{start_def.hour:02d}")
        self._s_min,  self._sv_s_min  = make_om(self._range_panel, mins,  s_min_def)

        for w in [self._s_day, self._s_mon, self._s_year]:
            w.pack(side="left", padx=2)
        ctk.CTkLabel(self._range_panel, text=" ", text_color=COLORS['text']).pack(side="left")
        for w in [self._s_hour, self._s_min]:
            w.pack(side="left", padx=2)


        # ── FIN ──────────────────────────────────────────────────
        ctk.CTkLabel(
            self._range_panel,
            text="Hasta:",
            text_color=COLORS['secondary'],
            font=font_s
        ).pack(side="left", padx=(4, 2))

        self._e_day,  self._sv_e_day  = make_om(self._range_panel, dias,  f"{now.day:02d}")
        self._e_mon,  self._sv_e_mon  = make_om(self._range_panel, meses, f"{now.month:02d}")
        self._e_year, self._sv_e_year = make_om(self._range_panel, años,  str(now.year))

        self._e_hour, self._sv_e_hour = make_om(self._range_panel, horas, f"{now.hour:02d}")
        self._e_min,  self._sv_e_min  = make_om(self._range_panel, mins,  e_min_def)

        for w in [self._e_day, self._e_mon, self._e_year]:
            w.pack(side="left", padx=2)
        ctk.CTkLabel(self._range_panel, text=" ", text_color=COLORS['text']).pack(side="left")
        for w in [self._e_hour, self._e_min]:
            w.pack(side="left", padx=2)

        # ── BOTÓN APLICAR ─────────────────────────────────────────
        self._apply_btn = make_futuristic_button(
            self._controls_frame,
            text="✓Aplicar",
            command=self._apply_custom_range,
            height=6,
            width=12,
            state="disabled"  # solo se habilita al abrir el panel, para evitar confusión
        )
        self._apply_btn.pack(side="right", padx=(10, 5))

    def _create_graphs_area(self, parent):
        graphs_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        graphs_frame.pack(fill="both", expand=True, padx=(0, 10), pady=(0, 10))

        self.fig = Figure(figsize=(9, 20), facecolor=COLORS['bg_medium'])
        self.fig.set_tight_layout(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=graphs_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=0)

        # Toolbar invisible — sus métodos se invocan desde botones propios
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.pack_forget()

        for text, cmd, w in [
            ("🏠 Inicio",  self.toolbar.home,          12),
            ("🔍 Zoom",    self.toolbar.zoom,           12),
            ("🖐️ Mover",  self.toolbar.pan,            12),
            (" Guardar",  self._export_figure_image,   12),
        ]:
            make_futuristic_button(
                self.toolbar_container, text=text, command=cmd, height=6, width=w
            ).pack(side="left", padx=5)

        self.canvas.mpl_connect('button_press_event',   self._on_click)
        self.canvas.mpl_connect('button_release_event', self._on_release)
        self.canvas.mpl_connect('motion_notify_event',  self._on_motion)

    def _create_stats_area(self, parent):
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
        buttons = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        buttons.pack(fill="x", pady=10, padx=10)

        for text, cmd, side, w in [
            ("Actualizar",       self._update_data,    "left",  18),
            ("Exportar CSV",     self._export_csv,     "left",  18),
            ("Limpiar Antiguos", self._clean_old_data, "left",  18),
            ("Cerrar",           self.destroy,         "right", 15),
        ]:
            make_futuristic_button(
                buttons, text=text, command=cmd, width=w, height=6
            ).pack(side=side, padx=5)

    # ─────────────────────────────────────────────
    # Control del panel de rango
    # ─────────────────────────────────────────────

    def _toggle_range_panel(self):
        """Muestra u oculta la fila de OptionMenus de rango personalizado."""
        if self._range_panel.winfo_ismapped():
            self._range_panel.pack_forget()
            self._toggle_btn.configure(text="󰙹 Rango")
            self._apply_btn.configure(state="disabled")
        else:
            # Insertar después del frame de controles de periodo
            self._range_panel.pack(
                fill="x", padx=10, pady=(0, 5),
                after=self._controls_frame
            )
            self._toggle_btn.configure(text="✕ Cerrar")
            self._apply_btn.configure(state="normal")


    # ─────────────────────────────────────────────
    # Lógica de actualización
    # ─────────────────────────────────────────────

    def _on_period_radio(self):
        """Al pulsar radio button fijo: desactiva modo custom y actualiza."""
        self._using_custom_range = False
        self._update_data()

    def _apply_custom_range(self):
        """Lee los OptionMenus y aplica el rango sin necesidad de teclado."""
        try:
            start_dt = datetime(
                year=int(self._sv_s_year.get()),
                month=int(self._sv_s_mon.get()),
                day=int(self._sv_s_day.get()),
                hour=int(self._sv_s_hour.get()),
                minute=int(self._sv_s_min.get())
            )
        except ValueError as e:
            custom_msgbox(self, f"Fecha de inicio inválida:\n{e}", "❌ Error")
            return

        try:
            end_dt = datetime(
                year=int(self._sv_e_year.get()),
                month=int(self._sv_e_mon.get()),
                day=int(self._sv_e_day.get()),
                hour=int(self._sv_e_hour.get()),
                minute=int(self._sv_e_min.get())
            )
        except ValueError as e:
            custom_msgbox(self, f"Fecha de fin inválida:\n{e}", "❌ Error")
            return

        if end_dt <= start_dt:
            custom_msgbox(self, "La fecha de fin debe ser\nposterior a la de inicio.", "⚠️ Rango inválido")
            return

        if (end_dt - start_dt).days > 90:
            custom_msgbox(self, "El rango no puede superar 90 días.", "⚠️ Rango demasiado amplio")
            return

        self._using_custom_range = True
        self._custom_start = start_dt
        self._custom_end   = end_dt

        logger.info(
            f"[HistoryWindow] Rango aplicado: "
            f"{start_dt.strftime('%Y-%m-%d %H:%M')} → {end_dt.strftime('%Y-%m-%d %H:%M')}"
        )
        self._update_data()

    def _update_data(self):
        """Actualiza estadísticas y gráficas según el modo activo."""
        if self._using_custom_range:
            start = self._custom_start
            end   = self._custom_end
            stats = self.analyzer.get_stats_between(start, end)
            rango_label = f"{start.strftime('%Y-%m-%d %H:%M')} → {end.strftime('%Y-%m-%d %H:%M')}"
            hours = None  # no se usa en modo custom
        else:
            period = self.period_var.get()
            hours  = {"24h": 24, "7d": 24 * 7, "30d": 24 * 30}[period]
            stats  = self.analyzer.get_stats(hours)
            rango_label = period

        total_records = self.logger.get_metrics_count()
        db_size       = self.logger.get_db_size_mb()

        stats_text = (
            f"• CPU promedio: {stats.get('cpu_avg', 0):.1f}%  "
            f"(min: {stats.get('cpu_min', 0):.1f}%, max: {stats.get('cpu_max', 0):.1f}%)\n"
            f"• RAM promedio: {stats.get('ram_avg', 0):.1f}%  "
            f"(min: {stats.get('ram_min', 0):.1f}%, max: {stats.get('ram_max', 0):.1f}%)\n"
            f"• Temp promedio: {stats.get('temp_avg', 0):.1f}°C  "
            f"(min: {stats.get('temp_min', 0):.1f}°C, max: {stats.get('temp_max', 0):.1f}°C)\n"
            f"• Red Down: {stats.get('down_avg', 0):.2f} MB/s  "
            f"(min: {stats.get('down_min', 0):.2f}, max: {stats.get('down_max', 0):.2f})\n"
            f"• Red Up: {stats.get('up_avg', 0):.2f} MB/s  "
            f"(min: {stats.get('up_min', 0):.2f}, max: {stats.get('up_max', 0):.2f})\n"
            f"• Disk Read: {stats.get('disk_read_avg', 0):.2f} MB/s  "
            f"(min: {stats.get('disk_read_min', 0):.2f}, max: {stats.get('disk_read_max', 0):.2f})\n"
            f"• Disk Write: {stats.get('disk_write_avg', 0):.2f} MB/s  "
            f"(min: {stats.get('disk_write_min', 0):.2f}, max: {stats.get('disk_write_max', 0):.2f})\n"
            f"• PWM promedio: {stats.get('pwm_avg', 0):.0f}  "
            f"(min: {stats.get('pwm_min', 0):.0f}, max: {stats.get('pwm_max', 0):.0f})\n"
            f"• Actualizaciones disponibles promedio: {stats.get('updates_available_avg', 0):.2f}\n"
            f"• Actualizaciones disponibles (min: {stats.get('updates_available_min', 0)})\n"
            f"• Actualizaciones disponibles (max: {stats.get('updates_available_max', 0)})\n"
            f"• Muestras: {stats.get('total_samples', 0)} en {rango_label}\n"
            f"• Total registros: {total_records}  |  DB: {db_size:.2f} MB"
        )
        self.stats_label.configure(text=stats_text)

        if self._using_custom_range:
            self._update_graphs_between(self._custom_start, self._custom_end)
        else:
            self._update_graphs(hours)

    # ─────────────────────────────────────────────
    # Gráficas
    # ─────────────────────────────────────────────

    _METRICS = [
        ('cpu_percent',     'CPU %',           'primary'),
        ('ram_percent',     'RAM %',           'secondary'),
        ('temperature',     'Temp °C',         'danger'),
        ('net_download_mb', 'Red Down MB/s',   'primary'),
        ('net_upload_mb',   'Red Up MB/s',     'secondary'),
        ('disk_read_mb',    'Disk Read MB/s',  'primary'),
        ('disk_write_mb',   'Disk Write MB/s', 'secondary'),
        ('fan_pwm',         'PWM',             'warning'),
    ]

    def _update_graphs(self, hours: int):
        self.fig.clear()
        axes = [self.fig.add_subplot(8, 1, i) for i in range(1, 9)]
        for (metric, ylabel, color_key), ax in zip(self._METRICS, axes):
            ts, vals = self.analyzer.get_graph_data(metric, hours)
            self._draw_metric(ax, ts, vals, ylabel, COLORS[color_key])
        self.fig.tight_layout()
        self.canvas.draw()

    def _update_graphs_between(self, start: datetime, end: datetime):
        self.fig.clear()
        axes = [self.fig.add_subplot(8, 1, i) for i in range(1, 9)]
        for (metric, ylabel, color_key), ax in zip(self._METRICS, axes):
            ts, vals = self.analyzer.get_graph_data_between(metric, start, end)
            self._draw_metric(ax, ts, vals, ylabel, COLORS[color_key])
        self.fig.tight_layout()
        self.canvas.draw()

    def _draw_metric(self, ax, timestamps, values, ylabel: str, color: str):
        ax.set_facecolor(COLORS['bg_dark'])
        ax.tick_params(colors=COLORS['text'])
        ax.set_ylabel(ylabel, color=COLORS['text'])
        ax.set_xlabel('Tiempo', color=COLORS['text'])
        ax.grid(True, alpha=0.2)
        if timestamps:
            ax.plot(timestamps, values, color=color, linewidth=1.5)

    # ─────────────────────────────────────────────
    # Exportación
    # ─────────────────────────────────────────────

    def _export_csv(self):
        if self._using_custom_range:
            start = self._custom_start
            end   = self._custom_end
            label = f"custom_{start.strftime('%Y%m%d%H%M')}_{end.strftime('%Y%m%d%H%M')}"
            path  = f"{DATA_DIR}/history_{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            try:
                self.analyzer.export_to_csv_between(path, start, end)
                custom_msgbox(self, f"Datos exportados a:\n{path}", "✅ Exportado")
            except Exception as e:
                custom_msgbox(self, f"Error al exportar:\n{e}", "❌ Error")
        else:
            period = self.period_var.get()
            hours  = {"24h": 24, "7d": 24 * 7, "30d": 24 * 30}[period]
            path   = f"{DATA_DIR}/history_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            try:
                self.analyzer.export_to_csv(path, hours)
                custom_msgbox(self, f"Datos exportados a:\n{path}", "✅ Exportado")
            except Exception as e:
                custom_msgbox(self, f"Error al exportar:\n{e}", "❌ Error")

    def _clean_old_data(self):
        from ui.widgets import confirm_dialog
        days = 7

        def do_clean():
            try:
                self.logger.clean_old_data(days=days)
                custom_msgbox(self, f"Datos mayores a {days} días eliminados.", "✅ Limpiado")
                logger.info(f"[HistoryWindow] Limpieza completada (>{days} días)")
                self._update_data()
            except Exception as e:
                logger.error(f"[HistoryWindow] Error limpiando: {e}")
                custom_msgbox(self, f"Error al limpiar:\n{e}", "❌ Error")

        confirm_dialog(
            parent=self,
            text=f"¿Eliminar datos mayores a {days} días?\n\nEsto liberará espacio en disco.",
            title="⚠️ Confirmar",
            on_confirm=do_clean,
            on_cancel=None
        )

    def _export_figure_image(self):
        import os
        try:
            save_dir = os.path.join(os.getcwd(), "data/screenshots")
            os.makedirs(save_dir, exist_ok=True)
            filepath = os.path.join(
                save_dir,
                f"graficas_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.png"
            )
            self.fig.savefig(
                filepath, dpi=150,
                facecolor=self.fig.get_facecolor(),
                bbox_inches='tight'
            )
            logger.info(f"[HistoryWindow] Figura guardada: {filepath}")
            custom_msgbox(self, f"Imagen guardada en:\n\n{filepath}", "✅ Captura Guardada")
        except Exception as e:
            logger.error(f"[HistoryWindow] Error guardando imagen: {e}")
            custom_msgbox(self, f"Error al guardar la imagen: {e}", "❌ Error")

    # ─────────────────────────────────────────────
    # Eventos matplotlib
    # ─────────────────────────────────────────────

    def _on_click(self, event):
        if event.inaxes:
            logger.debug(f"Click en gráfica: x={event.xdata}, y={event.ydata}")

    def _on_release(self, event):
        pass

    def _on_motion(self, event):
        pass
