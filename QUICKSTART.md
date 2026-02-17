# 🚀 Inicio Rápido - Dashboard en 5 Minutos

Guía ultra-rápida para tener el dashboard funcionando.

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

### **1. Menú Principal**
Al abrir verás 9 botones:

```
┌───────────────────────────────┐
│  Control     │  Monitor       │
│  Ventiladores│  Placa         │
├──────────────┼────────────────┤
│  Monitor     │  Monitor       │
│  Red         │  USB           │
├──────────────┼────────────────┤
│  Monitor     │  Lanzadores    │
│  Disco       │                │
├──────────────┼────────────────┤
│  Monitor     │  Cambiar       │
│  Procesos    │  Tema          │
├──────────────┴────────────────┤
│         Salir                 │
└───────────────────────────────┘
```

### **2. Explorar Monitores**
- **Monitor Placa**: Ver CPU, RAM, temperatura
- **Monitor Red**: Ver tráfico de red en vivo
- **Monitor USB**: Ver dispositivos conectados
- **Monitor Disco**: Ver espacio y temperatura NVMe
- **Monitor Procesos**: Gestionar procesos del sistema ⭐

### **3. Configurar Ventiladores**
1. Clic en "Control Ventiladores"
2. Selecciona modo:
   - **Auto**: Basado en temperatura (recomendado)
   - **Manual**: Control directo con slider
   - **Silent/Normal/Performance**: Presets rápidos
3. Si eliges Auto, personaliza la curva (opcional)

### **4. Cambiar Tema** 🎨
1. Clic en "Cambiar Tema"
2. Elige entre 15 temas
3. Clic en "Aplicar y Reiniciar"
4. ✨ El dashboard se reinicia con el nuevo tema

---

## 🔧 Configuración Básica

### **Ajustar Posición en Pantalla DSI**
Edita `config/settings.py`:
```python
DSI_X = 0     # Mover horizontalmente
DSI_Y = 0     # Mover verticalmente
```

### **Cambiar Pin PWM de Ventiladores**
```python
PWM_PIN = 18  # Cambiar al pin que uses
```

### **Añadir Lanzadores Personalizados**
```python
LAUNCHERS = [
    {
        "label": "Apagar",
        "script": "/usr/bin/poweroff"
    },
    {
        "label": "Tu Script",
        "script": "/ruta/a/tu/script.sh"
    }
]
```

---

## ❓ Problemas Comunes

### **No arranca**
```bash
# Verificar Python
python3 --version  # Debe ser 3.8+

# Reinstalar dependencias
pip install -r requirements.txt
```

### **No detecta temperatura**
```bash
sudo sensors-detect --auto
sudo systemctl restart lm-sensors
sensors  # Verificar que funciona
```

### **Ventiladores no responden**
```bash
# Verificar GPIO
gpio readall

# Ejecutar con sudo (temporal)
sudo python3 main.py
```

### **Speedtest no funciona**
```bash
sudo apt install speedtest-cli
```

---

## 📚 Siguiente Paso

¿Quieres profundizar?  
Lee el **[README.md](README.md)** completo para características avanzadas.

### **Temas Recomendados:**
- **Cyberpunk**: Original cyan neón ⚡
- **Matrix**: Verde Matrix 💚
- **Dracula**: Colores pastel 🦇
- **Tokyo Night**: Noche de Tokio 🌃
- **Nord**: Minimalista nórdico ❄️

### **Ventanas Más Útiles:**
- **Monitor Procesos**: Encuentra qué consume CPU/RAM ⭐
- **Monitor Red**: Speedtest y tráfico en vivo
- **Control Ventiladores**: Mantén tu Pi fresco

---

## 🎯 Tips Rápidos

1. **Esc** cierra cualquier ventana
2. El **modo Auto** de ventiladores funciona incluso cerrando la ventana
3. Puedes **buscar procesos** por nombre o comando
4. Los **temas se guardan** automáticamente
5. El **speedtest tarda ~30 segundos**, ten paciencia

---

## 🚀 ¡Ya Estás Listo!

Explora las ventanas, personaliza los colores, ajusta los ventiladores.

**¿Necesitas ayuda?** → [README.md](README.md)  
**¿Quieres más funciones?** → Abre un Issue en GitHub

---

**¡Disfruta tu dashboard!** 🎉
