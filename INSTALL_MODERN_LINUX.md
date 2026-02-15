# 🔧 Instalación en Sistemas Modernos (Ubuntu 23.04+, Debian 12+)

Si al usar `pip install` te sale un error como:
```
error: externally-managed-environment
```

**¡No te preocupes!** Es normal en sistemas modernos. Aquí están todas las soluciones:

---

## 🎯 Solución Rápida (Recomendada)

### Opción 1: Usar el Script Actualizado ⭐

```bash
cd system_dashboard
sudo ./install_system.sh
```

El script ahora usa automáticamente `--break-system-packages` que es lo que necesitas.

---

## 🛠️ Soluciones Manuales

### Opción 2: Instalar con --break-system-packages

```bash
# Con sudo (para todo el sistema)
sudo pip3 install --break-system-packages customtkinter psutil

# O sin sudo (solo para tu usuario)
pip3 install --user --break-system-packages customtkinter psutil
```

**¿Es seguro `--break-system-packages`?**
✅ Sí, solo omite la protección de PEP 668
✅ No rompe nada realmente
✅ Es el método recomendado por Python para este caso

---

### Opción 3: Usar pipx (Alternativa Moderna)

```bash
# 1. Instalar pipx
sudo apt-get install pipx
pipx ensurepath

# 2. Instalar las librerías
pipx install customtkinter
pipx install psutil

# 3. Ejecutar el dashboard
pipx run python3 main.py
```

**Ventajas de pipx:**
- ✅ Cada aplicación en su propio entorno aislado
- ✅ No conflictos con el sistema
- ✅ Recomendado por Ubuntu/Debian

---

### Opción 4: Paquetes del Sistema (Si Existen)

```bash
# Buscar si existen en los repos
apt search python3-customtkinter
apt search python3-psutil

# Si existen, instalar
sudo apt-get install python3-psutil
# (customtkinter probablemente no esté en repos)
```

**Nota:** `python3-psutil` SÍ suele estar, pero `customtkinter` NO.

---

### Opción 5: Usar requirements.txt con --break-system-packages

```bash
cd system_dashboard

# Crear requirements.txt si no existe
cat > requirements.txt << EOF
customtkinter>=5.2.0
psutil>=5.9.0
EOF

# Instalar
sudo pip3 install --break-system-packages -r requirements.txt
```

---

## 📊 Comparación de Métodos

| Método | Ventajas | Desventajas |
|--------|----------|-------------|
| `--break-system-packages` | ✅ Simple, rápido | ⚠️ Nombre suena peligroso |
| `pipx` | ✅ Aislado, limpio | ❌ Más complejo |
| Paquetes apt | ✅ Integrado | ❌ customtkinter no disponible |
| venv | ✅ Estándar | ❌ Tienes que activarlo |

---

## 🎯 Mi Recomendación para Tu Caso

Ya que dijiste que **NO quieres venv**, usa:

```bash
# Método 1: Con sudo (global)
sudo pip3 install --break-system-packages customtkinter psutil

# Método 2: Sin sudo (solo tu usuario)
pip3 install --user --break-system-packages customtkinter psutil
```

Luego ejecuta:
```bash
python3 main.py
```

**¡Y listo!** 🎉

---

## 🐛 Si Aún Así Falla

### Error: "pip3: command not found"
```bash
sudo apt-get install python3-pip
```

### Error: Permisos denegados
```bash
# Añade tu usuario al grupo necesario
sudo usermod -aG sudo $USER
# Reinicia sesión
```

### Error: "No module named 'tkinter'"
```bash
sudo apt-get install python3-tk
```

### Error al importar customtkinter
```bash
# Verificar instalación
pip3 list | grep customtkinter

# Si no aparece, reinstalar
pip3 install --user --break-system-packages --force-reinstall customtkinter
```

---

## 🔍 Verificar que Funcionó

```bash
# Probar customtkinter
python3 -c "import customtkinter; print('✅ CustomTkinter OK')"

# Probar psutil
python3 -c "import psutil; print('✅ psutil OK')"

# Si ambos muestran OK, ¡estás listo!
```

---

## 💡 Explicación: ¿Por Qué Pasa Esto?

**PEP 668** (Python Enhancement Proposal 668):
- Implementado en Ubuntu 23.04+, Debian 12+
- Protege el Python del sistema
- Evita que `pip install` rompa paquetes de apt
- Obliga a usar entornos virtuales O --break-system-packages

**En resumen:**
- Python dice: "No instales cosas con pip globalmente"
- Tú dices: "Pero yo sé lo que hago"
- Python dice: "Ok, pero usa --break-system-packages"

---

## 🚀 Comando Todo-en-Uno

Si quieres hacer TODO de golpe:

```bash
cd system_dashboard

# Instalar TODO con un comando
sudo apt-get update && \
sudo apt-get install -y python3-pip python3-tk lm-sensors && \
sudo pip3 install --break-system-packages customtkinter psutil && \
sudo sensors-detect --auto && \
echo "✅ ¡Instalación completa!"

# Ejecutar
python3 main.py
```

---

## 📝 Notas Importantes

1. **`--break-system-packages` NO rompe nada**
   - Es solo un nombre intimidante
   - Solo desactiva la protección PEP 668
   - Es seguro para aplicaciones independientes

2. **Si usas `--user`** (sin sudo)
   - Se instala en `~/.local/lib/python3.x/`
   - Solo tu usuario puede usar las librerías
   - NO necesita permisos de administrador

3. **Si usas `sudo`** (global)
   - Se instala en `/usr/local/lib/python3.x/`
   - Todos los usuarios pueden usar las librerías
   - Necesita permisos de administrador

---

## ✅ Resumen

**Tu caso específico:**
```bash
# Copiar y pegar esto:
sudo pip3 install --break-system-packages customtkinter psutil
```

**¿Funciona?**
```bash
python3 main.py
```

**¡Listo! 🎉**

---

¿Necesitas ayuda con algún error específico que te salga? Compártelo y te ayudo a resolverlo. 😊
