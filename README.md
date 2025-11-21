# Backend Estación Meteorológica Ibero

Sistema backend para la estación meteorológica IoT de la Universidad Iberoamericana. Recibe y procesa datos meteorológicos en tiempo real mediante protocolo MQTT.

## Descripción

Este proyecto es un suscriptor MQTT que se conecta a HiveMQ Cloud para recibir telemetría de una estación meteorológica que monitorea:

- **Datos meteorológicos**: Temperatura, humedad, presión atmosférica
- **Lluvia**: Intensidad, acumulación y duración
- **Viento**: Velocidad y dirección (min/max/avg)
- **Calidad del aire**: Partículas PM1, PM2, PM3
- **Luminosidad**: Medición en lux
- **Geolocalización**: Coordenadas GPS de la estación
- **Telemetría interna**: Temperatura y humedad del sistema

## Estructura de Datos

La estación envía un payload JSON con 23 métricas:

```json
{
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
```

## Requisitos

- Python 3.7+
- Conexión a internet
- Credenciales de acceso a HiveMQ Cloud

## Instalación

1. **Clonar el repositorio**

```bash
git clone https://github.com/Mozta/backend-estacion-ibero.git
cd backend-estacion-ibero
```

2. **Crear entorno virtual**

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

Copiar el archivo `.env.example` a `.env` y configurar:

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```env
BROKER=your_broker_url
PORT=8883
USERNAME=your_username
PASSWORD=your_password
TOPIC=your_topic
```

## Uso

Ejecutar el suscriptor MQTT:

```bash
python app.py
```

El sistema se conectará al broker y comenzará a recibir y mostrar los datos:

```
Conectado al broker MQTT
Suscrito a: estacion
Esperando mensajes... (Ctrl+C para salir)

Mensaje recibido
Topic : estacion
Payload crudo : {"lat":19.031917,"lon":-98.240528,...}
Como JSON: {'lat': 19.031917, 'lon': -98.240528, ...}
```

## Arquitectura

```
┌─────────────────┐
│  Estación IoT   │
│  (Sensores)     │
└────────┬────────┘
         │
         │ MQTT/TLS
         ▼
┌─────────────────┐
│  HiveMQ Cloud   │
│  (Broker MQTT)  │
└────────┬────────┘
         │
         │ MQTT/TLS
         ▼
┌─────────────────┐
│    app.py       │
│  (Suscriptor)   │
└─────────────────┘
```

## Características Técnicas

- **Protocolo**: MQTT v3.1.1
- **Seguridad**: TLS/SSL con certificados CA
- **QoS**: Configurable según necesidad
- **Reconexión**: Automática en caso de pérdida de conexión
- **Validación**: Variables de entorno requeridas verificadas al inicio

## Dependencias

```
paho-mqtt     # Cliente MQTT
certifi       # Certificados SSL/TLS
python-dotenv # Manejo de variables de entorno
```

## Seguridad

- Las credenciales se gestionan mediante variables de entorno
- El archivo `.env` está excluido del control de versiones
- Conexión cifrada mediante TLS/SSL
- Certificados CA confiables del sistema

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

- **Repositorio**: [github.com/Mozta/backend-estacion-ibero](https://github.com/Mozta/backend-estacion-ibero)
- **Issues**: [Reportar un problema](https://github.com/Mozta/backend-estacion-ibero/issues)
