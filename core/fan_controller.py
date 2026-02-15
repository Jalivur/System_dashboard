"""
Controlador de ventiladores
"""
from typing import List, Dict
from utils.file_manager import FileManager


class FanController:
    """Controlador para gestión de ventiladores"""
    
    def __init__(self):
        self.file_manager = FileManager()
    
    def compute_pwm_from_curve(self, temp: float) -> int:
        """
        Calcula el PWM basado en la curva y la temperatura
        
        Args:
            temp: Temperatura actual en °C
            
        Returns:
            Valor PWM (0-255)
        """
        curve = self.file_manager.load_curve()
        
        if not curve:
            return 0
        
        # Si está por debajo del primer punto
        if temp <= curve[0]["temp"]:
            return int(curve[0]["pwm"])
        
        # Si está por encima del último punto
        if temp >= curve[-1]["temp"]:
            return int(curve[-1]["pwm"])
        
        # Interpolación lineal entre puntos
        for i in range(len(curve) - 1):
            t1, pwm1 = curve[i]["temp"], curve[i]["pwm"]
            t2, pwm2 = curve[i + 1]["temp"], curve[i + 1]["pwm"]
            
            if t1 <= temp <= t2:
                # Interpolación lineal
                ratio = (temp - t1) / (t2 - t1)
                pwm = pwm1 + ratio * (pwm2 - pwm1)
                return int(pwm)
        
        return int(curve[-1]["pwm"])
    
    def get_pwm_for_mode(self, mode: str, temp: float, manual_pwm: int = 128) -> int:
        """
        Obtiene el PWM según el modo seleccionado
        
        Args:
            mode: Modo de operación (auto, manual, silent, normal, performance)
            temp: Temperatura actual
            manual_pwm: Valor PWM manual si mode='manual'
            
        Returns:
            Valor PWM calculado (0-255)
        """
        if mode == "manual":
            return max(0, min(255, manual_pwm))
        elif mode == "auto":
            return self.compute_pwm_from_curve(temp)
        elif mode == "silent":
            return 77
        elif mode == "normal":
            return 128
        elif mode == "performance":
            return 255
        else:
            return self.compute_pwm_from_curve(temp)
    
    def update_fan_state(self, mode: str, temp: float, current_target: int = None, 
                        manual_pwm: int = 128) -> Dict:
        """
        Actualiza el estado del ventilador
        
        Args:
            mode: Modo actual
            temp: Temperatura actual
            current_target: PWM objetivo actual
            manual_pwm: PWM manual configurado
            
        Returns:
            Diccionario con el nuevo estado
        """
        desired = self.get_pwm_for_mode(mode, temp, manual_pwm)
        desired = max(0, min(255, int(desired)))
        
        if desired != current_target:
            new_state = {"mode": mode, "target_pwm": desired}
            self.file_manager.write_state(new_state)
            return new_state
        
        return {"mode": mode, "target_pwm": current_target}
    
    def add_curve_point(self, temp: int, pwm: int) -> List[Dict]:
        """
        Añade un punto a la curva
        
        Args:
            temp: Temperatura en °C
            pwm: Valor PWM (0-255)
            
        Returns:
            Curva actualizada
        """
        curve = self.file_manager.load_curve()
        pwm = max(0, min(255, pwm))
        
        # Buscar si ya existe un punto con esa temperatura
        found = False
        for point in curve:
            if point["temp"] == temp:
                point["pwm"] = pwm
                found = True
                break
        
        if not found:
            curve.append({"temp": temp, "pwm": pwm})
        
        # Ordenar por temperatura
        curve = sorted(curve, key=lambda x: x["temp"])
        self.file_manager.save_curve(curve)
        
        return curve
    
    def remove_curve_point(self, temp: int) -> List[Dict]:
        """
        Elimina un punto de la curva
        
        Args:
            temp: Temperatura del punto a eliminar
            
        Returns:
            Curva actualizada
        """
        curve = self.file_manager.load_curve()
        curve = [p for p in curve if p["temp"] != temp]
        
        # Mantener al menos un punto
        if not curve:
            curve = [{"temp": 40, "pwm": 100}]
        
        self.file_manager.save_curve(curve)
        return curve
