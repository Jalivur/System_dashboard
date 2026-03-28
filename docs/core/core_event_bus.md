# `core.event_bus`

> **Ruta**: `core/event_bus.py`

> **Cobertura de documentación**: 🟢 100% (10/10)

Sistema central de Event Bus thread-safe para comunicación between servicios y UI.

Previene acceso directo a Tkinter desde threads secundarios.
Los servicios publican eventos, la UI se suscribe y actualiza widgets en el thread principal.

---

## Tabla de contenidos

**Funciones**
- [`get_event_bus()`](#get_event_bus)

**Clase [`EventBus`](#clase-eventbus)**
  - [`subscribe()`](#subscribe)
  - [`unsubscribe()`](#unsubscribe)
  - [`publish()`](#publish)
  - [`process_events()`](#process_events)
  - [`clear()`](#clear)
  - [`__new__()`](#__new__) _(privado)_
  - [`__init__()`](#__init__) _(privado)_
  - [`_dispatch_event()`](#_dispatch_event) _(privado)_

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

### `get_event_bus()`

```python
get_event_bus() -> EventBus
```

Obtiene la instancia global del event bus.

Returns:
    La instancia global del event bus.

## Clase `EventBus`

Proporciona un mecanismo de publicación y suscripción de eventos de forma thread-safe.

Args:
    None

Returns:
    None

Raises:
    None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_initialized` | `True` |
| `_event_queue` | `queue.Queue()` |
| `_lock` | `threading.RLock()` |

### Métodos públicos

#### `subscribe()`

```python
subscribe(self, event_name: str, callback: Callable) -> None
```

Suscribirse a un evento para recibir notificaciones cuando ocurra.

Args:
    event_name (str): Nombre del evento.
    callback (Callable): Función que se ejecutará al ocurrir el evento.

Returns:
    None

Raises:
    None

#### `unsubscribe()`

```python
unsubscribe(self, event_name: str, callback: Callable) -> None
```

Elimina una función de callback previamente registrada para un evento específico.

Args:
    event_name (str): Nombre del evento del que desuscribirse.
    callback (Callable): Función de callback a eliminar.

Returns:
    None

Raises:
    None

#### `publish()`

```python
publish(self, event_name: str, data: Any = None) -> None
```

Publica un evento de forma segura entre threads.

Args:
    event_name (str): Nombre del evento a publicar.
    data (Any, opcional): Datos asociados al evento. Por defecto es None.

Returns:
    None

Raises:
    None

#### `process_events()`

```python
process_events(self) -> None
```

Procesa eventos pendientes en la cola de eventos.

Args:
    None

Returns:
    None

Raises:
    Exception: Si ocurre un error durante el procesamiento de eventos.

#### `clear()`

```python
clear(self) -> None
```

Elimina todos los suscriptores y eventos pendientes de procesamiento.

Args:
    Ninguno.

Returns:
    None

Raises:
    Ninguna excepción.

### Métodos privados

#### `__new__()`

```python
__new__(cls)
```

Crea y devuelve la instancia única de la clase EventBus.

Args:
    None

Returns:
    La instancia única de la clase EventBus.

Raises:
    None

#### `__init__()`

```python
__init__(self)
```

Inicializa el EventBus singleton la primera vez que se instancia.

Args:
    None

Returns:
    None

Raises:
    None

#### `_dispatch_event()`

```python
_dispatch_event(self, event_name: str, data: Any) -> None
```

Ejecuta callbacks registrados para un evento específico con los datos proporcionados.

Args:
    event_name (str): Nombre del evento a dispatchar.
    data (Any): Datos asociados al evento.

Returns:
    None

Raises:
    Exception: Si un callback lanza una excepción durante su ejecución.
