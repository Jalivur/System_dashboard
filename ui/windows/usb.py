"""
Ventana de monitoreo de dispositivos USB
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
from ui.styles import make_futuristic_button, StyleManager
from ui.widgets import custom_msgbox
from utils.system_utils import SystemUtils


class USBWindow(ctk.CTkToplevel):
    """Ventana de monitoreo de dispositivos USB"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Referencias
        self.system_utils = SystemUtils()
        
        # Widgets dinámicos
        self.device_widgets = []
        
        # Configurar ventana
        self.title("Monitor USB")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        
        # Crear interfaz
        self._create_ui()
        
        # Cargar dispositivos iniciales
        self._refresh_devices()
    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        # Frame principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Encabezado
        header = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        header.pack(fill="x", pady=(10, 5), padx=10)
        
        # Título
        title = ctk.CTkLabel(
            header,
            text="DISPOSITIVOS USB",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold")
        )
        title.pack(side="left")
        
        # Botón refresh
        refresh_btn = make_futuristic_button(
            header,
            text="Actualizar",
            command=self._refresh_devices,
            width=15,
            height=5
        )
        refresh_btn.pack(side="right")
        
        # Área de scroll
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Canvas y scrollbar
        self.canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=self.canvas.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno para dispositivos
        self.devices_frame = ctk.CTkFrame(self.canvas, fg_color=COLORS['bg_medium'])
        self.canvas.create_window(
            (0, 0),
            window=self.devices_frame,
            anchor="nw",
            width=DSI_WIDTH-50
        )
        
        self.devices_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
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
    
    def _refresh_devices(self):
        """Refresca la lista de dispositivos USB"""
        # Limpiar widgets existentes
        for widget in self.device_widgets:
            widget.destroy()
        self.device_widgets.clear()
        
        # Obtener dispositivos separados
        storage_devices = self.system_utils.list_usb_storage_devices()
        other_devices = self.system_utils.list_usb_other_devices()
        
        # === SECCIÓN: ALMACENAMIENTO USB ===
        if storage_devices:
            self._create_storage_section(storage_devices)
        
        # === SECCIÓN: OTROS DISPOSITIVOS ===
        if other_devices:
            self._create_other_devices_section(other_devices)
        
        # Si no hay ningún dispositivo
        if not storage_devices and not other_devices:
            no_devices = ctk.CTkLabel(
                self.devices_frame,
                text="No se detectaron dispositivos USB",
                text_color=COLORS['warning'],
                font=(FONT_FAMILY, FONT_SIZES['medium']),
                justify="center"
            )
            no_devices.pack(pady=50)
            self.device_widgets.append(no_devices)
    
    def _create_storage_section(self, storage_devices: list):
        """Crea la sección de almacenamiento USB"""
        # Título de sección
        title = ctk.CTkLabel(
            self.devices_frame,
            text="ALMACENAMIENTO USB",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        title.pack(anchor="w", pady=(10, 10), padx=10)
        self.device_widgets.append(title)
        
        # Cada dispositivo de almacenamiento
        for idx, device in enumerate(storage_devices):
            self._create_storage_device_widget(device, idx)
    
    def _create_storage_device_widget(self, device: dict, index: int):
        """Crea widget para un dispositivo de almacenamiento"""
        # Frame del dispositivo
        device_frame = ctk.CTkFrame(
            self.devices_frame,
            fg_color=COLORS['bg_dark'],
            border_width=2,
            border_color=COLORS['success']
        )
        device_frame.pack(fill="x", pady=5, padx=10)
        self.device_widgets.append(device_frame)
        
        # Nombre y tamaño del disco
        name = device.get('name', 'USB Disk')
        size = device.get('size', '?')
        dev_type = device.get('type', 'disk')
        
        header_text = f"💾 {name} ({dev_type}) - {size}"
        
        header = ctk.CTkLabel(
            device_frame,
            text=header_text,
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        )
        header.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Información del dispositivo
        dev_path = device.get('dev', '?')
        info = ctk.CTkLabel(
            device_frame,
            text=f"Dispositivo: {dev_path}",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        info.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Botón expulsar (siempre mostrar)
        eject_btn = make_futuristic_button(
            device_frame,
            text="Expulsar",
            command=lambda d=device: self._eject_device(d),
            width=15,
            height=4
        )
        eject_btn.pack(anchor="w", padx=20, pady=(5, 10))
        
        # Mostrar particiones
        children = device.get('children', [])
        if children:
            for child in children:
                self._create_partition_widget(device_frame, child)
    
    def _create_partition_widget(self, parent, partition: dict):
        """Crea widget para una partición"""
        name = partition.get('name', '?')
        mount = partition.get('mount')
        size = partition.get('size', '?')
        
        # Texto de la partición
        part_text = f"  └─ Partición: {name} ({size})"
        if mount:
            part_text += f" | 📁 Montado en: {mount}"
        else:
            part_text += " | No montado"
        
        part_label = ctk.CTkLabel(
            parent,
            text=part_text,
            text_color=COLORS['primary'] if mount else COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wraplength=DSI_WIDTH - 80,
            anchor="w",
            justify="left"
        )
        part_label.pack(anchor="w", padx=30, pady=2)
    
    def _create_other_devices_section(self, other_devices: list):
        """Crea la sección de otros dispositivos USB"""
        # Título de sección
        title = ctk.CTkLabel(
            self.devices_frame,
            text="OTROS DISPOSITIVOS USB",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        title.pack(anchor="w", pady=(20, 10), padx=10)
        self.device_widgets.append(title)
        
        # Cada dispositivo
        for idx, device_line in enumerate(other_devices):
            self._create_other_device_widget(device_line, idx)
    
    def _create_other_device_widget(self, device_line: str, index: int):
        """Crea widget para otro dispositivo USB"""
        # Parsear la línea de lsusb
        device_info = self._parse_lsusb_line(device_line)
        
        # Frame del dispositivo
        device_frame = ctk.CTkFrame(
            self.devices_frame,
            fg_color=COLORS['bg_dark'],
            border_width=1,
            border_color=COLORS['primary']
        )
        device_frame.pack(fill="x", pady=3, padx=10)
        self.device_widgets.append(device_frame)
        
        # Contenedor interno
        inner = ctk.CTkFrame(device_frame, fg_color=COLORS['bg_dark'])
        inner.pack(fill="x", padx=5, pady=5)
        
        # Número
        num_label = ctk.CTkLabel(
            inner,
            text=f"#{index + 1}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            width=30
        )
        num_label.pack(side="left", padx=5)
        
        # Bus info
        bus_label = ctk.CTkLabel(
            inner,
            text=device_info['bus'],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            width=100
        )
        bus_label.pack(side="left", padx=5)
        
        # Descripción
        desc_label = ctk.CTkLabel(
            inner,
            text=device_info['description'],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wraplength=DSI_WIDTH - 200,
            anchor="w",
            justify="left"
        )
        desc_label.pack(side="left", padx=5, fill="x", expand=True)
    
    def _parse_lsusb_line(self, line: str) -> dict:
        """
        Parsea una línea de lsusb
        
        Args:
            line: Línea completa de lsusb
            
        Returns:
            Diccionario con bus y descripción
        """
        # Formato: Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
        parts = line.split()
        
        try:
            # Extraer Bus
            bus_idx = parts.index("Bus") + 1
            bus = f"Bus {parts[bus_idx]}"
            
            # Extraer Device
            dev_idx = parts.index("Device") + 1
            device_num = parts[dev_idx].rstrip(':')
            bus += f" Dev {device_num}"
            
            # Descripción (después del ID)
            id_idx = parts.index("ID") + 2
            description = " ".join(parts[id_idx:])
            
            # Limitar longitud
            if len(description) > 50:
                description = description[:47] + "..."
            
        except (ValueError, IndexError):
            bus = "Bus ?"
            description = line
        
        return {
            'bus': bus,
            'description': description
        }
    
    def _eject_device(self, device: dict):
        """Expulsa un dispositivo USB"""
        # Confirmar primero
        device_name = device.get('name', 'dispositivo')
        
        # Ejecutar expulsión
        success, message = self.system_utils.eject_usb_device(device)
        
        # Mostrar resultado
        if success:
            custom_msgbox(
                self,
                f"✅ {device_name}\n\n{message}\n\nAhora puedes desconectar el dispositivo de forma segura.",
                "Expulsión Exitosa"
            )
            # Refrescar lista
            self._refresh_devices()
        else:
            custom_msgbox(
                self,
                f"❌ Error al expulsar {device_name}:\n\n{message}",
                "Error"
            )
