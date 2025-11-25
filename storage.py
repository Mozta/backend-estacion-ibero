from typing import List, Optional
from datetime import datetime
from collections import deque
from models import WeatherReading, WeatherStats
import threading


class WeatherDataStore:
    """Almacenamiento en memoria thread-safe para lecturas meteorológicas"""
    
    def __init__(self, max_readings: int = 1000):
        """
        Args:
            max_readings: Número máximo de lecturas a mantener en memoria
        """
        self.max_readings = max_readings
        self._readings: deque[WeatherReading] = deque(maxlen=max_readings)
        self._lock = threading.Lock()
        self.mqtt_connected = False
    
    def add_reading(self, reading: WeatherReading) -> None:
        """Agregar una nueva lectura de forma thread-safe"""
        with self._lock:
            self._readings.append(reading)
    
    def get_latest(self, limit: int = 1) -> List[WeatherReading]:
        """Obtener las últimas N lecturas"""
        with self._lock:
            return list(self._readings)[-limit:]
    
    def get_all(self) -> List[WeatherReading]:
        """Obtener todas las lecturas almacenadas"""
        with self._lock:
            return list(self._readings)
    
    def get_by_time_range(
        self, 
        start_time: Optional[datetime] = None, 
        end_time: Optional[datetime] = None
    ) -> List[WeatherReading]:
        """Obtener lecturas en un rango de tiempo"""
        with self._lock:
            readings = list(self._readings)
        
        if start_time:
            readings = [r for r in readings if r.timestamp >= start_time]
        if end_time:
            readings = [r for r in readings if r.timestamp <= end_time]
        
        return readings
    
    def get_stats(self) -> WeatherStats:
        """Calcular estadísticas de las lecturas almacenadas"""
        with self._lock:
            readings = list(self._readings)
        
        if not readings:
            return WeatherStats(total_readings=0)
        
        temps = [r.temp for r in readings]
        humidities = [r.humidity for r in readings]
        wind_speeds = [r.wind_speed_avg for r in readings]
        wind_maxs = [r.wind_speed_max for r in readings]
        rain = [r.rain_accumulated for r in readings]
        
        return WeatherStats(
            total_readings=len(readings),
            avg_temp=sum(temps) / len(temps),
            max_temp=max(temps),
            min_temp=min(temps),
            avg_humidity=sum(humidities) / len(humidities),
            avg_wind_speed=sum(wind_speeds) / len(wind_speeds),
            max_wind_speed=max(wind_maxs),
            total_rain=sum(rain),
            first_reading=readings[0].timestamp,
            last_reading=readings[-1].timestamp
        )
    
    def count(self) -> int:
        """Obtener el número total de lecturas almacenadas"""
        with self._lock:
            return len(self._readings)
    
    def clear(self) -> None:
        """Limpiar todas las lecturas (útil para testing)"""
        with self._lock:
            self._readings.clear()


# Instancia global del store
weather_store = WeatherDataStore(max_readings=1000)
