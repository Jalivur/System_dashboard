# `core.disk_monitor`

> **Ruta**: `core/disk_monitor.py`

> **Cobertura de documentación**: 🟢 100% (12/12)

Monitor de disco

---

## Tabla de contenidos

**Clase [`DiskMonitor`](#clase-diskmonitor)**
  - [`start()`](#start)
  - [`stop()`](#stop)
  - [`is_running()`](#is_running)
  - [`get_current_stats()`](#get_current_stats)
  - [`update_history()`](#update_history)
  - [`get_history()`](#get_history)
  - [`get_nvme_smart()`](#get_nvme_smart)
  - [`level_color()`](#level_color)
  - [`__init__()`](#__init__) _(privado)_
  - [`_poll_loop()`](#_poll_loop) _(privado)_
  - [`_do_poll()`](#_do_poll) _(privado)_

---

## Dependencias internas

- `config.settings`
- `utils.system_utils`

## Imports

```python
import subprocess
import json
import threading
from collections import deque
from typing import Dict
from config.settings import HISTORY, UPDATE_MS, COLORS
from utils.system_utils import SystemUtils, get_logger
import psutil
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `DiskMonitor`

Inicializa el monitor de disco con historial y configuraciones de caché y actualización.

Args: 
    None

Returns: 
    None

Raises: 
    None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_system_utils` | `SystemUtils()` |
| `_usage_hist` | `deque(maxlen=HISTORY)` |
| `_read_hist` | `deque(maxlen=HISTORY)` |
| `_write_hist` | `deque(maxlen=HISTORY)` |
| `_nvme_temp_hist` | `deque(maxlen=HISTORY)` |
| `_cache_lock` | `threading.Lock()` |
| `_last_disk_io` | `psutil.disk_io_counters()` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |
| `_thread` | `None` |
| `_interval_s` | `max(UPDATE_MS / 1000.0, 1.0)` |

### Métodos públicos

#### `start()`

```python
start(self)
```

Inicia el monitoreo del disco en segundo plano.

Args:
    None

Returns:
    None

Raises:
    None

#### `stop()`

```python
stop(self)
```

Detiene el monitoreo del disco y libera recursos asociados.

Args: 
    None

Returns: 
    None

Raises: 
    None

#### `is_running()`

```python
is_running(self) -> bool
```

Indica si el servicio de monitoreo de disco está en ejecución.

Args:
    None

Returns:
    bool: True si el servicio está corriendo, False de lo contrario.

Raises:
    None

#### `get_current_stats()`

```python
get_current_stats(self) -> Dict
```

Retorna las estadísticas actuales del disco, incluyendo uso del disco, temperatura NVMe y velocidad de lectura/escritura.

Args:
    None

Returns:
    Dict: Un diccionario con las estadísticas actuales del disco.

Raises:
    None

#### `update_history()`

```python
update_history(self, stats: Dict) -> None
```

Actualiza los historiales de estadísticas del disco con los datos proporcionados.

Args:
    stats (Dict): Diccionario que contiene las estadísticas actuales del disco, 
                  incluyendo 'disk_usage', 'disk_read_mb', 'disk_write_mb' y 'nvme_temp'.

Returns:
    None

Raises:
    KeyError: Si el diccionario stats no contiene alguna clave esperada.

#### `get_history()`

```python
get_history(self) -> Dict
```

Obtiene todos los historiales de uso y rendimiento del disco.

Args:
    No requiere parámetros.

Returns:
    Diccionario con historiales de uso de disco, lecturas, escrituras y temperatura de NVMe.

Raises:
    No lanza excepciones.

#### `get_nvme_smart()`

```python
get_nvme_smart(self) -> dict
```

Recupera las métricas SMART extendidas del dispositivo NVMe mediante smartctl.

Args:
    Ninguno.

Returns:
    Un diccionario con las métricas SMART extendidas del NVMe.

Raises:
    No se lanzan excepciones explícitas, pero puede fallar si no hay dispositivo NVMe disponible o si smartctl no está instalado.

#### `level_color()`

```python
level_color(value: float, warn: float, crit: float) -> str
```

Determina el color según el nivel de un valor en relación con umbrales de advertencia y crítico.

Args:
    value (float): Valor actual
    warn (float): Umbral de advertencia
    crit (float): Umbral crítico

Returns:
    str: Color en formato hex

Raises:
    None

### Métodos privados

#### `__init__()`

```python
__init__(self)
```

Inicializa el monitor de disco con historiales y caché.

Args: None

Returns: None

Raises: None

#### `_poll_loop()`

```python
_poll_loop(self) -> None
```

Ejecuta el bucle principal de monitoreo de disco de forma continua.

Args:
    None

Returns:
    None

Raises:
    None

#### `_do_poll()`

```python
_do_poll(self)
```

Realiza un sondeo del uso del disco y actualiza la caché e historial.

Args:
    None

Returns:
    None

Raises:
    Exception: si ocurre un error durante el sondeo o actualización.
