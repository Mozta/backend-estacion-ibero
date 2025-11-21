import ssl
import json
import certifi
import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

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


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado al broker MQTT")
        client.subscribe(TOPIC)
        print(f"Suscrito a: {TOPIC}")
    else:
        print(f"Error de conexión. Código: {rc}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print("\nMensaje recibido")
    print(f"Topic : {msg.topic}")
    print(f"Payload crudo : {payload}")

    # Si esperas JSON:
    try:
        data = json.loads(payload)
        print("Como JSON:", data)
    except json.JSONDecodeError:
        pass


# Crear cliente con protocolo MQTT 3.1.1
client = mqtt.Client(
    client_id="python-suscriptor-1",
    protocol=mqtt.MQTTv311  # importante: v3.1.1
)

# Usuario y contraseña
client.username_pw_set(USERNAME, PASSWORD)

# Configurar TLS
client.tls_set(
    ca_certs=certifi.where(),              # CA confiable del sistema
    certfile=None,
    keyfile=None,
    tls_version=ssl.PROTOCOL_TLS_CLIENT
)

# (Opcional) si hay problemas de certificado, puedes descomentar:
# client.tls_insecure_set(True)

# Asignar callbacks
client.on_connect = on_connect
client.on_message = on_message

# Conexión
client.connect(BROKER, PORT, keepalive=60)

print("Esperando mensajes... (Ctrl+C para salir)")
client.loop_forever()
