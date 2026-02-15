"""
Estilos y temas para la interfaz
"""
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES


class StyleManager:
    """Gestor centralizado de estilos"""
    
    @staticmethod
    def style_radiobutton_tk(rb: tk.Radiobutton, 
                            fg: str = None, 
                            bg: str = None, 
                            hover_fg: str = None) -> None:
        """
        Aplica estilo a radiobutton de tkinter
        
        Args:
            rb: Widget radiobutton
            fg: Color de texto
            bg: Color de fondo
            hover_fg: Color al pasar el mouse
        """
        fg = fg or COLORS['primary']
        bg = bg or COLORS['bg_dark']
        hover_fg = hover_fg or COLORS['success']
        
        rb.config(
            fg=fg, 
            bg=bg, 
            selectcolor=bg, 
            activeforeground=fg, 
            activebackground=bg,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), 
            indicatoron=True
        )
        
        def on_enter(e): 
            rb.config(fg=hover_fg)
        
        def on_leave(e): 
            rb.config(fg=fg)
        
        rb.bind("<Enter>", on_enter)
        rb.bind("<Leave>", on_leave)
    
    @staticmethod
    def style_radiobutton_ctk(rb: ctk.CTkRadioButton) -> None:
        """
        Aplica estilo a radiobutton de customtkinter
        
        Args:
            rb: Widget radiobutton
        """
        rb.configure(
            radiobutton_width=25,
            radiobutton_height=25,
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            fg_color=COLORS['primary'],
        )
    
    @staticmethod
    def style_slider(slider: tk.Scale, color: str = None) -> None:
        """
        Aplica estilo a slider de tkinter
        
        Args:
            slider: Widget slider
            color: Color personalizado
        """
        color = color or COLORS['primary']
        slider.config(
            troughcolor=COLORS['secondary'], 
            sliderrelief="flat", 
            bd=0,
            highlightthickness=0, 
            fg=color, 
            bg=COLORS['bg_dark'], 
            activebackground=color
        )
    
    @staticmethod
    def style_slider_ctk(slider: ctk.CTkSlider, color: str = None) -> None:
        """
        Aplica estilo a slider de customtkinter
        
        Args:
            slider: Widget slider
            color: Color personalizado
        """
        color = color or "#10c5c5"
        slider.configure(
            fg_color=COLORS['secondary'],
            progress_color=color,
            button_color=color,
            button_hover_color=color,
            height=30
        )
    
    @staticmethod
    def style_scrollbar(sb: tk.Scrollbar, color: str = None) -> None:
        """
        Aplica estilo a scrollbar de tkinter
        
        Args:
            sb: Widget scrollbar
            color: Color personalizado
        """
        color = color or COLORS['bg_dark']
        sb.config(
            troughcolor=COLORS['secondary'], 
            bg=color, 
            activebackground=color,
            highlightthickness=0, 
            relief="flat"
        )
    
    @staticmethod
    def style_scrollbar_ctk(sb: ctk.CTkScrollbar, color: str = None) -> None:
        """
        Aplica estilo a scrollbar de customtkinter
        
        Args:
            sb: Widget scrollbar
            color: Color personalizado
        """
        color = color or COLORS['bg_dark']
        sb.configure(
            bg_color="#10c5c5",
            button_color=color,
            button_hover_color="#595959"
        )
    
    @staticmethod
    def style_ctk_scrollbar(scrollable_frame: ctk.CTkScrollableFrame, 
                           color: str = None) -> None:
        """
        Aplica estilo a scrollable frame de customtkinter
        
        Args:
            scrollable_frame: Widget scrollable frame
            color: Color personalizado
        """
        color = color or COLORS['secondary']
        scrollable_frame.configure(
            scrollbar_fg_color=color,
            scrollbar_button_color=COLORS['bg_dark'],
            scrollbar_button_hover_color="#595757"
        )


def make_futuristic_button(parent, text: str, command=None, 
                          width: int = None, height: int = None, 
                          font_size: int = None) -> ctk.CTkButton:
    """
    Crea un botón con estilo futurista
    
    Args:
        parent: Widget padre
        text: Texto del botón
        command: Función a ejecutar al hacer clic
        width: Ancho en unidades
        height: Alto en unidades
        font_size: Tamaño de fuente
        
    Returns:
        Widget CTkButton configurado
    """
    width = width or 20
    height = height or 10
    font_size = font_size or FONT_SIZES['large']
    
    btn = ctk.CTkButton(
        parent, 
        text=text, 
        command=command,
        fg_color=COLORS['bg_dark'], 
        hover_color=COLORS['bg_light'],
        border_width=3, 
        border_color=COLORS['border'],
        width=width * 8, 
        height=height * 8,
        font=(FONT_FAMILY, font_size, "bold"), 
        corner_radius=10
    )
    
    def on_enter(e): 
        btn.configure(fg_color=COLORS['bg_light'])
    
    def on_leave(e): 
        btn.configure(fg_color=COLORS['bg_dark'])
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn
