# 🚀 Roadmap: MQTT Monitoring en Tiempo Real

Especificación de la funcionalidad de monitoreo automático de estado de servicios ETAPA.

---

## 🎯 Objetivo

Automatizar la actualización del campo `estado_operativo` de servicios mediante monitoreo en tiempo real via **MQTT**, sin intervención manual del usuario.

---

## 📊 Arquitectura Propuesta

```
External Monitoring Agents
├─ Agent 1: Ping IPs públicas (cloud)
├─ Agent 2: Ping IPs privadas (red EMOV)
└─ Publish resultados a MQTT Broker
    ↓
MQTT Broker (mosquitto, AWS IoT, etc.)
    ↓
FACRET (cliente MQTT)
├─ Suscrito a topics: enlaces/{cod_serv}/estado
├─ Recibe payloads con UP/DOWN
├─ Actualiza JSON + crea evento
├─ Notifica UI
└─ Envía alertas (si DOWN > 15 min)
```

---

## 📡 MQTT Topics y Payloads

### Topic Propuesto

```
enlaces/{cod_serv}/estado
```

**Ejemplo:**
```
enlaces/IO247963/estado
enlaces/RDD01973/estado
```

### Payload

```json
{
  "op": "UP|DOWN",
  "ts": "2026-07-26T14:32:15Z",
  "latencia_ms": 45,
  "verificado_por": "agent_cloud"
}
```

**Campos:**
- `op` — Estado operativo (UP o DOWN)
- `ts` — Timestamp ISO de cuando se detectó el cambio
- `latencia_ms` — Latencia medida (opcional)
- `verificado_por` — Qué agente realizó la verificación

---

## 💻 Implementación en FACRET

### Paso 1: Crear `src/logic/mqtt_client.py`

```python
import paho.mqtt.client as mqtt
from logic.logger import get_logger
from logic.contracts_writer import update_servicio, add_evento
import json
from datetime import datetime

logger = get_logger(__name__)

class MQTTMonitor:
    def __init__(self, broker_address, port=1883):
        self.broker = broker_address
        self.port = port
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.downtime_tracker = {}  # {cod_serv: timestamp_cuando_bajo}
    
    def connect(self):
        """Conectar a MQTT broker"""
        logger.info(f"Conectando a MQTT {self.broker}:{self.port}")
        self.client.connect(self.broker, self.port, keepalive=60)
        self.client.loop_start()  # Conexión en background
        logger.info("MQTT conectado")
    
    def disconnect(self):
        """Desconectar"""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("MQTT desconectado")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback cuando conecta"""
        if rc == 0:
            logger.info("MQTT conectado exitosamente")
            # Suscribirse a todos los topics
            client.subscribe("enlaces/+/estado")
            logger.debug("Suscrito a: enlaces/+/estado")
        else:
            logger.error(f"MQTT error de conexión: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback cuando llega mensaje"""
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic
            
            # Parsear topic: enlaces/{cod_serv}/estado
            cod_serv = topic.split("/")[1]
            
            estado_nuevo = payload.get("op")
            timestamp = payload.get("ts", datetime.now().isoformat())
            
            logger.info(f"[MQTT] {cod_serv}: {estado_nuevo} @ {timestamp}")
            
            # Actualizar servicio en JSON
            self._actualizar_servicio(cod_serv, estado_nuevo, timestamp)
            
            # Checkear si debe enviar alerta (DOWN > 15 min)
            self._checkear_downtime(cod_serv, estado_nuevo, timestamp)
        
        except Exception as e:
            logger.error(f"Error procesando MQTT message: {e}")
    
    def _actualizar_servicio(self, cod_serv, estado_nuevo, timestamp):
        """Actualizar JSON y crear evento"""
        try:
            # Leer estado anterior (para el evento)
            estado_anterior = self._get_estado_actual(cod_serv)
            
            # Actualizar
            update_servicio(cod_serv, estado_operativo=estado_nuevo)
            
            # Crear evento
            add_evento(
                cod_serv=cod_serv,
                tipo="CAMBIO_OPERATIVO_AUTOMATICO",
                valor_anterior=estado_anterior,
                valor_nuevo=estado_nuevo,
                nota=f"Actualización automática via MQTT @ {timestamp}"
            )
            
            logger.info(f"Servicio {cod_serv} actualizado: {estado_anterior} → {estado_nuevo}")
        
        except Exception as e:
            logger.error(f"Error actualizando {cod_serv}: {e}")
    
    def _checkear_downtime(self, cod_serv, estado_nuevo, timestamp):
        """Checkear si debe enviar alerta"""
        if estado_nuevo == "DOWN":
            # Registrar timestamp cuando bajó
            if cod_serv not in self.downtime_tracker:
                self.downtime_tracker[cod_serv] = timestamp
                logger.warning(f"{cod_serv} DOWN detectado")
        
        elif estado_nuevo == "UP":
            # Servicio volvió UP
            if cod_serv in self.downtime_tracker:
                downtime_start = self.downtime_tracker.pop(cod_serv)
                # Calcular duración DOWN
                logger.info(f"{cod_serv} volvió UP (estuvo DOWN desde {downtime_start})")
    
    def _get_estado_actual(self, cod_serv):
        """Obtener estado actual del servicio (para eventos)"""
        # ← Implementar lectura de JSON actual
        return "UP"  # Placeholder
```

