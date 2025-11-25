from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta
from models import WeatherReading, WeatherStats, HealthCheck
from storage import weather_store
from mqtt_client import mqtt_client
from contextlib import asynccontextmanager
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup: Conectar MQTT
    logger.info("Iniciando aplicación...")
    mqtt_client.connect()
    yield
    # Shutdown: Desconectar MQTT
    logger.info("Cerrando aplicación...")
    mqtt_client.disconnect()


# Crear aplicación FastAPI
app = FastAPI(
    title="API Estación Meteorológica Ibero",
    description="API REST para consultar datos en tiempo real de la estación meteorológica IoT",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "name": "API Estación Meteorológica Ibero",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Estado de salud del sistema"""
    readings = weather_store.get_latest(1)
    last_reading_time = readings[0].timestamp if readings else None
    
    return HealthCheck(
        status="healthy" if weather_store.mqtt_connected else "degraded",
        mqtt_connected=weather_store.mqtt_connected,
        total_readings=weather_store.count(),
        last_reading_time=last_reading_time
    )


@app.get("/readings/latest", response_model=WeatherReading, tags=["Readings"])
async def get_latest_reading():
    """Obtener la lectura más reciente"""
    readings = weather_store.get_latest(1)
    if not readings:
        raise HTTPException(status_code=404, detail="No hay lecturas disponibles")
    return readings[0]


@app.get("/readings", response_model=List[WeatherReading], tags=["Readings"])
async def get_readings(
    limit: int = Query(default=100, ge=1, le=1000, description="Número de lecturas a retornar"),
    start_time: Optional[datetime] = Query(default=None, description="Fecha/hora de inicio (ISO 8601)"),
    end_time: Optional[datetime] = Query(default=None, description="Fecha/hora de fin (ISO 8601)")
):
    """
    Obtener lecturas con filtros opcionales
    
    - **limit**: Número máximo de lecturas a retornar (1-1000)
    - **start_time**: Filtrar lecturas desde esta fecha/hora
    - **end_time**: Filtrar lecturas hasta esta fecha/hora
    """
    if start_time or end_time:
        readings = weather_store.get_by_time_range(start_time, end_time)
    else:
        readings = weather_store.get_latest(limit)
    
    if not readings:
        raise HTTPException(status_code=404, detail="No se encontraron lecturas")
    
    return readings


@app.get("/readings/last-hour", response_model=List[WeatherReading], tags=["Readings"])
async def get_last_hour_readings():
    """Obtener todas las lecturas de la última hora"""
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    readings = weather_store.get_by_time_range(start_time, end_time)
    
    if not readings:
        raise HTTPException(status_code=404, detail="No hay lecturas en la última hora")
    
    return readings


@app.get("/readings/last-day", response_model=List[WeatherReading], tags=["Readings"])
async def get_last_day_readings():
    """Obtener todas las lecturas de las últimas 24 horas"""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    readings = weather_store.get_by_time_range(start_time, end_time)
    
    if not readings:
        raise HTTPException(status_code=404, detail="No hay lecturas en las últimas 24 horas")
    
    return readings


@app.get("/stats", response_model=WeatherStats, tags=["Statistics"])
async def get_statistics(
    start_time: Optional[datetime] = Query(default=None, description="Fecha/hora de inicio para estadísticas"),
    end_time: Optional[datetime] = Query(default=None, description="Fecha/hora de fin para estadísticas")
):
    """
    Obtener estadísticas calculadas de las lecturas
    
    Si no se especifican fechas, calcula sobre todas las lecturas en memoria
    """
    if start_time or end_time:
        # Calcular stats para el rango de tiempo especificado
        readings = weather_store.get_by_time_range(start_time, end_time)
        if not readings:
            raise HTTPException(status_code=404, detail="No hay lecturas en el rango especificado")
        
        # Crear un store temporal para calcular stats
        from storage import WeatherDataStore
        temp_store = WeatherDataStore()
        for reading in readings:
            temp_store.add_reading(reading)
        return temp_store.get_stats()
    else:
        return weather_store.get_stats()


@app.get("/readings/count", tags=["Statistics"])
async def get_readings_count():
    """Obtener el número total de lecturas almacenadas"""
    return {"total_readings": weather_store.count()}


@app.delete("/readings", tags=["Admin"])
async def clear_readings():
    """Limpiar todas las lecturas almacenadas (solo para testing)"""
    weather_store.clear()
    logger.warning("Todas las lecturas han sido eliminadas")
    return {"message": "Todas las lecturas han sido eliminadas"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
