# FASE 0: Estructura Metamórfica de Servicios

**Fecha:** 2026-11-10  
**Estado:** EN DEFINICIÓN  
**Objetivo:** Diseñar una BD flexible que soporte cambios de tipo de servicio sin perder histórico

---

## 🎯 Problema que resolvemos

**Hoy:** Respetas el inventario del proveedor tal cual:
```
COD.SERV | UBICACION | TIPO | BANDW | V.SERVICIO | F.I.S | F.F.S
I0247963 | CAPULISPAMBA | INTERNET | 25 MBPS | 45 | 2026-09-07 | 2029-09-06
```

**Mañana:** Un servicio puede cambiar:
- INTERNET → DATOS
- DATOS → INTERNET  
- Servicio A se da de baja (cambia fecha_fin)
- Tarifa cambia (de $45 a $50)

**El reto:** Soportar esos cambios **sin romper histórico de facturación**.

---

## 🏗️ Estructura Propuesta

### Nivel 1: MAESTRO DE SERVICIOS (respeta inventario)

```sql
SERVICIOS
├── cod_serv          [PK] → I0247963, RDD02300, etc.
├── ubicacion         → CAPULISPAMBA, PARADA MALL DEL ALTO, etc.
├── grupo_funcional   → G1, G2, G3, G4, G5
├── fecha_inicio      → 2026-09-07 (cuando inicia el contrato)
├── fecha_fin_planeada → 2029-09-06 (meta, puede cambiar)
├── estado            → ACTIVO, INACTIVO, CANCELADO
└── notas             → Información adicional
```

### Nivel 2: TIPOS DE SERVICIO (auditoría de cambios)

```sql
SERVICIO_TIPOS_HISTORICO
├── id                      [PK]
├── cod_serv                [FK] → I0247963
├── tipo_servicio           → INTERNET, DATOS, HOUSING
├── bandwidth               → 25 MBPS (snapshot del momento)
├── valor_servicio          → 45 (snapshot del momento)
├── fecha_vigencia_desde    → 2026-09-07
├── fecha_vigencia_hasta    → NULL (aún vigente) O fecha futura
├── fecha_cambio            → Cuándo se registró este cambio
├── usuario_cambio          → Quién lo cambió (auditoría)
└── motivo_cambio           → Por qué (cambio tarifa, migración, etc.)
```

**Ejemplo de metamorfosis:**
```
cod_serv: I0276542
  v1: 2026-09-07 a 2026-12-31 → INTERNET 25 MBPS, $45
  v2: 2027-01-01 a 2027-06-30 → DATOS 10 MBPS, $50 (cambio de tipo)
  v3: 2027-07-01 a NULL        → INTERNET 70 MBPS, $75 (vuelve a INTERNET)
```

### Nivel 3: CATÁLOGO DE TARIFAS

```sql
TARIFAS
├── tarifa_id                [PK] → TAR_001, TAR_002, etc.
├── nombre                   → "Internet 25 MBPS Estándar"
├── tipo_servicio            → INTERNET, DATOS, HOUSING
├── bandwidth                → 25 MBPS
├── valor_consumo_mensual    → 45
├── valor_instalacion        → (puede ser 0 para algunos tipos)
├── vigencia_desde           → 2026-09-07
└── vigencia_hasta           → NULL (vigente) O fecha futura
```

### Nivel 4: FACTURACIÓN MENSUAL (resultado del cálculo)

```sql
FACTURACION_MENSUAL
├── id                       [PK]
├── cod_serv                 [FK] → I0247963
├── año_mes                  → 202609 (septiembre 2026)
├── tipo_servicio_vigente    → INTERNET (snapshot del mes)
├── dias_facturables         → 24 (si fue mes parcial)
├── valor_consumo            → 36 (prorrateo: 45 × 24/30)
├── valor_instalacion        → 4 (prorrateo: 5 × 24/30)
├── total                    → 40
├── referencia_factura_xml   → FAC065528610_001.xml
├── fecha_calculo            → 2026-10-15 (cuándo se calculó)
└── estado                   → CALCULADO, VERIFICADO, PAGADO
```

