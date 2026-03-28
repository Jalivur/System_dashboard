# `core.fan_controller`

> **Ruta**: `core/fan_controller.py`

> **Cobertura de documentación**: 🟢 100% (10/10)

Controlador de ventiladores

---

## Tabla de contenidos

**Clase [`FanController`](#clase-fancontroller)**
  - [`start()`](#start)
  - [`stop()`](#stop)
  - [`is_running()`](#is_running)
  - [`compute_pwm_from_curve()`](#compute_pwm_from_curve)
  - [`get_pwm_for_mode()`](#get_pwm_for_mode)
  - [`update_fan_state()`](#update_fan_state)
  - [`add_curve_point()`](#add_curve_point)
  - [`remove_curve_point()`](#remove_curve_point)
  - [`__init__()`](#__init__) _(privado)_

---

## Dependencias internas

- `utils.file_manager`
- `utils.logger`

## Imports

```python
from typing import List, Dict
from utils.file_manager import FileManager
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `FanController`

Controlador stateless para ventiladores que calcula PWM según modo y curva de temperatura.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_file_manager` | `FileManager()` |
| `_running` | `True` |

### Métodos públicos

#### `start()`

```python
start(self) -> None
```

Activa el controlador del ventilador.

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

Detiene el controlador del ventilador.

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

Verifica si el servicio de control de ventiladores está en ejecución.

Args:
    None

Returns:
    bool: True si el servicio está corriendo, False de lo contrario.

Raises:
    None

#### `compute_pwm_from_curve()`

```python
compute_pwm_from_curve(self, temp: float) -> int
```

Calcula el valor PWM interpolando la temperatura en la curva cargada.

Args:
    temp: Temperatura actual en °C.

Returns:
    Valor PWM (0-255) correspondiente a la temperatura.

Raises:
    ValueError: Si la curva tiene menos de dos puntos.

#### `get_pwm_for_mode()`

```python
get_pwm_for_mode(self, mode: str, temp: float, manual_pwm: int = 128) -> int
```

Obtiene el valor PWM según el modo de operación y la temperatura actual.

Args:
    mode (str): Modo de operación (auto, manual, silent, normal, performance)
    temp (float): Temperatura actual
    manual_pwm (int): Valor PWM manual si mode='manual' (por defecto 128)

Returns:
    int: Valor PWM calculado (0-255)

Raises:
    Ninguna excepción específica, se registra un warning en caso de modo desconocido.

#### `update_fan_state()`

```python
update_fan_state(self, mode: str, temp: float, current_target: int = None, manual_pwm: int = 128) -> Dict
```

Actualiza el estado del ventilador según el modo y la temperatura actuales.

Args:
    mode (str): Modo de operación ('auto', 'manual', 'full', 'off').
    temp (float): Temperatura actual en grados Celsius.
    current_target (int): PWM objetivo actual. None si no hay estado previo.
    manual_pwm (int): Valor PWM para modo manual (0-255).

Returns:
    Dict: Estado actualizado con claves 'mode' y 'target_pwm'.

Raises:
    ValueError: Si el modo no es válido.

#### `add_curve_point()`

```python
add_curve_point(self, temp: int, pwm: int) -> List[Dict]
```

Añade o actualiza un punto en la curva temperatura-PWM.

Args:
    temp (int): Temperatura en °C del punto a añadir/actualizar.
    pwm (int): Ciclo de trabajo PWM (0-255) asociado.

Returns:
    List[Dict]: Curva ordenada tras la modificación.

Raises:
    None

#### `remove_curve_point()`

```python
remove_curve_point(self, temp: int) -> List[Dict]
```

Elimina el punto de la curva que coincide con la temperatura indicada.

Args:
    temp (int): Temperatura en °C del punto a eliminar.

Returns:
    List[Dict]: Curva actualizada tras la eliminación.

Raises:
    Ninguna excepción relevante.

Nota: Si la curva queda vacía, se añade automáticamente un punto por defecto.

### Métodos privados

#### `__init__()`

```python
__init__(self)
```

Inicializa el controlador del ventilador sin estado interno.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno
