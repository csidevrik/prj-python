# Plan de Implementación: Presupuesto Dinámico (Que Muta Sin Destruirse)

**Objetivo Real:** No es calcular presupuestos una vez. Es tener un **presupuesto que cambia constantemente** sin que mantenimiento manual te mate.

**El Problema:** 
- Hoy cambias 1 tarifa en el Excel → tienes que recalcular 100+ servicios manualmente
- Mañana agregan un servicio → más cálculos manuales
- Pasado: cambio de período → todo se recomputa
- **Resultado:** Excel se vuelve imposible de mantener a escala

**La Solución:**
Un presupuesto es una **entidad con versiones**:
- **v1.0** (Presupuesto inicial Sep 2026)
- **v1.1** (Se agrega servicio en Oct)
- **v1.2** (Se cambia tarifa en Nov)
- **v2.0** (Se inicia ETAPA-RE2 con cambios masivos)

Cada versión:
- ✅ Recalcula automáticamente
- ✅ Preserva histórico de cambios
- ✅ Es auditable (qué cambió, cuándo, por qué)
- ✅ NO requiere tocar Excel manualmente

**Estrategia:** Descomponer en 3 fases independientes. Completar una antes de pasar a la siguiente.

---

## FASE 1: Presupuesto Versionado (Que Muta Sin Romperse)

**Qué es:** Un presupuesto que **cambia sin que tengas que recalcular manualmente**.

**Escenario real:**
```
Sep 2026: Creas PRESUPUESTO v1.0
  - 50 servicios con tarifa inicial
  - Total: $50,000

Oct 2026: Te enteras que se agregaron 5 servicios nuevos
  - Editas: +5 servicios nuevos
  - Sistema genera v1.1 automáticamente
  - Nuevo total: $50,500 (recalculado sin tocar Excel)

Nov 2026: ETAPA EP informa que hay un upgrade de ancho de banda
  - Editas: servicio X cambia de $100 → $150
  - Sistema genera v1.2 automáticamente
  - Nuevo total: $50,650 (recalculado)
  - Auditoría: "¿Qué cambió?" → "Servicio X: $100→$150 el 15/11"

Dic 2026: Cliente pide reducción de servicios
  - Editas: elimina 3 servicios
  - Sistema genera v1.3 automáticamente
  - Nuevo total: $49,950 (recalculado)

Ahora tienes:
✅ Presupuesto v1.0 (histórico: cuál era el original)
✅ Presupuesto v1.1 (qué pasó en Oct)
✅ Presupuesto v1.2 (qué pasó en Nov)
✅ Presupuesto v1.3 (estado actual)
✅ Auditoría: cada cambio registrado con fecha y razón
```

**El problema que resuelve:**
- ❌ Antes: Cambiar 1 parámetro = recalcular todo el Excel manualmente
- ✅ Ahora: Cambiar 1 parámetro = sistema recalcula automáticamente, genera nueva versión, audita cambio

### Estructura: Presupuesto Versionado (JSON)

```json
{
  "presupuesto_id": "PRESUPUESTO_ETAPA_RE1_2026",
  "versiones": [
    {
      "numero_version": "v1.0",
      "fecha_creacion": "2026-09-01",
      "estado": "histórico",
      "cambio_realizado": "Presupuesto inicial con 50 servicios",
      "servicios": [
        {
          "servicio_id": "S001",
          "ubicacion": {
            "id": "U001",
            "nombre": "Ricaurte",
            "codigo_inst": "I0276496"
          },
          "periodo": "ETAPA-RE1",
          "fecha_inicio": "2026-09-08",
          "fecha_fin": "2029-09-06",
          "tarifa_vigente": 100.00,
          "total_presupuesto_servicio": 3610.00
        }
        // ... 49 servicios más
      ],
      "total_presupuesto_version": 385000.00
    },
    {
      "numero_version": "v1.1",
      "fecha_creacion": "2026-10-15",
      "estado": "histórico",
      "cambio_realizado": "Agregados 5 nuevos servicios (paradas G5)",
      "servicios": [
        // ... todos los servicios v1.0
        // ... + 5 nuevos servicios
      ],
      "total_presupuesto_version": 387500.00
    },
    {
      "numero_version": "v1.2",
      "fecha_creacion": "2026-11-10",
      "estado": "ACTUAL",  // <-- Este es el que está en vigor
      "cambio_realizado": "Servicio S015 (Radar) cambio de tarifa: 100→150 por upgrade",
      "servicios": [
        // ... todos los servicios con el cambio aplicado
      ],
      "total_presupuesto_version": 390000.00,
      "auditoria": {
        "tipo_cambio": "actualizar_tarifa",
        "servicio_afectado": "S015",
        "cambio_detalle": {
          "tarifa_anterior": 100.00,
          "tarifa_nueva": 150.00,
          "razon": "Upgrade de bandwidth 10→25 MBPS",
          "impacto_total": 3000.00  // 50 meses × $50 extra
        }
      }
    }
  ],
  "total_presupuesto_vigente": 390000.00,
  "historial_cambios": [
    {
      "fecha": "2026-09-01",
      "version": "v1.0",
      "cambio": "Inicial"
    },
    {
      "fecha": "2026-10-15",
      "version": "v1.1",
      "cambio": "Agregados 5 servicios"
    },
    {
      "fecha": "2026-11-10",
      "version": "v1.2",
      "cambio": "Cambio de tarifa en S015"
    }
  ]
}
```
```

### Lógica: Sistema de Versionado con Recálculo Automático

```python
class PresupuestoVersionado:
    """Un presupuesto que muta sin romperse"""
    
    def __init__(self, presupuesto_id, servicios_iniciales):
        self.presupuesto_id = presupuesto_id
        self.versiones = []
        self.version_actual = None
        
        # Crear v1.0 con servicios iniciales
        self.crear_nueva_version(
            numero_version="v1.0",
            cambio_realizado="Presupuesto inicial",
            servicios=servicios_iniciales
        )
    
    def crear_nueva_version(self, numero_version, cambio_realizado, servicios):
        """Genera una NUEVA VERSIÓN del presupuesto recalculando todo"""
        
        # Recalcular TODOS los servicios (esto es automático)
        servicios_calculados = [
            self.calcular_servicio(s) for s in servicios
        ]
        
        # Crear versión nueva
        nueva_version = {
            "numero_version": numero_version,
            "fecha_creacion": datetime.now(),
            "estado": "histórico",  # Por ahora
            "cambio_realizado": cambio_realizado,
            "servicios": servicios_calculados,
            "total_presupuesto": sum(s['total'] for s in servicios_calculados)
        }
        
        # Agregar a histórico
        self.versiones.append(nueva_version)
        
        # Marcar como actual
        if self.version_actual:
            self.version_actual['estado'] = 'histórico'
        self.version_actual = nueva_version
        self.version_actual['estado'] = 'ACTUAL'
        
        return nueva_version
    
    def cambiar_tarifa_servicio(self, servicio_id, nueva_tarifa, razon):
        """OPERACIÓN TÍPICA: cambiar tarifa de 1 servicio
        
        El sistema:
        1. Detecta qué servicio cambió
        2. Recalcula TODO automáticamente
        3. Genera NUEVA VERSIÓN
        4. Audita el cambio
        
        Resultado: No tocaste el Excel, todo se recalculó solo
        """
        
        # Copiar servicios de versión actual
        servicios_actualizados = copy.deepcopy(self.version_actual['servicios'])
        
        # Encontrar servicio y actualizar
        servicio_objetivo = next(s for s in servicios_actualizados if s['id'] == servicio_id)
        tarifa_anterior = servicio_objetivo['tarifa']
        servicio_objetivo['tarifa'] = nueva_tarifa
        
        # Crear NUEVA VERSIÓN (recalcula automáticamente)
        cambio_desc = f"Cambio de tarifa en {servicio_id}: ${tarifa_anterior:.2f} → ${nueva_tarifa:.2f}"
        nueva_version = self.crear_nueva_version(
            numero_version=self._generar_numero_version(),
            cambio_realizado=cambio_desc,
            servicios=servicios_actualizados
        )
        
        # Registrar auditoría del cambio
        nueva_version['auditoria'] = {
            'tipo': 'cambio_tarifa',
            'servicio_id': servicio_id,
            'tarifa_anterior': tarifa_anterior,
            'tarifa_nueva': nueva_tarifa,
            'razon': razon,
            'impacto_total': (nueva_tarifa - tarifa_anterior) * 36  # Meses del contrato
        }
        
        return nueva_version
    
    def agregar_servicios(self, nuevos_servicios, razon):
        """OPERACIÓN TÍPICA: agregar nuevos servicios
        
        El sistema:
        1. Detecta los nuevos servicios
        2. Recalcula TODO con los nuevos incluidos
        3. Genera NUEVA VERSIÓN
        4. Te muestra impacto: +$X por X nuevos servicios
        """
        
        servicios_actualizados = copy.deepcopy(self.version_actual['servicios'])
        servicios_actualizados.extend(nuevos_servicios)
        
        cambio_desc = f"Agregados {len(nuevos_servicios)} nuevos servicios"
        nueva_version = self.crear_nueva_version(
            numero_version=self._generar_numero_version(),
            cambio_realizado=cambio_desc,
            servicios=servicios_actualizados
        )
        
        nueva_version['auditoria'] = {
            'tipo': 'agregar_servicios',
            'cantidad': len(nuevos_servicios),
            'impacto_total': sum(s['total'] for s in nuevos_servicios),
            'razon': razon
        }
        
        return nueva_version
    
    def calcular_servicio(self, servicio):
        """Calcula un servicio mes a mes con su tarifa actual"""
        
        total_meses = calcular_meses_entre(servicio['fecha_inicio'], servicio['fecha_fin'])
        total_presupuesto = servicio['tarifa'] * total_meses
        
        return {
            **servicio,
            'total_meses': total_meses,
            'total': total_presupuesto
        }
    
    def obtener_comparativa_cambios(self):
        """Muestra qué cambió entre cada versión"""
        
        if len(self.versiones) < 2:
            return "Solo hay 1 versión (presupuesto inicial)"
        
        comparativas = []
        for i in range(1, len(self.versiones)):
            version_anterior = self.versiones[i-1]
            version_actual = self.versiones[i]
            
            comparativas.append({
                'de': version_anterior['numero_version'],
                'a': version_actual['numero_version'],
                'cambio': version_actual['cambio_realizado'],
                'total_anterior': version_anterior['total_presupuesto'],
                'total_nuevo': version_actual['total_presupuesto'],
                'diferencia': version_actual['total_presupuesto'] - version_anterior['total_presupuesto']
            })
        
        return comparativas

