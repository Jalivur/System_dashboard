# `core.network_monitor`

> **Ruta**: `core/network_monitor.py`

> **Cobertura de documentación**: 🟢 100% (15/15)

Monitor de red

---

## Tabla de contenidos

**Clase [`NetworkMonitor`](#clase-networkmonitor)**
  - [`start()`](#start)
  - [`stop()`](#stop)
  - [`is_running()`](#is_running)
  - [`get_current_stats()`](#get_current_stats)
  - [`update_history()`](#update_history)
  - [`adaptive_scale()`](#adaptive_scale)
  - [`update_dynamic_scale()`](#update_dynamic_scale)
  - [`get_history()`](#get_history)
  - [`run_speedtest()`](#run_speedtest)
  - [`get_speedtest_result()`](#get_speedtest_result)
  - [`reset_speedtest()`](#reset_speedtest)
  - [`net_color()`](#net_color)
  - [`__init__()`](#__init__) _(privado)_

---

## Dependencias internas

- `config.settings`
- `utils.logger`
- `utils.system_utils`

## Imports

```python
import json
import threading
import subprocess
from collections import deque
from typing import Dict, Optional
from config.settings import HISTORY, NET_MIN_SCALE, NET_MAX_SCALE, NET_IDLE_THRESHOLD, NET_IDLE_RESET_TIME, NET_MAX_MB, COLORS, NET_WARN, NET_CRIT
from utils.system_utils import SystemUtils
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `NetworkMonitor`

Inicia y gestiona el monitor de red para recopilar estadísticas y realizar pruebas de velocidad.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_system_utils` | `SystemUtils()` |
| `_running` | `True` |
| `_download_hist` | `deque(maxlen=HISTORY)` |
| `_upload_hist` | `deque(maxlen=HISTORY)` |
| `_last_net_io` | `{}` |
| `_last_used_iface` | `None` |
| `_dynamic_max` | `NET_MAX_MB` |
| `_idle_counter` | `0` |
| `_speedtest_result` | `{'status': 'idle', 'ping': 0, 'download': 0.0, 'upload': 0.0}` |

### Métodos públicos

#### `start()`

```python
start(self) -> None
```

Inicia el monitor de red.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `stop()`

```python
stop(self) -> None
```

Detiene el monitor de red y limpia los historiales y caché de speedtest.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `is_running()`

```python
is_running(self) -> bool
```

Indica si el monitor de red está actualmente activo.

Returns:
    bool: True si el monitor está activo, False en caso contrario.

#### `get_current_stats()`

```python
get_current_stats(self, interface: Optional[str] = None) -> Dict
```

Obtiene estadísticas actuales de red de una interfaz específica o mediante auto-detección.

Args:
    interface (str, opcional): Nombre de la interfaz de red o None para auto-detección. Por defecto es None.

Returns:
    dict: Diccionario con estadísticas de red, incluyendo la interfaz, velocidad de descarga y velocidad de subida.

Raises:
    None

#### `update_history()`

```python
update_history(self, stats: Dict) -> None
```

Actualiza el historial de velocidades de descarga y subida con los estadísticos proporcionados.

Args:
    stats (Dict): Diccionario con claves 'download_mb' y 'upload_mb' que contienen las velocidades de descarga y subida en megabytes.

Returns:
    None

Raises:
    None

#### `adaptive_scale()`

```python
adaptive_scale(self, current_max: float, recent_data: list) -> float
```

Ajusta la escala gráfica de manera adaptativa según los picos recientes de datos.

Args:
    current_max (float): El máximo actual de la escala.
    recent_data (list): Lista de datos de velocidades en MB/s de los últimos registros.

Returns:
    float: La nueva escala ajustada dentro del rango NET_MIN_SCALE a NET_MAX_SCALE.

Raises:
    None

#### `update_dynamic_scale()`

```python
update_dynamic_scale(self) -> None
```

Recalcula el máximo dinámico de escala en función del historial combinado de descarga y subida.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `get_history()`

```python
get_history(self) -> Dict
```

Obtiene el historial de uso de red.

Args: 
    Ninguno

Returns:
    Dict: Diccionario con los historiales de descarga y subida, y el máximo dinámico.

Raises:
    Ninguno

#### `run_speedtest()`

```python
run_speedtest(self) -> None
```

Ejecuta una prueba de velocidad de red utilizando la herramienta speedtest CLI de Ookla en un hilo separado.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `get_speedtest_result()`

```python
get_speedtest_result(self) -> Dict
```

Obtiene el resultado del speedtest.

Args:
    Ninguno

Returns:
    Dict: Una copia del resultado del speedtest.

Raises:
    Ninguno

#### `reset_speedtest()`

```python
reset_speedtest(self) -> None
```

Restablece el estado del test de velocidad a su condición inicial.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `net_color()`

```python
net_color(value: float) -> str
```

Determina el color según el tráfico de red en función de un valor de velocidad.

Args:
    value (float): Velocidad en MB/s.

Returns:
    str: Color en formato hexadecimal.

Raises:
    None

### Métodos privados

#### `__init__()`

```python
__init__(self)
```

Inicializa el monitor de red con historiales y configuraciones por defecto.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno
