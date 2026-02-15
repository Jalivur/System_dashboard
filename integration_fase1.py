import time
import psutil
import subprocess
from PIL import Image, ImageDraw, ImageFont
import os
import sys
sys.path.append("/home/jalivur/Documents/proyectopantallas")
from Code.expansion import Expansion
from Code.oled import OLED
import json
import os
import signal

# ========================================
# CONFIGURACIÓN INTEGRADA CON EL DASHBOARD
# ========================================

# Ruta al archivo de estado del dashboard
# Cambia esto a donde extraigas el proyecto system_dashboard
STATE_FILE = "/ruta/a/system_dashboard/data/fan_state.json"

# Ejemplo si lo pones en tu home:
# STATE_FILE = "/home/jalivur/system_dashboard/data/fan_state.json"

# Ejemplo si lo pones en Documents:
# STATE_FILE = "/home/jalivur/Documents/system_dashboard/data/fan_state.json"


# ========================================
# FUNCIONES
# ========================================

def read_fan_state():
    """Lee el estado de los ventiladores guardado por el dashboard"""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return None


stop_flag = False

def handle_exit(signum, frame):
    """Maneja la señal de salida limpia"""
    global stop_flag
    print(f"Señal {signum} recibida, saliendo...")
    stop_flag = True

# Capturar SIGTERM (pkill normal) y SIGINT (Ctrl+C)
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)


def get_cpu_temp():
    """Obtiene temperatura de la CPU"""
    temp = subprocess.check_output(
        ["vcgencmd", "measure_temp"]
    ).decode()
    return float(temp.replace("temp=", "").replace("'C\n", ""))


def fan_curve(temp):
    """Curva de ventilador por defecto (fallback)"""
    if temp < 40:
        return 40
    elif temp > 75:
        return 255
    else:
        return int((temp - 40) * (215 / 35) + 40)


def temp_to_color(temp):
    """Convierte temperatura a color RGB para LEDs"""
    if temp < 40:
        return (0, 255, 0)  # Verde
    elif temp > 75:
        return (255, 0, 0)  # Rojo
    else:
        ratio = (temp - 40) / 35
        r = int(255 * ratio)
        g = int(255 * (1 - ratio))
        return (r, g, 0)  # Degradado verde->amarillo->rojo


def smooth(prev, target, step=10):
    """Suaviza transición de colores"""
    return tuple(
        prev[i] + max(-step, min(step, target[i] - prev[i]))
        for i in range(3)
    )


def get_ip():
    """Obtiene IP principal"""
    for _ in range(10):  # hasta 10 intentos
        ip_output = subprocess.getoutput("hostname -I").split()
        if ip_output:
            return ip_output[0]
        time.sleep(1)
    return "No IP"


def get_ip_of_interface(iface_name="tun0"):
    """Obtiene IP de una interfaz específica (ej: VPN)"""
    addrs = psutil.net_if_addrs()
    if iface_name in addrs:
        for addr in addrs[iface_name]:
            if addr.family.name == "AF_INET":  # IPv4
                return addr.address
    return "No IP"


# ========================================
# INICIALIZACIÓN
# ========================================

board = Expansion()
oled = OLED()
oled.clear()
font = ImageFont.load_default()

# Estado anterior para optimizar actualizaciones OLED
last_state = {
    "cpu": None,
    "ram": None,
    "temp": None,
    "ip": None,
    "tun_ip": None,
    "fan0_duty": None,
    "fan1_duty": None
}


