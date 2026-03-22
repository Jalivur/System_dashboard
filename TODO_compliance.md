# TODO - Cumplimiento Reglas Arquitectura v4.3

## Fixes Pendientes

### 1. Wayland/labwc - Eliminar grab_set() [Prioridad ALTA]
Archivos:
- `ui/widgets/dialogs.py`: 4 llamadas popup.grab_set()
- `ui/main_system_actions.py`: 1 llamada selection_window.grab_set()

**Reemplazar con:**
```
self.transient(parent)
self.after(150, self.focus_set)
self.master.focus_force()  # Antes de destroy en _on_close
```
Pattern completo en regla 'Reglas Wayland/labwc'.

**Estado:** FIXED ✅ (reemplazados 5 grab_set por transient/focus_set)

## Verificado ✓

- ✅ Capas core/ui estrictas (no tkinter en core/)
- ✅ Patterns core: start/stop/is_running en disk_monitor.py (muestra otros)
- ✅ Logging % format (no f-strings)
- ✅ Icons desde settings.Icons
- ✅ Labels desde button_labels.py
- ✅ Persistencia local_settings_io.py con read/write/update_params/get_param

## Próximos Pasos
1. Fix grab_set
2. Audit completo patterns en todos core/*.py
3. Bump v4.3, update changelog
4. attempt_completion
