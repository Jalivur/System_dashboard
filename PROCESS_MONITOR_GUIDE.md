# 📊 Monitor de Procesos - Guía Completa

## 🎯 Descripción

El Monitor de Procesos permite visualizar y gestionar todos los procesos del sistema en tiempo real, con capacidades de búsqueda, filtrado y terminación de procesos.

---

## ✨ Características

### 📋 **Visualización de Procesos:**
- Lista de procesos activos (Top 20 por defecto)
- Información detallada: PID, Comando, Usuario, CPU%, RAM%
- **Comandos completos** con argumentos visibles
- Colores dinámicos según uso:
  - 🟢 Verde: < 30% (uso bajo)
  - 🟡 Amarillo: 30-70% (uso medio)
  - 🔴 Rojo: ≥ 70% (uso alto)

### 🔄 **Actualización en Tiempo Real:**
- Refresco automático cada 4 segundos
- **Pausa inteligente** durante interacciones (ordenar/filtrar/buscar)
- Reanudación automática

### 📊 **Estadísticas del Sistema:**
- Total de procesos activos
- Uso total de CPU
- RAM usada / total (GB y %)
- Uptime del sistema

### 🔍 **Búsqueda Avanzada:**
- Busca en nombre del proceso Y comando completo
- **Debounce** de 500ms (no busca cada letra)
- Resultados instantáneos
- Resalta procesos que coinciden

### ⚙️ **Filtros:**
- **Todos:** Muestra todos los procesos
- **Usuario:** Solo procesos del usuario actual
- **Sistema:** Solo procesos del sistema (root, etc)

### 📏 **Ordenación:**
- Ordena por cualquier columna (clic en header)
- Criterios: PID, Nombre, Usuario, CPU%, RAM%
- Orden ascendente / descendente

### 🔴 **Terminación de Procesos:**
- Botón "Matar" por proceso
- **Confirmación obligatoria** antes de terminar
- Intento de cierre limpio (SIGTERM)
- Forzado si no responde (SIGKILL)
- Mensajes de éxito/error

---

## 🖥️ Interfaz

```
┌──────────────────────────────────────────────────────────┐
│                  MONITOR DE PROCESOS                     │
│  Procesos: 245 | CPU: 12.5% | RAM: 4.2/16 GB | Up: 3d   │
├──────────────────────────────────────────────────────────┤
│  Buscar: [________]  Filtro: ⦿Todos  ○Usuario  ○Sistema │
├──────────────────────────────────────────────────────────┤
│ PID │ Proceso                        │ Usr │ CPU │ RAM │  │
├─────┼────────────────────────────────┼─────┼─────┼─────┤──┤
│1234 │python3 /home/user/dashboard.py │user │45.2%│12.1%│[X]│
│     │--debug --port=8000             │     │     │     │   │
├─────┼────────────────────────────────┼─────┼─────┼─────┼──┤
│5678 │/usr/bin/chrome                 │user │35.8%│ 8.4%│[X]│
│     │--app=youtube.com               │     │     │     │   │
├─────┼────────────────────────────────┼─────┼─────┼─────┼──┤
│9012 │systemd                         │root │ 2.1%│ 0.9%│[X]│
└─────┴────────────────────────────────┴─────┴─────┴─────┴──┘
                           [Cerrar]
```

---

## 📖 Uso

### **Abrir el Monitor:**
1. Desde el menú principal, clic en "Monitor Procesos"
2. La ventana se abre mostrando los procesos activos

### **Ordenar Procesos:**
1. Haz clic en cualquier columna del encabezado
2. Primera vez: Ordena descendente
3. Segunda vez: Invierte el orden
4. Actualización se pausa 2 segundos

### **Buscar un Proceso:**
1. Escribe en el campo "Buscar"
2. Espera 500ms (búsqueda automática)
3. Busca en nombre Y comando completo
4. Ejemplo: Buscar "chrome" encuentra todos los procesos Chrome

### **Filtrar por Tipo:**
1. **Todos:** Muestra todos los procesos del sistema
2. **Usuario:** Solo tus procesos
3. **Sistema:** Procesos del sistema (root, etc)

### **Matar un Proceso:**
1. Localiza el proceso en la lista
2. Clic en botón "Matar" rojo
3. Aparece confirmación:
   ```
   ¿Matar proceso 'chrome'?
   PID: 5678
   CPU: 35.8%
   ```
4. Confirma o cancela
5. Si confirmas:
   - Intento de cierre limpio (SIGTERM)
   - Si no responde en 3s → Forzado (SIGKILL)
   - Mensaje de éxito/error

