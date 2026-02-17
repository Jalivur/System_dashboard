# 🚀 Inicio Rápido - Dashboard v2.5

Guía ultra-rápida para tener el dashboard funcionando en 5 minutos.

---

## ⚡ Instalación Express (3 Comandos)

```bash
# 1. Clonar
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard

# 2. Instalar
chmod +x install.sh
./install.sh

# 3. Ejecutar
python3 main.py
```

**¡Listo!** El dashboard debería abrirse en tu pantalla DSI.

---

## 📋 Requisitos Mínimos

- ✅ Raspberry Pi 3/4/5
- ✅ Raspberry Pi OS (cualquier versión)
- ✅ Python 3.8+
- ✅ Conexión a internet (para instalación)

---

## 🎯 Primeros Pasos

### **Menú Principal (12 botones):**

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
│  Procesos       │  Servicios       │ ← NUEVO
├─────────────────┼──────────────────┤
│  Histórico      │  Cambiar         │
│  Datos          │  Tema            │ ← NUEVO
├─────────────────┼──────────────────┤
│  Reiniciar      │  Salir           │ ← NUEVO
└─────────────────┴──────────────────┘
```

### **Explora las Ventanas:**

#### **1. Monitor Placa** - Ver CPU, RAM, Temperatura
- CPU en tiempo real con gráfica
- RAM usada/total
- Temperatura del CPU

#### **2. Monitor Red** - Tráfico y Speedtest
- Download/Upload en vivo
- Speedtest de velocidad
- Lista de interfaces e IPs

#### **3. Monitor USB** - Dispositivos USB
- Ver dispositivos conectados
- Expulsar almacenamiento seguro

#### **4. Monitor Disco** - Espacio y temperatura
- Espacio usado/disponible
- Temperatura del NVMe
- Velocidad I/O

#### **5. Monitor Procesos** ⭐ - Gestión de procesos
- Ver procesos activos
- CPU y RAM por proceso
- Matar procesos

#### **6. Monitor Servicios** ⭐ NUEVO - Gestión systemd
- Start/Stop/Restart servicios
- Ver estado (active/inactive/failed)
- Habilitar/deshabilitar autostart
- Ver logs en tiempo real

#### **7. Histórico Datos** ⭐ NUEVO - Métricas históricas
- Gráficas de CPU, RAM, Temp
- Periodos: 24h, 7d, 30d
- Estadísticas y promedios
- Exportar a CSV

#### **8. Control Ventiladores** - Configurar PWM
- Modo Auto (curva de temperatura)
- Modo Manual (control directo)
- Presets: Silent/Normal/Performance

#### **9. Lanzadores** - Scripts personalizados
- Ejecutar scripts del sistema
- Apagar, reiniciar, etc.

#### **10. Cambiar Tema** 🎨 - 15 temas
- Cyberpunk, Matrix, Dracula, Nord...
- Reinicio automático

#### **11. Reiniciar** ⭐ NUEVO - Reinicio rápido
- Reinicia el dashboard
- Aplica cambios de código
- Con confirmación

---

## 🔧 Configuración Básica

### **Ajustar Posición en Pantalla DSI:**
Edita `config/settings.py`:
```python
DSI_X = 0     # Mover horizontalmente
DSI_Y = 0     # Mover verticalmente
```

### **Cambiar Pin PWM de Ventiladores:**
```python
PWM_PIN = 18  # Cambiar al pin que uses
```

### **Configurar Histórico de Datos:**
```python
DATA_COLLECTION_INTERVAL = 5  # Minutos entre recolecciones
DATA_RETENTION_DAYS = 90      # Días de retención
```

---

## ❓ Problemas Comunes

### **No arranca:**
```bash
python3 --version  # Debe ser 3.8+
pip install -r requirements.txt
```

### **No detecta temperatura:**
```bash
sudo sensors-detect --auto
sudo systemctl restart lm-sensors
sensors  # Verificar
```

### **Ventiladores no responden:**
```bash
gpio readall
sudo python3 main.py  # Temporal
```

### **Speedtest no funciona:**
```bash
sudo apt install speedtest-cli
```

### **Base de datos crece mucho:**
- Menú → "Histórico Datos" → "Limpiar Antiguos"
- Elimina datos >90 días

---

## 📚 Siguiente Paso

¿Quieres profundizar?  
Lee el **[README.md](README.md)** completo para características avanzadas.

---

## 🎯 Tips Rápidos

### **Gestión de Servicios:**
1. Abre "Monitor Servicios"
2. Busca servicio (ej: "nginx")
3. Start/Stop/Restart con un clic
4. Ver logs en tiempo real

### **Histórico de Datos:**
1. Abre "Histórico Datos"
2. Selecciona periodo (24h/7d/30d)
3. Ve gráficas de CPU, RAM, Temp
4. Exporta a CSV si necesitas

### **Cambio Rápido de Código:**
1. Edita archivo Python
2. Clic en "Reiniciar"
3. Confirma
4. ¡Dashboard se reinicia con cambios!

### **Temas Recomendados:**
- **Cyberpunk**: Original cyan neón ⚡
- **Matrix**: Verde Matrix 💚
- **Dracula**: Colores pastel 🦇
- **Tokyo Night**: Noche de Tokio 🌃
- **Nord**: Minimalista nórdico ❄️

### **Ventanas Más Útiles:**
- **Monitor Procesos**: Encuentra qué consume CPU/RAM
- **Monitor Servicios**: Gestiona systemd sin terminal ⭐
- **Histórico Datos**: Analiza tendencias ⭐
- **Control Ventiladores**: Mantén tu Pi fresco

---

## 🆕 Novedades v2.5

✅ **Monitor de Servicios** - Control completo de systemd  
✅ **Histórico de Datos** - SQLite + gráficas matplotlib  
✅ **Botón Reiniciar** - Reinicio rápido con un clic  
✅ **Recolección automática** - Background cada 5 min  
✅ **Exportación CSV** - Descarga datos históricos  

---

## 🚀 ¡Ya Estás Listo!

Explora las 11 ventanas, personaliza los colores, ajusta los ventiladores, analiza el histórico.

**¿Necesitas ayuda?** → [README.md](README.md)  
**¿Quieres más funciones?** → Abre un Issue en GitHub

---

**Dashboard v2.5: Profesional, Completo, Potente** 🎉✨