### Paso 2: Integrar en gui.py

```python
from logic.mqtt_client import MQTTMonitor

def main():
    mqtt_monitor = MQTTMonitor(
        broker_address=load_config().get("mqtt_broker", "localhost"),
        port=load_config().get("mqtt_port", 1883)
    )
    
    try:
        mqtt_monitor.connect()
        # ... resto de la app
    finally:
        mqtt_monitor.disconnect()
```

### Paso 3: Actualizar config

Agregar a `src/config/facs_config.json`:

```json
{
  "mqtt_broker": "localhost",
  "mqtt_port": 1883,
  "mqtt_enabled": true,
  "mqtt_alert_downtime_minutes": 15
}
```

---

## 🔔 Alertas Automáticas (Futuro)

Cuando un servicio está DOWN > 15 minutos:

```python
# En mqtt_client.py
def _checkear_downtime(self, cod_serv, estado_nuevo, timestamp):
    if estado_nuevo == "DOWN":
        # ... registrar timestamp
    elif estado_nuevo == "UP":
        downtime_minutes = (datetime.fromisoformat(timestamp) - datetime.fromisoformat(downtime_start)).total_seconds() / 60
        
        if downtime_minutes > 15:
            logger.critical(f"{cod_serv} estuvo DOWN {downtime_minutes:.0f} minutos")
            self._enviar_alerta_email(cod_serv, downtime_minutes)
```

---

## 📊 Métricas a Rastrear

Con MQTT implementado, FACRET podrá calcular:

1. **Uptime por servicio** — % de tiempo operativo
2. **Downtime acumulado** — duración total DOWN
3. **MTTR** (Mean Time To Repair) — tiempo promedio para recuperar
4. **Tendencias** — servicios problemáticos

---

## 🔧 Configuración en Producción

### Opción 1: MQTT Público (AWS IoT)

```json
{
  "mqtt_broker": "iot.eu-west-1.amazonaws.com",
  "mqtt_port": 8883,
  "mqtt_tls": true,
  "mqtt_cert": "/path/to/cert.pem"
}
```

### Opción 2: MQTT Local (Mosquitto)

```bash
# Instalar broker
docker run -d -p 1883:1883 eclipse-mosquitto

# Configurar FACRET
{
  "mqtt_broker": "localhost",
  "mqtt_port": 1883,
  "mqtt_enabled": true
}
```

---

## 📋 Plan de Implementación

| Fase | Tarea | Esfuerzo | Prioridad |
|------|-------|----------|-----------|
| 1 | Crear `logic/mqtt_client.py` | 3h | 🔴 Alta |
| 2 | Integrar en `gui.py` | 1h | 🔴 Alta |
| 3 | Tests unitarios | 2h | 🟡 Media |
| 4 | Alertas por email | 2h | 🟡 Media |
| 5 | Dashboard de uptime | 4h | 🟢 Baja |

**Total:** ~12 horas (1.5 días)

---

## 🎯 Beneficios

✅ Monitoreo automático sin intervención manual  
✅ Historial completo de cambios  
✅ Alertas proactivas ante problemas  
✅ Datos para renegociación de contratos  
✅ Mejor compliance con SLAs  

---

**Última actualización:** 26 de Julio 2026
