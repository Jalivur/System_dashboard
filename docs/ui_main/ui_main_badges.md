# `ui.main_badges`

> **Ruta**: `ui/main_badges.py`

> **Cobertura de documentación**: 🟢 100% (7/7)

Gestor de badges del menu principal.

Los badges son indicadores visuales circulares superpuestos sobre los botones
del menu que muestran contadores (servicios caidos, actualizaciones pendientes)
o valores de temperatura/CPU/RAM/disco.

Uso en MainWindow:
    self._badge_mgr = BadgeManager(menu_btns=self._menu_btns)
    self._badge_mgr.create(btn, key="updates", offset_index=0)
    self._badge_mgr.update("updates", value=3)
    self._badge_mgr.update_temp("temp_fan", temp=72, color="#ff4444")

---

## Tabla de contenidos

**Clase [`BadgeManager`](#clase-badgemanager)**
  - [`create()`](#create)
  - [`update()`](#update)
  - [`update_temp()`](#update_temp)
  - [`hide()`](#hide)
  - [`__init__()`](#__init__) _(privado)_
  - [`__contains__()`](#__contains__) _(privado)_

---

## Dependencias internas

- `config.settings`

## Imports

```python
import tkinter as tk
from config.settings import COLORS, FONT_FAMILY, Icons
```

## Clase `BadgeManager`

Administrador de badges de notificación para botones del menú.

Args:
    menu_btns (dict): Diccionario de botones del menú {etiqueta → CTkButton}.

Nota: Utiliza este diccionario para obtener el widget padre y recrear los badges 
      después de un cambio de pestaña.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_menu_btns` | `menu_btns` |

### Métodos públicos

#### `create()`

```python
create(self, btn, key: str, offset_index: int = 0) -> None
```

Crea un badge sobre un botón y lo registra bajo una clave específica.

Args:
    btn: CTkButton padre sobre el que se creará el badge.
    key (str): Clave interna para registrar el badge (ej. "updates", "temp_fan").
    offset_index (int): Desplazamiento horizontal del badge (0 = más a la derecha). Por defecto es 0.

Returns:
    None

Raises:
    None

#### `update()`

```python
update(self, key: str, value: int, color: str = None) -> None
```

Actualiza la visualización de un badge según su valor.

Args:
    key (str): Clave del badge a actualizar.
    value (int): Valor del badge; mayor que 0 lo muestra, igual a 0 lo oculta.
    color (str, opcional): Color de fondo del badge; si no se proporciona, se usa danger o warning según la clave.

Returns:
    None

Raises:
    Ninguna excepción específica.

#### `update_temp()`

```python
update_temp(self, key: str, temp: int, color: str) -> None
```

Actualiza el valor de temperatura de un badge existente.

Args:
    key (str): Clave del badge a actualizar.
    temp (int): Nuevo valor de temperatura.
    color (str): Color de fondo del badge.

Returns:
    None

Raises:
    None

#### `hide()`

```python
hide(self, key: str) -> None
```

Oculta el badge asociado a la clave dada sin modificar su valor.

Args:
    key (str): Clave del badge a ocultar.

Returns:
    None

Raises:
    None

### Métodos privados

#### `__init__()`

```python
__init__(self, menu_btns: dict)
```

Inicializa el administrador de insignias con una referencia a los botones del menú.

Args:
    menu_btns (dict): Diccionario de botones del menú donde cada clave es una etiqueta y cada valor es un CTkButton.

#### `__contains__()`

```python
__contains__(self, key: str) -> bool
```

Determina si existe un badge con la clave dada.

Args:
    key (str): Clave a verificar

Returns:
    bool: True si existe el badge, False en caso contrario
