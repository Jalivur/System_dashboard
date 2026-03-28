# `core.event_bus`

> **Ruta**: `core/event_bus.py`

> **Cobertura de documentación**: 🟢 100% (10/10)

Sistema central de Event Bus thread-safe para comunicación between servicios y UI.

Previene acceso directo a Tkinter desde threads secundarios.
Los servicios publican eventos, la UI se suscribe y actualiza widgets en el thread principal.

---

## Tabla de contenidos

**Funciones**
- [`get_event_bus()`](#funcion-get_event_bus)

**Clase [`EventBus`](#clase-eventbus)**
  - [`subscribe()`](#subscribeself-event_name-str-callback-callable-none)
  - [`unsubscribe()`](#unsubscribeself-event_name-str-callback-callable-none)
  - [`publish()`](#publishself-event_name-str-data-any-none-none)
  - [`process_events()`](#process_eventsself-none)
  - [`clear()`](#clearself-none)

---

## Dependencias internas

- `utils.logger`

## Imports

```python
import queue
import threading
from typing import Callable, Dict, Any, List
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Funciones

### `get_event_bus() -> EventBus`

Obtener la instancia global del event bus.

## Clase `EventBus`

Bus de eventos thread-safe singleton.

Uso:
    bus = EventBus()

    # Publicar evento desde thread secundario
    bus.publish("system.cpu_changed", {"cpu": 45.2})

    # Suscribirse en thread principal
    bus.subscribe("system.cpu_changed", callback)

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_initialized` | `True` |
| `_event_queue` | `queue.Queue()` |
| `_lock` | `threading.RLock()` |

### Métodos públicos

#### `subscribe(self, event_name: str, callback: Callable) -> None`

Suscribirse a un evento.

Args:
    event_name: Nombre del evento (ej: "system.cpu_changed")
    callback: Función que se ejecutará: callback(event_data)

#### `unsubscribe(self, event_name: str, callback: Callable) -> None`

Desuscribirse de un evento.

#### `publish(self, event_name: str, data: Any = None) -> None`

Publicar un evento (thread-safe).

Puede llamarse desde cualquier thread, incluidos threads secundarios.
Los callbacks se ejecutarán mediante root.after() desde el thread principal.

Args:
    event_name: Nombre del evento
    data: Datos del evento (dict recomendado)

#### `process_events(self) -> None`

Procesar eventos pendientes. LLamar desde main_update_loop o desde root.after().

Esto DEBE ejecutarse en el thread principal de Tkinter.

#### `clear(self) -> None`

Limpiar todos los suscriptores (útil para tests).

<details>
<summary>Métodos privados</summary>

#### `__new__(cls)`

Singleton thread-safe. Crea instancia única si no existe.

#### `__init__(self)`

Inicializa EventBus singleton (solo primera vez).
Configura queue, subscribers, RLock.

#### `_dispatch_event(self, event_name: str, data: Any) -> None`

Ejecutar callbacks para un evento.

</details>
