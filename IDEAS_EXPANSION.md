# 💡 Ideas de Expansión - Dashboard v2.5

Este documento contiene el roadmap de funcionalidades futuras y el estado de implementación actualizado.

---

## ✅ Implementado en v2.5

### **✅ 1. Monitor de Procesos en Tiempo Real** ⭐
**Estado**: IMPLEMENTADO en v2.0

**Funcionalidades actuales:**
- ✅ Lista de procesos en tiempo real (Top 20)
- ✅ Información: PID, Comando completo, Usuario, CPU%, RAM%
- ✅ Búsqueda por nombre o comando
- ✅ Filtros: Todos / Usuario / Sistema
- ✅ Ordenar por: PID, Nombre, CPU%, RAM%
- ✅ Matar procesos con confirmación
- ✅ Colores dinámicos según uso
- ✅ Actualización inteligente (pausa durante interacciones)
- ✅ Estadísticas del sistema: procesos totales, CPU, RAM, uptime

**Ver**: [PROCESS_MONITOR_GUIDE.md](PROCESS_MONITOR_GUIDE.md)

---

### **✅ 2. Monitor de Servicios systemd** ⭐
**Estado**: IMPLEMENTADO en v2.5

**Funcionalidades actuales:**
- ✅ Lista completa de servicios systemd
- ✅ Estados: active, inactive, failed con iconos
- ✅ Start/Stop/Restart servicios con confirmación
- ✅ Ver logs en tiempo real (últimas 50 líneas)
- ✅ Enable/Disable autostart
- ✅ Búsqueda por nombre o descripción
- ✅ Filtros: Todos / Activos / Inactivos / Fallidos
- ✅ Ordenación por nombre o estado
- ✅ Estadísticas: total, activos, fallidos, enabled

**Ver**: [SERVICE_MONITOR_GUIDE.md](SERVICE_MONITOR_GUIDE.md)

---

### **✅ 3. Histórico de Datos** ⭐
**Estado**: IMPLEMENTADO en v2.5

**Funcionalidades actuales:**
- ✅ Base de datos SQLite ligera (~5MB/10k registros)
- ✅ Recolección automática cada 5 minutos (background)
- ✅ Métricas guardadas: CPU, RAM, Temp, Disco, Red, PWM
- ✅ Visualización gráfica con matplotlib (3 gráficas)
- ✅ Periodos: 24 horas, 7 días, 30 días
- ✅ Estadísticas: promedios, mínimos, máximos
- ✅ Detección de anomalías automática
- ✅ Exportación a CSV
- ✅ Limpieza de datos antiguos (>90 días)
- ✅ Registro de eventos críticos

**Ver**: [HISTORICO_DATOS_GUIDE.md](HISTORICO_DATOS_GUIDE.md)

---

### **✅ 4. Sistema de Temas Personalizable** 🎨
**Estado**: IMPLEMENTADO en v2.0

**Funcionalidades actuales:**
- ✅ 15 temas pre-configurados
- ✅ Cambio con un clic
- ✅ Reinicio automático al aplicar
- ✅ Preview visual antes de aplicar
- ✅ Persistencia entre reinicios
- ✅ Todos los componentes usan colores del tema
- ✅ Sliders, scrollbars, botones temáticos

**Ver**: [THEMES_GUIDE.md](THEMES_GUIDE.md)

---

### **✅ 5. Botón de Reinicio Rápido** 🔄
**Estado**: IMPLEMENTADO en v2.5

**Funcionalidades actuales:**
- ✅ Botón "Reiniciar" en menú principal
- ✅ Reinicia el dashboard con un clic
- ✅ Aplica cambios de código y configuración
- ✅ Confirmación antes de reiniciar
- ✅ Perfecto para desarrollo

---

## 📊 En Evaluación (Próximas Versiones)

### **🔄 1. Monitor de Contenedores Docker**
**Prioridad**: Alta  
**Complejidad**: Media  
**Versión estimada**: v3.0

**Concepto:**
Dashboard específico para gestionar contenedores Docker desde la interfaz.

**Funcionalidades propuestas:**
```
┌──────────────────────────────────────────┐
│ CONTENEDORES (3 corriendo, 2 parados)   │
├──────────────┬────────┬──────┬───────────┤
│ Nombre       │ Estado │ CPU  │ Acciones  │
├──────────────┼────────┼──────┼───────────┤
│ 🟢 pihole    │ Up 5d  │ 2%   │ [⏸][🔄][🗑] │
│ 🟢 nextcloud │ Up 2h  │ 15%  │ [⏸][🔄][🗑] │
│ 🟢 postgres  │ Up 5d  │ 3%   │ [⏸][🔄][🗑] │
└──────────────┴────────┴──────┴───────────┘
```

**Características:**
- Start/Stop/Restart contenedores
- Ver logs en tiempo real
- Estadísticas de uso por contenedor
- Gestión de volúmenes
- Ver puertos expuestos
- Ejecutar comandos dentro del contenedor

**Implementación:**
- Usar `docker` Python SDK
- Comunicación con Docker daemon
- Similar a `docker ps`, `docker stats`

---

### **🔄 2. Monitor de GPU**
**Prioridad**: Baja  
**Complejidad**: Media  
**Versión estimada**: v3.0+

**Concepto:**
Monitoreo específico de GPU (NVIDIA/AMD).

**Funcionalidades propuestas:**
- Temperatura de GPU
- Uso de GPU (%)
- Uso de VRAM
- Frecuencia actual
- Power consumption
- Gráficas históricas

**Requisitos:**
- GPU compatible (NVIDIA/AMD)
- Drivers instalados
- nvidia-smi o radeontop

