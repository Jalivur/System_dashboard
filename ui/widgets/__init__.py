"""
Paquete de widgets personalizados
"""
from .graphs import GraphWidget, update_graph_lines, recolor_lines
from .dialogs import custom_msgbox, confirm_dialog, terminal_dialog

__all__ = ['GraphWidget', 'update_graph_lines', 'recolor_lines', 
           'custom_msgbox', 'confirm_dialog', 'terminal_dialog']
