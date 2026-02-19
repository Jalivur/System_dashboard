"""
Paquete de configuración
"""
from .settings import (
    # Rutas
    PROJECT_ROOT,
    DATA_DIR,
    SCRIPTS_DIR,
    STATE_FILE,
    CURVE_FILE,
    # Pantalla
    DSI_WIDTH,
    DSI_HEIGHT,
    DSI_X,
    DSI_Y,
    # Actualización y gráficas
    UPDATE_MS,
    HISTORY,
    GRAPH_WIDTH,
    GRAPH_HEIGHT,
    # Umbrales
    CPU_WARN,
    CPU_CRIT,
    TEMP_WARN,
    TEMP_CRIT,
    RAM_WARN,
    RAM_CRIT,
    # Red
    NET_WARN,
    NET_CRIT,
    NET_INTERFACE,
    NET_MAX_MB,
    NET_MIN_SCALE,
    NET_MAX_SCALE,
    NET_IDLE_THRESHOLD,
    NET_IDLE_RESET_TIME,
    # Lanzadores
    LAUNCHERS,
    # Tema y estilos
    SELECTED_THEME,
    COLORS,
    FONT_FAMILY,
    FONT_SIZES,
)
