# FASE 1 Presupuesto Versionado: Definición Conceptual

**Fecha:** 2026-11-04  
**Estado:** EN DEFINICIÓN — Esperando respuestas a preguntas A-F  
**Documento oficial:** Esta es la especificación de FASE 1 para implementación

---

## 🎯 Objetivo

Implementar un **Presupuesto Versionado** que:
1. Permita cambios sin recalcular manualmente 100+ servicios
2. Registre cada cambio (quién, cuándo, por qué)
3. Preserve histórico completo de versiones (v1.0, v1.1, v1.2, etc.)
4. Calcule automáticamente presupuesto mes a mes, considerando:
   - Servicios nuevos con instalación (prorrateo si inicia a mitad de mes)
   - Servicios antiguos sin instalación
   - Cambios de tarifa durante la vigencia
   - Base de 30 días comerciales (siempre)

---

## 📊 Estructura del Excel (PREGUNTA 1 — RESPONDIDA)

### Columnas Identificadas

```
Nro | GRUPO | COD_SERV | UBICACION | TIPO | UPBANDWIDTH | V_SERVICIO | 
P01-SEP | P01-INST | P02 | P02-INST | P03 | ... | TOTAL
```

### Dos Conceptos por Mes

- **P01-SEP**, **P02**, **P03**... = **Consumo del servicio** (tarifa mensual)
- **P01-INST**, **P02-INST**, **P03-INST**... = **Cargo de instalación** (único, solo servicios nuevos)

### Realidad Operativa (Octubre 2026)

- **Total servicios:** 99
- **Servicios nuevos desde 02/10:** 10 (con instalación)
- **Inventario del contratista:** AÚN SIN RECIBIR

---

## 🏗️ Modelo de Datos Propuesto

### ENTIDAD 1: TARIFA (catálogo reutilizable)

```json
{
  "tarifas": [
    {
      "id": "TAR_001",
      "nombre": "Internet 25 MBPS Estándar",
      "tipo": "INTERNET",
      "bandwidth": "25 MBPS",
      "v_consumo_mensual": 36000.00,
      "v_instalacion": 5000.00,
      "vigencia_desde": "2026-09-07",
      "vigencia_hasta": "2029-09-06"
    },
    {
      "id": "TAR_002",
      "nombre": "Datos 2 MBPS",
      "tipo": "DATOS",
      "bandwidth": "2 MBPS",
      "v_consumo_mensual": 45.00,
      "v_instalacion": 3000.00,
      "vigencia_desde": "2026-09-07",
      "vigencia_hasta": "2029-09-06"
    }
  ]
}
```

### ENTIDAD 2: SERVICIO (referencia a tarifa)

```json
{
  "servicios": [
    {
      "id": "S001",
      "cod_serv": "I0247963",
      "ubicacion": "CAPULISPAMBA",
      "grupo": "G1",
      "tarifa_id": "TAR_001",  // ← Reutiliza tarifa existente
      "fecha_inicio": "2026-09-08",
      "fecha_fin": "2029-09-06",
      "es_nuevo": true,
      "observacion": "Activado 08/09/2026"
    }
  ]
}
```

**Relación:** Un servicio **apunta a una tarifa** via `tarifa_id`. La instalación es propiedad de la TARIFA, no del servicio.

---

## 📐 Cálculo Prorrateado (PREGUNTA B — RESPONDIDA)

### Base: 30 días comerciales (SIEMPRE)

Incluso febrero con 28 días reales se cuenta como 30 para cálculo.

### Ejemplo: Servicio que inicia 16/10/2026

```
Octubre 2026:
- Días vigentes: 31 - 16 + 1 = 16 días
- Fracción: 16 / 30 = 0.5333
- Consumo: $36,000 × 0.5333 = $19,200
- Instalación: $5,000 × 0.5333 = $2,667  ← Prorrateada también
- TOTAL octubre: $21,867

Noviembre 2026 en adelante:
- Consumo: $36,000 (mes completo)
- Instalación: $0 (ya se cobró)
```

---

## 👤 Servicio Nuevo vs Antiguo

### Flujo Operativo

1. **Carlos recibe del coordinador:** "Estos 5 servicios son nuevos en octubre"
2. **Carlos marca en el sistema:** `es_nuevo: true` + `fecha_inicio: 2026-10-02`
3. **Sistema aplica automáticamente:**
   - Mes de inicio (octubre): consumo + instalación (prorrateado)
   - Meses siguientes: solo consumo
4. **Próxima actualización:** "Otros 3 servicios nuevos en noviembre"
   - Sistema genera **v1.1** automáticamente
   - Recalcula TODO con los nuevos servicios

### Nota Crítica

**NO hay forma automática de identificar servicios nuevos en XMLs** → Se indica manualmente basado en info del coordinador de cuenta.

---

## ❓ Preguntas Críticas Pendientes

### A. ¿Cada tarifa tiene `v_consumo_mensual` Y `v_instalacion` separados?

O ¿la instalación es por servicio individual?

**Implicaciones:**
- Si es por tarifa: más reutilizable, más sencillo
- Si es por servicio: más flexible, pero más data

### B. ¿La instalación es SIEMPRE el mismo valor para una tarifa?

O ¿algunos servicios de la misma tarifa tienen diferentes montos de instalación?

**Implicaciones:**
- Si es por tarifa: simplifica el modelo
- Si es por servicio: agrega campo `v_instalacion` a servicio

### C. ¿En el Excel actual hay columna que identifique "usa tarifa X"?

O ¿hay que mapearla manualmente (INTERNET 25 MBPS → TAR_001)?

**Implicaciones:**
- Si existe mapeo: lectura fácil del Excel
- Si no: requiere un paso de clasificación

### D. De los 10 servicios nuevos (02/10), ¿ya están en el Excel actual?

O ¿falta agregarlos?

### E. Cuando llegue el inventario del contratista, ¿esperas MÁS servicios nuevos?

¿Cuántos aprox?

### F. ¿Para FASE 1, comenzamos con 99 servicios o esperamos inventario completo?

**Implicaciones de timing:**
- Si 99: podemos empezar inmediatamente
- Si esperamos: ganamos precisión pero retrasamos

---

## 🚀 Próximos Pasos

1. **Responder preguntas A-F** → Cierra la estructura de datos
2. **Responder preguntas 2-7** del `PREGUNTAS_FASE1_PRESUPUESTO.md` → Cierra operación
3. **Comenzar FASE 1** → Código Python que:
   - Lee tarifas + servicios
   - Calcula mes a mes (prorrateo)
   - Genera JSON v1.0
   - Implementa cambios (tarifa, agregar, eliminar)
   - Crea nuevas versiones automáticamente

---

## 📅 Timeline

- **Apertura:** 2026-11-04
- **Cierre de definición:** 2026-11-04 (esperando respuestas)
- **Inicio FASE 1:** Cuando preguntas A-F estén respondidas

