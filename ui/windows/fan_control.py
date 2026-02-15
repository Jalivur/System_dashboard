"""
Ventana de control de ventiladores
"""
import tkinter as tk
import customtkinter as ctk
from typing import Optional
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, 
                             DSI_HEIGHT, DSI_X, DSI_Y)
from ui.styles import make_futuristic_button, StyleManager
from ui.widgets import custom_msgbox
from core.fan_controller import FanController
from core.system_monitor import SystemMonitor
from utils.file_manager import FileManager


class FanControlWindow(ctk.CTkToplevel):
    """Ventana de control de ventiladores y curvas PWM"""
    
    def __init__(self, parent, fan_controller: FanController, 
                 system_monitor: SystemMonitor):
        super().__init__(parent)
        
        # Referencias
        self.fan_controller = fan_controller
        self.system_monitor = system_monitor
        self.file_manager = FileManager()
        
        # Variables de estado
        self.mode_var = tk.StringVar()
        self.manual_pwm_var = tk.IntVar(value=128)
        self.curve_vars = []
        
        # Cargar estado inicial
        self._load_initial_state()
        
        # Configurar ventana
        self.title("Control de Ventiladores")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        
        # Crear interfaz
        self._create_ui()
    
    def _load_initial_state(self):
        """Carga el estado inicial desde archivo"""
        state = self.file_manager.load_state()
        self.mode_var.set(state.get("mode", "auto"))
        
        target = state.get("target_pwm")
        if target is not None:
            self.manual_pwm_var.set(target)
    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        # Frame principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Título
        title = ctk.CTkLabel(
            main,
            text="CONTROL DE VENTILADORES",
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
        
        # Frame interno
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>", 
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Sección de modo
        self._create_mode_section(inner)
        
        # Sección PWM manual
        self._create_manual_pwm_section(inner)
        
        # Sección de curva
        self._create_curve_section(inner)
        
        # Botones inferiores
        self._create_bottom_buttons(main)
    
    def _create_mode_section(self, parent):
        """Crea la sección de selección de modo"""
        mode_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        mode_frame.pack(fill="x", pady=10, padx=10)
        
        # Label
        mode_label = ctk.CTkLabel(
            mode_frame,
            text="MODO DE OPERACIÓN",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        )
        mode_label.pack(anchor="w", pady=(0, 10))
        
        # Radiobuttons
        modes_container = ctk.CTkFrame(mode_frame, fg_color=COLORS['bg_medium'])
        modes_container.pack(fill="x", pady=5)
        
        modes = [
            ("Auto", "auto"),
            ("Silent", "silent"),
            ("Normal", "normal"),
            ("Performance", "performance"),
            ("Manual", "manual")
        ]
        
        for text, value in modes:
            rb = ctk.CTkRadioButton(
                modes_container,
                text=text,
                variable=self.mode_var,
                value=value,
                command=lambda v=value: self._on_mode_change(v),
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=8)
            StyleManager.style_radiobutton_ctk(rb)
    
    def _create_manual_pwm_section(self, parent):
        """Crea la sección de PWM manual"""
        manual_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        manual_frame.pack(fill="x", pady=10, padx=10)
        
        # Label
        manual_label = ctk.CTkLabel(
            manual_frame,
            text="PWM MANUAL (0-255)",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        )
        manual_label.pack(anchor="w", pady=(0, 5))
        
        # Valor actual
        self.pwm_value_label = ctk.CTkLabel(
            manual_frame,
            text=f"Valor: {self.manual_pwm_var.get()}",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        self.pwm_value_label.pack(anchor="w", pady=(0, 10))
        
        # Slider
        slider = ctk.CTkSlider(
            manual_frame,
            from_=0,
            to=255,
            variable=self.manual_pwm_var,
            command=self._on_pwm_change,
            width=DSI_WIDTH - 100
        )
        slider.pack(fill="x", pady=5)
        StyleManager.style_slider_ctk(slider)
    
    def _create_curve_section(self, parent):
        """Crea la sección de curva temperatura-PWM"""
        curve_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        curve_frame.pack(fill="x", pady=10, padx=10)
        
        # Label
        curve_label = ctk.CTkLabel(
            curve_frame,
            text="CURVA TEMPERATURA-PWM",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        )
        curve_label.pack(anchor="w", pady=(0, 10))
        
        # Frame para la lista de puntos
        self.points_frame = ctk.CTkFrame(curve_frame, fg_color=COLORS['bg_dark'])
        self.points_frame.pack(fill="x", pady=5, padx=5)
        
        # Cargar y mostrar puntos
        self._refresh_curve_points()
        
        # Botones para añadir punto
        add_frame = ctk.CTkFrame(curve_frame, fg_color=COLORS['bg_medium'])
        add_frame.pack(fill="x", pady=10)
        
        add_label = ctk.CTkLabel(
            add_frame,
            text="Añadir Punto:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        add_label.pack(side="left", padx=5)
        
        # Entry para temperatura
        temp_label = ctk.CTkLabel(
            add_frame,
            text="Temp (°C):",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        temp_label.pack(side="left", padx=5)
        
        self.temp_entry = ctk.CTkEntry(
            add_frame,
            width=60,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        self.temp_entry.pack(side="left", padx=5)
        
        # Entry para PWM
        pwm_label = ctk.CTkLabel(
            add_frame,
            text="PWM:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        pwm_label.pack(side="left", padx=5)
        
        self.pwm_entry = ctk.CTkEntry(
            add_frame,
            width=60,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        self.pwm_entry.pack(side="left", padx=5)
        
        # Botón añadir
        add_btn = make_futuristic_button(
            add_frame,
            text="Añadir",
            command=self._add_curve_point,
            width=10,
            height=4,
            font_size=14
        )
        add_btn.pack(side="left", padx=5)
    
    def _refresh_curve_points(self):
        """Refresca la lista de puntos de la curva"""
        # Limpiar widgets existentes
        for widget in self.points_frame.winfo_children():
            widget.destroy()
        
        # Cargar curva actual
        curve = self.file_manager.load_curve()
        
        if not curve:
            no_points = ctk.CTkLabel(
                self.points_frame,
                text="No hay puntos en la curva",
                text_color=COLORS['warning'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            no_points.pack(pady=10)
            return
        
        # Mostrar cada punto
        for point in curve:
            temp = point['temp']
            pwm = point['pwm']
            
            point_frame = ctk.CTkFrame(self.points_frame, fg_color=COLORS['bg_medium'])
            point_frame.pack(fill="x", pady=2, padx=5)
            
            # Texto del punto
            point_label = ctk.CTkLabel(
                point_frame,
                text=f"{temp}°C → PWM {pwm}",
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            point_label.pack(side="left", padx=10)
            
            # Botón eliminar
            del_btn = make_futuristic_button(
                point_frame,
                text="Eliminar",
                command=lambda t=temp: self._remove_curve_point(t),
                width=10,
                height=3,
                font_size=12
            )
            del_btn.pack(side="right", padx=5)
    
    def _add_curve_point(self):
        """Añade un punto a la curva"""
        try:
            temp = int(self.temp_entry.get())
            pwm = int(self.pwm_entry.get())
            
            if temp < 0 or temp > 100:
                custom_msgbox(self, "La temperatura debe estar entre 0 y 100°C", "Error")
                return
            
            if pwm < 0 or pwm > 255:
                custom_msgbox(self, "El PWM debe estar entre 0 y 255", "Error")
                return
            
            # Añadir punto
            self.fan_controller.add_curve_point(temp, pwm)
            
            # Limpiar entradas
            self.temp_entry.delete(0, 'end')
            self.pwm_entry.delete(0, 'end')
            
            # Refrescar lista
            self._refresh_curve_points()
            
        except ValueError:
            custom_msgbox(self, "Por favor ingresa valores numéricos válidos", "Error")
    
    def _remove_curve_point(self, temp: int):
        """Elimina un punto de la curva"""
        self.fan_controller.remove_curve_point(temp)
        self._refresh_curve_points()
    
    def _create_bottom_buttons(self, parent):
        """Crea los botones inferiores"""
        bottom = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=10, padx=10)
        
        # Botón cerrar
        close_btn = make_futuristic_button(
            bottom,
            text="Cerrar",
            command=self.destroy,
            width=15,
            height=6
        )
        close_btn.pack(side="right", padx=5)
        
        # Botón refrescar
        refresh_btn = make_futuristic_button(
            bottom,
            text="Refrescar Curva",
            command=self._refresh_curve_points,
            width=15,
            height=6
        )
        refresh_btn.pack(side="right", padx=5)
    
    def _on_mode_change(self, mode: str):
        """Callback cuando cambia el modo"""
        self.file_manager.write_state({
            "mode": mode,
            "target_pwm": self.manual_pwm_var.get() if mode == "manual" else None
        })
    
    def _on_pwm_change(self, value):
        """Callback cuando cambia el PWM manual"""
        pwm = int(float(value))
        self.pwm_value_label.configure(text=f"Valor: {pwm}")
        
        if self.mode_var.get() == "manual":
            self.file_manager.write_state({
                "mode": "manual",
                "target_pwm": pwm
            })
