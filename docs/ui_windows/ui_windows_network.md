# `ui.windows.network`

> **Ruta**: `ui/windows/network.py`

> **Cobertura de documentación**: 🟢 100% (11/11)

Ventana de monitoreo de red

---

## Tabla de contenidos

**Clase [`NetworkWindow`](#clase-networkwindow)**
  - [`__init__()`](#__init__) _(privado)_
  - [`_create_ui()`](#_create_ui) _(privado)_
  - [`_build_content()`](#_build_content) _(privado)_
  - [`_create_traffic_cell()`](#_create_traffic_cell) _(privado)_
  - [`_create_interfaces_cell()`](#_create_interfaces_cell) _(privado)_
  - [`_create_speedtest_cell()`](#_create_speedtest_cell) _(privado)_
  - [`_update_interfaces()`](#_update_interfaces) _(privado)_
  - [`_run_speedtest()`](#_run_speedtest) _(privado)_
  - [`_update_speedtest()`](#_update_speedtest) _(privado)_
  - [`_update()`](#_update) _(privado)_

---

## Dependencias internas

- `config.settings`
- `ui.styles`
- `ui.widgets`
- `utils.logger`
- `utils.system_utils`

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, NET_INTERFACE, Icons
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import GraphWidget
from utils.system_utils import SystemUtils
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `NetworkWindow(ctk.CTkToplevel)`

Ventana emergente para monitorear el estado de la red.

Args:
    parent: Widget padre que crea esta ventana.
    network_monitor: Instancia del monitor de red para obtener estadísticas.

Raises:
    Ninguna excepción específica.

Returns:
    Ningún valor de retorno.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_network_monitor` | `network_monitor` |
| `_widgets` | `{}` |
| `_graphs` | `{}` |
| `_interface_update_counter` | `0` |
| `_banner_shown` | `False` |

### Métodos privados

#### `__init__()`

```python
__init__(self, parent, network_monitor)
```

Inicializa la ventana de monitoreo de red.

Args:
    parent: Widget padre (CTkToplevel).
    network_monitor: Instancia del monitor de red para obtener estadísticas.

Returns:
    None

Raises:
    None

#### `_create_ui()`

```python
_create_ui(self)
```

Crea la estructura principal de la interfaz de usuario de la ventana de red.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_build_content()`

```python
_build_content(self, inner)
```

Construye el contenido scrollable de la ventana de red.

Args:
    inner: El contenedor interno donde se construirá el contenido.

Returns:
    None

Raises:
    None

#### `_create_traffic_cell()`

```python
_create_traffic_cell(self, parent, row, col, title, key)
```

Crea una celda de tráfico de red con gráfica para mostrar datos de descarga o subida.

Args:
    parent: Frame contenedor de la celda.
    row: Número de fila en el grid.
    col: Número de columna en el grid.
    title: Título de la celda.
    key: Identificador de la celda ('download' o 'upload').

Returns:
    None

Raises:
    None

#### `_create_interfaces_cell()`

```python
_create_interfaces_cell(self, parent, row, col)
```

Crea la celda que muestra interfaces de red activas e IPs.

Args:
    parent: El padre de la celda.
    row (int): La fila de la celda.
    col (int): La columna de la celda.

Returns:
    None

Raises:
    None

#### `_create_speedtest_cell()`

```python
_create_speedtest_cell(self, parent, row, col)
```

Crea la celda para ejecutar y mostrar resultados de speedtest.

Args:
    parent: El padre de la celda.
    row: La fila donde se ubicará la celda.
    col: La columna donde se ubicará la celda.

Returns:
    None

Raises:
    None

#### `_update_interfaces()`

```python
_update_interfaces(self)
```

Actualiza la lista de interfaces de red con sus direcciones IP.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_run_speedtest()`

```python
_run_speedtest(self)
```

Inicia la ejecución de un test de velocidad de red.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_update_speedtest()`

```python
_update_speedtest(self)
```

Actualiza la visualización del resultado del speedtest según su estado.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_update()`

```python
_update(self)
```

Actualiza la interfaz de usuario de la ventana de red con datos del monitor de red.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno
