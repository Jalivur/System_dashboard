# `core.audio_service`

> **Ruta**: `core/audio_service.py`

> **Cobertura de documentación**: 🟢 100% (9/9)

Servicio de AudioService para control volumen/mute via amixer y play_test con aplay.
Operaciones síncronas, sin threads. Compatible Raspberry Pi OS.

---

## Tabla de contenidos

**Clase [`AudioService`](#clase-audioservice)**
  - [`get_volume()`](#get_volumeself-control-str-default_control-int)
  - [`set_volume()`](#set_volumeself-value-int-control-str-default_control-bool)
  - [`is_muted()`](#is_mutedself-control-str-default_control-bool)
  - [`set_mute()`](#set_muteself-muted-bool-control-str-default_control-bool)
  - [`toggle_mute()`](#toggle_muteself-control-str-default_control-bool)
  - [`play_test()`](#play_testself-wav_path-str-none-none-none)
  - [`get_controls()`](#get_controlsself-liststr)

---

## Dependencias internas

- `utils.logger`

## Imports

```python
import subprocess
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `AudioService`

Servicio de control de audio via amixer/aplay.
No usa thread daemon — las operaciones son síncronas y puntuales.
Cero imports de tkinter/ctk.

### Métodos públicos

#### `get_volume(self, control: str = DEFAULT_CONTROL) -> int`

Devuelve el volumen actual (0-100). -1 si error.

#### `set_volume(self, value: int, control: str = DEFAULT_CONTROL) -> bool`

Establece volumen 0-100. Devuelve True si éxito.

#### `is_muted(self, control: str = DEFAULT_CONTROL) -> bool`

Devuelve True si el canal está muteado.

#### `set_mute(self, muted: bool, control: str = DEFAULT_CONTROL) -> bool`

Mutea o desmutea el canal. Devuelve True si éxito.

#### `toggle_mute(self, control: str = DEFAULT_CONTROL) -> bool`

Invierte el estado mute. Devuelve el nuevo estado (True=muteado).

#### `play_test(self, wav_path: str | None = None) -> None`

Lanza aplay en background. Si wav_path es None usa Front_Center.wav.

#### `get_controls(self) -> list[str]`

Devuelve lista de controles amixer disponibles.

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa AudioService (no requiere parámetros).

</details>
