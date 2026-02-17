# 💡 Ideas de Expansión para el Dashboard

Este documento contiene el roadmap de funcionalidades futuras y el estado de implementación.

---

## ✅ Implementado en v2.0

### **✅ 1. Monitor de Procesos en Tiempo Real** ⭐
**Estado**: IMPLEMENTADO

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

### **✅ 2. Sistema de Temas Personalizable** 🎨
**Estado**: IMPLEMENTADO

**Funcionalidades actuales:**
- ✅ 15 temas pre-configurados
- ✅ Cambio con un clic
- ✅ Reinicio automático al aplicar
- ✅ Preview visual antes de aplicar
- ✅ Persistencia entre reinicios
- ✅ Todos los componentes (sliders, scrollbars) usan colores del tema

**Ver**: [THEMES_GUIDE.md](THEMES_GUIDE.md)

---

## 📊 En Evaluación (Próximas Versiones)

### **🔄 1. Monitor de Contenedores Docker**
**Prioridad**: Alta  
**Complejidad**: Media

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

---

### **🔄 2. Monitor de Servicios systemd**
**Prioridad**: Media  
**Complejidad**: Baja

**Concepto:**
Monitorear y gestionar servicios del sistema.

**Funcionalidades propuestas:**
```
┌─────────────────────────────────────────┐
│ SERVICIOS DEL SISTEMA                   │
├──────────────┬──────────┬───────────────┤
│ Servicio     │ Estado   │ Acciones      │
├──────────────┼──────────┼───────────────┤
│ 🟢 nginx     │ active   │ [⏸][🔄][🔄]   │
│ 🟢 ssh       │ active   │ [⏸][🔄][🔄]   │
│ 🔴 apache2   │ inactive │ [▶]           │
└──────────────┴──────────┴───────────────┘
```

**Características:**
- Ver todos los servicios
- Start/Stop/Restart servicios
- Ver logs de servicios
- Enable/Disable autostart
- Ver dependencias

---

### **🔄 3. Monitor de GPU**
**Prioridad**: Baja  
**Complejidad**: Media

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
- GPU compatible
- Drivers instalados
- nvidia-smi o radeontop

---

### **🔄 4. Histórico de Datos**
**Prioridad**: Media  
**Complejidad**: Alta

**Concepto:**
Guardar histórico de métricas para análisis posterior.

**Funcionalidades propuestas:**
- Guardar datos cada 5 minutos
- Ver gráficas de 24h, 7 días, 30 días
- Exportar a CSV
- Detectar patrones
- Alertas basadas en histórico

**Datos a guardar:**
- CPU, RAM, temperatura
- Tráfico de red
- Uso de disco
- PWM de ventiladores

---

## 🚀 Ideas Futuras (Backlog)

### **Notificaciones y Alertas**
- Alertas por temperatura alta
- Notificaciones de disco lleno
- Alertas por proceso consumiendo mucho
- Envío de alertas por email/Telegram

### **Automatización**
- Scripts programados (cron visual)
- Acciones automáticas según condiciones
- Profiles de ventiladores según hora del día
- Auto-reinicio de servicios caídos

### **Smart Home / IoT**
- Integración con Home Assistant
- Control de luces Philips Hue
- Sensores de temperatura externos
- Control de enchufes inteligentes

### **Multimedia**
- Control de Plex/Jellyfin
- Monitor de descargas (qBittorrent, Transmission)
- Gestión de media library
- Reproducción remota

### **Red Avanzada**
- Monitor de dispositivos en red (nmap)
- Bloqueo de IPs (firewall visual)
- VPN control panel
- DNS monitoring (Pi-hole stats)

### **Backup y Sincronización**
- Programar backups automáticos
- Sincronización con cloud (Nextcloud, Google Drive)
- Estado de backups
- Restauración visual

### **Seguridad**
- Monitor de intentos de login fallidos
- Análisis de logs de seguridad
- Escaneo de puertos abiertos
- Updates de sistema disponibles

---

## 🤝 Contribuir

¿Quieres implementar alguna de estas ideas?

1. Fork del repositorio
2. Crea una rama: `git checkout -b feature-nombre`
3. Implementa la funcionalidad
4. Pull Request con descripción detallada

### **Qué incluir en tu PR:**
- Código funcional
- Documentación (GUIA_TU_FEATURE.md)
- Actualización del README.md
- Tests si aplica

---

## 📊 Votación de Features

Si quieres una feature específica, abre un **Issue** con:
- Título: `[Feature Request] Nombre de la feature`
- Descripción detallada
- Casos de uso
- Mockups o ejemplos (opcional)

Las features más votadas (👍 reactions) tendrán prioridad.

---

## 🎯 Roadmap

### **v2.1** (Próximo)
- [ ] Monitor de Servicios systemd
- [ ] Mejoras en Monitor de Procesos (gráficas CPU/RAM por proceso)
- [ ] Más temas personalizables

### **v2.2**
- [ ] Monitor de Docker
- [ ] Histórico de datos (24h)
- [ ] Alertas configurables

### **v3.0**
- [ ] Monitor de GPU
- [ ] Notificaciones push
- [ ] API REST para integración

---

## 💬 Feedback

¿Tienes otras ideas? Abre un Issue con la etiqueta `idea` 💡

---

**Estado del proyecto**: Activamente desarrollado 🚀  
**Versión actual**: v2.0  
**Última actualización**: 2026-02-16
