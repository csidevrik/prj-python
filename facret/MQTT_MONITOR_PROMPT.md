# Prompt — Sistema de monitoreo MQTT para enlaces ETAPA EP

Quiero construir un sistema de monitoreo en tiempo real para los enlaces de internet
y datos contratados con ETAPA EP por EMOV EP (empresa de movilidad de Cuenca, Ecuador).
El objetivo es automatizar la detección de caídas, registrar historial de disponibilidad
y notificar automáticamente cuando un enlace baja.

---

## CONTEXTO DEL NEGOCIO

- **Cliente:** EMOV EP — administra ~140 servicios de conectividad contratados con ETAPA EP.
- **Tipos de enlace:**
  - `internet` (código IO*): enlace de internet a una agencia. Tiene IP pública asignada.
  - `datos` (código RDD*): circuito punto a punto entre dos extremos. Sin IP pública,
    se monitorea por IP privada interna.
- **Problema actual:** el campo `estado_operativo` (UP/DOWN) en los JSON se actualiza
  a mano. No hay registro automático de caídas ni duración de incidentes.
- **Objetivo final:** estadísticas de uptime por enlace para renegociar contratos con ETAPA EP
  y enviar notificaciones automáticas cuando un enlace cae más de 15 minutos.

---

## STACK TECNOLÓGICO

| Componente | Tecnología |
|---|---|
| Protocolo mensajería | MQTT (paho-mqtt) |
| Broker MQTT | Mosquitto (en VPS externo) |
| Agente publisher externo | Python script en VPS/AWS |
| Agente publisher interno | Python script en servidor red EMOV |
| Subscriber / servicio | Python + pywin32 (Servicio Windows) |
| Base de datos eventos | SQLite (eventos.db) |
| Notificaciones email | smtplib / SMTP corporativo |
| Integración con FACRET | Lee SQLite directamente (no suscribe MQTT) |
| Lenguaje | Python >= 3.11 |
| Gestión dependencias | Poetry |

---

## ARQUITECTURA

```
┌─────────────────────────────────────────────────────────────────┐
│  PUBLISHERS                                                     │
│                                                                 │
│  [monitor_externo.py]          [monitor_interno.py]             │
│  VPS/AWS (fuera de red EMOV)   Servidor red interna EMOV        │
│  · ping IPs públicas           · ping IPs privadas (RDD)        │
│  · enlaces IO*                 · enlaces RDD*                   │
│                                                                 │
│  Topic: enlaces/{cod_serv}/estado                               │
│  Payload: {"op": "DOWN"|"UP", "ts": "ISO-8601", "cod": "IO..."}│
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  BROKER — Mosquitto (VPS externo)                               │
│  Solo retransmite. No genera datos.                             │
│  Puerto: 1883 (o 8883 con TLS)                                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
               ┌───────────────┴────────────────┐
               │                                │
               ▼                                ▼
┌──────────────────────────┐     ┌──────────────────────────────┐
│  monitor_service.py      │     │  FACRET (app escritorio)     │
│  Servicio Windows        │     │  Lee SQLite — NO suscribe    │
│  (subscriber principal)  │     │  Muestra historial y UP/DOWN │
│                          │     │  en el dashboard de contratos│
│  Al recibir DOWN:        │     └──────────────────────────────┘
│  · INSERT en SQLite      │
│  · Actualiza JSON        │              ▼
│  · Inicia timer 15 min   │     ┌──────────────────────────────┐
│                          │     │  eventos.db (SQLite)         │
│  Si DOWN > 15 min:       │     │  tabla: eventos_enlace       │
│  · Envía email a ETAPA   │────►│  · id, cod_serv              │
│  · Notifica Discord      │     │  · ts_inicio, ts_fin         │
│                          │     │  · duracion_min              │
│  Al recibir UP:          │     │  · notificado (bool)         │
│  · Cierra evento SQLite  │     └──────────────────────────────┘
│  · Actualiza JSON a UP   │
└──────────────────────────┘
```

---

## ESTRUCTURA DE CARPETAS DEL PROYECTO

```
mqtt-monitor/
├── pyproject.toml
├── README.md
├── config/
│   └── services.json          # lista de servicios a monitorear (cod_serv + ip)
├── monitor_externo.py         # publisher — corre en VPS externo
├── monitor_interno.py         # publisher — corre en servidor interno EMOV
├── monitor_service.py         # subscriber + Windows Service
├── db/
│   ├── schema.sql             # CREATE TABLE eventos_enlace
│   └── db_manager.py         # funciones INSERT/SELECT/UPDATE sobre SQLite
├── notifier/
│   ├── email_sender.py        # envío de correo vía SMTP
│   └── discord_sender.py      # webhook Discord (opcional)
└── data/
    └── eventos.db             # base de datos SQLite generada en runtime
```

---

## MODELO DE DATOS (SQLite)

