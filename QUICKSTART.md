# 🚀 Inicio Rápido - Dashboard v2.5.1

---

## ⚡ Instalación (2 Comandos)

```bash
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard
chmod +x install_system.sh
sudo ./install_system.sh
python3 main.py
```

El script instala automáticamente las dependencias del sistema y Python, y pregunta si quieres configurar sensores y speedtest.

---

## 🔁 Alternativa con Entorno Virtual

Si prefieres aislar las dependencias:

```bash
chmod +x install.sh
./install.sh
source venv/bin/activate
python3 main.py
```

> Recuerda activar el entorno (`source venv/bin/activate`) cada vez que quieras ejecutar el dashboard.

---

## 📋 Requisitos Mínimos

- ✅ Raspberry Pi 3/4/5
- ✅ Raspberry Pi OS (cualquier versión)
- ✅ Python 3.8+
- ✅ Conexión a internet (para instalación)

---

## 🎯 Menú Principal (13 botones)

```
┌───────────────────────────────────┐
│  Control        │  Monitor         │
│  Ventiladores   │  Placa           │
├─────────────────┼──────────────────┤
│  Monitor        │  Monitor         │
│  Red            │  USB             │
├─────────────────┼──────────────────┤
│  Monitor        │  Lanzadores      │
│  Disco          │                  │
├─────────────────┼──────────────────┤
│  Monitor        │  Monitor         │
│  Procesos       │  Servicios       │
├─────────────────┼──────────────────┤
│  Histórico      │  Actualizaciones │
│  Datos          │                  │
├─────────────────┼──────────────────┤
│  Cambiar Tema   │  Reiniciar       │
├─────────────────┼──────────────────┤
│  Salir          │                  │
└─────────────────┴──────────────────┘
```

---

## 🖥️ Las 13 Ventanas

**1. Monitor Placa** — CPU, RAM y temperatura en tiempo real con gráficas

**2. Monitor Red** — Download/Upload en vivo, speedtest, lista de IPs

**3. Monitor USB** — Dispositivos conectados, expulsión segura

**4. Monitor Disco** — Espacio, temperatura NVMe, velocidad I/O

**5. Monitor Procesos** — Top 20 procesos, búsqueda, matar procesos

**6. Monitor Servicios** — Start/Stop/Restart systemd, ver logs

**7. Histórico Datos** — Gráficas CPU/RAM/Temp en 24h, 7d, 30d, exportar CSV

**8. Control Ventiladores** — Modo Auto/Manual/Silent/Normal/Performance, curvas PWM

**9. Lanzadores** — Scripts personalizados con terminal en vivo

**10. Actualizaciones** — Estado de paquetes, instalar con terminal integrada

**11. Cambiar Tema** — 15 temas (Cyberpunk, Matrix, Dracula, Nord...)

**12. Reiniciar** — Reinicia el dashboard aplicando cambios de código

**13. Salir** — Salir de la app o apagar el sistema

---

## 🔧 Configuración Básica

### Ajustar posición en pantalla DSI (`config/settings.py`):
```python
DSI_X = 0     # Posición horizontal
DSI_Y = 0     # Posición vertical
```

### Añadir scripts en Lanzadores:
```python
LAUNCHERS = [
    {"label": "Mi Script", "script": str(SCRIPTS_DIR / "mi_script.sh")},
]
```

---

## 📋 Ver Logs del Sistema

```bash
# En tiempo real
tail -f data/logs/dashboard.log

# Solo errores
grep ERROR data/logs/dashboard.log
```

---

## ❓ Problemas Comunes

| Problema | Solución |
|----------|----------|
| No arranca | `pip3 install --break-system-packages -r requirements.txt` |
| Temperatura 0 | `sudo sensors-detect --auto` |
| NVMe temp 0 | `sudo apt install smartmontools` |
| Speedtest falla | `sudo apt install speedtest-cli` |
| USB no expulsa | `sudo apt install udisks2` |
| Ver qué falla | `grep ERROR data/logs/dashboard.log` |

---

## 🆕 Novedades v2.5.1

✅ **Logging completo** — Todos los módulos loguean eventos y errores  
✅ **Ventana Actualizaciones** — Terminal integrada para instalar paquetes  
✅ **Caché de actualizaciones** — `apt update` solo al arranque y al pedir  
✅ **Fix arranque** — Servicio de datos ya no se detiene a los 3 segundos  
✅ **Terminal de apagado** — Visualiza el proceso de shutdown  

---

## 📚 Más Información

**[README.md](README.md)** — Documentación completa  
**[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** — Instalación detallada  
**[INDEX.md](INDEX.md)** — Índice de toda la documentación

---

**Dashboard v2.5.1** 🚀✨
