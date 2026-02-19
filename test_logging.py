#!/usr/bin/env python3
"""
Script de prueba manual del sistema de logging
Ejecutar desde la raíz del proyecto: python3 test_logging.py
Ver logs en tiempo real con: tail -f data/logs/dashboard.log
"""
import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import get_logger

logger = get_logger("test")

def separador(titulo):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")

def ok(msg):
    print(f"  ✅ {msg}")

def info(msg):
    print(f"  ℹ️  {msg}")


# ============================================================
# TEST FILE_MANAGER
# ============================================================
def test_file_manager():
    separador("FILE MANAGER")
    from config.settings import STATE_FILE, CURVE_FILE
    from utils.file_manager import FileManager

    # --- Test 1: load_state cuando no existe el archivo ---
    print("\n[1] load_state con archivo inexistente:")
    backup = None
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            backup = f.read()
        os.remove(STATE_FILE)

    state = FileManager.load_state()
    ok(f"Retornó estado por defecto: {state}")
    info("Debe aparecer en log: [DEBUG] load_state: no existe, usando estado por defecto")

    # Restaurar
    if backup:
        with open(STATE_FILE, "w") as f:
            f.write(backup)

    # --- Test 2: load_state con JSON corrupto ---
    print("\n[2] load_state con JSON corrupto:")
    with open(STATE_FILE, "w") as f:
        f.write("{ esto no es json válido !!!}")

    state = FileManager.load_state()
    ok(f"Retornó estado por defecto: {state}")
    info("Debe aparecer en log: [ERROR] load_state: JSON corrupto")

    # Restaurar estado válido
    FileManager.write_state({"mode": "auto", "target_pwm": None})
    ok("Estado restaurado correctamente")

    # --- Test 3: load_curve con archivo inexistente ---
    print("\n[3] load_curve con archivo inexistente:")
    curve_backup = None
    if os.path.exists(CURVE_FILE):
        with open(CURVE_FILE) as f:
            curve_backup = f.read()
        os.remove(CURVE_FILE)

    curve = FileManager.load_curve()
    ok(f"Retornó curva por defecto con {len(curve)} puntos")
    info("Debe aparecer en log: [DEBUG] load_curve: no existe, usando curva por defecto")

    if curve_backup:
        with open(CURVE_FILE, "w") as f:
            f.write(curve_backup)

    # --- Test 4: load_curve con JSON corrupto ---
    print("\n[4] load_curve con JSON corrupto:")
    with open(CURVE_FILE, "w") as f:
        f.write("{ corrupto }")

    curve = FileManager.load_curve()
    ok(f"Retornó curva por defecto con {len(curve)} puntos")
    info("Debe aparecer en log: [ERROR] load_curve: JSON corrupto")

    # Restaurar curva válida
    if curve_backup:
        with open(CURVE_FILE, "w") as f:
            f.write(curve_backup)
    else:
        FileManager.save_curve([{"temp": 50, "pwm": 128}])

    ok("Curva restaurada correctamente")

    # --- Test 5: write_state correcto ---
    print("\n[5] write_state normal:")
    FileManager.write_state({"mode": "auto", "target_pwm": 128})
    ok("Estado guardado sin errores")

    # --- Test 6: save_curve correcta ---
    print("\n[6] save_curve normal:")
    FileManager.save_curve([{"temp": 50, "pwm": 100}, {"temp": 70, "pwm": 200}])
    ok("Curva guardada sin errores")
    info("Debe aparecer en log: [INFO] save_curve: curva guardada (2 puntos)")


