"""
Gestión de archivos JSON para estado y configuración
"""
import json
import os
from typing import Dict, List, Any, Optional
from config.settings import STATE_FILE, CURVE_FILE


class FileManager:
    """Gestor centralizado de archivos JSON"""
    
    @staticmethod
    def write_state(data: Dict[str, Any]) -> None:
        """
        Escribe el estado de forma atómica usando archivo temporal
        
        Args:
            data: Diccionario con los datos a guardar
        """
        tmp = str(STATE_FILE) + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, STATE_FILE)
    
    @staticmethod
    def load_state() -> Dict[str, Any]:
        """
        Carga el estado guardado
        
        Returns:
            Diccionario con mode y target_pwm
        """
        default_state = {"mode": "auto", "target_pwm": None}
        
        try:
            with open(STATE_FILE) as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    return default_state
                return {
                    "mode": data.get("mode", "auto"),
                    "target_pwm": data.get("target_pwm")
                }
        except (FileNotFoundError, json.JSONDecodeError):
            return default_state
    
    @staticmethod
    def load_curve() -> List[Dict[str, int]]:
        """
        Carga la curva de ventiladores
        
        Returns:
            Lista de puntos ordenados por temperatura
        """
        default_curve = [
            {"temp": 40, "pwm": 100},
            {"temp": 50, "pwm": 100},
            {"temp": 60, "pwm": 100},
            {"temp": 70, "pwm": 63},
            {"temp": 80, "pwm": 81}
        ]
        
        try:
            with open(CURVE_FILE) as f:
                data = json.load(f)
                pts = data.get("points", [])
                
                if not isinstance(pts, list):
                    return default_curve
                
                sanitized = []
                for p in pts:
                    try:
                        temp = int(p.get("temp", 0))
                    except (ValueError, TypeError):
                        temp = 0
                    
                    try:
                        pwm = int(p.get("pwm", 0))
                    except (ValueError, TypeError):
                        pwm = 0
                    
                    pwm = max(0, min(255, pwm))
                    sanitized.append({"temp": temp, "pwm": pwm})
                
                if not sanitized:
                    return default_curve
                
                return sorted(sanitized, key=lambda x: x["temp"])
                
        except (FileNotFoundError, json.JSONDecodeError):
            return default_curve
    
    @staticmethod
    def save_curve(points: List[Dict[str, int]]) -> None:
        """
        Guarda la curva de ventiladores
        
        Args:
            points: Lista de puntos {temp, pwm}
        """
        data = {"points": points}
        tmp = str(CURVE_FILE) + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, CURVE_FILE)