# EJEMPLO DE USO:
presupuesto = PresupuestoVersionado("PRESUPUESTO_ETAPA_RE1_2026", servicios_iniciales)

# Mes 1: Descubres que hay 5 servicios más
presupuesto.agregar_servicios(
    nuevos_servicios=[...],
    razon="Paradas G5 agregadas en octubre"
)

# Mes 2: Cambio de tarifa en un servicio
presupuesto.cambiar_tarifa_servicio(
    servicio_id="S015",
    nueva_tarifa=150.00,
    razon="Upgrade bandwidth 10→25 MBPS"
)

# Ver comparativa de cambios
print(presupuesto.obtener_comparativa_cambios())
# Output:
# [
#   {
#     'de': 'v1.0',
#     'a': 'v1.1',
#     'cambio': 'Agregados 5 nuevos servicios',
#     'total_anterior': 385000.00,
#     'total_nuevo': 387500.00,
#     'diferencia': +2500.00
#   },
#   {
#     'de': 'v1.1',
#     'a': 'v1.2',
#     'cambio': 'Cambio de tarifa en S015: $100 → $150',
#     'total_anterior': 387500.00,
#     'total_nuevo': 390000.00,
#     'diferencia': +2500.00
#   }
# ]
```

**Lo que acabas de leer es la solución a tu problema de mantenimiento.**

### Salida esperada
```
PRESUPUESTO_ETAPA_RE1_2026
Estado: VERSIÓN v1.2 (ACTUAL)
Fecha última actualización: 2026-11-10

