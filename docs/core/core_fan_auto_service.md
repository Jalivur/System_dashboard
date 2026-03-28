# `core.fan_auto_service`

> **Ruta**: `core/fan_auto_service.py`

> **Cobertura de documentación**: 🟢 100% (10/10)

Servicio en segundo plano para modo AUTO de ventiladores

---

## Tabla de contenidos

**Clase [`FanAutoService`](#clase-fanautoservice)**
  - [`start()`](#start)
  - [`stop()`](#stop)
  - [`is_running()`](#is_running)
  - [`set_update_interval()`](#set_update_interval)
  - [`get_status()`](#get_status)
  - [`__new__()`](#__new__) _(privado)_
  - [`__init__()`](#__init__) _(privado)_
  - [`_run()`](#_run) _(privado)_
  - [`_update_auto_mode()`](#_update_auto_mode) _(privado)_

---

## Dependencias internas

- `core.fan_controller`
- `core.system_monitor`
- `utils`
- `utils.logger`

## Imports

```python
import threading
import time
from typing import Optional
from core.fan_controller import FanController
from core.system_monitor import SystemMonitor
from utils import FileManager
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `FanAutoService`

Servicio que actualiza automáticamente el PWM en modo AUTO.

Args:
    fan_controller (FanController): Controlador del ventilador.
    system_monitor (SystemMonitor): Monitor del sistema.

Returns:
    None

Raises:
    None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_fan_controller` | `fan_controller` |
| `_system_monitor` | `system_monitor` |
| `_file_manager` | `FileManager()` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |
| `_update_interval` | `2.0` |
| `_initialized` | `True` |

### Métodos públicos

#### `start()`

```python
start(self)
```

Inicia el servicio en segundo plano.

Args:
    Ninguno, utiliza atributos de instancia para la configuración.

Returns:
    Ninguno.

Raises:
    Ninguno.

#### `stop()`

```python
stop(self)
```

Detiene el servicio de ajuste automático del ventilador.

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

Indica si el servicio de ventilador automático está en ejecución.

Args:
    None

Returns:
    bool: True si el servicio está corriendo, False de lo contrario.

Raises:
    None

#### `set_update_interval()`

```python
set_update_interval(self, seconds: float)
```

Establece el intervalo de tiempo entre actualizaciones de polling auto-PWM.

Args:
    seconds (float): Intervalo en segundos entre actualizaciones.

Returns:
    None

Raises:
    None

#### `get_status()`

```python
get_status(self) -> dict
```

Retorna el estado actual del servicio de ventilador.

Args:
    None

Returns:
    dict: Diccionario con el estado del servicio, incluyendo si está en ejecución, 
          el intervalo de actualización y el estado del hilo.

Raises:
    None

### Métodos privados

#### `__new__()`

```python
__new__(cls, *args, **kwargs)
```

Crea una instancia única del servicio de forma thread-safe.

Args:
    *args: Argumentos posicionales.
    **kwargs: Argumentos clave-valor.

Returns:
    La instancia única del servicio.

#### `__init__()`

```python
__init__(self, fan_controller: FanController, system_monitor: SystemMonitor)
```

Inicializa el servicio de control de ventilador de forma automática.

Args:
    fan_controller (FanController): Controlador para calcular PWM.
    system_monitor (SystemMonitor): Monitor del sistema para obtener temperatura CPU.

#### `_run()`

```python
_run(self)
```

Ejecuta el bucle principal del servicio de ventilador automático.

Args:
    None

Returns:
    None

Raises:
    Exception

#### `_update_auto_mode()`

```python
_update_auto_mode(self)
```

Actualiza el modo automático del ventilador si está activado.

Args:
    None

Returns:
    None

Raises:
    Exception: Si ocurre un error al cargar o guardar el estado o al obtener estadísticas del sistema.
