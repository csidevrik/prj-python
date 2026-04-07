# Diseño — Módulo de Contratos ETAPA

Contexto de recuperación para continuar el diseño del panel de contratos en FACRET.

---

## Qué estamos construyendo

Una página `contracts_page.py` dentro de FACRET para administrar los servicios
contratados con ETAPA EP. Actualmente hay un contrato modelado: `ETAPA-RE1.json`
(22 servicios, 3 grupos). El objetivo es escalar a ~140 servicios en múltiples contratos.

---

## Problema central: modelo de datos plano vs entidades separadas

El JSON actual (`data/contracts/ETAPA-RE1.json`) tiene el campo `agencia` como un
simple string. Pero en realidad hay **tres tipos de servicio distintos** mezclados:

| Código  | sdwan | Tipo real                           | Entidad necesaria        |
| -------- | ----- | ----------------------------------- | ------------------------ |
| `IO*`  | true  | Enlace internet a una agencia       | Agencia (con dirección) |
| `IO*`  | false | Enlace internet simple/contingencia | Agencia o descripción   |
| `RDD*` | false | Enlace de datos punto a punto       | Dos extremos (A y B)     |

Una **Agencia** es una entidad con nombre y dirección propia.
Un **Enlace de datos** (RDD) conecta dos puntos — tiene `extremo_a` y `extremo_b`.
Un **Enlace de internet** (IO) conecta una agencia a internet — tiene un `agencia_id`.

---

## Modelo de datos propuesto

### Archivo 1: `data/agencias.json` (catálogo maestro, compartido entre contratos)

```json
{
  "CAPULISPAMBA": {
    "id": "CAPULISPAMBA",
    "nombre": "Agencia Capulispamba",
    "direccion": "",
    "tipo": "agencia"
  },
  "EMOV-PRINCIPAL": {
    "id": "EMOV-PRINCIPAL",
    "nombre": "EMOV Edificio Principal",
    "direccion": "Av. Gil Ramírez Dávalos",
    "tipo": "sede_central"
  }
}
```

### Archivo 2: `data/contracts/ETAPA-RE1.json` (refactorizado)

Cada servicio agrega `tipo` y reemplaza `agencia` string por referencia:

```json
// Enlace internet a agencia:
{
  "cod_serv": "IO247963",
  "tipo": "internet",
  "agencia_id": "CAPULISPAMBA",
  "bandwidth": "10 MBPS",
  "valor_mensual": 96.10,
  "sdwan": true,
  "estado": "ACTIVE",
  "estado_operativo": "UP",
  "grupo": "G1",
  "dias_servicio": 30,
  "vigencia_meses": 4,
  "fecha_inicio": "2025-03-09",
  "fecha_fin": "2025-06-09",
  "notas": "",
  "eventos": []
}

// Enlace de datos punto a punto:
{
  "cod_serv": "RDD01973",
  "tipo": "datos",
  "extremo_a": "CALAIRE2",
  "extremo_b": "JMONTALVO",
  "bandwidth": "20 MBPS",
  "valor_mensual": 45.00,
  "sdwan": false,
  "estado": "ACTIVE",
  "estado_operativo": "UP",
  "grupo": "G3",
  "dias_servicio": 30,
  "vigencia_meses": 36,
  "fecha_inicio": "2022-09-01",
  "fecha_fin": "2025-09-01",
  "notas": "",
  "eventos": []
}
```

---

## Estructura de archivos para escalar a 140 servicios

```
facret/data/
├── agencias.json                  ← catálogo único compartido
└── contracts/
    ├── ETAPA-RE1.json             ← Régimen Especial 1 (22 servicios, activo)
    ├── ETAPA-RE2.json             ← próximo contrato
    └── ...
```

La página `contracts_page.py` hace glob de `data/contracts/*.json`,
carga todos los contratos, los flattenea en una lista y resuelve
`agencia_id` → datos de `agencias.json` en memoria.

---

## Diseño del panel (lo que se ve en pantalla)