VERSIONES DISPONIBLES:
┌─────────────────────────────────────────────────────────────────┐
│ v1.0 (2026-09-01) - HISTÓRICO                                   │
│ └─ Presupuesto inicial con 50 servicios                         │
│    Total: $385,000.00                                            │
├─────────────────────────────────────────────────────────────────┤
│ v1.1 (2026-10-15) - HISTÓRICO                                   │
│ └─ Agregados 5 nuevos servicios (Paradas G5)                    │
│    Total: $387,500.00 (+$2,500.00)                              │
├─────────────────────────────────────────────────────────────────┤
│ v1.2 (2026-11-10) - ACTUAL ✓                                    │
│ └─ Cambio de tarifa en S015: $100→$150 (Upgrade 10→25 MBPS)     │
│    Total: $390,000.00 (+$2,500.00)                              │
└─────────────────────────────────────────────────────────────────┘

COMPARATIVA:
v1.0 → v1.1: +$2,500.00 (5 nuevos servicios)
v1.1 → v1.2: +$2,500.00 (upgrade en 1 servicio)
DIFERENCIA ACUMULADA: +$5,000.00 desde presupuesto inicial

PRESUPUESTO VIGENTE: $390,000.00
```

**Lo que TÚ ganas:**
- ✅ Cambias 1 parámetro (tarifa, agregar servicio)
- ✅ El sistema recalcula TODO automáticamente
- ✅ Generas NUEVA VERSIÓN sin tocar Excel
- ✅ Auditoría completa de qué cambió y cuándo
- ✅ Histórico completo (nunca pierdes información)
- ✅ Comparativas: qué diferencia hay entre versiones

**Lo que ANTES hacías manualmente en Excel:**
- ❌ Encontrar la tarifa en la hoja
- ❌ Cambiarla
- ❌ Seleccionar rango de 100+ servicios
- ❌ Presionar F9 para recalcular
- ❌ Copiar nuevos números
- ❌ Actualizar resumen
- ❌ Documentar qué cambió (o no documentar nada)

**Lo que AHORA haces con el sistema:**
- ✅ 1 click: `presupuesto.cambiar_tarifa_servicio("S015", 150.00, "Upgrade")`
- ✅ El sistema genera v1.2 recalculado automáticamente
- ✅ Todo auditado
- ✅ LISTO

### ✅ Lo que aprendemos:
- Cómo **iterar mes a mes**
- Cómo **calcular la fracción de prorrateo** (primero y último mes)
- Cómo **tabular resultados** para ver el flujo completo
- **NUEVO:** Cómo **documentar discrepancias** entre lo correcto y lo que ETAPA EP cobra
- **NUEVO:** Cómo **auditar** cuánto dinero pierdes exactamente

### 🎯 Aplicación estratégica (el "guante blanco")

Una vez que calcules esto para **todos los servicios**, tendrás un reporte tipo:

```
AUDITORÍA DE PRESUPUESTOS ETAPA-RE1/RE2
Período: 2026-09-07 a 2029-09-06

Total servicios auditados: 100
Servicios con discrepancias: 15 (14.5%)

DINERO PERDIDO POR CRITERIOS DE ETAPA EP:
- Offset +1 día (new services):        $450.00
- Cambios de bandwidth sin notificación: $280.00
- Cambios de período sin ajuste:        $120.00
                                        --------
TOTAL DINERO PENDIENTE DE RECLAMAR:     $850.00

DATOS PARA RECLAMO FORMAL:
✓ Fechas exactas de discrepancias
✓ Tarifas afectadas
✓ Cálculos correctos vs. facturados
✓ Auditoría de aceptaciones previas
✓ Solicitud de reembolso con precisión
```

**Esto es lo que ETAPA EP no quiere que tengas:** prueba documentada de dinero no reclamado.

---

## FASE 2: Servicio con Cambio de Tipo

**Qué es:** El servicio arranca como INTERNET, pero a mitad de su vigencia cambia a DATOS con tarifa diferente.

**Escenario real del análisis:**
```
Ubicación: "I0247963" (Ejemplo hipotético)
Período: ETAPA-RE1 → ETAPA-RE2 (cambio en 2026-09-07)

ETAPA-RE1 (2026-09-07 a 2026-09-06):
  - Tipo: INTERNET 10 MBPS
  - Tarifa: $100.00 / mes