```sql
CREATE TABLE eventos_enlace (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    cod_serv     TEXT NOT NULL,          -- "IO247969", "RDD01973"
    ts_inicio    TEXT NOT NULL,          -- ISO-8601 cuando detectó DOWN
    ts_fin       TEXT,                   -- ISO-8601 cuando detectó UP (NULL si sigue DOWN)
    duracion_min REAL,                   -- calculado al cerrar el evento
    notificado   INTEGER DEFAULT 0,      -- 1 si ya se envió email a ETAPA
    origen       TEXT DEFAULT 'externo'  -- "externo" | "interno"
);

CREATE INDEX idx_cod_serv ON eventos_enlace(cod_serv);
CREATE INDEX idx_ts_inicio ON eventos_enlace(ts_inicio);
```

---

## FORMATO DE MENSAJES MQTT

**Topic:** `enlaces/{cod_serv}/estado`

**Payload DOWN:**
```json
{
  "op": "DOWN",
  "cod": "IO247969",
  "ts": "2025-04-07T14:32:00",
  "origen": "externo"
}
```

**Payload UP:**
```json
{
  "op": "UP",
  "cod": "IO247969",
  "ts": "2025-04-07T14:47:30",
  "origen": "externo"
}
```

---

## LÓGICA DEL PUBLISHER (monitor_externo.py / monitor_interno.py)

```python
# Pseudocódigo — lógica principal del agente publisher
import subprocess, json, time
import paho.mqtt.client as mqtt

BROKER = "vps.dominio.com"
SERVICES = cargar_services_json()   # lista de {cod_serv, ip}
estados = {}                        # estado anterior por servicio

while True:
    for svc in SERVICES:
        up = ping(svc["ip"])        # True / False
        nuevo_estado = "UP" if up else "DOWN"

        if estados.get(svc["cod_serv"]) != nuevo_estado:
            # solo publica cuando HAY UN CAMBIO — no cada ciclo
            payload = {"op": nuevo_estado, "cod": svc["cod_serv"],
                       "ts": ahora_iso(), "origen": ORIGEN}
            mqtt_client.publish(f"enlaces/{svc['cod_serv']}/estado",
                                json.dumps(payload))
            estados[svc["cod_serv"]] = nuevo_estado

    time.sleep(30)   # intervalo de chequeo
```

> **Clave:** el publisher solo publica cuando el estado **cambia** (de UP a DOWN o
> viceversa). No publica cada ciclo. Esto minimiza el tráfico MQTT.

---

## LÓGICA DEL SUBSCRIBER (monitor_service.py)

```python
# Pseudocódigo — lógica principal del servicio subscriber
import json, threading
import paho.mqtt.client as mqtt
from db.db_manager import abrir_evento, cerrar_evento, marcar_notificado
from notifier.email_sender import enviar_alerta_etapa

timers = {}   # timers activos por cod_serv (para el umbral de 15 min)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    cod  = data["cod"]
    op   = data["op"]

    if op == "DOWN":
        abrir_evento(cod, data["ts"], data["origen"])
        # inicia timer: si sigue DOWN en 15 min → notifica
        t = threading.Timer(15 * 60, notificar_si_sigue_down, args=[cod])
        t.start()
        timers[cod] = t

    elif op == "UP":
        if cod in timers:
            timers[cod].cancel()    # cancela el timer — se recuperó a tiempo
            del timers[cod]
        cerrar_evento(cod, data["ts"])

def notificar_si_sigue_down(cod: str):
    # solo notifica si el evento sigue abierto (ts_fin IS NULL)
    if evento_sigue_abierto(cod):
        enviar_alerta_etapa(cod)
        marcar_notificado(cod)

mqtt_client.subscribe("enlaces/+/estado")   # suscribe a todos los servicios
mqtt_client.on_message = on_message
mqtt_client.loop_forever()
```

---

## INTEGRACIÓN CON FACRET

La app de escritorio FACRET **no se conecta a MQTT**. Solo lee la base de datos SQLite:

```python
# En contracts_page.py — historial de eventos de un servicio seleccionado
from db.db_manager import get_eventos_por_servicio

eventos = get_eventos_por_servicio(cod_serv)
# muestra en el panel de detalle: fecha, duración, estado
```

El JSON del contrato también es actualizado por el servicio Windows, de modo que
cuando FACRET carga la página, el `estado_operativo` ya refleja la realidad.

---

## PLAN DE IMPLEMENTACIÓN (en orden)

1. **`config/services.json`** — lista de servicios con cod_serv + ip a monitorear
2. **`db/schema.sql` + `db/db_manager.py`** — base de datos SQLite y funciones CRUD
3. **`monitor_externo.py`** — publisher para IPs públicas (corre en VPS)
4. **`monitor_interno.py`** — publisher para IPs privadas/RDD (corre en servidor EMOV)
5. **Mosquitto** — instalación y configuración en VPS
6. **`notifier/email_sender.py`** — envío SMTP cuando DOWN > 15 min
7. **`monitor_service.py`** — subscriber completo con timers y lógica de notificación
8. **Instalar como Servicio Windows** con `pywin32`
9. **Integrar lectura SQLite en FACRET** — historial en panel de detalle

---

## REFERENCIA

- Proyecto FACRET (app desktop): `facret/FLET_BASE_PROMPT.md`
- Diseño del módulo de contratos: `facret/CONTRACTS_DESIGN.md`
- Documentación completa del sistema: `facret/README.md`
