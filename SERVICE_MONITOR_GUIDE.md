# 🔧 Guía Paso a Paso: Implementar Monitor de Servicios systemd

Esta guía te enseñará a crear una ventana completa para monitorear y gestionar servicios de systemd (nginx, ssh, docker, etc.).

---

## 📋 Índice de Pasos

1. [Detectar servicios systemd](#paso-1-detectar-servicios-systemd)
2. [Crear ServiceMonitor en core/](#paso-2-crear-servicemonitor-en-core)
3. [Crear la ventana ServiceWindow](#paso-3-crear-la-ventana-servicewindow)
4. [Añadir botón al menú principal](#paso-4-añadir-botón-al-menú-principal)
5. [Probar todo](#paso-5-probar-todo)

---

## 🎯 Objetivo Final

Crear una ventana que muestre:
- ✅ Lista de servicios systemd
- ✅ Estado actual (active, inactive, failed)
- ✅ Start/Stop/Restart servicios
- ✅ Ver logs en tiempo real
- ✅ Enable/Disable autostart
- ✅ Búsqueda y filtros

**Vista previa:**
```
┌────────────────────────────────────────────────┐
│          MONITOR DE SERVICIOS                  │
│  Total: 245 | Activos: 180 | Fallidos: 2      │
├────────────────────────────────────────────────┤
│  Buscar: [_____]  Filtro: ⦿Todos ○Activos     │
├──────────────┬──────────┬──────────────────────┤
│ Servicio     │ Estado   │ Acciones            │
├──────────────┼──────────┼──────────────────────┤
│ 🟢 nginx     │ active   │ [⏸] [🔄] [👁] [⚙️]  │
│ 🟢 ssh       │ active   │ [⏸] [🔄] [👁] [⚙️]  │
│ 🟢 docker    │ active   │ [⏸] [🔄] [👁] [⚙️]  │
│ 🔴 apache2   │ inactive │ [▶] [🔄] [👁] [⚙️]  │
│ 🔴 mysql     │ failed   │ [▶] [🔄] [👁] [⚙️]  │
└──────────────┴──────────┴──────────────────────┘
         [Refrescar]              [Cerrar]
```

---

## Paso 1: Detectar servicios systemd

### 1.1 Abrir terminal y probar comandos

```bash
# Listar todos los servicios
systemctl list-units --type=service --all

# Ver estado de un servicio
systemctl status nginx

# Ver si está enabled
systemctl is-enabled nginx

# Ver logs
journalctl -u nginx -n 50
```

### 1.2 Entender la salida

**systemctl list-units --type=service --all** devuelve:
```
UNIT                    LOAD   ACTIVE   SUB     DESCRIPTION
nginx.service          loaded active   running A high performance web server
ssh.service            loaded active   running OpenBSD Secure Shell server
docker.service         loaded active   running Docker Application Container Engine
apache2.service        loaded inactive dead    The Apache HTTP Server
```

**Campos importantes:**
- `UNIT`: Nombre del servicio
- `LOAD`: loaded / not-found
- `ACTIVE`: active / inactive / failed
- `SUB`: running / dead / exited
- `DESCRIPTION`: Descripción del servicio

---

## Paso 2: Crear ServiceMonitor en core/

### 2.1 Crear archivo `core/service_monitor.py`

```python
"""
Monitor de servicios systemd
"""
import subprocess
import re
from typing import List, Dict, Optional


class ServiceMonitor:
    """Monitor de servicios del sistema"""
    
    def __init__(self):
        """Inicializa el monitor de servicios"""
        self.sort_by = "name"  # name, state
        self.sort_reverse = False
        self.filter_type = "all"  # all, active, inactive, failed
    
    def get_services(self) -> List[Dict]:
        """
        Obtiene lista de servicios systemd
        
        Returns:
            Lista de diccionarios con información de servicios
        """
        services = []
        
        try:
            # Listar todos los servicios
            result = subprocess.run(
                ["systemctl", "list-units", "--type=service", "--all", "--no-pager"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return []
            
            # Parsear salida
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                # Saltar headers y footers
                if not line.strip() or line.startswith('UNIT') or line.startswith('●') or 'loaded units listed' in line:
                    continue
                
                # Parsear línea
                parts = line.split()
                if len(parts) < 4:
                    continue
                
                unit = parts[0]
                load = parts[1]
                active = parts[2]
                sub = parts[3]
                description = ' '.join(parts[4:]) if len(parts) > 4 else ''
                
                # Solo servicios .service
                if not unit.endswith('.service'):
                    continue
                
                # Extraer nombre sin .service
                name = unit.replace('.service', '')
                
                # Aplicar filtro
                if self.filter_type == "active" and active != "active":
                    continue
                elif self.filter_type == "inactive" and active != "inactive":
                    continue
                elif self.filter_type == "failed" and active != "failed":
                    continue
                
                services.append({
                    'name': name,
                    'unit': unit,
                    'load': load,
                    'active': active,
                    'sub': sub,
                    'description': description,
                    'enabled': self._check_enabled(unit)
                })
            
        except Exception as e:
            print(f"Error getting services: {e}")
            return []
        
        # Ordenar
        if self.sort_by == "name":
            services.sort(key=lambda x: x['name'].lower(), reverse=self.sort_reverse)
        elif self.sort_by == "state":
            # Ordenar por estado: active > inactive > failed
            state_order = {'active': 0, 'inactive': 1, 'failed': 2}
            services.sort(
                key=lambda x: state_order.get(x['active'], 3),
                reverse=self.sort_reverse
            )
        
        return services
    
    def _check_enabled(self, unit: str) -> bool:
        """
        Verifica si un servicio está enabled
        
        Args:
            unit: Nombre del servicio (ej: nginx.service)
            
        Returns:
            True si está enabled
        """
        try:
            result = subprocess.run(
                ["systemctl", "is-enabled", unit],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0 and result.stdout.strip() == "enabled"
        except Exception:
            return False
    
    def start_service(self, name: str) -> tuple[bool, str]:
        """
        Inicia un servicio
        
        Args:
            name: Nombre del servicio
            
        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "start", f"{name}.service"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, f"Servicio '{name}' iniciado correctamente"
            else:
                return False, f"Error: {result.stderr}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def stop_service(self, name: str) -> tuple[bool, str]:
        """
        Detiene un servicio
        
        Args:
            name: Nombre del servicio
            
        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "stop", f"{name}.service"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, f"Servicio '{name}' detenido correctamente"
            else:
                return False, f"Error: {result.stderr}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def restart_service(self, name: str) -> tuple[bool, str]:
        """
        Reinicia un servicio
        
        Args:
            name: Nombre del servicio
            
        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "restart", f"{name}.service"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, f"Servicio '{name}' reiniciado correctamente"
            else:
                return False, f"Error: {result.stderr}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def enable_service(self, name: str) -> tuple[bool, str]:
        """
        Habilita autostart de un servicio
        
        Args:
            name: Nombre del servicio
            
        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "enable", f"{name}.service"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, f"Autostart habilitado para '{name}'"
            else:
                return False, f"Error: {result.stderr}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def disable_service(self, name: str) -> tuple[bool, str]:
        """
        Deshabilita autostart de un servicio
        
        Args:
            name: Nombre del servicio
            
        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "disable", f"{name}.service"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, f"Autostart deshabilitado para '{name}'"
            else:
                return False, f"Error: {result.stderr}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_logs(self, name: str, lines: int = 50) -> str:
        """
        Obtiene logs de un servicio
        
        Args:
            name: Nombre del servicio
            lines: Número de líneas a obtener
            
        Returns:
            Logs del servicio
        """
        try:
            result = subprocess.run(
                ["journalctl", "-u", f"{name}.service", "-n", str(lines), "--no-pager"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error obteniendo logs: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def search_services(self, query: str) -> List[Dict]:
        """
        Busca servicios por nombre o descripción
        
        Args:
            query: Texto a buscar
            
        Returns:
            Lista de servicios que coinciden
        """
        query = query.lower()
        all_services = self.get_services()
        
        return [s for s in all_services 
                if query in s['name'].lower() or query in s['description'].lower()]
    
    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas de servicios
        
        Returns:
            Diccionario con estadísticas
        """
        services = self.get_services()
        
        total = len(services)
        active = len([s for s in services if s['active'] == 'active'])
        inactive = len([s for s in services if s['active'] == 'inactive'])
        failed = len([s for s in services if s['active'] == 'failed'])
        enabled = len([s for s in services if s['enabled']])
        
        return {
            'total': total,
            'active': active,
            'inactive': inactive,
            'failed': failed,
            'enabled': enabled
        }
    
    def set_sort(self, column: str, reverse: bool = False):
        """
        Configura el orden
        
        Args:
            column: Columna por la que ordenar (name, state)
            reverse: Si ordenar invertido
        """
        self.sort_by = column
        self.sort_reverse = reverse
    
    def set_filter(self, filter_type: str):
        """
        Configura el filtro
        
        Args:
            filter_type: Tipo de filtro (all, active, inactive, failed)
        """
        self.filter_type = filter_type
    
    def get_state_color(self, state: str) -> str:
        """
        Obtiene color según estado
        
        Args:
            state: Estado del servicio (active, inactive, failed)
            
        Returns:
            Nombre del color en COLORS
        """
        if state == "active":
            return "success"
        elif state == "failed":
            return "danger"
        else:
            return "text_dim"
```

### 2.2 Actualizar `core/__init__.py`

Añadir al final:
```python
from .service_monitor import ServiceMonitor

__all__ = [
    'FanController',
    'SystemMonitor',
    'NetworkMonitor',
    'FanAutoService',
    'DiskMonitor',
    'ProcessMonitor',
    'ServiceMonitor'  # ← NUEVO
]
```

---

## Paso 3: Crear la ventana ServiceWindow

### 3.1 Crear archivo `ui/windows/service.py`

```python
"""
Ventana de monitor de servicios systemd
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from ui.styles import make_futuristic_button
from ui.widgets import confirm_dialog, custom_msgbox
from core.service_monitor import ServiceMonitor


class ServiceWindow(ctk.CTkToplevel):
    """Ventana de monitor de servicios"""
    
    def __init__(self, parent, service_monitor: ServiceMonitor):
        super().__init__(parent)
        
        # Referencias
        self.service_monitor = service_monitor
        
        # Estado
        self.search_var = ctk.StringVar()
        self.filter_var = ctk.StringVar(value="all")
        self.update_paused = False
        self.update_job = None
        
        # Configurar ventana
        self.title("Monitor de Servicios")
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
        
        # Título y estadísticas
        self._create_header(main)
        
        # Controles (búsqueda y filtros)
        self._create_controls(main)
        
        # Encabezados de columnas
        self._create_column_headers(main)
        
        # Área de scroll para servicios
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Limitar altura
        max_height = DSI_HEIGHT - 250
        
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
        
        # Frame interno para servicios
        self.service_frame = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=self.service_frame, anchor="nw", width=DSI_WIDTH-50)
        self.service_frame.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Botones inferiores
        bottom = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=10, padx=10)
        
        refresh_btn = make_futuristic_button(
            bottom,
            text="Refrescar",
            command=self._force_update,
            width=15,
            height=6
        )
        refresh_btn.pack(side="left", padx=5)
        
        close_btn = make_futuristic_button(
            bottom,
            text="Cerrar",
            command=self.destroy,
            width=15,
            height=6
        )
        close_btn.pack(side="right", padx=5)
    
    def _create_header(self, parent):
        """Crea el encabezado con estadísticas"""
        header = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        header.pack(fill="x", padx=10, pady=(10, 5))
        
        title = ctk.CTkLabel(
            header,
            text="MONITOR DE SERVICIOS",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold")
        )
        title.pack(pady=(10, 5))
        
        self.stats_label = ctk.CTkLabel(
            header,
            text="Cargando...",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        self.stats_label.pack(pady=(0, 10))
    
    def _create_controls(self, parent):
        """Crea controles de búsqueda y filtros"""
        controls = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        controls.pack(fill="x", padx=10, pady=5)
        
        # Búsqueda
        search_frame = ctk.CTkFrame(controls, fg_color=COLORS['bg_dark'])
        search_frame.pack(side="left", padx=10, pady=10)
        
        ctk.CTkLabel(
            search_frame,
            text="Buscar:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(0, 5))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            width=200,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        search_entry.pack(side="left")
        search_entry.bind("<KeyRelease>", lambda e: self._on_search_change())
        
        # Filtros
        filter_frame = ctk.CTkFrame(controls, fg_color=COLORS['bg_dark'])
        filter_frame.pack(side="left", padx=20, pady=10)
        
        ctk.CTkLabel(
            filter_frame,
            text="Filtro:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(0, 5))
        
        for filter_type, label in [("all", "Todos"), ("active", "Activos"), 
                                   ("inactive", "Inactivos"), ("failed", "Fallidos")]:
            rb = ctk.CTkRadioButton(
                filter_frame,
                text=label,
                variable=self.filter_var,
                value=filter_type,
                command=self._on_filter_change,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=5)
            from ui.styles import StyleManager
            StyleManager.style_radiobutton_ctk(rb)
    
    def _create_column_headers(self, parent):
        """Crea encabezados de columnas"""
        headers = ctk.CTkFrame(parent, fg_color=COLORS['bg_light'])
        headers.pack(fill="x", padx=10, pady=(5, 0))
        
        headers.grid_columnconfigure(0, weight=2, minsize=150)  # Servicio
        headers.grid_columnconfigure(1, weight=1, minsize=100)  # Estado
        headers.grid_columnconfigure(2, weight=1, minsize=80)   # Autostart
        headers.grid_columnconfigure(3, weight=3, minsize=300)  # Acciones
        
        columns = [
            ("Servicio", "name"),
            ("Estado", "state"),
            ("Autostart", None),
            ("Acciones", None)
        ]
        
        for i, (label, sort_key) in enumerate(columns):
            if sort_key:
                btn = ctk.CTkButton(
                    headers,
                    text=label,
                    command=lambda k=sort_key: self._on_sort_change(k),
                    fg_color=COLORS['bg_medium'],
                    hover_color=COLORS['bg_dark'],
                    font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                    height=30
                )
            else:
                btn = ctk.CTkLabel(
                    headers,
                    text=label,
                    text_color=COLORS['text'],
                    font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
                )
            
            btn.grid(row=0, column=i, sticky="ew", padx=2, pady=5)
    
    def _on_sort_change(self, column: str):
        """Cambia el orden"""
        self.update_paused = True
        
        if self.service_monitor.sort_by == column:
            self.service_monitor.sort_reverse = not self.service_monitor.sort_reverse
        else:
            self.service_monitor.set_sort(column, reverse=False)
        
        self._update_now()
        self.after(2000, self._resume_updates)
    
    def _on_filter_change(self):
        """Cambia el filtro"""
        self.update_paused = True
        self.service_monitor.set_filter(self.filter_var.get())
        self._update_now()
        self.after(2000, self._resume_updates)
    
    def _on_search_change(self):
        """Callback cuando cambia la búsqueda"""
        self.update_paused = True
        
        if hasattr(self, '_search_timer'):
            self.after_cancel(self._search_timer)
        
        self._search_timer = self.after(500, self._do_search)
    
    def _do_search(self):
        """Ejecuta la búsqueda"""
        self._update_now()
        self.after(3000, self._resume_updates)
    
    def _update(self):
        """Actualiza la lista de servicios"""
        if not self.winfo_exists():
            return
        
        if self.update_paused:
            self.update_job = self.after(UPDATE_MS * 5, self._update)  # 10 segundos
            return
        
        self._update_now()
        self.update_job = self.after(UPDATE_MS * 5, self._update)  # 10 segundos
    
    def _update_now(self):
        """Actualiza inmediatamente"""
        if not self.winfo_exists():
            return
        
        # Actualizar estadísticas
        stats = self.service_monitor.get_stats()
        self.stats_label.configure(
            text=f"Total: {stats['total']} | "
                 f"Activos: {stats['active']} | "
                 f"Inactivos: {stats['inactive']} | "
                 f"Fallidos: {stats['failed']} | "
                 f"Autostart: {stats['enabled']}"
        )
        
        # Limpiar servicios anteriores
        for widget in self.service_frame.winfo_children():
            widget.destroy()
        
        # Obtener servicios
        search_query = self.search_var.get()
        if search_query:
            services = self.service_monitor.search_services(search_query)
        else:
            services = self.service_monitor.get_services()
        
        # Limitar a top 30
        services = services[:30]
        
        # Mostrar servicios
        for i, service in enumerate(services):
            self._create_service_row(service, i)
    
    def _create_service_row(self, service: dict, row: int):
        """Crea una fila para un servicio"""
        bg_color = COLORS['bg_dark'] if row % 2 == 0 else COLORS['bg_medium']
        row_frame = ctk.CTkFrame(self.service_frame, fg_color=bg_color)
        row_frame.pack(fill="x", pady=2)
        
        row_frame.grid_columnconfigure(0, weight=2, minsize=150)
        row_frame.grid_columnconfigure(1, weight=1, minsize=100)
        row_frame.grid_columnconfigure(2, weight=1, minsize=80)
        row_frame.grid_columnconfigure(3, weight=3, minsize=300)
        
        # Icono y nombre
        state_icon = "🟢" if service['active'] == 'active' else "🔴"
        state_color = COLORS[self.service_monitor.get_state_color(service['active'])]
        
        name_label = ctk.CTkLabel(
            row_frame,
            text=f"{state_icon} {service['name']}",
            text_color=state_color,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
        )
        name_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Estado
        ctk.CTkLabel(
            row_frame,
            text=service['active'],
            text_color=state_color,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Autostart
        autostart_text = "✓" if service['enabled'] else "✗"
        autostart_color = COLORS['success'] if service['enabled'] else COLORS['text_dim']
        ctk.CTkLabel(
            row_frame,
            text=autostart_text,
            text_color=autostart_color,
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).grid(row=0, column=2, sticky="center", padx=5, pady=5)
        
        # Botones de acción
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=3, sticky="ew", padx=5, pady=3)
        
        # Start/Stop
        if service['active'] == 'active':
            stop_btn = ctk.CTkButton(
                actions_frame,
                text="⏸",
                command=lambda s=service: self._stop_service(s),
                fg_color=COLORS['warning'],
                hover_color=COLORS['danger'],
                width=40,
                height=25,
                font=(FONT_FAMILY, 14)
            )
            stop_btn.pack(side="left", padx=2)
        else:
            start_btn = ctk.CTkButton(
                actions_frame,
                text="▶",
                command=lambda s=service: self._start_service(s),
                fg_color=COLORS['success'],
                hover_color="#00aa00",
                width=40,
                height=25,
                font=(FONT_FAMILY, 14)
            )
            start_btn.pack(side="left", padx=2)
        
        # Restart
        restart_btn = ctk.CTkButton(
            actions_frame,
            text="🔄",
            command=lambda s=service: self._restart_service(s),
            fg_color=COLORS['primary'],
            width=40,
            height=25,
            font=(FONT_FAMILY, 12)
        )
        restart_btn.pack(side="left", padx=2)
        
        # Logs
        logs_btn = ctk.CTkButton(
            actions_frame,
            text="👁",
            command=lambda s=service: self._view_logs(s),
            fg_color=COLORS['bg_light'],
            width=40,
            height=25,
            font=(FONT_FAMILY, 12)
        )
        logs_btn.pack(side="left", padx=2)
        
        # Enable/Disable
        if service['enabled']:
            disable_btn = ctk.CTkButton(
                actions_frame,
                text="⚙",
                command=lambda s=service: self._disable_service(s),
                fg_color=COLORS['text_dim'],
                width=40,
                height=25,
                font=(FONT_FAMILY, 12)
            )
            disable_btn.pack(side="left", padx=2)
        else:
            enable_btn = ctk.CTkButton(
                actions_frame,
                text="⚙",
                command=lambda s=service: self._enable_service(s),
                fg_color=COLORS['secondary'],
                width=40,
                height=25,
                font=(FONT_FAMILY, 12)
            )
            enable_btn.pack(side="left", padx=2)
    
    def _start_service(self, service: dict):
        """Inicia un servicio"""
        def do_start():
            success, message = self.service_monitor.start_service(service['name'])
            custom_msgbox(self, message, "Iniciar Servicio")
            if success:
                self._force_update()
        
        confirm_dialog(
            parent=self,
            text=f"¿Iniciar servicio '{service['name']}'?",
            title="⚠️ Confirmar",
            on_confirm=do_start,
            on_cancel=None
        )
    
    def _stop_service(self, service: dict):
        """Detiene un servicio"""
        def do_stop():
            success, message = self.service_monitor.stop_service(service['name'])
            custom_msgbox(self, message, "Detener Servicio")
            if success:
                self._force_update()
        
        confirm_dialog(
            parent=self,
            text=f"¿Detener servicio '{service['name']}'?\n\n"
                 f"El servicio dejará de funcionar.",
            title="⚠️ Confirmar",
            on_confirm=do_stop,
            on_cancel=None
        )
    
    def _restart_service(self, service: dict):
        """Reinicia un servicio"""
        def do_restart():
            success, message = self.service_monitor.restart_service(service['name'])
            custom_msgbox(self, message, "Reiniciar Servicio")
            if success:
                self._force_update()
        
        confirm_dialog(
            parent=self,
            text=f"¿Reiniciar servicio '{service['name']}'?",
            title="⚠️ Confirmar",
            on_confirm=do_restart,
            on_cancel=None
        )
    
    def _view_logs(self, service: dict):
        """Muestra logs de un servicio"""
        logs = self.service_monitor.get_logs(service['name'], lines=30)
        
        # Crear ventana de logs
        logs_window = ctk.CTkToplevel(self)
        logs_window.title(f"Logs: {service['name']}")
        logs_window.geometry("700x500")
        
        # Textbox con logs
        textbox = ctk.CTkTextbox(
            logs_window,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wrap="word"
        )
        textbox.pack(fill="both", expand=True, padx=10, pady=10)
        textbox.insert("1.0", logs)
        textbox.configure(state="disabled")
        
        # Botón cerrar
        close_btn = make_futuristic_button(
            logs_window,
            text="Cerrar",
            command=logs_window.destroy,
            width=15,
            height=6
        )
        close_btn.pack(pady=10)
    
    def _enable_service(self, service: dict):
        """Habilita autostart"""
        def do_enable():
            success, message = self.service_monitor.enable_service(service['name'])
            custom_msgbox(self, message, "Habilitar Autostart")
            if success:
                self._force_update()
        
        confirm_dialog(
            parent=self,
            text=f"¿Habilitar autostart para '{service['name']}'?\n\n"
                 f"El servicio se iniciará automáticamente al arrancar.",
            title="⚠️ Confirmar",
            on_confirm=do_enable,
            on_cancel=None
        )
    
    def _disable_service(self, service: dict):
        """Deshabilita autostart"""
        def do_disable():
            success, message = self.service_monitor.disable_service(service['name'])
            custom_msgbox(self, message, "Deshabilitar Autostart")
            if success:
                self._force_update()
        
        confirm_dialog(
            parent=self,
            text=f"¿Deshabilitar autostart para '{service['name']}'?\n\n"
                 f"El servicio NO se iniciará automáticamente al arrancar.",
            title="⚠️ Confirmar",
            on_confirm=do_disable,
            on_cancel=None
        )
    
    def _force_update(self):
        """Fuerza actualización inmediata"""
        self.update_paused = False
        self._update_now()
    
    def _resume_updates(self):
        """Reanuda actualizaciones"""
        self.update_paused = False
```

### 3.2 Actualizar `ui/windows/__init__.py`

Añadir:
```python
from .service import ServiceWindow

__all__ = [
    'MonitorWindow',
    'NetworkWindow',
    'USBWindow',
    'LaunchersWindow',
    'ThemeSelector',
    'FanControlWindow',
    'DiskWindow',
    'ProcessWindow',
    'ServiceWindow'  # ← NUEVO
]
```

---

## Paso 4: Añadir botón al menú principal

### 4.1 Actualizar `main.py`

En la sección de imports (~línea 15):
```python
from core import (SystemMonitor, FanController, NetworkMonitor, 
                  FanAutoService, DiskMonitor, ProcessMonitor, ServiceMonitor)  # ← Añadir
```

Después de crear los otros monitores (~línea 60):
```python
process_monitor = ProcessMonitor()
service_monitor = ServiceMonitor()  # ← NUEVO
```

Al crear MainWindow (~línea 79):
```python
app = MainWindow(
    root,
    system_monitor=system_monitor,
    fan_controller=fan_controller,
    network_monitor=network_monitor,
    disk_monitor=disk_monitor,
    process_monitor=process_monitor,
    service_monitor=service_monitor,  # ← NUEVO
    update_interval=UPDATE_MS
)
```

### 4.2 Actualizar `ui/main_window.py`

En el método `__init__` (~línea 14):
```python
def __init__(self, root, system_monitor, fan_controller, network_monitor, 
             disk_monitor, process_monitor, service_monitor, update_interval=2000):  # ← Añadir
    # ...
    self.service_monitor = service_monitor  # ← Añadir
```

En `_create_menu_buttons` añadir botón (~línea 128):
```python
buttons_config = [
    ("Control Ventiladores", self.open_fan_control),
    ("Monitor Placa", self.open_monitor_window),
    ("Monitor Red", self.open_network_window),
    ("Monitor USB", self.open_usb_window),
    ("Monitor Disco", self.open_disk_window),
    ("Lanzadores", self.open_launchers),
    ("Monitor Procesos", self.open_process_window),
    ("Monitor Servicios", self.open_service_window),  # ← NUEVO
    ("Cambiar Tema", self.open_theme_selector),
    ("Salir", self.exit_application),
]
```

En `__init__` añadir variable (~línea 40):
```python
self.service_window = None  # ← NUEVO
```

Añadir método al final de la clase:
```python
def open_service_window(self):
    """Abre el monitor de servicios"""
    if self.service_window is None or not self.service_window.winfo_exists():
        from ui.windows.service import ServiceWindow
        self.service_window = ServiceWindow(
            self.root,
            self.service_monitor
        )
    else:
        self.service_window.lift()
```

---

## Paso 5: Probar todo

### 5.1 Ejecutar el dashboard

```bash
python3 main.py
```

### 5.2 Abrir Monitor de Servicios

Clic en "Monitor Servicios" en el menú principal.

### 5.3 Probar funcionalidades

**Buscar:**
- Escribe "nginx" → Debería filtrar solo nginx

**Filtrar:**
- Selecciona "Activos" → Solo servicios activos
- Selecciona "Fallidos" → Solo servicios fallidos

**Ordenar:**
- Clic en "Servicio" → Ordena alfabéticamente
- Clic en "Estado" → Ordena por estado (active primero)

**Acciones:**
- **▶** Inicia servicio (requiere sudo)
- **⏸** Detiene servicio (requiere sudo)
- **🔄** Reinicia servicio (requiere sudo)
- **👁** Ver logs del servicio
- **⚙** Enable/Disable autostart (requiere sudo)

### 5.4 Configurar sudo sin contraseña (opcional)

Para que no pida contraseña cada vez:

```bash
sudo visudo
```

Añadir al final:
```
tu-usuario ALL=(ALL) NOPASSWD: /bin/systemctl
```

Reemplaza `tu-usuario` con tu nombre de usuario.

---

## 🎯 Resultado Final

Ahora tienes un **Monitor de Servicios completo** que:
- ✅ Lista todos los servicios systemd
- ✅ Muestra estado (active/inactive/failed)
- ✅ Indica autostart (enabled/disabled)
- ✅ Permite Start/Stop/Restart servicios
- ✅ Muestra logs en tiempo real
- ✅ Habilita/deshabilita autostart
- ✅ Búsqueda y filtros
- ✅ Actualización automática cada 10s
- ✅ Confirmación antes de cada acción

---

## ⚠️ Consideraciones de Seguridad

1. **Requiere permisos sudo**: Las operaciones sobre servicios requieren sudo
2. **Servicios críticos**: Ten cuidado al detener servicios del sistema
3. **Logs sensibles**: Los logs pueden contener información sensible

**No detengas estos servicios:**
- `systemd` (PID 1)
- `dbus`
- `NetworkManager` (perderás red)
- `sshd` (si estás conectado por SSH)

---

## 🚀 Mejoras Futuras

- [ ] Ver dependencias de servicios
- [ ] Gráficas de uso de recursos por servicio
- [ ] Ejecutar comandos personalizados en servicios
- [ ] Export de logs a archivo
- [ ] Alertas cuando un servicio falla
- [ ] Timeline de cambios de estado

---

**¡Monitor de Servicios implementado!** 🔧✨