ETAPA-RE2 (2026-09-07 en adelante):
  - Tipo: INTERNET 25 MBPS (UPGRADE)
  - Tarifa: $150.00 / mes
```

### Entrada de datos (JSON con cambios)
```json
{
  "servicio_id": "S002",
  "ubicacion": {
    "id": "U002",
    "nombre": "I0247963",
    "codigo_inst": "I0247963"
  },
  "periodo": {
    "id": "ETAPA-RE1",
    "fecha_inicio": "2026-09-07",
    "fecha_fin": "2029-09-06"
  },
  "tarifa": {
    "fecha_vigencia_desde": "2026-09-08",
    "fecha_vigencia_hasta": "2029-09-06",
    "tipo_inicial": "INTERNET",
    "valor_base": 100.00,
    "cambios": [
      {
        "fecha_cambio": "2026-10-10",  // <-- CAMBIO
        "nuevo_tipo": "INTERNET",
        "nuevo_valor_mensual": 150.00,  // 10 MBPS → 25 MBPS
        "razon": "Upgrade de bandwidth"
      }
    ]
  }
}
```

### Lógica mejorada (Pseudocódigo)
```python
def calcular_presupuesto_con_cambios(servicio):
    """Igual a Fase 1, pero aplica cambios de tarifa cuando corresponde"""
    
    resultados = []
    fecha_actual = servicio['tarifa']['fecha_vigencia_desde']
    fecha_fin = servicio['tarifa']['fecha_vigencia_hasta']
    
    while fecha_actual <= fecha_fin:
        mes = fecha_actual.strftime('%Y-%m')
        
        # NUEVO: Buscar tarifa considerando cambios
        tarifa_vigente = buscar_tarifa_vigente(
            servicio['tarifa'],
            fecha_actual  # <-- ¿Cuál tarifa aplica en esta fecha?
        )
        
        dias_a_facturar = calcular_dias_facturados(
            fecha_inicio_real=servicio['tarifa']['fecha_vigencia_desde'],
            mes_consultado=fecha_actual
        )
        
        fraccion = dias_a_facturar / 30
        valor_facturado = tarifa_vigente * fraccion
        
        # NUEVO: Registrar si hay cambio en este mes
        cambio_en_mes = buscar_cambio_en_mes(
            servicio['tarifa']['cambios'],
            fecha_actual
        )
        
        resultado = {
            'mes': mes,
            'dias_facturados': dias_a_facturar,
            'tarifa': tarifa_vigente,
            'valor_facturado': valor_facturado,
            'cambio': cambio_en_mes  # Null o {descripción del cambio}
        }
        
        resultados.append(resultado)
        fecha_actual = proxima_fecha_mes(fecha_actual)
    
    return resultados
```

### Salida esperada
```
Servicio: S002 (I0247963)
Período: 2026-09-08 → 2029-09-06

Mes          Días   Tarifa    Valor      Cambio
2026-09      22/30  $100.00   $73.33     (inicio)
2026-10      30/30  $100.00   $100.00    
2026-10      (✓)    $150.00   (aprox)    CAMBIO: Upgrade 10→25 MBPS el 10/10
2026-11      30/30  $150.00   $150.00    
2026-12      30/30  $150.00   $150.00
...

