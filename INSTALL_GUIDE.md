# 🔧 Guía de Instalación Completa

Guía detallada para instalar el Dashboard en cualquier sistema Linux.

---

## 🎯 Sistemas Soportados

### ✅ **Soporte Completo (100%)**
- Raspberry Pi OS (Bullseye, Bookworm)
- Kali Linux (en Raspberry Pi)

### ✅ **Soporte Parcial (~85%)**
- Ubuntu (20.04, 22.04, 23.04+, 24.04)
- Debian (11, 12+)
- Linux Mint
- Fedora / CentOS / RHEL
- Arch Linux / Manjaro

**Nota**: En sistemas no-Raspberry Pi, el control de ventiladores PWM puede no funcionar. Todo lo demás funciona perfectamente.

---

## ⚡ Método 1: Instalación Automática (Recomendado)

### **Script de Instalación**

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard

# 2. Dar permisos y ejecutar
chmod +x install.sh
./install.sh

# 3. Ejecutar
python3 main.py
```

**El script instalará automáticamente:**
- ✅ Dependencias del sistema (python3-pip, python3-tk, lm-sensors)
- ✅ Dependencias Python (customtkinter, psutil, Pillow)
- ✅ Speedtest-cli (opcional)
- ✅ Configurará sensores

---

## 🛠️ Método 2: Instalación Manual con Entorno Virtual

### **Paso 1: Instalar Dependencias del Sistema**

```bash
# Actualizar repositorios
sudo apt update

# Instalar herramientas básicas
sudo apt install -y python3 python3-pip python3-venv python3-tk git

# Instalar lm-sensors para temperatura
sudo apt install -y lm-sensors

# Opcional: Speedtest
sudo apt install -y speedtest-cli

# Detectar sensores (primera vez)
sudo sensors-detect --auto
```

### **Paso 2: Clonar Repositorio**

```bash
cd ~
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard
```

### **Paso 3: Crear Entorno Virtual**

```bash
# Crear venv
python3 -m venv venv

# Activar venv
source venv/bin/activate

# Tu prompt debería cambiar a: (venv) user@host:~$
```

### **Paso 4: Instalar Dependencias Python**

```bash
# Dentro del venv
pip install --upgrade pip
pip install -r requirements.txt
```

### **Paso 5: Ejecutar**

```bash
# Asegurarte que el venv está activo
source venv/bin/activate

# Ejecutar
python3 main.py
```

### **Paso 6: Crear Launcher (Opcional)**

```bash
# Para ejecutar sin activar venv manualmente
chmod +x create_desktop_launcher.sh
./create_desktop_launcher.sh
```

---

## 🚀 Método 3: Instalación Sin Entorno Virtual

**⚠️ Advertencia**: En Ubuntu 23.04+ y Debian 12+ necesitarás usar `--break-system-packages` o el script automático.

### **Opción A: Usar Script Automático** ⭐

```bash
cd system-dashboard
sudo ./install_system.sh
```

### **Opción B: Manual**

```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install -y python3 python3-pip python3-tk lm-sensors speedtest-cli

# Instalar dependencias Python (método según tu sistema)
```

#### **En sistemas antiguos (Ubuntu 22.04, Debian 11):**
```bash
pip install -r requirements.txt
```

#### **En sistemas modernos (Ubuntu 23.04+, Debian 12+):**
```bash
pip install -r requirements.txt --break-system-packages
```

**O usar pipx:**
```bash
sudo apt install pipx
pipx install customtkinter
pipx install psutil
pipx install Pillow
```

### **Ejecutar**

```bash
python3 main.py
```

---

## 🐛 Solución de Problemas

### **Error: externally-managed-environment**

**Síntoma:**
```
error: externally-managed-environment
```

**Causa**: Sistema moderno (Ubuntu 23.04+, Debian 12+) que protege paquetes del sistema.

**Soluciones:**

1. **Opción 1: Usar venv** (Recomendado)
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Opción 2: Usar --break-system-packages**
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```

3. **Opción 3: Usar pipx**
   ```bash
   sudo apt install pipx
   pipx install customtkinter psutil Pillow
   ```

---

### **Error: ModuleNotFoundError: No module named 'customtkinter'**

**Causa**: Dependencias no instaladas.

**Solución:**
```bash
# Si usas venv
source venv/bin/activate
pip install customtkinter

# Si no usas venv
pip install customtkinter --break-system-packages
```

---

### **Error: No se detecta temperatura**

**Síntoma:**
```
Temp: N/A
```

**Solución:**
```bash
# Detectar sensores
sudo sensors-detect --auto

# Reiniciar servicio
sudo systemctl restart lm-sensors

# Verificar que funciona
sensors
# Debería mostrar: coretemp-isa-0000, etc.
```

**Si aún no funciona:**
```bash
# Cargar módulos manualmente
sudo modprobe coretemp
```

---

### **Error: Ventiladores no responden**

