"""
Script puntual para corregir el desfase UTC en los registros históricos.
Suma 1 hora a todos los timestamps de las tablas metrics y events.

Uso: python3 fix_timestamps.py
"""
import sqlite3
from datetime import datetime

DB_PATH = "data/history.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Contar registros antes
cursor.execute("SELECT COUNT(*) FROM metrics")
n_metrics = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM events")
n_events = cursor.fetchone()[0]

print(f"Registros encontrados: {n_metrics} métricas, {n_events} eventos")
print("Aplicando corrección +1h...")

# Sumar 1 hora a todos los timestamps
cursor.execute("""
    UPDATE metrics
    SET timestamp = datetime(timestamp, '+1 hour')
""")
cursor.execute("""
    UPDATE events
    SET timestamp = datetime(timestamp, '+1 hour')
""")

conn.commit()

# Verificar un par de registros para confirmar
cursor.execute("SELECT timestamp FROM metrics ORDER BY timestamp DESC LIMIT 3")
rows = cursor.fetchall()
print("\nÚltimos timestamps tras la corrección:")
for r in rows:
    print(f"  {r[0]}")

conn.close()
print("\nHecho. Todos los registros corregidos.")
