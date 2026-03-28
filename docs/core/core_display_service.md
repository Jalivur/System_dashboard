# `core.display_service`

> **Ruta**: `core/display_service.py`

> **Cobertura de documentación**: 🟢 100% (25/25)

Servicio de control de brillo de la pantalla.
Detecta automáticamente el método disponible:
  - 'sysfs'     : /sys/class/backlight/ (driver kernel estándar)
  - 'wlr-randr' : Wayland (Raspberry Pi OS Bookworm por defecto)
  - 'xrandr'    : X11
  - 'none'      : no disponible (ventana muestra aviso)

Hardware: Freenove FNK0100K (4.3" IPS DSI) — Raspberry Pi 5.

---

## Tabla de contenidos

**Funciones**
- [`_find_backlight()`](#_find_backlight) _(privada)_
- [`_detect_method()`](#_detect_method) _(privada)_

**Clase [`DisplayService`](#clase-displayservice)**
  - [`start()`](#start)
  - [`stop()`](#stop)
  - [`is_running()`](#is_running)
  - [`is_available()`](#is_available)
  - [`get_method()`](#get_method)
  - [`get_brightness()`](#get_brightness)
  - [`set_brightness()`](#set_brightness)
  - [`screen_off()`](#screen_off)
  - [`screen_on()`](#screen_on)
  - [`notify_activity()`](#notify_activity)
  - [`enable_dim_on_idle()`](#enable_dim_on_idle)
  - [`disable_dim_on_idle()`](#disable_dim_on_idle)
  - [`__init__()`](#__init__) _(privado)_
  - [`_set_sysfs()`](#_set_sysfs) _(privado)_
  - [`_set_wlr()`](#_set_wlr) _(privado)_
  - [`_set_xrandr()`](#_set_xrandr) _(privado)_
  - [`_start_dim_timer()`](#_start_dim_timer) _(privado)_
  - [`_cancel_dim_timer()`](#_cancel_dim_timer) _(privado)_
  - [`_on_dim()`](#_on_dim) _(privado)_
  - [`_on_off()`](#_on_off) _(privado)_
  - [`_save_state()`](#_save_state) _(privado)_
  - [`_load_state()`](#_load_state) _(privado)_

---

## Dependencias internas

- `utils.logger`

## Imports

```python
import subprocess
import threading
import json
from pathlib import Path
from typing import Optional
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `DSI_OUTPUT` | `'DSI-2'` |
| `BRIGHTNESS_MIN` | `10` |
| `BRIGHTNESS_MAX` | `100` |
| `BRIGHTNESS_OFF` | `0` |
| `DIM_TIMEOUT_S` | `120` |
| `OFF_TIMEOUT_S` | `2400000` |

## Funciones privadas

### `_find_backlight()`

```python
_find_backlight() -> Optional[Path]
```

Busca la primera ruta válida de ajuste de brillo en la lista de candidatos.

Args:
    Ninguno.

Returns:
    La ruta del ajuste de brillo si se encuentra, None en caso contrario.

Raises:
    Ninguno.

### `_detect_method()`

```python
_detect_method() -> str
```

Detecta el método disponible para controlar el brillo.

Args:
    None

Returns:
    El método disponible como cadena ('sysfs', 'wlr-randr', 'xrandr' o 'none').

Raises:
    None

## Clase `DisplayService`

Servicio de control de visualización que gestiona el brillo de la pantalla.

Args: None

Returns: None

Raises: None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_method` | `_detect_method()` |
| `_backlight` | `_find_backlight() if self._method == 'sysfs' else None` |
| `_lock` | `threading.Lock()` |
| `_dimmed` | `False` |
| `_running` | `True` |

### Métodos públicos

#### `start()`

```python
start(self) -> None
```

Activa el servicio de visualización.

Args:
    None

Returns:
    None

Raises:
    None

#### `stop()`

```python
stop(self) -> None
```

Detiene el servicio de visualización y cancela los temporizadores de atenuación.

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

Indica si el servicio de pantalla está actualmente en ejecución.

Args:
    None

Returns:
    bool: True si el servicio está corriendo, False de lo contrario.

Raises:
    None

#### `is_available()`

```python
is_available(self) -> bool
```

Indica si hay algún método de control de brillo disponible.

Args:
    None

Returns:
    bool: True si hay algún método disponible, False de lo contrario.

Raises:
    None

#### `get_method()`

```python
get_method(self) -> str
```

Devuelve el método activo de visualización.

Returns:
    El método activo como cadena, puede ser 'sysfs', 'wlr-randr', 'xrandr' o 'none'.

#### `get_brightness()`

```python
get_brightness(self) -> int
```

Devuelve el brillo actual en porcentaje.

Args:
    None

Returns:
    int: El brillo actual como un entero entre 0 y 100.

Raises:
    None

#### `set_brightness()`

```python
set_brightness(self, pct: int) -> bool
```

Establece el brillo de la pantalla en un porcentaje específico.
Args:
    pct (int): Porcentaje de brillo entre 0 y 100.
Returns:
    bool: True si la operación fue exitosa, False en caso contrario.
Raises:
    None

#### `screen_off()`

```python
screen_off(self) -> bool
```

Apaga la pantalla estableciendo el brillo en su nivel mínimo.

Args:
    No requiere parámetros adicionales.

Returns:
    bool: Indicador de éxito en la operación.

Raises:
    No se lanzan excepciones explícitas.

#### `screen_on()`

```python
screen_on(self) -> bool
```

Enciende la pantalla al último nivel de brillo guardado.

Args:
    None

Returns:
    bool: Indicador de si se ha podido encender la pantalla.

Raises:
    None

#### `notify_activity()`

```python
notify_activity(self)
```

Notifica una interacción del usuario para actualizar el estado de la pantalla.

Args:
    None

Returns:
    None

Raises:
    None

#### `enable_dim_on_idle()`

```python
enable_dim_on_idle(self)
```

Activa el modo de reducción de brillo por inactividad.

Args:
    None

Returns:
    None

Raises:
    None

#### `disable_dim_on_idle()`

```python
disable_dim_on_idle(self)
```

Desactiva el ahorro de energía por inactividad cancelando los temporizadores correspondientes.
Args: 
Returns: 
Raises:

### Métodos privados

#### `__init__()`

```python
__init__(self)
```

Inicializa el servicio de visualización detectando el método de ajuste de brillo disponible.

Args: None

Returns: None

Raises: None

#### `_set_sysfs()`

```python
_set_sysfs(self, pct: int) -> bool
```

Establece el brillo del sistema mediante sysfs.

Args:
    pct (int): Porcentaje de brillo.

Returns:
    bool: True si se estableció correctamente, False en caso de error.

Raises:
    PermissionError: Si no se tienen permisos para acceder a sysfs.

#### `_set_wlr()`

```python
_set_wlr(self, pct: int) -> bool
```

Establece el brillo de la pantalla utilizando wlr-randr.

Args:
    pct (int): Porcentaje de brillo.

Returns:
    bool: True si se estableció correctamente, False en caso de error.

Raises:
    Exception: Si ocurre un error al ejecutar el comando wlr-randr.

#### `_set_xrandr()`

```python
_set_xrandr(self, pct: int) -> bool
```

Configura el brillo de la pantalla utilizando xrandr.

Args:
    pct (int): Porcentaje de brillo.

Returns:
    bool: True si la operación es exitosa, False en caso contrario.

Raises:
    Exception: Si ocurre un error durante la ejecución del comando xrandr.

#### `_start_dim_timer()`

```python
_start_dim_timer(self)
```

Inicia o reinicia el temporizador para disminuir la intensidad por inactividad.

Args:
    None

Returns:
    None

Raises:
    None

#### `_cancel_dim_timer()`

```python
_cancel_dim_timer(self)
```

Cancela el temporizador activo de reducción de brillo si existe.

Args:
    None

Returns:
    None

Raises:
    None

#### `_on_dim()`

```python
_on_dim(self)
```

Disminuye la intensidad de la pantalla al 20% y programa el apagado después de un período de inactividad.

Args: None

Returns: None

Raises: None

#### `_on_off()`

```python
_on_off(self)
```

Apaga la pantalla cuando se produce un evento de inactividad.

Args:
    None

Returns:
    None

Raises:
    None

#### `_save_state()`

```python
_save_state(self)
```

Persiste el estado actual en un archivo de configuración.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Exception: Si ocurre un error al guardar el estado.

#### `_load_state()`

```python
_load_state(self)
```

Carga y restaura el estado de brillo persistido si es válido.

Args: 
    None

Returns: 
    None

Raises: 
    Exception si no se puede cargar el estado.
