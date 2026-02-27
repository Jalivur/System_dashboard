# 📦 Guía Rápida: requirements.txt

## 🎯 ¿Qué es?

Un archivo que lista todas las **dependencias Python** de tu proyecto para instalarlas automáticamente.

---

## 📝 Contenido del archivo

```txt
# Dependencias Python
customtkinter>=5.2.0
psutil>=5.9.0
matplotlib>=3.5.0
python-dotenv>=1.0.0
```

**Significado:**
- `customtkinter>=5.2.0` → Interfaz gráfica (versión 5.2.0 o superior)
- `psutil>=5.9.0` → Monitor de sistema (versión 5.9.0 o superior)
- `matplotlib>=3.5.0` → Gráficas históricas (versión 3.5.0 o superior)
- `python-dotenv>=1.0.0` → Variables de entorno desde `.env` (Homebridge, Telegram, Pi-hole)

---

## 🚀 Cómo usar

### Instalar dependencias:

```bash
# En sistemas modernos (Ubuntu 23.04+, Debian 12+)
pip3 install --break-system-packages -r requirements.txt

# En sistemas antiguos
pip3 install -r requirements.txt

# O con sudo (global)
sudo pip3 install -r requirements.txt
```

---

## 🔧 Operadores de versión

| Operador | Significado | Ejemplo |
|----------|-------------|---------|
| `>=` | Versión mínima | `psutil>=5.9.0` |
| `==` | Versión exacta | `psutil==5.9.5` |
| `<=` | Versión máxima | `psutil<=6.0.0` |
| `~=` | Compatible | `psutil~=5.9.0` (5.9.x) |

---

## ✅ Buenas prácticas

### ✅ Hacer:
- Usar versiones mínimas (`>=`) en lugar de exactas
- Comentar dependencias opcionales
- Mantener el archivo actualizado

### ❌ Evitar:
- No especificar versiones (puede romper)
- Versiones exactas innecesarias (muy restrictivo)
- Incluir TODO con `pip freeze` (archivo enorme)

---

## 🧪 Verificar instalación

```bash
# Ver qué tienes instalado
pip3 list

# Ver versión específica
pip3 show customtkinter

# Comprobar problemas
pip3 check
```

---

## 📊 Dependencias del Sistema

**NOTA:** requirements.txt solo lista dependencias **Python**. 

Las dependencias del **sistema** (como `lm-sensors` o `arp-scan`) se instalan con:

```bash
# Ubuntu/Debian/Raspberry Pi
sudo apt-get install lm-sensors usbutils udisks2 smartmontools arp-scan

# Fedora/RHEL
sudo dnf install lm-sensors usbutils udisks2 arp-scan
```

### Dependencias del sistema requeridas en v3.2:

| Paquete | Uso | Obligatorio |
|---------|-----|-------------|
| `lm-sensors` | Temperatura CPU | ✅ Sí |
| `usbutils` | Listar dispositivos USB | ✅ Sí |
| `udisks2` | Expulsión segura USB | ✅ Sí |
| `smartmontools` | Temperatura NVMe | ✅ Sí |
| `arp-scan` | Escáner de red local (v3.2) | ✅ Sí |
| `speedtest` (Ookla CLI) | Speedtest integrado | ⚙️ Opcional |

### Sudoers para arp-scan:

`arp-scan` necesita privilegios de root. Configura sudoers para ejecutarlo sin contraseña:

```bash
echo "usuario ALL=(ALL) NOPASSWD: /usr/sbin/arp-scan" | sudo tee /etc/sudoers.d/arp-scan
```

Sustituye `usuario` por tu usuario del sistema (normalmente `pi` en Raspberry Pi OS).

---

## 🎯 Resumen

**¿Qué es?** → Lista de dependencias Python  
**¿Para qué?** → Instalar todo automáticamente  
**¿Cómo usar?** → `pip3 install --break-system-packages -r requirements.txt`  
**¿Dónde?** → Raíz del proyecto  

---

**Tip:** En sistemas modernos (Ubuntu 23.04+), usa `--break-system-packages` para evitar errores de PEP 668.
