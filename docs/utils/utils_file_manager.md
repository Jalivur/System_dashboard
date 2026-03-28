# `utils.file_manager`

> **Ruta**: `utils/file_manager.py`

> **Cobertura de documentación**: 🟢 100% (5/5)

Gestión de archivos JSON para estado y configuración

---

## Tabla de contenidos

**Clase [`FileManager`](#clase-filemanager)**
  - [`write_state()`](#write_statedata-dictstr-any-none)
  - [`load_state()`](#load_state-dictstr-any)
  - [`load_curve()`](#load_curve-listdictstr-int)
  - [`save_curve()`](#save_curvepoints-listdictstr-int-none)

---

## Dependencias internas

- `config.settings`
- `utils.logger`

## Imports

```python
import json
import os
from typing import Dict, List, Any
from config.settings import STATE_FILE, CURVE_FILE
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `FileManager`

Gestor centralizado de archivos JSON

### Métodos públicos

#### `write_state(data: Dict[str, Any]) -> None`

Escribe el estado de forma atómica usando archivo temporal

Args:
    data: Diccionario con los datos a guardar

#### `load_state() -> Dict[str, Any]`

Carga el estado guardado

Returns:
    Diccionario con mode y target_pwm

#### `load_curve() -> List[Dict[str, int]]`

Carga la curva de ventiladores

Returns:
    Lista de puntos ordenados por temperatura

#### `save_curve(points: List[Dict[str, int]]) -> None`

Guarda la curva de ventiladores

Args:
    points: Lista de puntos {temp, pwm}
