# 💡 Ideas de Expansión - Dashboard v3.2

---

## ✅ Implementado

### **1. Monitor de Procesos en Tiempo Real**
**Implementado en v2.0**
- ✅ Lista en tiempo real (Top 20) con PID, comando, usuario, CPU%, RAM%
- ✅ Búsqueda por nombre o comando
- ✅ Filtros: Todos / Usuario / Sistema
- ✅ Ordenar por PID, Nombre, CPU%, RAM%
- ✅ Matar procesos con confirmación
- ✅ Colores dinámicos según uso
- ✅ Pausa inteligente durante interacciones
- ✅ Estadísticas: procesos totales, CPU, RAM, uptime

---

### **2. Monitor de Servicios systemd**
**Implementado en v2.5**
- ✅ Lista completa de servicios systemd
- ✅ Estados: active, inactive, failed con iconos
- ✅ Start/Stop/Restart con confirmación
- ✅ Ver logs en tiempo real (últimas 50 líneas)
- ✅ Enable/Disable autostart
- ✅ Búsqueda y filtros (Todos / Activos / Inactivos / Fallidos)
- ✅ Estadísticas: total, activos, fallidos, enabled

---

### **3. Histórico de Datos**
**Implementado en v2.5 — ampliado en v2.5.1**
- ✅ Base de datos SQLite (~5MB/10k registros)
- ✅ Recolección automática cada 5 minutos en background
- ✅ Métricas guardadas: CPU, RAM, Temp, Disco I/O, Red, PWM, actualizaciones
- ✅ **8 gráficas**: CPU, RAM, Temperatura, Red Download, Red Upload, Disk Read, Disk Write, PWM
- ✅ Periodos: 24h, 7d, 30d
- ✅ Estadísticas completas: promedios, mínimos, máximos de todas las métricas
- ✅ Detección de anomalías automática
- ✅ Exportación a CSV
- ✅ Exportación de gráficas como imagen PNG
- ✅ Limpieza de datos antiguos configurable
- ✅ **Zoom, pan y navegación** sobre las gráficas (toolbar matplotlib)
- ✅ Registro de eventos críticos en BD separada

---

### **4. Sistema de Temas**
**Implementado en v2.0**
- ✅ 15 temas pre-configurados
- ✅ Cambio con un clic y reinicio automático
- ✅ Preview visual antes de aplicar
- ✅ Persistencia entre reinicios
- ✅ Todos los componentes usan colores del tema (sliders, scrollbars, radiobuttons)

---

### **5. Reinicio y Apagado**
**Implementado en v2.5**
- ✅ Botón Reiniciar con confirmación (aplica cambios de código)
- ✅ Botón Salir con opción de apagar el sistema
- ✅ Terminal de apagado (visualiza apagado.sh en vivo)

---

### **6. Actualizaciones del Sistema**
**Implementado en v2.5.1**
- ✅ Verificación al arranque en background (no bloquea la UI)
- ✅ Sistema de caché 12h (no repite apt update innecesariamente)
- ✅ Ventana dedicada con estado visual
- ✅ Instalación con terminal integrada en vivo
- ✅ Botón Buscar para forzar comprobación manual
- ✅ Refresco automático del estado tras instalar

---

### **7. Sistema de Logging Completo**
**Implementado en v2.5.1**
- ✅ Cobertura 100% en módulos core y UI
- ✅ Niveles diferenciados: DEBUG, INFO, WARNING, ERROR
- ✅ Rotación automática 2MB con backup
- ✅ Archivo fijo `data/logs/dashboard.log`

---

### **8. Lanzadores de Scripts**
**Implementado desde v1.0 — mejorado en v2.5.1**
- ✅ Scripts personalizados configurables en `settings.py`
- ✅ Terminal integrada que muestra el output en vivo
- ✅ Confirmación previa a ejecución
- ✅ Layout en grid configurable

---

