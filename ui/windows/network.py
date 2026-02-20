"""
Ventana de monitoreo de red
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH,
                             DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, NET_INTERFACE)
from ui.styles import StyleManager, make_futuristic_button
from ui.widgets import GraphWidget
from core.network_monitor import NetworkMonitor
from utils.system_utils import SystemUtils


class NetworkWindow(ctk.CTkToplevel):
    """Ventana de monitoreo de red"""
    
    def __init__(self, parent, network_monitor: NetworkMonitor):
        super().__init__(parent)
        
        # Referencias
        self.network_monitor = network_monitor
        
        # Widgets para actualización
        self.widgets = {}
        self.graphs = {}
        
        # Configurar ventana
        self.title("Monitor de Red")
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
            text="MONITOR DE RED",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold")
        )
        title.pack(pady=(10, 10))
        
        # Interfaz actual
        self.interface_label = ctk.CTkLabel(
            main,
            text="Interfaz: Detectando...",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        self.interface_label.pack(pady=(0, 20))
        
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
        
        # Frame interno
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Secciones
        self._create_interfaces_section(inner)  # NUEVO
        self._create_download_section(inner)
        self._create_upload_section(inner)
        self._create_speedtest_section(inner)
        
        # Botones inferiores
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
    
    def _create_interfaces_section(self, parent):
        """Crea la sección de interfaces e IPs"""
        
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        frame.pack(fill="x", pady=10, padx=10)
        
        # Título
        title = ctk.CTkLabel(
            frame,
            text="INTERFACES Y IPs",
            text_color=COLORS['success'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        title.pack(anchor="w", pady=(10, 10), padx=10)
        
        # Contenedor para las interfaces
        self.interfaces_container = ctk.CTkFrame(frame, fg_color=COLORS['bg_dark'])
        self.interfaces_container.pack(fill="x", padx=10, pady=(0, 10))
        
        # Obtener y mostrar interfaces
        self._update_interfaces()
    
    def _update_interfaces(self):
        """Actualiza la lista de interfaces e IPs"""

        
        # Limpiar widgets anteriores
        for widget in self.interfaces_container.winfo_children():
            widget.destroy()
        
        # Obtener IPs
        interfaces = SystemUtils.get_interfaces_ips()
        
        if not interfaces:
            no_iface = ctk.CTkLabel(
                self.interfaces_container,
                text="No se detectaron interfaces",
                text_color=COLORS['warning'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            no_iface.pack(pady=5)
            return
        
        # Mostrar cada interfaz
        for iface, ip in sorted(interfaces.items()):
            # Color especial para tun0 (VPN)
            if iface.startswith('tun'):
                text_color = COLORS['success']  # Verde para VPN
                icon = "🔒"  # Candado para VPN
            elif iface.startswith(('eth', 'enp')):
                text_color = COLORS['primary']  # Cyan para ethernet
                icon = "🌐"
            elif iface.startswith(('wlan', 'wlp')):
                text_color = COLORS['warning']  # Amarillo para wifi
                icon = "󰖩"
            else:
                text_color = COLORS['text']  # Blanco para otras
                icon = "•"
            
            iface_label = ctk.CTkLabel(
                self.interfaces_container,
                text=f"{icon} {iface}: {ip}",
                text_color=text_color,
                font=(FONT_FAMILY, FONT_SIZES['medium']),
                anchor="w"
            )
            iface_label.pack(anchor="w", pady=2, padx=10)
    
    def _create_download_section(self, parent):
        """Crea la sección de descarga"""
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        frame.pack(fill="x", pady=10, padx=10)
        
        # Label
        label = ctk.CTkLabel(
            frame,
            text="DESCARGA",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        label.pack(anchor="w", pady=(5, 0), padx=10)
        
        # Valor
        value_label = ctk.CTkLabel(
            frame,
            text="0.00 MB/s | Escala: 10.00",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        value_label.pack(anchor="e", pady=(0, 5), padx=10)
        
        # Gráfica
        graph = GraphWidget(frame, width=DSI_WIDTH-80, height=120)
        graph.pack(pady=(0, 10))
        
        # Guardar referencias
        self.widgets['download_label'] = label
        self.widgets['download_value'] = value_label
        self.graphs['download'] = graph
    
    def _create_upload_section(self, parent):
        """Crea la sección de subida"""
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        frame.pack(fill="x", pady=10, padx=10)
        
        # Label
        label = ctk.CTkLabel(
            frame,
            text="SUBIDA",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        label.pack(anchor="w", pady=(5, 0), padx=10)
        
        # Valor
        value_label = ctk.CTkLabel(
            frame,
            text="0.00 MB/s | Escala: 10.00",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        value_label.pack(anchor="e", pady=(0, 5), padx=10)
        
        # Gráfica
        graph = GraphWidget(frame, width=DSI_WIDTH-80, height=120)
        graph.pack(pady=(0, 10))
        
        # Guardar referencias
        self.widgets['upload_label'] = label
        self.widgets['upload_value'] = value_label
        self.graphs['upload'] = graph
    
    def _create_speedtest_section(self, parent):
        """Crea la sección de speedtest"""
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        frame.pack(fill="x", pady=10, padx=10)
        
        # Título
        title = ctk.CTkLabel(
            frame,
            text="SPEEDTEST",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        title.pack(anchor="w", pady=(5, 10), padx=10)
        
        # Resultado
        self.speedtest_result = ctk.CTkLabel(
            frame,
            text="Haz clic en 'Ejecutar Test' para comenzar",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            justify="left"
        )
        self.speedtest_result.pack(pady=(0, 10), padx=10)
        
        # Botón
        btn_frame = ctk.CTkFrame(frame, fg_color=COLORS['bg_dark'])
        btn_frame.pack(pady=(0, 10))
        
        self.speedtest_btn = make_futuristic_button(
            btn_frame,
            text="Ejecutar Test",
            command=self._run_speedtest,
            width=20,
            height=6
        )
        self.speedtest_btn.pack()
    
    def _run_speedtest(self):
        """Ejecuta el speedtest"""
        # Verificar si ya hay uno corriendo
        result = self.network_monitor.get_speedtest_result()
        if result['status'] == 'running':
            return
        
        # Resetear y ejecutar
        self.network_monitor.reset_speedtest()
        self.network_monitor.run_speedtest()
        
        # Actualizar UI
        self.speedtest_btn.configure(state="disabled")
        self.speedtest_result.configure(
            text="Ejecutando test...",
            text_color=COLORS['warning']
        )
    
    def _update(self):
        """Actualiza los datos de red"""
        if not self.winfo_exists():
            return
        
        # Obtener estadísticas
        stats = self.network_monitor.get_current_stats(NET_INTERFACE)
        self.network_monitor.update_history(stats)
        self.network_monitor.update_dynamic_scale()
        
        history = self.network_monitor.get_history()
        
        # Actualizar interfaz
        self.interface_label.configure(
            text=f"Interfaz: {stats['interface']}"
        )
        
        # Actualizar descarga
        dl_color = self.network_monitor.net_color(stats['download_mb'])
        self.widgets['download_label'].configure(text_color=dl_color)
        self.widgets['download_value'].configure(
            text=f"{stats['download_mb']:.2f} MB/s | Escala: {history['dynamic_max']:.2f}",
            text_color=dl_color
        )
        self.graphs['download'].update(
            history['download'],
            history['dynamic_max'],
            dl_color
        )
        
        # Actualizar subida
        ul_color = self.network_monitor.net_color(stats['upload_mb'])
        self.widgets['upload_label'].configure(text_color=ul_color)
        self.widgets['upload_value'].configure(
            text=f"{stats['upload_mb']:.2f} MB/s | Escala: {history['dynamic_max']:.2f}",
            text_color=ul_color
        )
        self.graphs['upload'].update(
            history['upload'],
            history['dynamic_max'],
            ul_color
        )
        
        # Actualizar speedtest
        self._update_speedtest()
        
        # Actualizar interfaces (cada 5 segundos para no sobrecargar)
        if not hasattr(self, '_interface_update_counter'):
            self._interface_update_counter = 0
        
        self._interface_update_counter += 1
        if self._interface_update_counter >= 5:  # Cada 5 ciclos (10 segundos)
            self._update_interfaces()
            self._interface_update_counter = 0
        
        # Programar siguiente actualización
        self.after(UPDATE_MS, self._update)
    
    def _update_speedtest(self):
        """Actualiza el resultado del speedtest"""
        result = self.network_monitor.get_speedtest_result()
        status = result['status']
        
        if status == 'idle':
            self.speedtest_result.configure(
                text="Haz clic en 'Ejecutar Test' para comenzar",
                text_color=COLORS['text']
            )
            self.speedtest_btn.configure(state="normal")
        
        elif status == 'running':
            self.speedtest_result.configure(
                text="Ejecutando test de velocidad...",
                text_color=COLORS['warning']
            )
            self.speedtest_btn.configure(state="disabled")
        
        elif status == 'done':
            ping = result['ping']
            download = result['download']
            upload = result['upload']
            
            self.speedtest_result.configure(
                text=f"Ping: {ping} ms\n↓ {download:.2f} MB/s\n↑ {upload:.2f} MB/s",
                text_color=COLORS['success']
            )
            self.speedtest_btn.configure(state="normal")
        
        elif status == 'timeout':
            self.speedtest_result.configure(
                text="Timeout: El test tardó demasiado",
                text_color=COLORS['danger']
            )
            self.speedtest_btn.configure(state="normal")
        
        elif status == 'error':
            self.speedtest_result.configure(
                text="Error ejecutando el test\nVerifica que speedtest-cli esté instalado",
                text_color=COLORS['danger']
            )
            self.speedtest_btn.configure(state="normal")