TOTAL ETAPA-RE1: $1,300.00 (con cambio el 10/10)
TOTAL ETAPA-RE2: $2,550.00 (tarifa mejorada)
GRAN TOTAL: $3,850.00
```

### ✅ Lo que aprendemos:
- Cómo **buscar qué tarifa aplica** en cada mes
- Cómo **detectar cambios dentro del mes**
- Cómo **registrar auditoría** (cuándo cambió, qué cambió)
- Cómo **recalcular automáticamente** si cambian tarifas

---

## FASE 3: Escalar a 100+ Servicios

**Qué es:** Ejecutar Fase 1 + Fase 2 para todos los servicios en batch.

### Entrada: CSV o JSON con todos los servicios
```csv
servicio_id,ubicacion,codigo_inst,fecha_inicio,fecha_fin,tarifa_inicial,cambios_json
S001,Ricaurte,I0276496,2026-09-08,2029-09-06,100.00,[]
S002,I0247963,I0247963,2026-09-08,2029-09-06,100.00,"[{""fecha"":""2026-10-10"",""nuevo_valor"":150.00}]"
S003,Hospital IESS,I0276542,2026-09-09,2029-09-06,200.00,[]
...
S100+,... más servicios
```

### Lógica batch (Pseudocódigo)
```python
def procesar_todos_los_servicios(archivo_servicios):
    """Lee el archivo y calcula presupuesto para cada uno"""
    
    resultados_totales = {
        'por_servicio': {},
        'por_ubicacion': {},
        'resumen_general': {}
    }
    
    servicios = leer_csv_o_json(archivo_servicios)
    
    for servicio in servicios:
        # FASE 1/2: Calcular este servicio
        presupuesto = calcular_presupuesto_con_cambios(servicio)
        
        # Guardar en resultados
        resultados_totales['por_servicio'][servicio['id']] = presupuesto
        
        # Agregar por ubicación
        ubicacion = servicio['ubicacion']
        if ubicacion not in resultados_totales['por_ubicacion']:
            resultados_totales['por_ubicacion'][ubicacion] = []
        resultados_totales['por_ubicacion'][ubicacion].append(presupuesto)
    
    # Generar resúmenes
    resultados_totales['resumen_general'] = generar_resumen(resultados_totales)
    
    return resultados_totales

def generar_resumen(resultados):
    """Crea totales por período, tipo, etc."""
    return {
        'total_100_servicios': sum(...),
        'total_por_periodo': { 'ETAPA-RE1': ..., 'ETAPA-RE2': ... },
        'total_por_tipo': { 'INTERNET': ..., 'DATOS': ... },
        'servicios_con_cambios': count(...),
        'servicios_sin_cambios': count(...)
    }
```

### Salida: 3 archivos
```
1. presupuestos_detallado.csv
   (100+ servicios × 37 meses = 3,700+ líneas)
   
   servicio_id,ubicacion,mes,tarifa,dias,valor_facturado,cambio
   S001,Ricaurte,2026-09,100.00,22,73.33,
   S001,Ricaurte,2026-10,100.00,30,100.00,
   ...

2. presupuestos_resumen.json
   {
     "S001": {
       "ubicacion": "Ricaurte",
       "total": 3610.00,
       "meses": 37,
       "cambios": 0
     },
     "S002": {
       "ubicacion": "I0247963",
       "total": 3850.00,
       "meses": 37,
       "cambios": 1  // <-- Upgrade de ancho de banda
     }
   }

3. presupuestos_consolidado.json
   {
     "total_general": 385000.00,
     "cantidad_servicios": 100,
     "cantidad_ubicaciones": 85,
     "servicios_con_cambios": 12,
     "cambios_por_tipo": {
       "upgrade_bandwidth": 12,
       "cambio_tipo_servicio": 0,
       "otro": 0
     }
   }