---

## 🔄 Flujo de Datos

### Caso 1: Servicio estable (sin cambios)

```
INVENTARIO (proveedor)
    ↓
SERVICIOS + SERVICIO_TIPOS_HISTORICO (v1)
    ↓
TARIFAS (TAR_001: INTERNET 25 MBPS, $45)
    ↓
FACTURACION_MENSUAL (calcular cada mes con tarifa vigente)
    ↓
REPORTES (generar informe de pago)
```

### Caso 2: Servicio con metamorfosis

```
Octubre: I0276542 es INTERNET 25 MBPS
    ↓
Noviembre: "Carlos: cambiar a DATOS 10 MBPS"
    ↓
SERVICIO_TIPOS_HISTORICO
    v1: INTERNET 25 MBPS (sep-oct)
    v2: DATOS 10 MBPS (nov en adelante)
    ↓
FACTURACION_MENSUAL
    Octubre:  INTERNET, $45
    Noviembre: DATOS, $50 (nueva tarifa)
    ↓
REPORTES: Histórico completo, auditable
```

---

## 📋 Tipos de Servicios Identificados

Del inventario, tienes 3 tipos base:

### 1. INTERNET (Un extremo, pool de IPs públicas)
- Ejemplos: I0247963 (25 MBPS), I0277070 (70 MBPS)
- Tarificación: Consumo mensual + Instalación (típicamente)
- Cambio posible: → DATOS

### 2. DATOS (Extremo A y B, sin IP pública)
- Ejemplos: RDD02300 (50 MBPS), RDD02301 (2 MBPS)
- Tarificación: Consumo mensual + Instalación
- Cambio posible: → INTERNET

### 3. HOUSING (Alquiler de espacio en rack)
- Ejemplos: HOU00013
- Tarificación: Solo alquiler mensual (NO instalación)
- Cambio posible: Raro, pero soportado

---

## ✅ Ventajas de esta estructura

1. **Respeta inventario del proveedor** (exactamente como llega)
2. **Soporta metamorfosis** (servicio cambia tipo sin perder historia)
3. **Auditable** (quién cambió qué, cuándo y por qué)
4. **Flexible en tarificación** (cada tipo puede tener estructuras diferentes)
5. **Cálculo de costos preciso** (prorrateo correcto en cambios)
6. **Histórico completo** (para reportes y auditoría)
7. **Fácil de consultar** (por mes, por grupo, por tipo)

---

## 🚀 Próximos pasos

1. **Definir qué herramienta:** SQL (PostgreSQL) o NoSQL (MongoDB)
2. **Crear scripts SQL** para crear tablas
3. **Implementar lógica de prorrateo** (30 días comerciales)
4. **Cargar datos iniciales** desde Excel y facturas XML
5. **Crear reportes** para alimentar tu plantilla Word
6. **Luego:** FASE 1 (Presupuesto Versionado) se construye sobre esto

---

## 📊 Matriz de decisión

| Aspecto | Opción |
|---------|--------|
| **BD** | SQL (PostgreSQL) - relaciones claras, auditoría fácil |
| **Prorrateo** | Siempre 30 días (como acordaste) |
| **Cambios** | Registrar en SERVICIO_TIPOS_HISTORICO con fecha y usuario |
| **Facturación** | Mensual, con snapshot de tipo/tarifa vigente |
| **Auditoría** | Columnas: usuario_cambio, fecha_cambio, motivo_cambio |

---

## 📝 Preguntas para cerrar FASE 0

1. ¿SQL o NoSQL? (recomiendo SQL por relaciones y auditoría)
2. ¿Dónde guardar la BD? (PostgreSQL local vs. cloud)
3. ¿Quién puede hacer cambios?** (solo tú, o más usuarios)
4. ¿Retención de datos:** (cuánto tiempo guardar histórico)
5. ¿Integración con facturas:** (automática o manual)

