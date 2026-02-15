# 🔗 Guía de Integración con fase1.py

Esta guía explica cómo integrar tu aplicación OLED (`fase1.py`) con el Dashboard para que ambos funcionen juntos.

---

## 🎯 ¿Cómo Funciona la Integración?

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  DASHBOARD (system_dashboard)                          │
│  - Interfaz gráfica                                    │
│  - Control de ventiladores                             │
│  - Guarda estado en: data/fan_state.json              │
│                                                         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Escribe fan_state.json
                   │ {"mode": "auto", "target_pwm": 128}
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  ARCHIVO COMPARTIDO                                     │
│  📄 data/fan_state.json                                │
│  {"mode": "auto", "target_pwm": 128}                   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Lee fan_state.json
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  OLED MONITOR (fase1.py / integration_fase1.py)       │
│  - Muestra CPU, RAM, Temp en OLED                     │
│  - Controla LEDs RGB                                   │
│  - Aplica PWM de ventiladores                         │
│  - Lee estado desde: data/fan_state.json              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Pasos de Integración

### 1️⃣ Instalar el Dashboard

```bash
# Descargar y extraer system_dashboard
cd ~
unzip system_dashboard_WITH_THEMES.zip
cd system_dashboard

# Instalar dependencias
sudo ./install_system.sh
```

### 2️⃣ Configurar Ruta en fase1.py

Edita tu `fase1.py` (o usa el nuevo `integration_fase1.py`):

```python
# En la línea ~13, cambia:
STATE_FILE = "/home/jalivur/system_dashboard/data/fan_state.json"

# Ajusta la ruta donde hayas puesto el proyecto
```

### 3️⃣ Ejecutar Ambos Programas

**Terminal 1** - Dashboard:
```bash
cd ~/system_dashboard
python3 main.py
```

**Terminal 2** - OLED Monitor:
```bash
cd /ruta/a/tu/fase1
python3 integration_fase1.py
# O tu fase1.py modificado
```

---

## 🔄 Flujo de Datos

### Cuando Cambias el Modo en el Dashboard:

1. **Usuario** hace clic en "Control Ventiladores"
2. **Dashboard** cambia el modo a "Manual" y PWM a 200
3. **Dashboard** guarda en `data/fan_state.json`:
   ```json
   {
     "mode": "manual",
     "target_pwm": 200
   }
   ```
4. **fase1.py** lee el archivo cada 1 segundo
5. **fase1.py** aplica PWM=200 a los ventiladores
6. **OLED** muestra "Fan1:78% Fan2:78%" (200/255 = 78%)

### Sincronización:

- ✅ Dashboard escribe cada vez que cambias algo
- ✅ fase1 lee cada 1 segundo
- ✅ PWM se aplica inmediatamente si cambia
- ✅ Sin conflictos (escritura atómica con .tmp)

---

## ⚙️ Modos Disponibles

El Dashboard soporta 5 modos:

| Modo | PWM | Descripción |
|------|-----|-------------|
| **Auto** | Dinámico | Basado en curva temperatura-PWM |
| **Manual** | Usuario | Tú eliges el valor (0-255) |
| **Silent** | 77 | Silencioso (30%) |
| **Normal** | 128 | Normal (50%) |
| **Performance** | 255 | Máximo (100%) |

El archivo `fan_state.json` siempre tiene `target_pwm` calculado, independientemente del modo.

---

## 🛠️ Configuración Avanzada

### Opción 1: Usar Rutas Relativas (Recomendado)

Modifica `integration_fase1.py`:

```python
import os
from pathlib import Path

# Ruta relativa al home del usuario
HOME = Path.home()
STATE_FILE = HOME / "system_dashboard" / "data" / "fan_state.json"
```

### Opción 2: Variable de Entorno

```bash
# En ~/.bashrc o ~/.profile
export DASHBOARD_DATA="/home/jalivur/system_dashboard/data"

# En fase1.py
STATE_FILE = os.environ.get("DASHBOARD_DATA", "/home/jalivur/system_dashboard/data") + "/fan_state.json"
```

### Opción 3: Enlace Simbólico

```bash
# Crear enlace en ubicación fija
ln -s ~/system_dashboard/data/fan_state.json /tmp/fan_state.json

# En fase1.py
STATE_FILE = "/tmp/fan_state.json"
```

---

## 🚀 Autostart de Ambos Programas

### Método 1: systemd (Recomendado)

**Dashboard:**
```bash
# Crear servicio
sudo nano /etc/systemd/system/dashboard.service
```

```ini
[Unit]
Description=System Dashboard
After=graphical.target

[Service]
Type=simple
User=jalivur
WorkingDirectory=/home/jalivur/system_dashboard
Environment="DISPLAY=:0"
ExecStart=/usr/bin/python3 /home/jalivur/system_dashboard/main.py
Restart=always

[Install]
WantedBy=graphical.target
```

**OLED Monitor:**
```bash
sudo nano /etc/systemd/system/oled-monitor.service
```