# ============================================================
# TEST SYSTEM_UTILS
# ============================================================
def test_system_utils():
    separador("SYSTEM UTILS")
    from utils.system_utils import SystemUtils

    # --- Test 1: get_cpu_temp ---
    print("\n[1] get_cpu_temp:")
    temp = SystemUtils.get_cpu_temp()
    ok(f"Temperatura obtenida: {temp}°C")
    if temp == 0.0:
        info("Retornó 0.0 — revisa el log para ver qué método falló")
    else:
        info("Temperatura real leída correctamente")

    # --- Test 2: get_hostname ---
    print("\n[2] get_hostname:")
    hostname = SystemUtils.get_hostname()
    ok(f"Hostname: {hostname}")

    # --- Test 3: get_nvme_temp ---
    print("\n[3] get_nvme_temp:")
    nvme = SystemUtils.get_nvme_temp()
    ok(f"Temperatura NVMe: {nvme}°C")
    if nvme == 0.0:
        info("Retornó 0.0 — puede que no haya NVMe o falten permisos (normal)")
        info("Revisa el log: debe aparecer qué método falló (smartctl/sysfs)")

    # --- Test 4: list_usb_storage_devices ---
    print("\n[4] list_usb_storage_devices:")
    usb = SystemUtils.list_usb_storage_devices()
    ok(f"Dispositivos USB encontrados: {len(usb)}")
    for d in usb:
        info(f"  → {d.get('name')} ({d.get('dev')})")

    # --- Test 5: list_usb_other_devices ---
    print("\n[5] list_usb_other_devices:")
    otros = SystemUtils.list_usb_other_devices()
    ok(f"Otros dispositivos USB: {len(otros)}")

    # --- Test 6: get_interfaces_ips ---
    print("\n[6] get_interfaces_ips:")
    ips = SystemUtils.get_interfaces_ips()
    ok(f"Interfaces detectadas: {len(ips)}")
    for iface, ip in ips.items():
        info(f"  → {iface}: {ip}")

    # --- Test 7: run_script con script inexistente ---
    print("\n[7] run_script con script inexistente:")
    success, msg = SystemUtils.run_script("/ruta/que/no/existe.sh")
    ok(f"Retornó success={success}, msg='{msg}'")
    info("Debe aparecer en log: [ERROR] run_script: script no encontrado")

    # --- Test 8: run_script real (crea uno temporal) ---
    print("\n[8] run_script con script válido:")
    tmp_script = "/tmp/test_dashboard.sh"
    with open(tmp_script, "w") as f:
        f.write("#!/bin/bash\necho 'Script de prueba OK'\nexit 0\n")
    os.chmod(tmp_script, 0o755)

    success, msg = SystemUtils.run_script(tmp_script)
    ok(f"Retornó success={success}, msg='{msg}'")
    info("Debe aparecer en log: [INFO] Script ejecutado correctamente")
    os.remove(tmp_script)


# ============================================================
# TEST NETWORK_MONITOR
# ============================================================
def test_network_monitor():
    separador("NETWORK MONITOR (SPEEDTEST)")
    from core.network_monitor import NetworkMonitor

    monitor = NetworkMonitor()

    # --- Test 1: get_current_stats ---
    print("\n[1] get_current_stats:")
    stats = monitor.get_current_stats()
    ok(f"Interfaz: {stats['interface']}, ↓{stats['download_mb']:.3f} MB/s, ↑{stats['upload_mb']:.3f} MB/s")

    # --- Test 2: speedtest completo ---
    print("\n[2] Speedtest (puede tardar ~30-60s):")
    info("Iniciando speedtest... espera")
    monitor.run_speedtest()

    # Esperar resultado con timeout
    timeout = 90
    start = time.time()
    while time.time() - start < timeout:
        result = monitor.get_speedtest_result()
        status = result['status']

        if status == 'running':
            print(f"  ⏳ Ejecutando... ({int(time.time()-start)}s)", end='\r')
            time.sleep(2)
        elif status == 'done':
            print()
            ok(f"Ping: {result['ping']}ms | ↓{result['download']:.2f} MB/s | ↑{result['upload']:.2f} MB/s")
            info("Debe aparecer en log: [INFO] Speedtest completado con las métricas")
            break
        elif status == 'timeout':
            print()
            ok(f"Speedtest timeout (esperado si la conexión es lenta)")
            info("Debe aparecer en log: [WARNING] Speedtest timeout")
            break
        elif status == 'error':
            print()
            ok(f"Speedtest error (puede que speedtest-cli no esté instalado)")
            info("Debe aparecer en log: [ERROR] con el motivo del fallo")
            break
    else:
        print()
        info("Timeout de espera alcanzado en el script de prueba")

    # --- Test 3: speedtest con binario inexistente (simulado) ---
    print("\n[3] Verificar log de speedtest-cli no encontrado:")
    info("Para probar esto, renombra temporalmente speedtest-cli y ejecuta de nuevo")
    info("Debe aparecer en log: [ERROR] speedtest-cli no encontrado")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  TEST DE LOGGING - Dashboard v2.5.1")
    print("  Abre otra terminal y ejecuta:")
    print("  tail -f data/logs/dashboard.log")
    print("="*60)

    # Preguntar si hacer el speedtest (tarda mucho)
    hacer_speedtest = "--speedtest" in sys.argv or "-s" in sys.argv

    try:
        test_file_manager()
    except Exception as e:
        print(f"\n❌ Error en test_file_manager: {e}")

    try:
        test_system_utils()
    except Exception as e:
        print(f"\n❌ Error en test_system_utils: {e}")

    if hacer_speedtest:
        try:
            test_network_monitor()
        except Exception as e:
            print(f"\n❌ Error en test_network_monitor: {e}")
    else:
        separador("NETWORK MONITOR (SPEEDTEST)")
        print("\n  ⏭️  Saltado. Para incluir el speedtest ejecuta:")
        print("     python3 test_logging.py --speedtest")

    separador("RESULTADO FINAL")
    print("\n  Revisa data/logs/dashboard.log para verificar los mensajes.")
    print("  Todos los tests deberían mostrar ✅ sin excepciones no capturadas.\n")