**Notas:**
- Baja prioridad (Raspberry Pi sin GPU dedicada)
- Útil para otros SBCs con GPU

---

### **🔄 3. Alertas y Notificaciones**
**Prioridad**: Media  
**Complejidad**: Media  
**Versión estimada**: v3.0

**Concepto:**
Sistema de alertas configurable con notificaciones externas.

**Funcionalidades propuestas:**
- Alertas por temperatura alta (>80°C)
- Alertas por CPU alta sostenida (>90%)
- Alertas por disco lleno (>95%)
- Alertas por servicios caídos
- Notificaciones por email
- Notificaciones por Telegram
- Notificaciones por webhook

**Configuración:**
```python
ALERTS = {
    'temperature': {
        'threshold': 80,
        'notify': ['email', 'telegram']
    },
    'cpu': {
        'threshold': 90,
        'duration': 300,  # 5 minutos sostenido
        'notify': ['telegram']
    }
}
```

---

### **🔄 4. Gráficas Mejoradas**
**Prioridad**: Media  
**Complejidad**: Baja  
**Versión estimada**: v2.6

**Concepto:**
Mejorar las gráficas existentes del histórico.

**Funcionalidades propuestas:**
- Gráfica de Red (download/upload histórico)
- Gráfica de Disco (I/O histórico)
- Gráfica de PWM del ventilador
- Zoom en gráficas
- Selección de rango personalizado
- Comparación de periodos
- Líneas de umbral configurables

---

## 🚀 Ideas Futuras (Backlog)

### **Automatización:**
- Scripts programados (cron visual)
- Acciones automáticas según condiciones
- Profiles de ventiladores según hora del día
- Auto-reinicio de servicios caídos
- Backup automático de configuración

### **Smart Home / IoT:**
- Integración con Home Assistant
- Control de luces Philips Hue
- Sensores de temperatura externos
- Control de enchufes inteligentes
- Dashboard de sensores

### **Multimedia:**
- Control de Plex/Jellyfin
- Monitor de descargas (qBittorrent, Transmission)
- Gestión de media library
- Reproducción remota
- Stats de uso multimedia

### **Red Avanzada:**
- Monitor de dispositivos en red (nmap)
- Bloqueo de IPs (firewall visual)
- VPN control panel
- DNS monitoring (Pi-hole stats)
- Port scanning

### **Backup y Sincronización:**
- Programar backups automáticos
- Sincronización con cloud (Nextcloud, Google Drive)
- Estado de backups con progreso
- Restauración visual
- Versionado de backups

### **Seguridad:**
- Monitor de intentos de login fallidos
- Análisis de logs de seguridad
- Escaneo de puertos abiertos
- Updates de sistema disponibles
- Firewall status

### **API REST:**
- Endpoint para métricas actuales
- Endpoint para histórico
- Endpoint para control de servicios
- Autenticación con tokens
- Documentación Swagger

### **Machine Learning:**
- Predicción de uso de CPU/RAM
- Detección de anomalías avanzada
- Recomendaciones de optimización
- Predicción de fallos
- Clustering de patrones

---

## 🤝 Contribuir

¿Quieres implementar alguna de estas ideas?

1. Fork del repositorio
2. Crea una rama: `git checkout -b feature-nombre`
3. Implementa la funcionalidad
4. Pull Request con descripción detallada

### **Qué incluir en tu PR:**
- Código funcional y probado
- Documentación (GUIA_TU_FEATURE.md)
- Actualización del README.md
- Tests si aplica
- Screenshots o demos

---

## 📊 Votación de Features

Si quieres una feature específica, abre un **Issue** con:
- Título: `[Feature Request] Nombre de la feature`
- Descripción detallada con casos de uso
- Mockups o ejemplos (opcional)
- Por qué sería útil

Las features más votadas (👍 reactions) tendrán prioridad.

---

## 🎯 Roadmap

### **v2.5** ✅ ACTUAL - 2026-02-17
- ✅ Monitor de Servicios systemd
- ✅ Histórico de Datos con SQLite
- ✅ Botón de Reinicio rápido
- ✅ Recolección automática background
- ✅ Exportación CSV
- ✅ Detección de anomalías

### **v2.6** (Próximo) - Q1 2026
- [ ] Gráficas mejoradas (Red, Disco, PWM)
- [ ] Zoom y selección de rango
- [ ] Comparación de periodos
- [ ] Mejoras UI generales

### **v3.0** (Futuro) - Q2 2026
- [ ] Monitor de Docker
- [ ] Alertas y notificaciones
- [ ] API REST básica
- [ ] Plugin system

### **v3.5** (Futuro) - Q3 2026
- [ ] Monitor de GPU
- [ ] Integración Home Assistant
- [ ] Machine Learning básico
- [ ] Dashboard web

---

## 💬 Feedback

¿Tienes otras ideas? Abre un Issue con la etiqueta `idea` 💡

---

## 📈 Progreso del Proyecto

### **Funcionalidades Totales:**
- ✅ Implementadas: 5 grandes funciones (Procesos, Servicios, Histórico, Temas, Reinicio)
- 🔄 En evaluación: 4 funciones (Docker, GPU, Alertas, Gráficas)
- 💭 Ideas futuras: 30+ funciones en backlog

### **Cobertura:**
- Monitoreo básico: ✅ 100%
- Control avanzado: ✅ 100%
- Histórico: ✅ 100%
- Alertas: ⏳ 0%
- Automatización: ⏳ 0%
- Integración externa: ⏳ 0%

---

**Estado del proyecto**: Activamente desarrollado 🚀  
**Versión actual**: v2.5  
**Última actualización**: 2026-02-17  
**Próxima versión**: v2.6 (Q1 2026)
