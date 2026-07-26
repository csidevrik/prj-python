# 🎨 Diseño — Módulo de Contratos ETAPA

Arquitectura y modelo de datos del módulo de gestión de contratos y servicios.

---

## 📋 Contexto

FACRET incluye un módulo completo para administrar los servicios contratados con **ETAPA EP**. Actualmente administra un contrato (`ETAPA-RE1.json`) con 22 servicios organizados en 3 grupos.

El diseño escala a ~140 servicios en múltiples contratos.

---

## 🏛️ Modelo de Datos

### Concepto: 3 Tipos de Servicios

| Tipo | Código | Descripción | Entidad |
|------|--------|-------------|---------|
| **Internet** | `IO*` | Enlace a internet de una agencia | `Agencia` (referencia) |
| **Internet Contingencia** | `IO*` | Contingencia/backup a internet | Descripción string |
| **Datos** | `RDD*` | Enlace punto a punto entre dos ubicaciones | `Extremo A` ↔ `Extremo B` |

### Catálogo de Agencias (`data/agencias.json`)

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
  },
  ...
}
```

**Propósito:** Catálogo único compartido entre contratos. Si un servicio es tipo "internet", resuelve `agencia_id` aquí.

---

### Contrato (`data/contracts/ETAPA-RE1.json`)

Estructura de servicios:

```json
{
  "id": "ETAPA-RE1",
  "proveedor": "ETAPA EP",
  "vigencia_inicio": "2022-09-01",
  "vigencia_fin": "2025-09-01",
  "meses_vigencia": 36,
  "valor_mensual_total": 3754.09,
  "servicios": [
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
    },
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
      ...
    },
    ...
  ]
}
```

---

## 🏗️ Dataclasses (`src/models/models.py`)

Estructura Python de los datos:

```python
@dataclass
class Agencia:
    id: str
    nombre: str
    direccion: str = ""
    tipo: str = "agencia"

@dataclass
class Evento:
    fecha: str          # ISO timestamp
    tipo: str           # "CAMBIO_ESTADO", "CAMBIO_OPERATIVO", etc.
    valor_anterior: str
    valor_nuevo: str
    nota: str = ""

@dataclass
class EnlaceInternet:
    cod_serv: str
    agencia_id: str     # Referencia a agencias.json
    bandwidth: str
    valor_mensual: float
    sdwan: bool = False
    estado: str = "ACTIVE"
    estado_operativo: str = "UP"
    grupo: str = "G1"
    dias_servicio: int = 30
    vigencia_meses: int = 36
    fecha_inicio: str = ""
    fecha_fin: str = ""
    notas: str = ""
    eventos: list[Evento] = None

@dataclass
class EnlaceDatos:
    cod_serv: str
    extremo_a: str      # Ubicación A
    extremo_b: str      # Ubicación B
    bandwidth: str
    valor_mensual: float
    sdwan: bool = False
    estado: str = "ACTIVE"
    estado_operativo: str = "UP"
    grupo: str = "G1"
    dias_servicio: int = 30
    vigencia_meses: int = 36
    fecha_inicio: str = ""
    fecha_fin: str = ""
    notas: str = ""
    eventos: list[Evento] = None

@dataclass
class GrupoServicios:
    id: str
    servicios: list[EnlaceInternet | EnlaceDatos]

@dataclass
class Contrato:
    id: str
    proveedor: str
    vigencia_inicio: str
    vigencia_fin: str
    grupos: list[GrupoServicios]
    
    def servicios_flat(self) -> list:
        """Retorna todos los servicios en una lista plana"""
        return [s for g in self.grupos for s in g.servicios]
```

---

## 📂 Estructura de Archivos

```
facret/data/
├── agencias.json                  ← Catálogo único (22 agencias)
└── contracts/
    ├── ETAPA-RE1.json             ← Régimen Especial 1 (22 servicios, ACTIVO)
    ├── ETAPA-RE2.json             ← Próximo contrato (futuro)
    └── ...
```

---

## 🔄 Flujos Clave

### Flujo 1: Cargar Contratos

```
main.py → gui.py
  ↓
pages/contracts_page.py.__init__()
  ↓
