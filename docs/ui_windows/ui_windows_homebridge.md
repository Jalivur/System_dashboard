# `ui.windows.homebridge`

> **Ruta**: `ui/windows/homebridge.py`

> **Cobertura de documentación**: 🟢 100% (19/19)

Ventana de control de dispositivos Homebridge
Muestra enchufes e interruptores y permite encenderlos / apagarlos

---

## Tabla de contenidos

**Clase [`HomebridgeWindow`](#clase-homebridgewindow)**
  - [`__init__()`](#__init__) _(privado)_
  - [`_create_ui()`](#_create_ui) _(privado)_
  - [`_schedule_update()`](#_schedule_update) _(privado)_
  - [`_force_refresh()`](#_force_refresh) _(privado)_
  - [`_fetch_and_render()`](#_fetch_and_render) _(privado)_
  - [`_render()`](#_render) _(privado)_
  - [`_create_device_card()`](#_create_device_card) _(privado)_
  - [`_card_switch()`](#_card_switch) _(privado)_
  - [`_card_thermostat()`](#_card_thermostat) _(privado)_
  - [`_card_sensor()`](#_card_sensor) _(privado)_
  - [`_card_blind()`](#_card_blind) _(privado)_
  - [`_toggle()`](#_toggle) _(privado)_
  - [`_set_status()`](#_set_status) _(privado)_
  - [`_on_close()`](#_on_close) _(privado)_

---

## Dependencias internas

- `config.settings`
- `core.homebridge_monitor`
- `ui.styles`
- `ui.widgets`
- `utils.logger`

## Imports

```python
import threading
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, Icons
from ui.styles import StyleManager, make_futuristic_button, make_window_header, make_homebridge_switch
from ui.widgets import custom_msgbox
from core.homebridge_monitor import HomebridgeMonitor
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `HB_UPDATE_MS` | `5000` |

## Clase `HomebridgeWindow(ctk.CTkToplevel)`

Representa una ventana de control para dispositivos Homebridge.

Args:
    parent: Ventana padre que contiene esta ventana.
    homebridge_monitor: Monitor de Homebridge asociado a esta ventana.

Raises:
    Ninguna excepción específica.

Returns:
    Ninguno.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_hb` | `homebridge_monitor` |
| `_accessories` | `[]` |
| `_update_job` | `None` |
| `_busy` | `False` |

### Métodos privados

#### `__init__()`

```python
__init__(self, parent, homebridge_monitor: HomebridgeMonitor)
```

Inicializa la ventana de Homebridge con un monitor y configuración básica.

Args:
    parent (object): El objeto padre de la ventana.
    homebridge_monitor (HomebridgeMonitor): El monitor de Homebridge asociado a la ventana.

Returns:
    None

Raises:
    None

#### `_create_ui()`

```python
_create_ui(self)
```

Crea todos los elementos de la interfaz de usuario de la ventana.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_schedule_update()`

```python
_schedule_update(self)
```

Programa la actualización periódica de los dispositivos.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_force_refresh()`

```python
_force_refresh(self)
```

Fuerza una actualización inmediata de los dispositivos Homebridge.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_fetch_and_render()`

```python
_fetch_and_render(self)
```

Obtiene los accesorios de Homebridge y los renderiza en la UI de forma asíncrona.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `_render()`

```python
_render(self, accessories)
```

Renderiza la lista de accesorios en tarjetas de dispositivos en la interfaz.

Args:
    accessories (list): Lista de accesorios a renderizar.

Returns:
    None

Raises:
    Exception: Si ocurre un error al configurar la etiqueta de estado.

#### `_create_device_card()`

```python
_create_device_card(self, acc: dict, grid_row: int, grid_col: int)
```

Crea y posiciona una tarjeta para un dispositivo Homebridge específico en la interfaz gráfica.

Args:
    acc (dict): Diccionario con información del dispositivo.
    grid_row (int): Fila de la cuadrícula donde se posicionará la tarjeta.
    grid_col (int): Columna de la cuadrícula donde se posicionará la tarjeta.

Returns:
    None

#### `_card_switch()`

```python
_card_switch(self, card, acc, disabled)
```

Crea un interruptor de encendido/apagado para un accesorio Homebridge.

Args:
    card: El contenedor donde se renderizará el interruptor.
    acc: El accesorio Homebridge que se controla con el interruptor.
    disabled: Indica si el interruptor está desactivado.

Returns:
    None

Raises:
    None

#### `_card_thermostat()`

```python
_card_thermostat(self, card, acc, disabled)
```

Crea la interfaz de un termostato con temperatura actual y controles de objetivo.

Args:
    card: El contenedor donde se renderizará el termostato.
    acc: Un diccionario con información del termostato, incluyendo 'displayName', 'current_temp' y 'target_temp'.
    disabled: No se utiliza en este método.

Returns:
    None

Raises:
    None

#### `_card_sensor()`

```python
_card_sensor(self, card, acc)
```

Crea la interfaz de un sensor de temperatura y humedad en la tarjeta proporcionada.

Args:
    card: El contenedor donde se creará el sensor.
    acc: Un diccionario con información del sensor, incluyendo "displayName", "temp" y "humidity".

Returns:
    None

Raises:
    None

#### `_card_blind()`

```python
_card_blind(self, card, acc, disabled)
```

Crea la interfaz de una persiana/estor con barra de progreso de posición.

Args:
    card: El contenedor donde se creará la interfaz.
    acc: Un diccionario con información sobre el accesorio, incluyendo "displayName" y "position".
    disabled: No se utiliza en este método.

Returns:
    None

Raises:
    None

#### `_toggle()`

```python
_toggle(self, unique_id: str, turn_on: bool)
```

Envía comando ON/OFF a un dispositivo Homebridge en segundo plano de forma asíncrona.

Args:
    unique_id (str): Identificador único del dispositivo.
    turn_on (bool): Indica si se debe encender (True) o apagar (False) el dispositivo.

Raises:
    Ninguna excepción es propagada, se maneja internamente mostrando un mensaje de error si corresponde.

#### `_set_status()`

```python
_set_status(self, text: str)
```

Actualiza el texto de estado en la barra inferior de la ventana.

Args:
    text (str): El nuevo texto de estado.

Raises:
    Exception: Si ocurre un error al actualizar el texto de estado.

#### `_on_close()`

```python
_on_close(self)
```

Maneja el cierre de la ventana, cancelando trabajos pendientes y liberando recursos.

Args: 
    None

Returns: 
    None

Raises: 
    None
