# `ui.windows.launchers`

> **Ruta**: `ui/windows/launchers.py`

> **Cobertura de documentación**: 🟢 100% (6/6)

Módulo de ventana de lanzadores para System Dashboard.

Proporciona una interfaz gráfica para ejecutar scripts del sistema configurados
en `config.settings.LAUNCHERS`. Cada lanzador muestra confirmación antes de
ejecución y abre terminal integrada para monitoreo en tiempo real.

Dependencias:
- customtkinter
- config.settings
- ui.styles, ui.widgets
- utils.system_utils, utils.logger

---

## Tabla de contenidos

**Clase [`LaunchersWindow`](#clase-launcherswindow)**
  - [`__init__()`](#__init__) _(privado)_
  - [`_create_ui()`](#_create_ui) _(privado)_
  - [`_create_launcher_buttons()`](#_create_launcher_buttons) _(privado)_
  - [`_run_script()`](#_run_script) _(privado)_

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
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, LAUNCHERS, Icons
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import confirm_dialog, terminal_dialog
from utils.system_utils import SystemUtils
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `LaunchersWindow(ctk.CTkToplevel)`

Representa una ventana emergente que contiene lanzadores de scripts del sistema.

Args:
    parent: Widget padre que representa la ventana principal del dashboard.

Configura la geometría, colores y título de la ventana, y crea la interfaz de usuario completa.

### Atributos públicos

| Atributo | Valor inicial |
|----------|---------------|
| `system_utils` | `SystemUtils()` |

### Métodos privados

#### `__init__()`

```python
__init__(self, parent)
```

Inicializa la ventana de lanzadores.

Args:
    parent: Widget padre (ventana principal del dashboard).

Returns:
    None

Raises:
    None

#### `_create_ui()`

```python
_create_ui(self)
```

Crea la interfaz de usuario para la ventana de lanzadores.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_create_launcher_buttons()`

```python
_create_launcher_buttons(self, parent)
```

Crea los botones de lanzadores en un diseño de rejilla dentro de la ventana.

Args:
    parent: El elemento padre donde se crearán los botones.

Returns:
    None

Raises:
    None

#### `_run_script()`

```python
_run_script(self, script_path: str, label: str)
```

Ejecuta un script tras confirmar su ejecución.

Args:
    script_path (str): Ruta absoluta al script ejecutable.
    label (str): Nombre descriptivo del lanzador para logging y UI.

Raises:
    Ninguna excepción específica.