**Causa**: Pin GPIO incorrecto o sin permisos.

**Solución:**

1. **Verificar pin:**
   ```bash
   gpio readall
   # Verificar que PWM_PIN=18 corresponde a un pin PWM
   ```

2. **Probar con sudo** (temporal):
   ```bash
   sudo python3 main.py
   ```

3. **Añadir usuario a grupo gpio** (permanente):
   ```bash
   sudo usermod -a -G gpio $USER
   # Cerrar sesión y volver a entrar
   ```

---

### **Error: ImportError: libGL.so.1**

**Causa**: Falta librería OpenGL.

**Solución:**
```bash
sudo apt install -y libgl1-mesa-glx
```

---

### **Error: Speedtest no funciona**

**Causa**: speedtest-cli no instalado.

**Solución:**
```bash
sudo apt install speedtest-cli

# Verificar
speedtest-cli --version
```

---

### **Error: No se ve la ventana**

**Causa**: Posición incorrecta.

**Solución**: Editar `config/settings.py`:
```python
DSI_X = 0  # Cambiar según tu pantalla
DSI_Y = 0
DSI_WIDTH = 800   # Ajustar a tu resolución
DSI_HEIGHT = 480
```

---

## 📦 Dependencias Completas

### **Dependencias del Sistema:**
```bash
python3          # >= 3.8
python3-pip      # Gestor de paquetes
python3-venv     # Entornos virtuales (opcional)
python3-tk       # Tkinter
lm-sensors       # Lectura de sensores
speedtest-cli    # Tests de velocidad (opcional)
git              # Control de versiones
```

### **Dependencias Python:**
```
customtkinter==5.2.0    # UI moderna
psutil==5.9.5           # Info del sistema
Pillow==10.0.0          # Procesamiento de imágenes
```

---

## 🔐 Permisos

### **GPIO (para ventiladores):**

```bash
# Añadir usuario a grupos necesarios
sudo usermod -a -G gpio,i2c,spi $USER

# Cerrar sesión y volver a entrar
```

### **Ejecutar sin sudo:**

El dashboard debería funcionar sin sudo, excepto:
- Control de ventiladores (requiere acceso GPIO)
- Algunos scripts en Lanzadores

---

## 🚀 Autoarranque (Opcional)

### **Método 1: systemd**

```bash
# Crear servicio
sudo nano /etc/systemd/system/dashboard.service
```

Contenido:
```ini
[Unit]
Description=System Dashboard
After=graphical.target

[Service]
Type=simple
User=tu-usuario
WorkingDirectory=/home/tu-usuario/system-dashboard
ExecStart=/home/tu-usuario/system-dashboard/venv/bin/python3 main.py
Restart=on-failure

[Install]
WantedBy=graphical.target
```

Activar:
```bash
sudo systemctl enable dashboard.service
sudo systemctl start dashboard.service
```

---

### **Método 2: autostart**

```bash
# Crear archivo autostart
mkdir -p ~/.config/autostart
nano ~/.config/autostart/dashboard.desktop
```

Contenido:
```ini
[Desktop Entry]
Type=Application
Name=System Dashboard
Exec=/home/tu-usuario/system-dashboard/venv/bin/python3 /home/tu-usuario/system-dashboard/main.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
```

---

## 🧪 Verificación de Instalación

### **Test completo:**

```bash
# 1. Verificar Python
python3 --version  # Debe ser >= 3.8

# 2. Verificar módulos
python3 -c "import customtkinter; print('CustomTkinter OK')"
python3 -c "import psutil; print('psutil OK')"
python3 -c "import PIL; print('Pillow OK')"

# 3. Verificar sensores
sensors  # Debe mostrar temperaturas

# 4. Verificar speedtest
speedtest-cli --version

# 5. Ejecutar dashboard
python3 main.py
```

---

## 💡 Tips de Instalación

1. **Usa el script automático** si es tu primera vez
2. **Usa venv** si quieres mantener el sistema limpio
3. **No uses sudo** para instalar paquetes Python (usa venv)
4. **Detecta sensores** la primera vez con `sudo sensors-detect`
5. **Revisa los logs** si algo falla: `journalctl -xe`

---

## 📊 Tiempos de Instalación

| Método | Tiempo | Dificultad |
|--------|--------|------------|
| Script automático | ~5 min | ⭐ Fácil |
| Manual con venv | ~10 min | ⭐⭐ Media |
| Manual sin venv | ~8 min | ⭐⭐ Media |

---

## 🆘 Ayuda Adicional

**¿Problemas con la instalación?**

1. Revisa esta guía completa
2. Verifica [QUICKSTART.md](QUICKSTART.md) para problemas comunes
3. Revisa [README.md](README.md) sección Troubleshooting
4. Abre un Issue en GitHub con:
   - Sistema operativo y versión
   - Versión de Python
   - Mensaje de error completo
   - Comando que ejecutaste

---

**¡Instalación completa!** 🎉