logic.contracts_loader.load_contratos()
  ├─ Carga agencias.json en memoria
  ├─ Glob de contracts/*.json
  ├─ Para cada servicio, resuelve agencia_id → Agencia
  └─ Retorna lista plana de servicios

→ Tabla en UI actualizada
```

**Código:**
```python
# src/logic/contracts_loader.py
def load_contratos():
    agencias = load_agencias()  # En memoria
    contratos = []
    
    for path in sorted(_CONTRACTS_DIR.glob("*.json")):
        with open(path) as f:
            data = json.load(f)
        
        # Procesar servicios, resolviendo referencias
        servicios = []
        for s in data["servicios"]:
            if s["tipo"] == "internet":
                agencia = agencias[s["agencia_id"]]
                # Crear EnlaceInternet
            elif s["tipo"] == "datos":
                # Crear EnlaceDatos
            servicios.append(...)
        
        contratos.append(...)
    
    return contratos
```

---

### Flujo 2: Editar Servicio

```
User selecciona fila en tabla
  ↓
Aparece diálogo con campos editables:
├─ estado_operativo (dropdown: UP/DOWN)
├─ notas (texto libre)
└─ [botón Guardar]

User hace clic "Guardar"
  ↓
logic.contracts_writer.update_servicio()
├─ Encuentra archivo .json por cod_serv
├─ Actualiza solo campos editables
├─ Agrega evento al historial
└─ Guarda archivo

→ Tabla actualizada
```

**Código:**
```python
# src/logic/contracts_writer.py
def update_servicio(cod_serv, estado_operativo, notas):
    # 1. Encontrar qué archivo contiene este cod_serv
    for path in _CONTRACTS_DIR.glob("*.json"):
        with open(path) as f:
            data = json.load(f)
        
        for servicio in data["servicios"]:
            if servicio["cod_serv"] == cod_serv:
                # 2. Actualizar campos
                servicio["estado_operativo"] = estado_operativo
                servicio["notas"] = notas
                
                # 3. Agregar evento
                servicio["eventos"].append({
                    "fecha": datetime.now().isoformat(),
                    "tipo": "CAMBIO_OPERATIVO",
                    "valor_anterior": "UP",  # ← capturado antes
                    "valor_nuevo": estado_operativo,
                    "nota": "Actualización manual"
                })
                
                # 4. Guardar
                with open(path, "w") as f:
                    json.dump(data, f, indent=2)
                return True
    
    return False
```

---

### Flujo 3: Monitoreo en Tiempo Real (Roadmap)

```
External Monitoring
  ↓
MQTT Topic: enlaces/{cod_serv}/estado
  ├─ Payload: {"op": "DOWN"|"UP", "ts": "ISO-timestamp"}
  ↓
FACRET subscribed to topics
  ↓
MQTT Callback
  ├─ Parsea payload
  ├─ Llama update_servicio(cod_serv, estado_operativo="UP"|"DOWN")
  ├─ Crea evento automático
  └─ Actualiza UI
  ↓
Si DOWN por > 15 min:
  ├─ Envía email a ETAPA EP
  └─ Registra en log crítico
```

Ver [docs/ROADMAP/mqtt-monitoring.md](ROADMAP/mqtt-monitoring.md) para detalles.

---

## 🎯 Panel UI (`src/pages/contracts_page.py`)

### Estructura

```
┌─────────────────────────────────────────────────────────┐
│  [+ Agregar]  [Editar]  [Eliminar]  [🔍 Búsqueda...]  │
├─────────────────────────────────────────────────────────┤
│  Nro │ Estado │ Grupo │ COD │ BW │ Agencia/Extremo │ $ │
│  1   │ ACTIVO │ G1    │ IO* │ 10 │ CAPULISPAMBA    │99 │
│  2   │ ACTIVO │ G1    │ IO* │ 10 │ CALAIRE2        │96 │
│  ...                                                    │
│  (tabla plana — todos los servicios)                   │
└─────────────────────────────────────────────────────────┘
           ↓ al seleccionar
┌─────────────────────────────────────────────────────────┐
│  FICHA DETALLADA                                        │
│                                                         │
│  Código: IO247963     Contrato: ETAPA-RE1              │
│  Tipo: Internet       Agencia: CAPULISPAMBA            │
│  Estado: ACTIVO       Op: UP                           │
│  BW: 10 MBPS          Valor: $96.10                    │
│  Vigencia: 2022-09-01 a 2025-09-01 (36 meses)          │
│  Notas: ___________________________                     │
│  [Editar]  [Eliminar]  [Ver Historial]                │
└─────────────────────────────────────────────────────────┘
```

### Características

- ✅ **Búsqueda en tiempo real** — filtra por cod_serv, agencia, estado
- ✅ **Tabla sorteable** — hacer clic en columnas para ordenar
- ✅ **Diálogo de edición** — campos editables + historial de eventos
- ✅ **Confirmación de eliminación** — evita borrados accidentales
- ✅ **Historial de eventos** — quién cambió qué y cuándo

---

## 📊 Estadísticas Actualmente Rastreadas

Por contrato:
- Valor mensual total
- Número de servicios por estado (ACTIVE, CANCELED)
- Número de servicios por grupo (G1, G2, G3)
- Uptime promedio (cuando MQTT esté implementado)

---

## 🔜 Próximas Mejoras

1. **MQTT Monitoring** — actualización automática de `estado_operativo`
2. **Alertas** — email automático si servicio DOWN > 15 min
3. **SQLite** — historial persistente con búsqueda avanzada
4. **Reportes** — exportar a CSV/PDF con estadísticas

---

**Última actualización:** 26 de Julio 2026
