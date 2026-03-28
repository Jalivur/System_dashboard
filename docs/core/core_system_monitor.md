# `core.system_monitor`

> **Ruta**: `core/system_monitor.py`

> **Cobertura de documentación**: 🟢 100% (11/11)

Monitor del sistema
Monitor centralizado de métricas CPU, RAM, temperatura y uptime con histórico para UI.
Thread background no-bloqueante, thread-safe con lock.

---

## Tabla de contenidos

**Clase [`SystemMonitor`](#clase-systemmonitor)**
  - [`start()`](#startself-none)
  - [`stop()`](#stopself-none)
  - [`is_running()`](#is_runningself-bool)
  - [`get_current_stats()`](#get_current_statsself-dict)
  - [`update_history()`](#update_historyself-stats-dict-none)
  - [`get_history()`](#get_historyself-dict)
  - [`level_color()`](#level_colorvalue-float-warn-float-crit-float-str)

---

## Dependencias internas

- `config.settings`
- `utils.logger`
- `utils.system_utils`

## Imports

```python
import time
import threading
import psutil
from collections import deque
from typing import Dict
from config.settings import HISTORY, UPDATE_MS, COLORS
from utils.system_utils import SystemUtils
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `SystemMonitor`

Monitor centralizado de recursos del sistema.

Las métricas se actualizan en un thread de background cada UPDATE_MS ms.
La UI siempre lee del caché (get_current_stats / get_cached_stats),
nunca bloquea el hilo principal de Tkinter.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_system_utils` | `SystemUtils()` |
| `_cpu_hist` | `deque(maxlen=HISTORY)` |
| `_ram_hist` | `deque(maxlen=HISTORY)` |
| `_temp_hist` | `deque(maxlen=HISTORY)` |
| `_cache_lock` | `threading.Lock()` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |
| `_thread` | `None` |
| `_interval_s` | `max(UPDATE_MS / 1000.0, 1.0)` |

### Métodos públicos

#### `start(self) -> None`

Inicia el thread de sondeo background (daemon=True).

Idempotente. Log de inicio con intervalo.

#### `stop(self) -> None`

Detiene el monitor limpiamente.

Join thread timeout 3s, resetea cache. Log de detención.

#### `is_running(self) -> bool`

Indica si el monitor está activo.

Returns:
    bool: True si el thread de polling está corriendo.

#### `get_current_stats(self) -> Dict`

Obtiene métricas actuales del cache (thread-safe).

Returns:
    Dict: {'cpu': float, 'ram': float, 'ram_used': int, 'temp': float, 'uptime_str': str}

#### `update_history(self, stats: Dict) -> None`

Actualiza deques históricos para gráficos (últimos HISTORY puntos).

Args:
    stats (Dict): Métricas actuales CPU/RAM/TEMP.

#### `get_history(self) -> Dict`

Retorna listas históricas para UI/gráficos.

Returns:
    Dict: {'cpu': [...], 'ram': [...], 'temp': [...]}

#### `level_color(value: float, warn: float, crit: float) -> str`

Determina color semáforo por umbrales (primary/warning/danger).

Args:
    value (float): Valor métrica (CPU%, RAM%, TEMP).
    warn (float): Umbral warning.
    crit (float): Umbral crítico.

Returns:
    str: Clase color de config.COLORS.

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el monitor del sistema.

Crea SystemUtils, deques históricos maxlen=HISTORY, cache inicial,
configura lock y parámetros de polling. Inicia automáticamente el thread.

#### `_poll_loop(self) -> None`

Bucle principal del thread de sondeo background (daemon=True).

#### `_do_poll(self) -> None`

Captura rápida de métricas CPU/RAM/TEMP/UPTIME y actualiza caché.
Maneja exceptions silenciosamente.

</details>
