# `config.local_settings_io`

> **Ruta**: `config/local_settings_io.py`

> **Cobertura de documentación**: 🟢 100% (7/7)

config/local_settings_io.py

Lectura y escritura de config/local_settings.py de forma segura y sin
conflictos entre módulos que necesitan persistir claves distintas.

Formato del fichero:
  - Sección "# ── Parámetros" — variables sueltas (DSI_X, CPU_WARN, WEATHER_*)
  - Sección "# ── Iconos"     — asignaciones Icons.ATTR = "\Uxxxxxxxx"

Cualquier módulo que necesite leer o escribir local_settings.py debe
importar este módulo y usar read() / write_params() / write_icons().
Nunca escribir directamente el fichero desde fuera de este módulo.

---

## Tabla de contenidos

**Funciones**
- [`read()`](#funcion-read)
- [`write()`](#funcion-write)
- [`update_params()`](#funcion-update_params)
- [`write_params()`](#funcion-write_params)
- [`write_icons()`](#funcion-write_icons)
- [`update_icons()`](#funcion-update_icons)
- [`get_param()`](#funcion-get_param)

---

## Imports

```python
import os
import re
import logging
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `logging.getLogger(__name__)` |

## Funciones

### `read() -> tuple`

Lee local_settings.py y devuelve (param_overrides, icon_overrides).

  param_overrides : dict  {str: any}          — variables sueltas
  icon_overrides  : dict  {str: str}           — {ATTR: "\Uxxxxxxxx"}

### `write(param_overrides: dict, icon_overrides: dict) -> None`

Escribe local_settings.py completo con ambas secciones.
Sobrescribe el fichero — llamar siempre con el estado completo.

### `update_params(new_params: dict) -> None`

Merge seguro: lee el estado actual, aplica new_params encima y escribe.
Los iconos y el resto de parámetros existentes se conservan intactos.

### `write_params(param_overrides: dict) -> None`

Escribe solo parámetros, preservando los iconos existentes.

### `write_icons(icon_overrides: dict) -> None`

Escribe solo iconos, preservando los parámetros existentes.

### `update_icons(new_icons: dict) -> None`

Merge seguro: lee el estado actual, aplica new_icons encima y escribe.
Los parámetros y el resto de iconos existentes se conservan intactos.

### `get_param(key: str, default = None)`

Lee un único parámetro de local_settings.py sin importar el módulo.
