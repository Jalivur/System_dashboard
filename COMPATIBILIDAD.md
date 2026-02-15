# 🌐 Compatibilidad Multiplataforma - Resumen

## 🎯 ¿En qué sistemas funciona?

### ✅ Funciona al 100% (TODO)
- **Raspberry Pi OS** (Raspbian)
- **Kali Linux** (en Raspberry Pi)

### ✅ Funciona al ~85% (sin control de ventiladores)
- **Ubuntu** (20.04, 22.04, 23.04+)
- **Debian** (11, 12+)
- **Linux Mint**
- **Fedora, CentOS, RHEL**
- **Arch Linux, Manjaro**

---

## 📊 Tabla de Compatibilidad

| Componente | Raspberry Pi | Otros Linux | Notas |
|------------|--------------|-------------|-------|
| **Interfaz gráfica** | ✅ | ✅ | 100% compatible |
| **Monitor sistema** | ✅ | ✅ | CPU, RAM, Temp, Disco |
| **Monitor red** | ✅ | ✅ | Download, Upload, Speedtest |
| **Monitor USB** | ✅ | ✅ | Con dependencias |
| **Lanzadores** | ✅ | ✅ | Scripts bash |
| **Temas** | ✅ | ✅ | 15 temas |
| **Control ventiladores** | ✅ | ❌ | Solo con GPIO |

---

## 🔧 Dependencias por Sistema

### Ubuntu/Debian/Raspberry Pi:
```bash
sudo apt-get install lm-sensors usbutils udisks2
pip3 install --break-system-packages customtkinter psutil
```

### Fedora/RHEL:
```bash
sudo dnf install lm-sensors usbutils udisks2
pip3 install customtkinter psutil
```

### Arch Linux:
```bash
sudo pacman -S lm-sensors usbutils udisks2
pip3 install customtkinter psutil
```

---

## ⚠️ Limitación: Control de Ventiladores

El control de ventiladores PWM **SOLO funciona en Raspberry Pi** porque requiere:
- GPIO pins
- Hardware específico
- Librería de control GPIO

**En otros sistemas Linux:** El botón de ventiladores no funcionará, pero el resto del dashboard (85%) funciona perfectamente.

---

## 💡 Uso Recomendado

- **Raspberry Pi:** Usa TODO al 100%
- **Ubuntu/Debian Desktop:** Monitor de sistema completo (sin ventiladores)
- **Servidores:** Requiere X11 para la interfaz gráfica
- **Kali Linux (RPi):** Funciona al 100% igual que Raspbian

---

## 🚀 Verificación Rápida

```bash
# Verificar Python
python3 --version  # Debe ser 3.8+

# Verificar temperatura
sensors  # o vcgencmd measure_temp

# Verificar USB
lsusb
lsblk
```

---

**Conclusión:** El dashboard funciona en cualquier Linux con interfaz gráfica. Solo el control de ventiladores es específico de Raspberry Pi con GPIO.
