# `ui.windows.log_config_window`

> **Ruta**: `ui/windows/log_config_window.py`

> **Cobertura de documentación**: 🟢 100% (15/15)

Ventana de configuración del sistema de logging en runtime.
Permite cambiar niveles de fichero y consola, controlar módulos
individualmente y forzar la rotación del log.

Diseño ligero para Wayland/labwc:
  - Handlers globales: dos CTkOptionMenu (uno por handler)
  - Módulos: tk.Listbox nativo (un solo widget X11) + CTkScrollbar + un CTkOptionMenu compartido

Ubicación: ui/windows/log_config_window.py

---

## Tabla de contenidos

**Funciones**
- [`_level_name()`](#_level_name) _(privada)_

**Clase [`LogConfigWindow`](#clase-logconfigwindow)**
  - [`__init__()`](#__init__) _(privado)_
  - [`_create_ui()`](#_create_ui) _(privado)_
  - [`_build_left()`](#_build_left) _(privado)_
  - [`_build_handler_row()`](#_build_handler_row) _(privado)_
  - [`_on_file_level_change()`](#_on_file_level_change) _(privado)_
  - [`_on_console_level_change()`](#_on_console_level_change) _(privado)_
  - [`_build_right()`](#_build_right) _(privado)_
  - [`_reload_modules()`](#_reload_modules) _(privado)_
  - [`_on_listbox_select()`](#_on_listbox_select) _(privado)_
  - [`_apply_module_level()`](#_apply_module_level) _(privado)_
  - [`_force_rollover()`](#_force_rollover) _(privado)_
  - [`_reset_all_modules()`](#_reset_all_modules) _(privado)_
  - [`_on_close()`](#_on_close) _(privado)_

---

## Dependencias internas

- `config.settings`
- `ui.styles`
- `ui.widgets.dialogs`
- `utils.logger`

## Imports

```python
import logging
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets.dialogs import custom_msgbox
from utils.logger import get_logger, get_dashboard_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Funciones privadas

### `_level_name()`

```python
_level_name(level: int) -> str
```

Convierte un nivel numérico de logging en su nombre legible.

Args:
    level (int): Nivel numérico de logging.

Returns:
    str: Nombre del nivel o el nombre por defecto si no está mapeado.

## Clase `LogConfigWindow(ctk.CTkToplevel)`

Ventana de control de niveles de logging en runtime.

Args:
    parent: Ventana padre (CTkToplevel).

Returns:
    None

Raises:
    None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_dl` | `get_dashboard_logger()` |
| `_file_level_var` | `ctk.StringVar(master=self, value=_level_name(status['file_level']))` |
| `_console_level_var` | `ctk.StringVar(master=self, value=_level_name(status['console_level']))` |
| `_console_exact_var` | `ctk.BooleanVar(master=self, value=status['console_exact'])` |
| `_console_active` | `status['console_active']` |
| `_module_level_var` | `ctk.StringVar(master=self, value=_HEREDAR)` |

### Métodos privados

#### `__init__()`

```python
__init__(self, parent)
```

Inicializa la ventana de configuración de logging.

Configura posición y estado de handlers/módulos.

Args:
    parent: Ventana padre (CTkToplevel).

Raises:
    None

#### `_create_ui()`

```python
_create_ui(self)
```

Crea la estructura principal de la UI para la configuración de logging.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_build_left()`

```python
_build_left(self, parent)
```

Construye la columna izquierda de la ventana de configuración de logs.

Args:
    parent: El padre de la columna izquierda.

Returns:
    None

Raises:
    None

#### `_build_handler_row()`

```python
_build_handler_row(self, parent, label: str, var, active: bool, command)
```

Crea una fila horizontal reusable para selector de nivel de handler.

Args:
    parent: Frame contenedor.
    label (str): Etiqueta a mostrar (ej: "Fichero:").
    var: StringVar con nivel actual.
    active (bool): Indica si el handler está habilitado.
    command: Callback a ejecutar al cambiar el nivel.

Returns:
    None

Raises:
    None

#### `_on_file_level_change()`

```python
_on_file_level_change(self, value: str)
```

Actualiza el nivel de logging del handler de fichero según el valor seleccionado.

Args:
    value (str): Nuevo nivel de logging.

Returns:
    None

Raises:
    None

#### `_on_console_level_change()`

```python
_on_console_level_change(self, value: str = None)
```

Establece el nivel de precisión del registro en la consola según el valor seleccionado.

Args:
    value (str): El nuevo nivel de precisión. Si no se proporciona, se usa el valor actual.

Returns:
    None

Raises:
    None

#### `_build_right()`

```python
_build_right(self, parent)
```

Construye la columna derecha de la ventana de configuración de logs.

Args:
    parent: El elemento padre donde se construirá la columna derecha.

#### `_reload_modules()`

```python
_reload_modules(self)
```

Recarga la lista de módulos activos desde dashboard_logger y actualiza la lista visualizada.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_on_listbox_select()`

```python
_on_listbox_select(self, _event)
```

Actualiza el selector y el estado del módulo según la selección realizada en el listbox.

Args:
    _event: Evento de selección en el listbox.

Returns:
    None

Raises:
    None

#### `_apply_module_level()`

```python
_apply_module_level(self)
```

Aplica el nivel de log seleccionado al módulo actualmente elegido y actualiza la lista y el estado.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_force_rollover()`

```python
_force_rollover(self)
```

Fuerza la rotación manual del archivo de log y muestra una confirmación.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_reset_all_modules()`

```python
_reset_all_modules(self)
```

Restablece todos los módulos a nivel HEREDAR y recarga listbox.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_on_close()`

```python
_on_close(self)
```

Maneja el evento de cierre de la ventana de configuración de registro.

Args:
    None

Returns:
    None

Raises:
    None
