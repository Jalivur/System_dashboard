"""
Ventana de monitoreo de disco
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH,
                             DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS)
from ui.styles import make_futuristic_button
from ui.widgets import GraphWidget
from core.disk_monitor import DiskMonitor


class DiskWindow(ctk.CTkToplevel):
    """Ventana de monitoreo de disco"""
    
    def __init__(self, parent, disk_monitor: DiskMonitor):
        super().__init__(parent)
        
        # Referencias
        self.disk_monitor = disk_monitor
        
        # Widgets para actualización
        self.widgets = {}
        self.graphs = {}
        
        # Configurar ventana
        self.title("Monitor de Disco")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        
        # Crear interfaz
        self._create_ui()
        
        # Iniciar actualización
        self._update()
    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        # Frame principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Título
        title = ctk.CTkLabel(
            main,
            text="MONITOR DE DISCO",
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
        
        from ui.styles import StyleManager
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Secciones (AQUÍ CREAS CADA SECCIÓN)
        self._create_usage_section(inner)       # Uso de disco
        self._create_disk_io_section(inner)
        self._create_nvme_temp_section(inner)   # Temperatura NVMe (NUEVO)
        
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
        
    def _create_metric_section(self, parent, title: str, metric_key: str,
                               unit: str, max_val: float = 100):
        """Crea una sección genérica para una métrica"""
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        frame.pack(fill="x", pady=10, padx=10)
        
        # Label del título
        label = ctk.CTkLabel(
            frame,
            text=title,
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        label.pack(anchor="w", pady=(5, 0), padx=10)
        
        # Valor actual
        value_label = ctk.CTkLabel(
            frame,
            text=f"0.0 {unit}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'])
        )
        value_label.pack(anchor="e", pady=(0, 5), padx=10)
        
        # Gráfica
        graph = GraphWidget(frame, width=DSI_WIDTH-80, height=100)
        graph.pack(pady=(0, 10))
        
        # Guardar referencias
        self.widgets[f"{metric_key}_label"] = label
        self.widgets[f"{metric_key}_value"] = value_label
        self.graphs[metric_key] = {
            'widget': graph,
            'max_val': max_val
        }    
    def _create_usage_section(self, parent):
        """Crea la sección de uso de disco"""
        # TODO: Implementar (similar a MonitorWindow)
        # Frame con label, valor y gráfica
        self._create_metric_section(parent, "DISCO %", "disk", "%", 100)

    def _create_disk_io_section(self, parent):
        """Crea la sección de I/O de disco"""
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        frame.pack(fill="x", pady=10, padx=10)
        
        # Título
        title = ctk.CTkLabel(
            frame,
            text="I/O DE DISCO",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        title.pack(anchor="w", pady=(5, 10), padx=10)
        
        # Escritura
        write_label = ctk.CTkLabel(
            frame,
            text="ESCRITURA",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        )
        write_label.pack(anchor="w", pady=(0, 0), padx=10)
        
        write_value = ctk.CTkLabel(
            frame,
            text="0.0 MB/s",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'])
        )
        write_value.pack(anchor="e", pady=(0, 5), padx=10)
        
        write_graph = GraphWidget(frame, width=DSI_WIDTH-80, height=80)
        write_graph.pack(pady=(0, 10))
        
        # Lectura
        read_label = ctk.CTkLabel(
            frame,
            text="LECTURA",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        )
        read_label.pack(anchor="w", pady=(0, 0), padx=10)
        
        read_value = ctk.CTkLabel(
            frame,
            text="0.0 MB/s",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'])
        )
        read_value.pack(anchor="e", pady=(0, 5), padx=10)
        
        read_graph = GraphWidget(frame, width=DSI_WIDTH-80, height=80)
        read_graph.pack(pady=(0, 10))
        
        # Guardar referencias
        self.widgets['disk_write_label'] = write_label
        self.widgets['disk_write_value'] = write_value
        self.widgets['disk_read_label'] = read_label
        self.widgets['disk_read_value'] = read_value
        
        self.graphs['disk_write'] = {
            'widget': write_graph,
            'max_val': 50
        }
        self.graphs['disk_read'] = {
            'widget': read_graph,
            'max_val': 50
        }
    
    def _create_nvme_temp_section(self, parent):
        """Crea la sección de temperatura NVMe"""
        # TODO: Implementar (NUEVO)

        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        frame.pack(fill="x", pady=10, padx=10)

        # Label
        label = ctk.CTkLabel(
            frame,
            text="TEMPERATURA NVMe",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        label.pack(anchor="w", pady=(5, 0), padx=10)

        # Valor
        value_label = ctk.CTkLabel(
            frame,
            text="0.0 °C",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'])
        )
        value_label.pack(anchor="e", pady=(0, 5), padx=10)

        # Gráfica
        graph = GraphWidget(frame, width=DSI_WIDTH-80, height=100)
        graph.pack(pady=(0, 10))

        # Guardar referencias
        self.widgets['nvme_temp_label'] = label
        self.widgets['nvme_temp_value'] = value_label
        self.graphs['nvme_temp'] = {
            'widget': graph,
            'max_val': 85  # Temperatura máxima NVMe
        }

    def _update(self):
        """Actualiza los datos del disco"""
        if not self.winfo_exists():
            return
        
        # Obtener estadísticas actuales
        stats = self.disk_monitor.get_current_stats()
        self.disk_monitor.update_history(stats)
        history = self.disk_monitor.get_history()
        
        # TODO: Actualizar cada sección con sus datos
        # Actualizar Disco (uso)
        self._update_metric(
            'disk',
            stats['disk_usage'],
            history['disk_usage'],
            "%",
            60,
            80
        )
        
        # Actualizar Disco I/O
        self._update_disk_io(
            'disk_write',
            stats['disk_write_mb'],
            history['disk_write']
        )
        
        self._update_disk_io(
            'disk_read',
            stats['disk_read_mb'],
            history['disk_read']
        )
        
        # self._update_nvme_temp(stats, history)
        # Temperatura NVMe (NUEVO)
        self._update_metric(
            'nvme_temp',
            stats['nvme_temp'],
            history['nvme_temp'],
            "°C",
            60,  # warning
            70   # critical
        )
        
        # Programar siguiente actualización
        self.after(UPDATE_MS, self._update)
    def _update_metric(self, key, value, history, unit, warn, crit):
        """Actualiza una métrica genérica"""
        # Determinar color
        color = self.disk_monitor.level_color(value, warn, crit)
        
        # Actualizar valor
        value_widget = self.widgets[f"{key}_value"]
        value_widget.configure(
            text=f"{value:.1f} {unit}",
            text_color=color
        )
        
        # Actualizar label
        label_widget = self.widgets[f"{key}_label"]
        label_widget.configure(text_color=color)
        
        # Actualizar gráfica
        graph_info = self.graphs[key]
        graph_info['widget'].update(history, graph_info['max_val'], color)
        
    def _update_disk_io(self, key: str, value: float, history: list):
        """Actualiza métricas de I/O de disco"""
        # Determinar color (10 MB/s = warning, 50 MB/s = critical)
        color = self.disk_monitor.level_color(value, 10, 50)
        
        # Actualizar valor
        value_widget = self.widgets[f"{key}_value"]
        value_widget.configure(
            text=f"{value:.1f} MB/s",
            text_color=color
        )
        
        # Actualizar label
        label_widget = self.widgets[f"{key}_label"]
        label_widget.configure(text_color=color)
        
        # Actualizar gráfica
        graph_info = self.graphs[key]
        graph_info['widget'].update(history, graph_info['max_val'], color)