```

### ✅ Lo que aprendemos:
- Cómo **automatizar el proceso** para 100+ servicios
- Cómo **generar reportes** en diferentes niveles (detalle, resumen, consolidado)
- Cómo **auditar cambios** a nivel masivo

---

## Roadmap de Implementación

| Fase | Duración | Complejidad | Resultado |
|------|----------|-------------|-----------|
| 1    | 1-2 días | 🟢 Baja    | Una función Python que calcula 1 servicio simple |
| 2    | 2-3 días | 🟡 Media   | Extender a servicios con cambios de tarifa |
| 3    | 1-2 días | 🟡 Media   | Procesar 100+ servicios en batch |

**Total estimado:** 4-7 días de trabajo real (no abrumador si lo haces en fases).

---

## Por Qué Esta Descomposición Funciona

### 1. **Cada fase es independiente**
   - Fase 1 NO necesita saber de cambios
   - Fase 2 extiende Fase 1 sin reescribir
   - Fase 3 solo replica Fase 1/2 en loop

### 2. **Probar es fácil**
   - Fase 1: Prueba con 1 servicio, verifica números vs Excel
   - Fase 2: Prueba con el servicio de radares (el problemático)
   - Fase 3: Prueba con 5 servicios, luego escala a 100+

### 3. **Los cambios son predecibles**
   - No hay lógica sorpresa
   - Todo se resume en: "¿Qué tarifa aplica en cada mes?"
   - Eso se calcula de forma determinística desde JSON

### 4. **Reutilizable**
   - Mañana necesitas agregar otro tipo de cambio (ej: cambio de ubicación)
   - Solo extiendes el JSON y la función de "buscar tarifa vigente"

---

## Siguiente Paso: Preguntas para Fase 1

### Sobre el Excel actual:

1. **¿Estructura actual?**
   - ¿Qué columnas tiene? (ubicación, código_inst, fecha_inicio, tarifa, etc.)
   - ¿Cuántas filas? (servicios individuales o agrupados)
   - ¿Una sola hoja o separadas (RE1 / RE2)?
   - ¿Fórmulas o valores hardcodeados?

2. **¿Cómo cambias tarifas hoy?**
   - ¿Editas directamente en Excel?
   - ¿El cambio recalcula automáticamente o tienes que hacerlo manual?
   - ¿Qué tan frecuente ocurren cambios? (semanal, mensual)

### Sobre cambios que ocurren:

3. **¿Qué tipos de cambios necesitas registrar?**
   - ✅ Cambio de tarifa (como el upgrade de bandwidth)
   - ✅ Agregar servicio nuevo
   - ✅ Eliminar/desactivar servicio
   - ✅ Cambio de período (RE1→RE2)
   - ✅ Otros cambios

4. **¿Con qué frecuencia ocurren?**
   - ¿Cambios diarios, semanales, mensuales?
   - ¿Hay épocas "alborotadas" (ej: inicio de período) vs. meses tranquilos?

### Sobre almacenamiento:

5. **¿Dónde guardar las versiones?**
   - JSON en `facret/data/presupuestos/` (recomendado: fácil de auditar)
   - Base de datos (si la tienes, cuál)
   - Ambas (JSON para auditoría + DB para búsquedas rápidas)

6. **¿Cómo usar en FACRET?**
   - ¿Mostrar en UI las versiones disponibles?
   - ¿Permitir "revertir" a una versión anterior?
   - ¿Generar reportes Excel desde una versión específica?

### Sobre el flujo:

7. **¿Cuál sería tu workflow ideal?**
   - Hoy: "cambio algo en Excel, espero a que recalcule"
   - Mañana: "hago click en 'cambiar tarifa', el sistema genera v1.1, listo"
   - ¿Es así como lo ves?

---

## Plan de Ejecución Fase 1

**Una vez me respondas lo anterior, haré:**

1. **Paso 1:** Leer tu Excel actual e identificar estructura
2. **Paso 2:** Convertir servicios a JSON con estado v1.0
3. **Paso 3:** Implementar clase `PresupuestoVersionado` (la que viste arriba)
4. **Paso 4:** Crear funciones para:
   - `cambiar_tarifa_servicio()`
   - `agregar_servicios()`
   - `eliminar_servicio()`
   - `obtener_comparativa()`
5. **Paso 5:** Validar contra 5-10 servicios (verificar números vs Excel)
6. **Paso 6:** Integrar en FACRET (UI para ver/cambiar/auditar)

**Tiempo estimado:** 4-6 días (dependiendo de complejidad).

**Resultado:** 
- ✅ **Excel muere.** Ahora los cambios se hacen en FACRET
- ✅ **Recalculos automáticos.** Cambias 1 parámetro, todo se recalcula
- ✅ **Historial completo.** Sabes qué cambió, cuándo, por qué
- ✅ **Sin mantenimiento manual.** Ya nunca más tendrás que tocar Excel para presupuestos
- ✅ **Auditoría documentada.** Cada cambio registrado, cada versión guardada

**Lo que ANTES te mataba de tiempo:**
- Cambiar una tarifa en Excel
- Esperar a que recalcule
- Copiar números
- Documentar (o no) qué cambió

**Lo que AHORA es:**
```python
presupuesto.cambiar_tarifa_servicio("S015", 150.00, "Upgrade 10→25 MBPS")
# Sistema genera v1.2 automáticamente
# Auditoría creada automáticamente
# Listo
```
