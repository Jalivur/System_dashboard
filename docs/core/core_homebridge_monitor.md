# `core.homebridge_monitor`

> **Ruta**: `core/homebridge_monitor.py`

> **Cobertura de documentación**: 🟢 100% (19/19)

Monitor de Homebridge
Integración con la API REST de homebridge-config-ui-x
Credenciales cargadas desde .env (nunca hardcodeadas)

Incluye sondeo ligero en background cada 30s para mantener
los badges del menú actualizados sin necesidad de abrir la ventana.

---

## Tabla de contenidos

**Clase [`HomebridgeMonitor`](#clase-homebridgemonitor)**
  - [`start()`](#startself-none)
  - [`stop()`](#stopself-none)
  - [`is_running()`](#is_runningself-bool)
  - [`get_accessories()`](#get_accessoriesself-listdict)
  - [`get_accessories_cached()`](#get_accessories_cachedself-listdict)
  - [`toggle()`](#toggleself-unique_id-str-turn_on-bool-bool)
  - [`is_reachable()`](#is_reachableself-bool)
  - [`get_offline_count()`](#get_offline_countself-int)
  - [`get_on_count()`](#get_on_countself-int)
  - [`get_fault_count()`](#get_fault_countself-int)
  - [`set_brightness()`](#set_brightnessself-unique_id-str-brightness-int-bool)
  - [`set_target_temp()`](#set_target_tempself-unique_id-str-temp-float-bool)

---

## Dependencias internas

- `utils.logger`

## Imports

```python
import json
import os
import threading
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional
from utils.logger import get_logger
from dotenv import load_dotenv
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `HOMEBRIDGE_HOST` | `os.environ.get('HOMEBRIDGE_HOST', '')` |
| `HOMEBRIDGE_PORT` | `int(os.environ.get('HOMEBRIDGE_PORT', '8581'))` |
| `HOMEBRIDGE_USER` | `os.environ.get('HOMEBRIDGE_USER', '')` |
| `HOMEBRIDGE_PASS` | `os.environ.get('HOMEBRIDGE_PASS', '')` |
| `HOMEBRIDGE_URL` | `f'http://{HOMEBRIDGE_HOST}:{HOMEBRIDGE_PORT}'` |
| `REQUEST_TIMEOUT` | `5` |
| `POLL_INTERVAL_S` | `30` |

<details>
<summary>Funciones privadas</summary>

### `_load_env()`

Carga variables de .env sin dependencias externas.
Si python-dotenv está disponible lo usa; si no, parsea el archivo a mano.

</details>

## Clase `HomebridgeMonitor`

Monitor y controlador de dispositivos Homebridge.

- Sondeo ligero en background cada 30s (1 petición HTTP ~1KB).
- La ventana lee self._accessories desde memoria sin petición extra.
- Los badges del menú siempre reflejan el estado real.
- toggle() fuerza un sondeo inmediato tras el comando.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_token_lock` | `threading.Lock()` |
| `_accessories_lock` | `threading.Lock()` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |

### Métodos públicos

#### `start(self) -> None`

Arranca el sondeo en background.
Llamar desde main.py justo después de instanciar.

#### `stop(self) -> None`

Detiene el sondeo limpiamente.
Llamar en cleanup() de main.py.

#### `is_running(self) -> bool`

Verifica si el servicio está corriendo.

#### `get_accessories(self) -> List[Dict]`

Consulta Homebridge y actualiza self._accessories.
Ahora reconoce 5 tipos de dispositivo:
  switch      — característica On (enchufe / interruptor)
  thermostat  — CurrentTemperature + TargetTemperature
  sensor      — CurrentTemperature o CurrentRelativeHumidity (solo lectura)
  blind       — CurrentPosition (persiana / estor)
  light       — On + Brightness (luz regulable)

#### `get_accessories_cached(self) -> List[Dict]`

Devuelve la lista en memoria sin hacer ninguna petición HTTP.
Usar desde la ventana para el refresco visual inmediato.

#### `toggle(self, unique_id: str, turn_on: bool) -> bool`

Cambia el estado On/Off de un accesorio.
Tras el comando lanza un sondeo inmediato para que los badges
reflejen el cambio sin esperar los 30s del ciclo normal.

#### `is_reachable(self) -> bool`

True si la última consulta fue exitosa.

#### `get_offline_count(self) -> int`

1 si Homebridge no respondió en la última consulta. 0 en cualquier otro caso.

#### `get_on_count(self) -> int`

Número de enchufes encendidos. Badge naranja en el menú.

#### `get_fault_count(self) -> int`

Número de dispositivos con StatusFault=1. Badge rojo en el menú.

#### `set_brightness(self, unique_id: str, brightness: int) -> bool`

Establece el brillo de una luz Homebridge (0-100%).

Args:
    unique_id (str): ID único del accesorio.
    brightness (int): Brillo 0-100, clamped.

Returns:
    bool: True si comando enviado OK.

#### `set_target_temp(self, unique_id: str, temp: float) -> bool`

Establece la temperatura objetivo de un termostato.

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Constructor. Inicializa locks, caches, chequea .env vars.

Carga HOMEBRIDGE_HOST/PORT/USER/PASS desde .env (manual fallback).

#### `_poll_loop(self) -> None`

Bucle de background. Primera consulta inmediata al arrancar
para poblar los badges lo antes posible.

#### `_authenticate(self) -> bool`

Obtiene un token JWT. Devuelve True si tiene éxito.

#### `_get_token(self) -> Optional[str]`

Devuelve el token actual; si no existe intenta autenticar.

#### `_request(self, method: str, path: str, body: Optional[Dict] = None) -> Optional[Dict]`

Petición autenticada. Si el token caduca (401) lo renueva una vez.

</details>