### **9. Servicio de Limpieza Automática**
**Implementado en v2.6**
- ✅ `CleanupService` en `core/` — singleton, daemon thread
- ✅ Limpieza automática de CSV exportados (máx. 10)
- ✅ Limpieza automática de PNG exportados (máx. 10)
- ✅ Limpieza periódica de BD SQLite (registros >30 días, cada 24h)
- ✅ `force_cleanup()` para limpieza manual desde la UI
- ✅ Red de seguridad por tamaño en `DataLogger` (>5MB → limpia a 7 días)

---

### **10. Notificaciones Visuales en el Menú**
**Implementado en v2.6**
- ✅ 10 badges en el menú principal con alertas en tiempo real
- ✅ Temperatura, CPU, RAM, Disco, Servicios fallidos, Actualizaciones, Homebridge (3), Pi-hole

---

### **11. Header Unificado con Status Dinámico**
**Implementado en v2.7**
- ✅ `make_window_header()` centralizado en `ui/styles.py`
- ✅ Header en todas las ventanas: título + status + botón ✕ táctil 52×42px
- ✅ Status dinámico en Monitor Placa, Monitor Disco y Monitor Red
- ✅ Speedtest migrado a CLI oficial de Ookla (`--format=json`, MB/s reales)

---

### **12. Integración Homebridge**
**Implementado en v2.8 — extendido en v3.1**
- ✅ `HomebridgeMonitor` — JWT, sondeo 30s, caché en memoria
- ✅ 5 tipos de dispositivo: switch, light, thermostat, sensor, blind
- ✅ Tarjetas adaptativas en `HomebridgeWindow`
- ✅ `set_brightness()`, `set_target_temp()`
- ✅ 3 badges en el menú: offline, encendidos, fallo

---

### **13. Optimización de Rendimiento — UI sin bloqueos**
**Implementado en v2.9**
- ✅ `SystemMonitor` y `ServiceMonitor` con caché en background thread
- ✅ `_update()` de `MainWindow` solo lee cachés — sin syscalls bloqueantes
- ✅ `is-enabled` en llamada batch

---

### **14. Visor de Logs**
**Implementado en v3.0**
- ✅ Filtros por nivel, módulo (CTkEntry), texto libre e intervalo de fechas/horas
- ✅ Colores por nivel, selector rápido, exportación, recarga manual

---

### **15. Alertas Externas por Telegram**
**Implementado en v3.1**
- ✅ `AlertService` — anti-spam edge-trigger + sustain 60s, 5 métricas
- ✅ Sin dependencias nuevas (urllib stdlib)
- ✅ Configurable por `.env`

---

### **16. Escáner de Red Local**
**Implementado en v3.2**
- ✅ `NetworkScanner` — arp-scan con paths explícitos, thread background, auto-refresco 60s
- ✅ `NetworkLocalWindow` — lista scrollable con IP, MAC y fabricante
- ✅ Sudoers preconfigurado para ejecutar sin contraseña

---

### **17. Integración Pi-hole v6**
**Implementado en v3.2**
- ✅ `PiholeMonitor` — API v6 (sesión sid), sondeo 60s, renovación automática, logout limpio
- ✅ `PiholeWindow` — estadísticas en tiempo real: queries, bloqueadas, % bloqueo, clientes, dominios
- ✅ Badge `pihole_offline` en el menú
- ✅ Configurable por `.env`: `PIHOLE_HOST`, `PIHOLE_PORT`, `PIHOLE_PASSWORD`

---

### **18. Historial de Alertas**
**Implementado en v3.2**
- ✅ Persistencia en `data/alert_history.json` (máx. 100 entradas, FIFO)
- ✅ `AlertHistoryWindow` — tarjetas con franja lateral coloreada por nivel (naranja/rojo)
- ✅ Orden cronológico inverso (más reciente primero)
- ✅ Botón "Borrar todo" con confirmación

---

## 🔄 Planificado v3.3

### **Pantalla de Inicio / Dashboard Resumen**
**Complejidad**: 🟡 Media — 3-4h  
**Archivos**: `ui/windows/overview.py` (nuevo), `ui/main_window.py` (botón)

