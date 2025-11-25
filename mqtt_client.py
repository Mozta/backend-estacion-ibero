import ssl
import json
import certifi
import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from models import WeatherReading
from storage import weather_store
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

BROKER = os.getenv("BROKER")
PORT = int(os.getenv("PORT", "8883"))
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
TOPIC = os.getenv("TOPIC")

# Validar que las variables requeridas estén configuradas
if not all([BROKER, USERNAME, PASSWORD, TOPIC]):
    raise ValueError("Faltan variables de entorno requeridas. Verifica tu archivo .env")

# Type assertions para el análisis estático
assert BROKER is not None
assert USERNAME is not None
assert PASSWORD is not None
assert TOPIC is not None


class MQTTClient:
    """Cliente MQTT thread-safe integrado con FastAPI"""
    
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.connected = False
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback cuando se establece conexión con el broker"""
        if rc == 0:
            logger.info("Conectado al broker MQTT")
            self.connected = True
            weather_store.mqtt_connected = True
            client.subscribe(TOPIC)
            logger.info(f"Suscrito a: {TOPIC}")
        else:
            logger.error(f"Error de conexión. Código: {rc}")
            self.connected = False
            weather_store.mqtt_connected = False
    
    def on_disconnect(self, client, userdata, rc):
        """Callback cuando se pierde la conexión"""
        logger.warning(f"Desconectado del broker MQTT. Código: {rc}")
        self.connected = False
        weather_store.mqtt_connected = False
    
    def on_message(self, client, userdata, msg):
        """Callback cuando se recibe un mensaje"""
        try:
            payload = msg.payload.decode("utf-8")
            logger.info(f"Mensaje recibido en topic: {msg.topic}")
            
            # Parsear JSON
            data = json.loads(payload)
            
            # Validar y crear objeto WeatherReading
            reading = WeatherReading(**data)
            
            # Almacenar en memoria
            weather_store.add_reading(reading)
            logger.info(f"Lectura almacenada. Total: {weather_store.count()}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar JSON: {e}")
        except Exception as e:
            logger.error(f"Error al procesar mensaje: {e}")
    
    def connect(self):
        """Establecer conexión con el broker MQTT"""
        try:
            # Crear cliente con protocolo MQTT 3.1.1
            self.client = mqtt.Client(
                client_id="fastapi-backend",
                protocol=mqtt.MQTTv311
            )
            
            # Usuario y contraseña
            self.client.username_pw_set(USERNAME, PASSWORD)
            
            # Configurar TLS
            self.client.tls_set(
                ca_certs=certifi.where(),
                certfile=None,
                keyfile=None,
                tls_version=ssl.PROTOCOL_TLS_CLIENT
            )
            
            # Asignar callbacks
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message
            
            # Conexión
            self.client.connect(BROKER, PORT, keepalive=60)
            
            # Iniciar loop en thread separado
            self.client.loop_start()
            logger.info("Cliente MQTT iniciado")
            
        except Exception as e:
            logger.error(f"Error al conectar con MQTT: {e}")
            raise
    
    def disconnect(self):
        """Desconectar del broker MQTT"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Cliente MQTT desconectado")


# Instancia global del cliente MQTT
mqtt_client = MQTTClient()
