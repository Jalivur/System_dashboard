"""
Diálogos y ventanas modales personalizadas
"""
import customtkinter as ctk
from ui.styles import make_futuristic_button
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES


def custom_msgbox(parent, text: str, title: str = "Info") -> None:
    """
    Muestra un cuadro de mensaje personalizado
    
    Args:
        parent: Ventana padre
        text: Texto del mensaje
        title: Título del diálogo
    """
    popup = ctk.CTkToplevel(parent)
    popup.overrideredirect(True)
    
    # Contenedor
    frame = ctk.CTkFrame(popup)
    frame.pack(fill="both", expand=True)
    
    # Título
    title_lbl = ctk.CTkLabel(
        frame, 
        text=title,
        text_color=COLORS['primary'],
        font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
    )
    title_lbl.pack(anchor="center", pady=(0, 10))
    
    # Texto
    text_lbl = ctk.CTkLabel(
        frame, 
        text=text,
        text_color=COLORS['text'],
        font=(FONT_FAMILY, FONT_SIZES['medium']),
        compound="left",
        wraplength=800
    )
    text_lbl.pack(anchor="center", pady=(0, 15))
    
    # Botón OK
    btn = make_futuristic_button(
        frame, 
        text="OK",
        command=popup.destroy,
        width=15, 
        height=6, 
        font_size=16
    )
    btn.pack()
    
    # Calcular tamaño
    popup.update_idletasks()
    
    w = popup.winfo_reqwidth()
    h = popup.winfo_reqheight()
    
    max_w = parent.winfo_screenwidth() - 40
    max_h = parent.winfo_screenheight() - 40
    
    w = min(w, max_w)
    h = min(h, max_h)
    
    # Centrar
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (w // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (h // 2)
    
    popup.geometry(f"{w}x{h}+{x}+{y}")
    
    popup.lift()
    popup.focus_force()
    popup.grab_set()


def confirm_dialog(parent, text: str, title: str = "Confirmar", 
                   on_confirm=None, on_cancel=None) -> None:
    """
    Muestra un diálogo de confirmación
    
    Args:
        parent: Ventana padre
        text: Texto del mensaje
        title: Título del diálogo
        on_confirm: Callback al confirmar
        on_cancel: Callback al cancelar
    """
    popup = ctk.CTkToplevel(parent)
    popup.overrideredirect(True)
    
    frame = ctk.CTkFrame(popup)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Título
    title_lbl = ctk.CTkLabel(
        frame, 
        text=title,
        text_color=COLORS['primary'],
        font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
    )
    title_lbl.pack(anchor="center", pady=(0, 10))
    
    # Texto
    text_lbl = ctk.CTkLabel(
        frame, 
        text=text,
        text_color=COLORS['text'],
        font=(FONT_FAMILY, FONT_SIZES['medium']),
        wraplength=600
    )
    text_lbl.pack(anchor="center", pady=(0, 20))
    
    # Botones
    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
    btn_frame.pack()
    
    def _on_confirm():
        popup.destroy()
        if on_confirm:
            on_confirm()
    
    def _on_cancel():
        popup.destroy()
        if on_cancel:
            on_cancel()
    
    btn_confirm = make_futuristic_button(
        btn_frame,
        text="Confirmar",
        command=_on_confirm,
        width=15,
        height=6,
        font_size=16
    )
    btn_confirm.pack(side="left", padx=5)
    
    btn_cancel = make_futuristic_button(
        btn_frame,
        text="Cancelar",
        command=_on_cancel,
        width=15,
        height=6,
        font_size=16
    )
    btn_cancel.pack(side="left", padx=5)
    
    # Centrar
    popup.update_idletasks()
    w = popup.winfo_reqwidth()
    h = popup.winfo_reqheight()
    
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (w // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (h // 2)
    
    popup.geometry(f"{w}x{h}+{x}+{y}")
    
    popup.lift()
    popup.focus_force()
    popup.grab_set()