---

## 🎨 Personalización

### **Ajustar Columnas:**
Edita `ui/windows/process_window.py` líneas ~295-300:

```python
# Anchos de columnas
row_frame.grid_columnconfigure(0, weight=1, minsize=70)   # PID
row_frame.grid_columnconfigure(1, weight=3, minsize=200)  # Proceso
row_frame.grid_columnconfigure(2, weight=2, minsize=100)  # Usuario
row_frame.grid_columnconfigure(3, weight=1, minsize=80)   # CPU
row_frame.grid_columnconfigure(4, weight=1, minsize=80)   # RAM
row_frame.grid_columnconfigure(5, weight=1, minsize=100)  # Acción
```

### **Cambiar Intervalo de Actualización:**
Línea ~268:
```python
self.update_job = self.after(UPDATE_MS * 2, self._update)  # 4 segundos
# Cambiar a UPDATE_MS * 3 para 6 segundos
```

### **Cambiar Límite de Procesos:**
Línea ~265:
```python
processes = self.process_monitor.get_processes(limit=20)  # Top 20
# Cambiar a limit=50 para ver más
```

### **Ajustar Wrap del Texto:**
Línea ~333:
```python
wraplength=350  # Ancho antes de saltar línea
# Más ancho (500) = menos líneas
# Más estrecho (250) = más líneas
```

---

## ⚠️ Advertencias

### **Matar Procesos del Sistema:**
- ⚠️ Ten cuidado al matar procesos de `root`
- Algunos procesos son críticos para el sistema
- Si no estás seguro, NO lo mates

### **Procesos que NO se deben Matar:**
- `systemd` (PID 1)
- `init`
- `kernel` threads (entre corchetes)
- Procesos de X11/Wayland si usas interfaz gráfica

### **Sin Permisos:**
- No puedes matar procesos de otros usuarios (sin sudo)
- Aparecerá error: "Sin permisos para terminar proceso"

---

## 🐛 Troubleshooting

### **Problema: Lista vacía**
**Causa:** Filtro muy restrictivo  
**Solución:** Selecciona "Todos" en filtros

### **Problema: Búsqueda no encuentra**
**Causa:** Búsqueda case-sensitive o comando truncado  
**Solución:** Busca por nombre corto (ej: "chrome" no "google-chrome")

### **Problema: No puedo matar proceso**
**Causa:** Sin permisos  
**Solución:** Ejecuta dashboard con sudo (no recomendado) o solo mata tus procesos

### **Problema: Interfaz laggy**
**Causa:** Demasiados procesos visibles  
**Solución:** Reduce límite a 10-15 en línea 265

---

## 💡 Tips

1. **Ordena por CPU%** para encontrar procesos que consumen más
2. **Ordena por RAM%** para encontrar memory leaks
3. **Usa filtro Usuario** para ver solo tus procesos
4. **Busca por comando** para encontrar scripts específicos
5. **El texto largo se ajusta** en múltiples líneas automáticamente

---

## 🔧 Arquitectura

### **Backend: `core/process_monitor.py`**
- Obtiene procesos con `psutil`
- Filtra, ordena, busca
- Termina procesos con `SIGTERM`/`SIGKILL`
- Obtiene estadísticas del sistema

### **Frontend: `ui/windows/process_window.py`**
- Interfaz con `customtkinter`
- Grid layout para tabla
- Canvas con scroll
- Actualización automática con pausa inteligente

---

## 📊 Ejemplos de Uso

### **Encontrar proceso que consume CPU:**
1. Clic en columna "CPU%"
2. Procesos ordenados por uso de CPU
3. El primero es el que más usa

### **Matar todos los Chrome:**
1. Buscar: "chrome"
2. Aparecen todos los procesos Chrome
3. Matar uno por uno

### **Ver solo mis procesos:**
1. Filtro: Usuario
2. Solo aparecen procesos con tu nombre de usuario

### **Monitorear un script:**
1. Buscar: nombre del script
2. Ver CPU y RAM en tiempo real
3. Matar si se cuelga

---

## 🎯 Casos de Uso

✅ Identificar procesos que consumen recursos  
✅ Encontrar y matar procesos colgados  
✅ Monitorear scripts en ejecución  
✅ Detectar memory leaks  
✅ Ver qué programas están corriendo  
✅ Gestionar procesos del usuario  
✅ Debugging de aplicaciones  

---

**¡Monitor de procesos profesional integrado en tu dashboard!** 📊✨
