# 📚 Índice de Documentación - System Dashboard v2.7

Guía completa de toda la documentación del proyecto actualizada.

---

## 🚀 Documentos Esenciales

### **Para Empezar:**
1. **[README.md](README.md)** ⭐  
   Documentación completa del proyecto v2.7. **Empieza aquí.**

2. **[QUICKSTART.md](QUICKSTART.md)** ⚡  
   Instalación y ejecución en 5 minutos.

---

## 📖 Guías por Tema

### 🎨 **Personalización**

**[THEMES_GUIDE.md](THEMES_GUIDE.md)**  
- Lista completa de 15 temas
- Cómo crear temas personalizados
- Paletas de colores de cada tema
- Cambiar tema desde código

---

### 🔧 **Instalación**

**[INSTALL_GUIDE.md](INSTALL_GUIDE.md)**  
- Instalación en Raspberry Pi OS
- Instalación en Kali Linux
- Instalación en otros Linux
- Solución de problemas comunes
- Métodos: venv, sin venv, script automático

---

### ⚙️ **Características Avanzadas**

**[PROCESS_MONITOR_GUIDE.md](PROCESS_MONITOR_GUIDE.md)**  
- Monitor de procesos completo
- Búsqueda y filtrado
- Terminación de procesos
- Personalización de columnas

**[SERVICE_MONITOR_GUIDE.md](SERVICE_MONITOR_GUIDE.md)**  
- Monitor de servicios systemd
- Start/Stop/Restart servicios
- Enable/Disable autostart
- Ver logs en tiempo real
- Implementación paso a paso

**[HISTORICO_DATOS_GUIDE.md](HISTORICO_DATOS_GUIDE.md)**  
- Sistema de histórico completo
- Base de datos SQLite
- Visualización con matplotlib
- Recolección automática
- Exportación CSV
- Implementación paso a paso

**[FAN_CONTROL_GUIDE.md](FAN_CONTROL_GUIDE.md)** (si existe)  
- Configuración de ventiladores PWM
- Crear curvas personalizadas
- Modos de operación
- Servicio background

**[NETWORK_GUIDE.md](NETWORK_GUIDE.md)** (si existe)  
- Monitor de tráfico de red
- Speedtest integrado (CLI oficial Ookla)
- Auto-detección de interfaz
- Lista de IPs

---

### 🏗️ **Arquitectura**

**[ARCHITECTURE.md](ARCHITECTURE.md)** (si existe)  
- Estructura del proyecto
- Patrones de diseño
- Flujo de datos
- Cómo extender funcionalidad

---

### 🤝 **Integración**

**[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)**  
- Integrar con fase1.py (OLED)
- Compartir estado de ventiladores
- API de archivos JSON
- Sincronización entre procesos

---

### 💡 **Ideas y Expansión**

**[IDEAS_EXPANSION.md](IDEAS_EXPANSION.md)**  
- ✅ Funcionalidades implementadas (Procesos, Servicios, Histórico, Badges, Header unificado)
- 🔄 En evaluación (Docker, GPU)
- 💭 Ideas futuras (Alertas, Automatización)
- Roadmap v3.0

---

## 📋 Archivos de Soporte

### **Configuración:**
- `requirements.txt` - Dependencias Python
- `install.sh` - Script de instalación automática
- `config/settings.py` - Configuración global
- `config/themes.py` - Definición de 15 temas

### **Scripts:**
- `main.py` - Punto de entrada
- `scripts/` - Scripts personalizados

### **Compatibilidad:**
- `COMPATIBILIDAD.md` - Sistemas soportados
- `REQUIREMENTS.md` - Requisitos detallados

---

## 🗂️ Estructura de Documentos v2.7

```
📚 Documentación/
├── README.md                    ⭐ Documento principal v2.7
├── QUICKSTART.md                ⚡ Inicio rápido
├── INDEX.md                     📑 Este archivo
├── INSTALL_GUIDE.md             🔧 Instalación
├── THEMES_GUIDE.md              🎨 Guía de temas
├── PROCESS_MONITOR_GUIDE.md     ⚙️ Monitor de procesos
├── SERVICE_MONITOR_GUIDE.md     🔧 Monitor de servicios
├── HISTORICO_DATOS_GUIDE.md     📊 Histórico de datos
├── INTEGRATION_GUIDE.md         🤝 Integración
├── IDEAS_EXPANSION.md           💡 Ideas futuras
├── COMPATIBILIDAD.md            🌐 Compatibilidad
└── REQUIREMENTS.md              📋 Requisitos
```

---

## 🎯 Flujo de Lectura Recomendado

### **Usuario Nuevo:**
1. README.md - Leer sección "Características"
2. QUICKSTART.md - Instalar y ejecutar
3. THEMES_GUIDE.md - Personalizar colores
4. Explorar las 13 ventanas del dashboard 🎉

### **Usuario Avanzado:**
1. README.md completo
2. PROCESS_MONITOR_GUIDE.md - Gestión avanzada
3. SERVICE_MONITOR_GUIDE.md - Control de servicios
4. HISTORICO_DATOS_GUIDE.md - Análisis de datos
5. Personalizar configuración

