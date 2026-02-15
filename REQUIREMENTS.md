# 📦 Guía Rápida: requirements.txt

## 🎯 ¿Qué es?

Un archivo que lista todas las **dependencias Python** de tu proyecto para instalarlas automáticamente.

---

## 📝 Contenido del archivo

```txt
# Dependencias Python
customtkinter>=5.2.0
psutil>=5.9.0
```

**Significado:**
- `customtkinter>=5.2.0` → Interfaz gráfica (versión 5.2.0 o superior)
- `psutil>=5.9.0` → Monitor de sistema (versión 5.9.0 o superior)

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

Las dependencias del **sistema** (como `lm-sensors`) se instalan con:

```bash
# Ubuntu/Debian/Raspberry Pi
sudo apt-get install lm-sensors usbutils udisks2

# Fedora/RHEL
sudo dnf install lm-sensors usbutils udisks2
```

---

## 🎯 Resumen

**¿Qué es?** → Lista de dependencias Python  
**¿Para qué?** → Instalar todo automáticamente  
**¿Cómo usar?** → `pip3 install -r requirements.txt`  
**¿Dónde?** → Raíz del proyecto  

---

**Tip:** En sistemas modernos (Ubuntu 23.04+), usa `--break-system-packages` para evitar errores de PEP 668.