- Ventana resumen que muestra las métricas más importantes en un solo vistazo
- Widgets compactos: temperatura, CPU, RAM, disco, red, servicios fallidos, Pi-hole
- Actualización en tiempo real sin abrir múltiples ventanas
- Ideal como pantalla de reposo — siempre visible en la DSI

---

### **Control de Brillo de Pantalla DSI**
**Complejidad**: 🟢 Baja — 1-2h  
**Archivos**: `core/display_service.py` (nuevo), añadir a menú o settings

- Control del backlight vía `/sys/class/backlight/`
- Slider táctil de brillo en la UI
- Modo ahorro: bajar brillo automáticamente tras X minutos sin interacción
- Apagado de pantalla programable (útil por la noche)

---

### **Gestor de Conexiones VPN**
**Complejidad**: 🟡 Media — 3h  
**Archivos**: `core/vpn_monitor.py` (nuevo), `ui/windows/vpn_window.py` (nuevo)

- Estado de la VPN en tiempo real (conectado/desconectado, IP, servidor)
- Botones conectar/desconectar desde la UI
- Compatible con WireGuard y OpenVPN
- Badge en menú si VPN está desconectada

---

## 🚀 Ideas Futuras (Backlog)

**Backup**: programar backups de configuración, estado con progreso, sincronización NAS

**Seguridad**: intentos de login fallidos SSH, logs de seguridad, estado firewall ufw

**API REST**: endpoints para métricas, histórico y control de servicios desde la red local

---

## 🎯 Roadmap

### **v2.5.1** ✅ — 2026-02-20
- ✅ Logging completo, Ventana Actualizaciones, 8 gráficas, fix atexit

### **v2.6** ✅ — 2026-02-22
- ✅ Badges visuales en menú, CleanupService, Fan control con entries

### **v2.7** ✅ — 2026-02-23
- ✅ Header unificado, status dinámico, Speedtest Ookla CLI

### **v2.8** ✅ — 2026-02-23
- ✅ Integración Homebridge completa, JWT, 3 badges

### **v2.9** ✅ — 2026-02-24
- ✅ Caché background en SystemMonitor y ServiceMonitor, CTkSwitch táctil

### **v3.0** ✅ — 2026-02-26
- ✅ Visor de Logs, exports organizados, fix grab_set

### **v3.1** ✅ — 2026-02-26
- ✅ Alertas Telegram, Homebridge 5 tipos, UI diálogo salir mejorada

### **v3.2** ✅ ACTUAL — 2026-02-27
- ✅ Escáner Red Local (arp-scan), Pi-hole v6, Historial Alertas, fix filtro módulo logs

### **v3.3** (Próxima)
- [ ] Dashboard resumen / pantalla de reposo
- [ ] Control brillo pantalla DSI
- [ ] Gestor conexiones VPN

---

## 📈 Cobertura actual

| Área | Estado |
|------|--------|
| Monitoreo básico (CPU, RAM, Temp, Disco, Red) | ✅ 100% |
| Control avanzado (Ventiladores, Procesos, Servicios) | ✅ 100% |
| Histórico y análisis | ✅ 100% |
| Actualizaciones del sistema | ✅ 100% |
| Logging y observabilidad | ✅ 100% |
| Notificaciones visuales internas | ✅ 100% |
| UI unificada y táctil | ✅ 100% |
| Integración Homebridge (5 tipos) | ✅ 100% |
| Visor de logs con filtros y exportación | ✅ 100% |
| Exports organizados y limpieza automática | ✅ 100% |
| Alertas externas Telegram | ✅ 100% |
| Historial de alertas | ✅ 100% |
| Panel de red local (arp-scan) | ✅ 100% |
| Pi-hole v6 stats | ✅ 100% |
| Dashboard resumen / pantalla reposo | ⏳ 0% |
| Control brillo pantalla DSI | ⏳ 0% |
| Gestor conexiones VPN | ⏳ 0% |

---

**Versión actual**: v3.2 — **Próxima**: v3.3 — **Última actualización**: 2026-02-27
