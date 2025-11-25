from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class WeatherReading(BaseModel):
    """Modelo de datos para una lectura de la estación meteorológica"""
    
    # Ubicación
    lat: float = Field(..., description="Latitud GPS")
    lon: float = Field(..., description="Longitud GPS")
    
    # Temperatura y humedad
    temp: float = Field(..., description="Temperatura exterior (°C)")
    humidity: float = Field(..., ge=0, le=100, description="Humedad exterior (%)")
    pressure: float = Field(..., description="Presión atmosférica (hPa)")
    
    # Lluvia
    rain_intensity: float = Field(..., ge=0, description="Intensidad de lluvia")
    rain_intensity_max: float = Field(..., ge=0, description="Intensidad máxima de lluvia")
    rain_accumulated: float = Field(..., ge=0, description="Lluvia acumulada (mm)")
    rain_duration: float = Field(..., ge=0, description="Duración de lluvia (s)")
    
    # Viento
    wind_speed_min: float = Field(..., ge=0, description="Velocidad mínima del viento (m/s)")
    wind_speed_max: float = Field(..., ge=0, description="Velocidad máxima del viento (m/s)")
    wind_speed_avg: float = Field(..., ge=0, description="Velocidad promedio del viento (m/s)")
    wind_dir_min: float = Field(..., ge=0, le=360, description="Dirección mínima del viento (°)")
    wind_dir_max: float = Field(..., ge=0, le=360, description="Dirección máxima del viento (°)", alias="wind_dir_máx")
    wind_dir_avg: float = Field(..., ge=0, le=360, description="Dirección promedio del viento (°)")
    
    # Luminosidad
    lux: float = Field(..., ge=0, description="Luminosidad (lm/m²)", alias="Luxlm/m2")
    
    # Sensores internos
    temp_int: float = Field(..., description="Temperatura interna (°C)")
    hum_int: float = Field(..., ge=0, le=100, description="Humedad interna (%)")
    heating_temp: float = Field(..., description="Temperatura de calentamiento (°C)")
    
    # Estados
    dumping_state: int = Field(..., description="Estado de volcado")
    
    # Calidad del aire
    PM1: float = Field(..., ge=0, description="Partículas PM1.0 (µg/m³)")
    PM2: float = Field(..., ge=0, description="Partículas PM2.5 (µg/m³)")
    PM3: float = Field(..., ge=0, description="Partículas PM10 (µg/m³)")
    
    # Metadatos (agregados por el sistema)
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Timestamp de recepción")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "lat": 19.031917,
                "lon": -98.240528,
                "temp": 23.62,
                "humidity": 53.3,
                "pressure": 790.2,
                "rain_intensity": 0,
                "rain_intensity_max": 0,
                "rain_accumulated": 0,
                "rain_duration": 255833.33,
                "wind_speed_min": 0.7,
                "wind_speed_max": 0.9,
                "wind_speed_avg": 0.8,
                "wind_dir_min": 198.4,
                "wind_dir_máx": 219.7,
                "wind_dir_avg": 208.2,
                "Luxlm/m2": 2185,
                "temp_int": 43,
                "hum_int": 24.3,
                "heating_temp": 24.37,
                "dumping_state": 0,
                "PM1": 0,
                "PM2": 0,
                "PM3": 0
            }
        }


class WeatherStats(BaseModel):
    """Estadísticas calculadas de las lecturas"""
    total_readings: int
    avg_temp: Optional[float] = None
    max_temp: Optional[float] = None
    min_temp: Optional[float] = None
    avg_humidity: Optional[float] = None
    avg_wind_speed: Optional[float] = None
    max_wind_speed: Optional[float] = None
    total_rain: Optional[float] = None
    first_reading: Optional[datetime] = None
    last_reading: Optional[datetime] = None


class HealthCheck(BaseModel):
    """Estado de salud del sistema"""
    status: str
    mqtt_connected: bool
    total_readings: int
    last_reading_time: Optional[datetime] = None
