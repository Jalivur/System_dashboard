"""
Gestor centralizado de ventanas y botones del menú principal.

Controla qué botones son visibles según la sección "ui" de services.json.
Los servicios y los botones son decisiones INDEPENDIENTES — parar un servicio
no oculta su botón, y ocultar un botón no para su servicio.

Uso en MainWindow:
    self._wm = WindowManager(registry, self._menu_btns)
    self._wm.apply_config()   # oculta los botones deshabilitados en el JSON
"""
from utils.logger import get_logger

logger = get_logger(__name__)


class WindowManager:
    """
    Gestiona la visibilidad de botones del menú recolocándolos sin huecos.

    Mapeo: clave del JSON "ui" → texto exacto del botón en MainWindow.
    Cuando cambia la visibilidad de cualquier botón se rehace el grid completo
    solo con los botones visibles, en orden, 2 columnas.
    """

    # Mapeo clave_json → texto exacto del botón (iconos incluidos tal cual)
    _BTN_MAP = {
        "fan_control":      "󰈐  Control Ventiladores",
        "led_window":       "󰟖  LEDs RGB",
        "monitor_window":   "󰚗  Monitor Placa",
        "network_window":   "🌐 Monitor Red",
        "usb_window":       "󱇰 Monitor USB",
        "disk_window":      "  Monitor Disco",
        "launchers":        "󱓞  Lanzadores",
        "process_window":   "⚙️ Monitor Procesos",
        "service_window":   "⚙️ Monitor Servicios",
        "services_manager": "⚙️  Servicios Dashboard",
        "crontab_window":   "🕐  Gestor Crontab",
        "history_window":   "󱘿  Histórico Datos",
        "update_window":    "󰆧  Actualizaciones",
        "homebridge":       "󰟐  Homebridge",
        "log_viewer":       "󰷐  Visor de Logs",
        "network_local":    "🖧  Red Local",
        "pihole":           "🕳  Pi-hole",
        "vpn_window":       "🔒  Gestor VPN",
        "alert_history":    "  Historial Alertas",
        "display_window":   "󰃟  Brillo Pantalla",
        "overview":         "📊  Resumen Sistema",
        "camera_window":    "📷  Cámara",
        "theme_selector":   "󰔎  Cambiar Tema",
        # Reiniciar y Salir son siempre visibles — no están en el JSON
    }

    # Botones siempre visibles, van siempre al final
    _ALWAYS_VISIBLE = [
        "🔧  Gestor de Botones",
        "󰑓 Reiniciar",
        "󰿅  Salir",
    ]

    def __init__(self, registry, menu_btns: dict):
        self._registry  = registry
        self._menu_btns = menu_btns
        self._columns   = 2

    def apply_config(self) -> None:
        """Aplica la configuración inicial y rehace el grid."""
        self._regrid()

    def show(self, key: str) -> None:
        """Hace visible un botón y rehace el grid."""
        self._registry._config["ui"][key] = True
        self._regrid()
        logger.info("[WindowManager] Botón visible: %s", key)

    def hide(self, key: str) -> None:
        """Oculta un botón y rehace el grid."""
        self._registry._config["ui"][key] = False
        self._regrid()
        logger.info("[WindowManager] Botón oculto: %s", key)

    def _regrid(self) -> None:
        """Saca todos del grid y recoloca solo los visibles, sin huecos."""
        # 1. Sacar todos del grid
        for btn in self._menu_btns.values():
            btn.grid_remove()

        # 2. Botones controlables visibles (en orden del _BTN_MAP)
        visible = []
        for key, btn_text in self._BTN_MAP.items():
            btn = self._menu_btns.get(btn_text)
            if btn is None:
                continue
            if self._registry.ui_enabled(key):
                visible.append(btn)

        # 3. Botones siempre visibles al final
        for btn_text in self._ALWAYS_VISIBLE:
            btn = self._menu_btns.get(btn_text)
            if btn is not None:
                visible.append(btn)

        # 4. Recolocar en grid 2 columnas
        for i, btn in enumerate(visible):
            btn.grid(row=i // self._columns, column=i % self._columns,
                     padx=10, pady=10, sticky="nsew")