### **Desarrollador:**
1. ARCHITECTURE.md - Estructura del proyecto
2. README.md sección "Arquitectura"
3. `ui/styles.py` → `make_window_header()` para añadir nuevas ventanas
4. Código fuente en `core/` y `ui/`
5. IDEAS_EXPANSION.md - Ver qué se puede añadir

---

## 🔍 Buscar por Tema

### **¿Cómo hacer X?**
- **Cambiar tema** → THEMES_GUIDE.md
- **Instalar** → QUICKSTART.md o INSTALL_GUIDE.md
- **Ver procesos** → PROCESS_MONITOR_GUIDE.md
- **Gestionar servicios** → SERVICE_MONITOR_GUIDE.md
- **Ver histórico** → HISTORICO_DATOS_GUIDE.md
- **Configurar ventiladores** → FAN_CONTROL_GUIDE.md
- **Integrar con OLED** → INTEGRATION_GUIDE.md
- **Añadir nueva ventana con header** → `ui/styles.py` → `make_window_header()`
- **Añadir funciones** → ARCHITECTURE.md + IDEAS_EXPANSION.md

### **¿Tengo un problema?**
- **No arranca** → QUICKSTART.md sección "Problemas Comunes"
- **Ventiladores no funcionan** → FAN_CONTROL_GUIDE.md
- **Temperatura no se lee** → INSTALL_GUIDE.md
- **Speedtest falla** → README.md sección "Instalación Manual" (CLI Ookla)
- **Base de datos crece** → HISTORICO_DATOS_GUIDE.md
- **Servicios no se gestionan** → SERVICE_MONITOR_GUIDE.md
- **Otro problema** → README.md sección "Troubleshooting"

---

## 📊 Estadísticas del Proyecto v2.7

- **Archivos Python**: 41
- **Líneas de código**: ~12,500
- **Ventanas**: 13 ventanas funcionales
- **Temas**: 15 temas pre-configurados
- **Documentos**: 12 guías
- **Servicios background**: 3 (FanAuto + DataCollection + Cleanup)

---

## 🆕 Novedades en v2.7

### **Funcionalidades Nuevas:**
- ✅ **Header unificado** `make_window_header()` en todas las ventanas
- ✅ **Status dinámico** en tiempo real integrado en el header
- ✅ **Botón ✕ táctil** (52×42px) optimizado para DSI sin teclado
- ✅ **Speedtest Ookla CLI** oficial (JSON, MB/s reales)

---

## 📧 Ayuda Adicional

**¿No encuentras lo que buscas?**

1. Busca en README.md (Ctrl+F)
2. Revisa los ejemplos en las guías
3. Abre un Issue en GitHub
4. Revisa el código fuente (está comentado)

---

## 🔗 Enlaces Rápidos

| Tema | Documento |
|------|-----------|
| **Inicio Rápido** | [QUICKSTART.md](QUICKSTART.md) |
| **Características** | [README.md#características](README.md#características-principales) |
| **Instalación** | [INSTALL_GUIDE.md](INSTALL_GUIDE.md) |
| **Temas** | [THEMES_GUIDE.md](THEMES_GUIDE.md) |
| **Procesos** | [PROCESS_MONITOR_GUIDE.md](PROCESS_MONITOR_GUIDE.md) |
| **Servicios** | [SERVICE_MONITOR_GUIDE.md](SERVICE_MONITOR_GUIDE.md) |
| **Histórico** | [HISTORICO_DATOS_GUIDE.md](HISTORICO_DATOS_GUIDE.md) |
| **Troubleshooting** | [README.md#troubleshooting](README.md#troubleshooting) |
| **Ideas Futuras** | [IDEAS_EXPANSION.md](IDEAS_EXPANSION.md) |

---

## 🎯 Guías de Implementación

Si quieres implementar funciones nuevas, tenemos guías paso a paso:

| Función | Guía | Dificultad |
|---------|------|------------|
| **Monitor de Procesos** | PROCESS_MONITOR_GUIDE.md | Media |
| **Monitor de Servicios** | SERVICE_MONITOR_GUIDE.md | Media |
| **Histórico de Datos** | HISTORICO_DATOS_GUIDE.md | Alta |
| **Nueva ventana con header** | `ui/styles.py` → `make_window_header()` | Baja |

---

## 📈 Evolución de la Documentación

| Versión | Documentos | Páginas | Características |
|---------|------------|---------|-----------------|
| **v1.0** | 8 | ~50 | Básico |
| **v2.0** | 10 | ~80 | + Procesos, Temas |
| **v2.5** | 12 | ~120 | + Servicios, Histórico |
| **v2.6** | 12 | ~130 | + Badges, CleanupService |
| **v2.7** | 12 | ~140 | + Header unificado, Speedtest Ookla ⭐ |

---

**¡Toda la información que necesitas está aquí!** 📚✨