def draw_oled_smart(cpu, ram, temp, ip, tun_ip, fan0_duty, fan1_duty):
    """
    Dibuja en OLED solo si hay cambios
    Optimiza para reducir parpadeos
    """
    changed = (
        round(cpu, 1) != last_state["cpu"] or
        round(ram, 1) != last_state["ram"] or
        int(temp) != last_state["temp"] or
        ip != last_state["ip"] or
        tun_ip != last_state["tun_ip"] or
        fan0_duty != last_state["fan0_duty"] or
        fan1_duty != last_state["fan1_duty"]
    )

    if not changed:
        return

    oled.clear()
    oled.draw_text(f"CPU: {cpu:>5.1f} %", (0, 0))
    oled.draw_text(f"RAM: {ram:>5.1f} %", (0, 12))
    oled.draw_text(f"TEMP:{temp:>5.1f} C", (0, 24))
    oled.draw_text(f"IP: {ip}", (0, 36))
    
    # Mostrar IP VPN o estado ventiladores
    if tun_ip != "No IP":
        oled.draw_text(f"VPN: {tun_ip}", (0, 48))
    else:
        oled.draw_text(f"Fan1:{fan0_duty}% Fan2:{fan1_duty}%", (0, 48))
    
    oled.show()

    # Guardar estado
    last_state["cpu"] = round(cpu, 1)
    last_state["ram"] = round(ram, 1)
    last_state["temp"] = int(temp)
    last_state["ip"] = ip
    last_state["tun_ip"] = tun_ip
    last_state["fan0_duty"] = fan0_duty
    last_state["fan1_duty"] = fan1_duty


# ========================================
# BUCLE PRINCIPAL
# ========================================

try:
    print("Iniciando monitor OLED + Control de ventiladores...")
    print(f"Leyendo estado desde: {STATE_FILE}")
    
    board.set_fan_mode(1)  # Manual
    board.set_led_mode(1)  # RGB fijo
    
    current_color = (0, 255, 0)
    last_pwm = None
    last_ip = None
    last_ip_time = 0
    last_state_file = None
    last_state_time = 0
    last_temp = None
    last_temp_time = 0
    
    while not stop_flag:
        # CPU y RAM
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        # Temperatura (cada 1 segundo)
        now = time.time()
        if now - last_temp_time > 1:
            last_temp = get_cpu_temp()
            last_temp_time = now
        temp = last_temp
        
        # IP (cada 20 segundos)
        now = time.time()
        if now - last_ip_time > 20:
            last_ip = get_ip()
            last_tun_ip = get_ip_of_interface("tun0")
            last_ip_time = now
        ip = last_ip
        tun_ip = last_tun_ip

        # ========================================
        # LEER ESTADO DEL DASHBOARD (cada 1 segundo)
        # ========================================
        now = time.time()
        if now - last_state_time > 1:
            state = read_fan_state()
            last_state_file = state
            last_state_time = now
            
            # Debug: mostrar estado leído
            if state:
                print(f"Estado leído: modo={state.get('mode')}, PWM={state.get('target_pwm')}")
        else:
            state = last_state_file

        # Determinar PWM según estado del dashboard
        fan_pwm = None

        if state:
            mode = state.get("mode")
            
            # El dashboard ya calcula el PWM para todos los modos
            # Solo necesitamos leer target_pwm
            fan_pwm = state.get("target_pwm")
            
            if fan_pwm is not None:
                print(f"Usando PWM del dashboard: {fan_pwm} (modo: {mode})")

        # Fallback de seguridad (si no hay estado o archivo)
        if fan_pwm is None:
            fan_pwm = fan_curve(temp)
            print(f"Usando curva local (fallback): PWM={fan_pwm}")

        # Aplicar PWM solo si cambia
        if fan_pwm != last_pwm:
            board.set_fan_duty(fan_pwm, fan_pwm)
            last_pwm = fan_pwm

        # Calcular porcentaje para OLED
        fan_percent = int(fan_pwm * 100 / 255) if fan_pwm else 0
        fan0_duty = fan_percent
        fan1_duty = fan_percent

        # Actualizar color de LEDs según temperatura
        target_color = temp_to_color(temp)
        current_color = smooth(current_color, target_color)
        board.set_all_led_color(*current_color)

        # Actualizar OLED
        draw_oled_smart(cpu, ram, temp, ip, tun_ip, fan0_duty, fan1_duty)

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Salida limpia (Ctrl+C)")
except Exception as e:
    print(f"Error inesperado: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("Limpiando...")
    oled.clear()
    board.set_all_led_color(0, 0, 0)
    board.set_fan_duty(0, 0)
    print("Apagado completo.")
