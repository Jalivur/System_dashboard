# `core.system_monitor`

> **Ruta**: `core/system_monitor.py`

> **Cobertura de documentación**: 🟢 100% (11/11)

Monitor del sistema
Monitor centralizado de métricas CPU, RAM, temperatura y uptime con histórico para UI.
Thread background no-bloqueante, thread-safe con lock.

---

## Tabla de contenidos

**Clase [`SystemMonitor`](#clase-systemmonitor)**
  - [`start()`](#start)
  - [`stop()`](#stop)
  - [`is_running()`](#is_running)
  - [`get_current_stats()`](#get_current_stats)
  - [`update_history()`](#update_history)
  - [`get_history()`](#get_history)
  - [`level_color()`](#level_color)
  - [`__init__()`](#__init__) _(privado)_
  - [`_poll_loop()`](#_poll_loop) _(privado)_
  - [`_do_poll()`](#_do_poll) _(privado)_

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

Inicializa el monitor del sistema.

Crea las utilidades del sistema, inicializa los historiales de métricas,
configura el caché y el bloqueo de acceso. Inicia automáticamente el thread
de actualización en segundo plano.

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

#### `start()`

```python
start(self) -> None
```

Inicia el hilo de sondeo en segundo plano para monitorear el sistema.

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

Detiene el monitor del sistema de manera limpia.

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

Indica si el monitor del sistema está actualmente en ejecución.

Returns:
    bool: True si el monitor está activo, False en caso contrario.

#### `get_current_stats()`

```python
get_current_stats(self) -> Dict
```

Obtiene las estadísticas actuales del sistema.

Args:
    Ninguno

Returns:
    Dict: Un diccionario con las estadísticas actuales del sistema, 
          incluyendo 'cpu', 'ram', 'ram_used', 'temp' y 'uptime_str'.

Raises:
    Ninguno

#### `update_history()`

```python
update_history(self, stats: Dict) -> None
```

Actualiza los registros históricos de estadísticas del sistema para su representación gráfica.

Args:
    stats (Dict): Diccionario con las métricas actuales de CPU, RAM y temperatura.

Returns:
    None

Raises:
    None

#### `get_history()`

```python
get_history(self) -> Dict
```

Retorna un diccionario con listas históricas de uso de recursos del sistema.

Args:
    Ninguno

Returns:
    Dict: Un diccionario con claves 'cpu', 'ram', 'temp' y valores correspondientes a listas de históricos.

Raises:
    Ninguno

#### `level_color()`

```python
level_color(value: float, warn: float, crit: float) -> str
```

Determina el color semáforo según umbrales de warning y crítico.

Args:
    value (float): Valor de la métrica (CPU%, RAM%, TEMP).
    warn (float): Umbral de warning.
    crit (float): Umbral crítico.

Returns:
    str: Clase de color correspondiente.

Raises:
    None

### Métodos privados

#### `__init__()`

```python
__init__(self)
```

Inicializa el monitor del sistema.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `_poll_loop()`

```python
_poll_loop(self) -> None
```

Ejecuta el bucle principal del hilo de sondeo en segundo plano.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_do_poll()`

```python
_do_poll(self) -> None
```

Captura rápida de métricas del sistema y actualiza la caché.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno, las excepciones se manejan silenciosamente.