```
┌─────────────────────────────────────────────────────────────────┐
│  [+ Agregar]                                                    │
│                                                                 │
│  Nro │ Estado │ Grupo │ COD_SERV │ Bandwidth │ Agencia │ Valor  │
│  ... │  ...   │  ...  │   ...    │    ...    │   ...   │  ...   │
│  (tabla plana — todos los servicios de todos los contratos)     │
└─────────────────────────────────────────────────────────────────┘
                    ↓ al seleccionar una fila
┌─────────────────────────────────────────────────────────────────┐
│  [view selected detail]                                         │
│                                                                 │
│  Si tipo == "internet":                                         │
│    Ficha Agencia: nombre, dirección, otros enlaces en la misma  │
│    Ficha Servicio: código, bandwidth, valor, fechas, estado     │
│                                                                 │
│  Si tipo == "datos":                                            │
│    Extremo A: nombre/descripción                                │
│    Extremo B: nombre/descripción                                │
│    Ficha Servicio: código, bandwidth, valor, fechas, estado     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Plan de implementación (en orden)

1. ~~**Refactorizar `ETAPA-RE1.json`**~~ ✅ — campo `tipo` agregado, `agencia` string
   reemplazado por `agencia_id` (internet) o `extremo_a`/`extremo_b` (datos)
2. ~~**Crear `data/agencias.json`**~~ ✅ — 22 entidades (agencias, sedes, datacenter,
   nodos proveedor, externos); RDD02235 extremos: EMOV-MISICATA ↔ ETAPA-CEBOLLAR
3. ~~**Dataclasses en `src/models/models.py`**~~ ✅ — `Agencia`, `Evento`,
   `EnlaceInternet`, `EnlaceDatos`, `GrupoServicios`, `Contrato`;
   `Contrato.servicios_flat()` devuelve lista plana de todos los servicios
4. ~~**Crear `src/logic/contracts_loader.py`**~~ ✅ — `load_agencias()`, `load_contratos()`,
   `load_servicios_flat()`; resuelve agencias en memoria al parsear cada servicio
5. ~~**Crear `src/pages/contracts_page.py`**~~ ✅ — toolbar (search + Agregar/Editar/Eliminar),
   tabla con filtro en tiempo real, detalle a la derecha (split layout);
   diálogo de edición con campos de solo lectura (contrato) + editables (estado_operativo,
   ip_publica, notas) + sección para registrar eventos; confirmación antes de eliminar
   **`src/logic/contracts_writer.py`** ✅ — `update_servicio()` y `add_evento()`;
   busca el archivo .json por cod_serv y escribe solo los campos editables
6. ~~**Registrar en `menu_config.py`**~~ ✅ — key `"contracts"`, label "Contratos ETAPA",
   icono `RECEIPT_LONG_OUTLINED`

---

## Estado actual del JSON (antes de refactorizar)

El archivo `data/contracts/ETAPA-RE1.json` existe y tiene:

- Contrato: `ETAPA-RE1`, proveedor ETAPA EP, 2022-09-01 a 2025-09-01, 36 meses
- G1 (14 servicios): IO*, sdwan=true, 5/10 MBPS, agencias de campo
- G2 (4 servicios): IO*, mix sdwan, edificio principal + contingencia + data center
- G3 (5 servicios): RDD*, sdwan=false, 2/20 MBPS, uno CANCELED
- Total mensual: 3754.09 USD

---

## Visión de monitoreo en tiempo real (roadmap)

Arquitectura planeada para que `estado_operativo` se actualice solo, sin edición manual:

- **Agente externo** (servidor cloud): ping a IPs públicas → publica en MQTT
- **Agente interno** (servidor red EMOV): ping a IPs privadas → publica en MQTT
- **Cliente MQTT en FACRET**: suscrito a topics por servicio → actualiza JSON + crea evento
- **Umbral 15 min DOWN** → envío automático de email a ETAPA EP
- **Estadísticas acumuladas** → uptime real por servicio → insumo para renegociación de contratos

Topic MQTT propuesto: `enlaces/{cod_serv}/estado`
Payload: `{"op": "DOWN"|"UP", "ts": "ISO-timestamp"}`

Ver sección completa en `README.md` → "Visión: Monitoreo en tiempo real".

**Corrección de datos aplicada:** RDD01972 (CANCELED) tenía `estado_operativo: "UP"` — 
corregido a `"DOWN"` (un servicio cancelado no puede estar operativo).

---

## Referencia de arquitectura UI

Ver `facret/FLET_BASE_PROMPT.md` para patrones de páginas, router, temas y componentes.




> "Lee `facret/CONTRACTS_DESIGN.md` y `facret/FLET_BASE_PROMPT.md` y retomamos el módulo de contratos ETAPA"
>
