"""
Análisis de datos históricos
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from config.settings import DATA_DIR
from utils.logger import get_logger

logger = get_logger(__name__)


class DataAnalyzer:
    """Analiza datos históricos de la base de datos"""

    def __init__(self, db_path: str = f"{DATA_DIR}/history.db"):
        self.db_path = db_path

    def get_data_range(self, hours: int = 24) -> List[Dict]:
        """
        Obtiene datos de las últimas X horas

        Args:
            hours: Número de horas hacia atrás

        Returns:
            Lista de diccionarios con los datos
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cutoff_time = datetime.now() - timedelta(hours=hours)

            cursor.execute('''
                SELECT * FROM metrics
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
            ''', (cutoff_time,))

            rows = cursor.fetchall()
            conn.close()

            logger.debug(f"[DataAnalyzer] get_data_range: {len(rows)} registros obtenidos (últimas {hours}h)")
            return [dict(row) for row in rows]

        except sqlite3.OperationalError as e:
            logger.error(f"[DataAnalyzer] get_data_range: error de base de datos: {e}")
            return []
        except Exception as e:
            logger.error(f"[DataAnalyzer] get_data_range: error inesperado: {e}")
            return []

    def get_stats(self, hours: int = 24) -> Dict:
        """
        Obtiene estadísticas de las últimas X horas

        Args:
            hours: Número de horas hacia atrás

        Returns:
            Diccionario con estadísticas
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_time = datetime.now() - timedelta(hours=hours)

            cursor.execute('''
                SELECT 
                    AVG(cpu_percent) as cpu_avg,
                    MAX(cpu_percent) as cpu_max,
                    MIN(cpu_percent) as cpu_min,
                    AVG(ram_percent) as ram_avg,
                    MAX(ram_percent) as ram_max,
                    MIN(ram_percent) as ram_min,
                    AVG(temperature) as temp_avg,
                    MAX(temperature) as temp_max,
                    MIN(temperature) as temp_min,
                    AVG(net_download_mb) as down_avg,
                    MAX(net_download_mb) as down_max,
                    MIN(net_download_mb) as down_min,
                    AVG(net_upload_mb) as up_avg,
                    MAX(net_upload_mb) as up_max,
                    MIN(net_upload_mb) as up_min,
                    AVG(disk_read_mb) as disk_read_avg,
                    MAX(disk_read_mb) as disk_read_max,
                    MIN(disk_read_mb) as disk_read_min,
                    AVG(disk_write_mb) as disk_write_avg,
                    MAX(disk_write_mb) as disk_write_max,
                    MIN(disk_write_mb) as disk_write_min,
                    AVG(fan_pwm) as pwm_avg,
                    MAX(fan_pwm) as pwm_max,
                    MIN(fan_pwm) as pwm_min,
                    COUNT(*) as total_samples
                FROM metrics
                WHERE timestamp >= ?
            ''', (cutoff_time,))

            row = cursor.fetchone()
            conn.close()

            if row and row[24]:
                logger.debug(f"[DataAnalyzer] get_stats: {row[24]} muestras en las últimas {hours}h")
                return {
                    'cpu_avg': round(row[0], 1) if row[0] else 0,
                    'cpu_max': round(row[1], 1) if row[1] else 0,
                    'cpu_min': round(row[2], 1) if row[2] else 0,
                    'ram_avg': round(row[3], 1) if row[3] else 0,
                    'ram_max': round(row[4], 1) if row[4] else 0,
                    'ram_min': round(row[5], 1) if row[5] else 0,
                    'temp_avg': round(row[6], 1) if row[6] else 0,
                    'temp_max': round(row[7], 1) if row[7] else 0,
                    'temp_min': round(row[8], 1) if row[8] else 0,
                    'down_avg': round(row[9], 2) if row[9] else 0,
                    'down_max': round(row[10], 2) if row[10] else 0,
                    'down_min': round(row[11], 2) if row[11] else 0,
                    'up_avg': round(row[12], 2) if row[12] else 0,
                    'up_max': round(row[13], 2) if row[13] else 0,
                    'up_min': round(row[14], 2) if row[14] else 0,
                    'disk_read_avg': round(row[15], 2) if row[15] else 0,
                    'disk_read_max': round(row[16], 2) if row[16] else 0,
                    'disk_read_min': round(row[17], 2) if row[17] else 0,
                    'disk_write_avg': round(row[18], 2) if row[18] else 0,
                    'disk_write_max': round(row[19], 2) if row[19] else 0,
                    'disk_write_min': round(row[20], 2) if row[20] else 0,
                    'pwm_avg': round(row[21], 0) if row[21] else 0,
                    'pwm_max': round(row[22], 0) if row[22] else 0,
                    'pwm_min': round(row[23], 0) if row[23] else 0,
                    'total_samples': row[24]
                }

            logger.debug(f"[DataAnalyzer] get_stats: sin datos en las últimas {hours}h")
            return {}

        except sqlite3.OperationalError as e:
            logger.error(f"[DataAnalyzer] get_stats: error de base de datos: {e}")
            return {}
        except Exception as e:
            logger.error(f"[DataAnalyzer] get_stats: error inesperado: {e}")
            return {}

    def detect_anomalies(self, hours: int = 24) -> List[Dict]:
        """
        Detecta anomalías en los datos

        Args:
            hours: Número de horas hacia atrás

        Returns:
            Lista de anomalías detectadas
        """
        anomalies = []
        stats = self.get_stats(hours)

        if not stats:
            return anomalies

        if stats.get('cpu_avg', 0) > 80:
            anomalies.append({
                'type': 'cpu_high',
                'severity': 'warning',
                'message': f"CPU promedio alta: {stats['cpu_avg']:.1f}%"
            })
            logger.warning(f"[DataAnalyzer] Anomalía detectada: CPU promedio {stats['cpu_avg']:.1f}%")

        if stats.get('temp_max', 0) > 80:
            anomalies.append({
                'type': 'temp_high',
                'severity': 'critical',
                'message': f"Temperatura máxima: {stats['temp_max']:.1f}°C"
            })
            logger.warning(f"[DataAnalyzer] Anomalía detectada: temperatura máxima {stats['temp_max']:.1f}°C")

        if stats.get('ram_avg', 0) > 85:
            anomalies.append({
                'type': 'ram_high',
                'severity': 'warning',
                'message': f"RAM promedio alta: {stats['ram_avg']:.1f}%"
            })
            logger.warning(f"[DataAnalyzer] Anomalía detectada: RAM promedio {stats['ram_avg']:.1f}%")

        return anomalies

    def get_graph_data(self, metric: str, hours: int = 24) -> Tuple[List, List]:
        """
        Obtiene datos para gráficas

        Args:
            metric: Métrica a obtener (cpu_percent, ram_percent, temperature, etc)
            hours: Número de horas hacia atrás

        Returns:
            Tupla (timestamps, values)
        """
        try:
            data = self.get_data_range(hours)

            timestamps = []
            values = []

            for entry in data:
                ts = datetime.fromisoformat(entry['timestamp'])
                timestamps.append(ts)
                values.append(entry.get(metric, 0))

            return timestamps, values

        except Exception as e:
            logger.error(f"[DataAnalyzer] get_graph_data: error obteniendo datos de '{metric}': {e}")
            return [], []

    def export_to_csv(self, output_path: str, hours: int = 24):
        """
        Exporta datos a CSV

        Args:
            output_path: Ruta del archivo CSV a crear
            hours: Número de horas a exportar
        """
        import csv

        try:
            data = self.get_data_range(hours)

            if not data:
                logger.warning(f"[DataAnalyzer] export_to_csv: sin datos para exportar (últimas {hours}h)")
                return

            with open(output_path, 'w', newline='') as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in data:
                    writer.writerow(row)

            logger.info(f"[DataAnalyzer] export_to_csv: {len(data)} registros exportados a {output_path}")

        except OSError as e:
            logger.error(f"[DataAnalyzer] export_to_csv: error escribiendo {output_path}: {e}")
        except Exception as e:
            logger.error(f"[DataAnalyzer] export_to_csv: error inesperado: {e}")
