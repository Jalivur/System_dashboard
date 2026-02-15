"""
Widgets para gráficas y visualización
"""
import customtkinter as ctk
from typing import List
from config.settings import GRAPH_WIDTH, GRAPH_HEIGHT


class GraphWidget:
    """Widget para gráficas de línea"""
    
    def __init__(self, parent, width: int = None, height: int = None):
        """
        Inicializa el widget de gráfica
        
        Args:
            parent: Widget padre
            width: Ancho del canvas
            height: Alto del canvas
        """
        self.width = width or GRAPH_WIDTH
        self.height = height or GRAPH_HEIGHT
        
        self.canvas = ctk.CTkCanvas(
            parent, 
            width=self.width, 
            height=self.height,
            bg="#111111", 
            highlightthickness=0
        )
        
        self.lines = []
        self._create_lines()
    
    def _create_lines(self) -> None:
        """Crea las líneas en el canvas"""
        self.lines = [
            self.canvas.create_line(0, 0, 0, 0, fill="#00ffff", width=2)
            for _ in range(self.width)
        ]
    
    def update(self, data: List[float], max_val: float, color: str = "#00ffff") -> None:
        """
        Actualiza la gráfica con nuevos datos
        
        Args:
            data: Lista de valores a graficar
            max_val: Valor máximo para normalización
            color: Color de las líneas
        """
        if not data or max_val <= 0:
            return
        
        n = len(data)
        if n < 2:
            return
        
        # Calcular puntos
        x_step = self.width / max(n - 1, 1)
        
        for i in range(min(n - 1, len(self.lines))):
            val1 = max(0, min(max_val, data[i]))
            val2 = max(0, min(max_val, data[i + 1]))
            
            y1 = self.height - (val1 / max_val) * self.height
            y2 = self.height - (val2 / max_val) * self.height
            
            x1 = i * x_step
            x2 = (i + 1) * x_step
            
            self.canvas.coords(self.lines[i], x1, y1, x2, y2)
            self.canvas.itemconfig(self.lines[i], fill=color)
    
    def recolor(self, color: str) -> None:
        """
        Cambia el color de todas las líneas
        
        Args:
            color: Nuevo color
        """
        for line in self.lines:
            self.canvas.itemconfig(line, fill=color)
    
    def pack(self, **kwargs):
        """Pack del canvas"""
        self.canvas.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid del canvas"""
        self.canvas.grid(**kwargs)


def update_graph_lines(canvas, lines: List, data: List[float], max_val: float) -> None:
    """
    Actualiza líneas de gráfica (función legacy para compatibilidad)
    
    Args:
        canvas: Canvas de tkinter
        lines: Lista de IDs de líneas
        data: Datos a graficar
        max_val: Valor máximo
    """
    if not data or max_val <= 0:
        return
    
    n = len(data)
    if n < 2:
        return
    
    width = canvas.winfo_width() or GRAPH_WIDTH
    height = canvas.winfo_height() or GRAPH_HEIGHT
    
    x_step = width / max(n - 1, 1)
    
    for i in range(min(n - 1, len(lines))):
        val1 = max(0, min(max_val, data[i]))
        val2 = max(0, min(max_val, data[i + 1]))
        
        y1 = height - (val1 / max_val) * height
        y2 = height - (val2 / max_val) * height
        
        x1 = i * x_step
        x2 = (i + 1) * x_step
        
        canvas.coords(lines[i], x1, y1, x2, y2)


def recolor_lines(canvas, lines: List, color: str) -> None:
    """
    Cambia el color de las líneas (función legacy)
    
    Args:
        canvas: Canvas de tkinter
        lines: Lista de IDs de líneas
        color: Nuevo color
    """
    for line in lines:
        canvas.itemconfig(line, fill=color)
