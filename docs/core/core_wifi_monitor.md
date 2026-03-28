# `core.wifi_monitor`

> **Ruta**: `core/wifi_monitor.py`

> **Cobertura de documentación**: 🟢 100% (21/21)

Monitor de conexión WiFi profesional.
Recopila SSID, señal (dBm), calidad link, bitrate, ruido, tráfico RX/TX Mbps.
Thread daemon cada 5s, históricos, cambio interfaz en caliente, persistencia.
Fallback ip/iwconfig/ifconfig.

---

## Tabla de contenidos

**Clase [`WiFiMonitor`](#clase-wifimonitor)**
  - [`start()`](#startself)
  - [`stop()`](#stopself)
  - [`is_running()`](#is_runningself-bool)
  - [`get_signal_history()`](#get_signal_historyself-list)
  - [`set_interface()`](#set_interfaceself-iface-str-none)
  - [`get_available_interfaces()`](#get_available_interfaces-list)
  - [`get_stats()`](#get_statsself-dict)
  - [`interface()`](#interfaceself-str)
  - [`signal_color()`](#signal_colordbm-optionalint-colors-dict-str)
  - [`signal_quality_pct()`](#signal_quality_pctdbm-optionalint-int)

---

## Dependencias internas

- `config.local_settings_io`
- `config.settings`
- `utils.logger`

## Imports

```python
import re
import subprocess
import threading
from collections import deque
from typing import Optional
from config.settings import HISTORY
from datetime import datetime
from utils.logger import get_logger
from config.local_settings_io import get_param
from config.local_settings_io import update_params
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `WIFI_SIGNAL_GOOD` | `-60` |
| `WIFI_SIGNAL_WARN` | `-75` |

<details>
<summary>Funciones privadas</summary>

### `_run(cmd: list) -> str`

Ejecuta comando shell y retorna stdout limpio o vacío en fallo.

Timeout 5s. Log warning en exceptions.

### `_parse_iwconfig(raw: str) -> dict`

Parsea salida `iwconfig <iface>` → métricas WiFi.

Returns:
    dict: {"ssid": str, "signal_dbm": int|None, "link_quality": int|None, 
           "link_quality_max": int|None, "bitrate": str, "noise_dbm": int|None}

### `_parse_iw_link(raw: str) -> dict`

Parsea salida `iw dev <iface> link` como fallback.

Returns:
    dict: {"ssid": str, "signal_dbm": int|None, "bitrate": str}

</details>

## Clase `WiFiMonitor`

Monitor completo de WiFi con históricos, tráfico realtime, cambio interfaz dinámica.

Thread-safe, persistencia interfaz, umbrales dBm, métricas iwconfig/iw fallback.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_iface` | `interface or self._load_saved_interface() or _IFACE_DEFAULT` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |
| `_lock` | `threading.Lock()` |
| `_thread` | `None` |
| `_signal_hist` | `deque(maxlen=HISTORY)` |
| `_rx_hist` | `deque(maxlen=HISTORY)` |
| `_tx_hist` | `deque(maxlen=HISTORY)` |

### Métodos públicos

#### `start(self)`

Inicia thread daemon de polling cada 5s.

Idempotente, log interfaz.

#### `stop(self)`

Detiene servicio.

Join 6s, resetea estado. Log.

#### `is_running(self) -> bool`

Estado running.

Returns:
    bool

#### `get_signal_history(self) -> list`

Histórico señal dBm (últimos HISTORY puntos).

Returns:
    list[int]

#### `set_interface(self, iface: str) -> None`

Cambia interfaz en runtime.

Resetea históricos/tráfico. Persiste. Próximo poll usa nueva iface.

#### `get_available_interfaces() -> list`

Lista wlan* interfaces desde /proc/net/dev.

Returns:
    list[str]: sorted wlan0, wlan1...

#### `get_stats(self) -> dict`

Snapshot completo thread-safe no-bloqueante.

Returns:
    dict: info, velocidades, históricos, timestamp.

#### `interface(self) -> str`

Interfaz actual (read-only).

Returns:
    str: e.g. "wlan0"

#### `signal_color(dbm: Optional[int], colors: dict) -> str`

Color semáforo por dBm.

Args:
    dbm (int|None): Nivel señal.
    colors (dict): {'success', 'warning', 'danger', 'text_dim'}

Returns:
    str: Clave color.

#### `signal_quality_pct(dbm: Optional[int]) -> int`

Convierte dBm → % calidad (0-100, no lineal).

Returns:
    int: 0 (pésimo) - 100 (excelente)

<details>
<summary>Métodos privados</summary>

#### `__init__(self, interface: Optional[str] = None)`

Inicializa monitor.

Args:
    interface (str, optional): wlan0/wlan1. Prioridad: arg → settings → wlan0.

#### `_load_saved_interface() -> Optional[str]`

Carga interfaz desde local_settings.py.

Returns:
    str or None

#### `_persist_interface(iface: str) -> None`

Persiste iface en local_settings.py.

#### `_loop(self)`

Thread loop: poll inicial + repeat cada _POLL_INTERVAL.

#### `_poll(self)`

Ciclo de polling: iwconfig/iw + proc/net/dev → update info/hist/tráfico.

#### `_read_proc_net_dev(self, iface: str) -> tuple`

Lee bytes RX/TX desde /proc/net/dev para iface.

Returns:
    tuple[int, int]: (rx_bytes, tx_bytes)

#### `_calc_speed(self, rx: int, tx: int) -> tuple`

Calcula Mbps desde bytes prev/current div _POLL_INTERVAL.

Actualiza _prev_rx/tx. Wrap around manejo max(0, delta).

Returns:
    tuple[float, float]: (rx_mbps, tx_mbps)

</details>