```ini
[Unit]
Description=OLED Monitor
After=network.target

[Service]
Type=simple
User=jalivur
WorkingDirectory=/home/jalivur/proyectopantallas
ExecStart=/usr/bin/python3 /home/jalivur/proyectopantallas/integration_fase1.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Activar:**
```bash
sudo systemctl enable dashboard.service
sudo systemctl enable oled-monitor.service

sudo systemctl start dashboard.service
sudo systemctl start oled-monitor.service

# Ver logs
sudo journalctl -u dashboard.service -f
sudo journalctl -u oled-monitor.service -f
```

### Método 2: Crontab @reboot

```bash
crontab -e
```

Añadir:
```cron
@reboot sleep 30 && DISPLAY=:0 /usr/bin/python3 /home/jalivur/system_dashboard/main.py &
@reboot sleep 10 && /usr/bin/python3 /home/jalivur/proyectopantallas/integration_fase1.py &
```

---

## 🐛 Solución de Problemas

### El OLED no muestra cambios de ventilador

**Verificar que el archivo existe:**
```bash
ls -la ~/system_dashboard/data/fan_state.json
```

**Ver contenido:**
```bash
cat ~/system_dashboard/data/fan_state.json
# Debe mostrar: {"mode": "...", "target_pwm": ...}
```

**Ver logs de fase1:**
```bash
# Añadir debug al inicio
python3 integration_fase1.py
# Verás: "Estado leído: modo=auto, PWM=128"
```

### El PWM no cambia

**Verificar permisos:**
```bash
chmod 644 ~/system_dashboard/data/fan_state.json
```

**Verificar que fase1 lee el archivo:**
```python
# Añadir en el código de fase1:
if state:
    print(f"DEBUG: Estado leído = {state}")
```

### Los dos programas pelean por los ventiladores

**Esto NO debería pasar** porque:
- Dashboard solo ESCRIBE el estado
- fase1 solo LEE el estado
- fase1 es quien aplica el PWM físicamente

Si pasa:
1. Cierra el Dashboard
2. Solo ejecuta fase1
3. Verifica que funciona
4. Vuelve a abrir Dashboard

---

## 💡 Tips y Trucos

### Ver Estado en Tiempo Real

```bash
# Terminal dedicado
watch -n 1 cat ~/system_dashboard/data/fan_state.json
```

### Script de Debug

```bash
#!/bin/bash
# debug_integration.sh

echo "=== Estado del Dashboard ==="
cat ~/system_dashboard/data/fan_state.json | python3 -m json.tool

echo ""
echo "=== Procesos corriendo ==="
ps aux | grep -E "main.py|fase1.py|integration_fase1.py"

echo ""
echo "=== Temperatura actual ==="
vcgencmd measure_temp
```

### Notificaciones de Cambio

Añade a `integration_fase1.py`:

```python
last_mode = None

# En el bucle:
if state and state.get("mode") != last_mode:
    new_mode = state.get("mode")
    print(f"🔔 Modo cambiado: {last_mode} → {new_mode}")
    # Opcionalmente, mostrar en OLED temporalmente
    last_mode = new_mode
```

---

## 📊 Monitoreo

### Ver Logs en Tiempo Real

```bash
# Dashboard
tail -f ~/system_dashboard/dashboard.log

# OLED Monitor
tail -f ~/proyectopantallas/oled_monitor.log
```

### Crear Logs

Añade al inicio de `integration_fase1.py`:

```python
import logging

logging.basicConfig(
    filename='/home/jalivur/proyectopantallas/oled_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# En el bucle:
if state:
    logging.info(f"PWM aplicado: {fan_pwm}, Modo: {state.get('mode')}")
```

---

## ✅ Checklist de Integración

- [ ] Dashboard instalado y funcionando
- [ ] Archivo `fan_state.json` se crea al cambiar modo
- [ ] Ruta correcta configurada en fase1.py
- [ ] fase1.py lee el archivo correctamente
- [ ] PWM se aplica a los ventiladores físicos
- [ ] OLED muestra el porcentaje correcto
- [ ] Ambos programas arrancan al inicio (opcional)
- [ ] Logs configurados (opcional)

---

## 🎯 Resultado Final

Una vez integrado correctamente:

✅ Cambias modo en Dashboard → Ventiladores responden inmediatamente
✅ OLED muestra estado actual de ventiladores
✅ LEDs cambian color según temperatura
✅ Todo funciona sin conflictos
✅ Puedes cerrar Dashboard, fase1 sigue funcionando
✅ Puedes cerrar fase1, Dashboard sigue guardando estado

---

## 📞 ¿Problemas?

Si tienes problemas con la integración:

1. Verifica rutas con `ls -la`
2. Verifica contenido con `cat`
3. Añade `print()` para debug
4. Ejecuta manualmente primero (no autostart)
5. Revisa logs de systemd si usas servicios

---

**¡Disfruta de tu sistema integrado!** 🎉
