# `core.fan_auto_service`

> **Ruta**: `core/fan_auto_service.py`

> **Cobertura de documentación**: 🟢 100% (10/10)

Servicio en segundo plano para modo AUTO de ventiladores

---

## Tabla de contenidos

**Clase [`FanAutoService`](#clase-fanautoservice)**
  - [`start()`](#startself)
  - [`stop()`](#stopself)
  - [`is_running()`](#is_runningself-bool)
  - [`set_update_interval()`](#set_update_intervalself-seconds-float)
  - [`get_status()`](#get_statusself-dict)

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
Se ejecuta en segundo plano independiente de la UI.

Características:
- Singleton: Solo una instancia en toda la aplicación
- Thread-safe: Seguro para concurrencia
- Daemon: Se cierra automáticamente con el programa
- Independiente de UI: Funciona con o sin ventanas abiertas

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

#### `start(self)`

Inicia thread daemon para bucle auto-PWM.

Args:
    Ninguno (usa self._fan_controller, self._system_monitor).

#### `stop(self)`

Detiene el servicio.

#### `is_running(self) -> bool`

Verifica si el servicio está corriendo.

#### `set_update_interval(self, seconds: float)`

Configura intervalo de polling auto-PWM (mín 1s).

Args:
    seconds (float): Segundos entre updates.

#### `get_status(self) -> dict`

Retorna estado para UI (running, interval, thread_alive).

Returns:
    dict: Status dict del servicio.

<details>
<summary>Métodos privados</summary>

#### `__new__(cls, *args, **kwargs)`

Singleton thread-safe para única instancia del servicio.

#### `__init__(self, fan_controller: FanController, system_monitor: SystemMonitor)`

Inicializa singleton FanAutoService (solo primera vez).

Args:
    fan_controller (FanController): Para calcular PWM.
    system_monitor (SystemMonitor): Para temperatura CPU.

#### `_run(self)`

Bucle principal del servicio.

#### `_update_auto_mode(self)`

Actualiza el PWM si está en modo auto.

</details>
