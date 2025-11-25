# API Estación Meteorológica - FastAPI

## Estructura del Proyecto

```
backend-estacion-ibero/
├── api.py              # Aplicación FastAPI principal
├── mqtt_client.py      # Cliente MQTT integrado
├── models.py           # Modelos Pydantic
├── storage.py          # Almacenamiento en memoria
├── app.py              # Script MQTT standalone (legacy)
├── requirements.txt    # Dependencias
├── .env                # Variables de entorno
├── .env.example        # Plantilla de variables
└── README.md           # Documentación
```

## Endpoints Disponibles

### Root & Health

- `GET /` - Información de la API
- `GET /health` - Estado del sistema y conexión MQTT

### Lecturas

- `GET /readings/latest` - Última lectura recibida
- `GET /readings` - Listado de lecturas con filtros
  - Query params: `limit`, `start_time`, `end_time`
- `GET /readings/last-hour` - Lecturas de la última hora
- `GET /readings/last-day` - Lecturas de las últimas 24 horas

### Estadísticas

- `GET /stats` - Estadísticas calculadas
- `GET /readings/count` - Total de lecturas

### Admin

- `DELETE /readings` - Limpiar todas las lecturas

## Iniciar el Servidor

### Modo Desarrollo

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Modo Producción

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

## Documentación Interactiva

Una vez iniciado el servidor:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Ejemplos de Uso

### Obtener última lectura

```bash
curl http://localhost:8000/readings/latest
```

### Obtener lecturas con filtro de tiempo

```bash
curl "http://localhost:8000/readings?limit=50&start_time=2025-11-21T00:00:00"
```

### Obtener estadísticas

```bash
curl http://localhost:8000/stats
```

### Verificar salud del sistema

```bash
curl http://localhost:8000/health
```

## Características

✅ **Validación automática** con Pydantic
✅ **Documentación OpenAPI** generada automáticamente
✅ **CORS configurado** para desarrollo frontend
✅ **Thread-safe** almacenamiento en memoria
✅ **Logging estructurado** para debugging
✅ **Manejo de errores** con códigos HTTP apropiados
✅ **Cliente MQTT** en background integrado con FastAPI lifecycle

## Arquitectura

```
┌──────────────┐
│ Estación IoT │
└──────┬───────┘
       │ MQTT
       ▼
┌──────────────┐
│ HiveMQ Cloud │
└──────┬───────┘
       │ MQTT
       ▼
┌──────────────────────────┐
│   mqtt_client.py         │
│   (Background Thread)    │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│   storage.py             │
│   (In-Memory Store)      │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│   api.py (FastAPI)       │
│   REST Endpoints         │
└──────────────────────────┘
       │
       ▼
┌──────────────────────────┐
│   Clientes HTTP          │
│   (Frontend, Apps, etc)  │
└──────────────────────────┘
```

## Buenas Prácticas Implementadas

1. **Separación de responsabilidades**

   - `models.py`: Definición de esquemas
   - `storage.py`: Capa de persistencia
   - `mqtt_client.py`: Comunicación MQTT
   - `api.py`: Endpoints REST

2. **Type hints** en todas las funciones

3. **Validación de datos** con Pydantic

4. **Thread-safety** con locks para operaciones concurrentes

5. **Manejo de lifecycle** con startup/shutdown events

6. **Logging apropiado** en lugar de prints

7. **Documentación inline** con docstrings

8. **Variables de entorno** para configuración sensible

## Próximos Pasos (Fase 2)

- [ ] Integrar base de datos (PostgreSQL)
- [ ] Agregar autenticación JWT
- [ ] Implementar paginación en endpoints
- [ ] Agregar cache con Redis
- [ ] Crear tests unitarios y de integración
- [ ] Dockerizar la aplicación
- [ ] Configurar CI/CD
