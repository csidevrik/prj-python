# Reglas de trabajo para Claude en este proyecto

> Este archivo NO se carga automáticamente (no se llama `CLAUDE.md`). Si empiezas una sesión nueva, especialmente en otra PC, dile a Claude: **"lee claudio.md"** al inicio.

## Regla principal: no avanzar sin autorización explícita

Antes de:
- Editar o crear archivos de código.
- Correr comandos (Bash/PowerShell), instalar dependencias, o instalar software (ej. Docker).
- Levantar o modificar contenedores/servicios.

Claude debe **explicar qué va a hacer y por qué**, y esperar un **"sí" explícito** antes de ejecutar. No se debe encadenar varios pasos solo porque el usuario aprobó una decisión de diseño (por ejemplo, responder preguntas sobre cómo modelar datos no es aprobación para instalar software o correr scripts).

**Motivo:** en una sesión anterior, tras resolver unas preguntas de diseño sobre el modelo de datos de contratos, Claude instaló Docker Desktop, editó varios archivos, actualizó dependencias y corrió pruebas end-to-end sin pausar a explicar el plan completo primero. El usuario lo marcó como un problema: quiere entender primero, decidir después.

## Excepciones

- Documentación (`.md`) y respuestas explicativas no requieren esta pausa salvo que impliquen tocar código o correr comandos.
- Preguntas de solo lectura (leer archivos, `git status`, explorar el repo) no requieren autorización previa.

---

## Análisis y Decisiones: Gestión de Infraestructura (Septiembre 2026)

### Contexto
Se requiere extender FACRET para gestionar nuevas instalaciones:
- **19 Paradas Inteligentes** (I0276496-I0276525, instaladas 08/09/2026)
- **3 Oficinas EMOV** (I0276542-I0276544, instaladas 09/09/2026)
- **Upgrades de bandwidth** en servicios existentes (IO247963, etc.: 10→25 MBPS)
- **Radares futuros** (comienzan 02/10/2026, aún no activos)

### Complejidad Real Identificada

**Esto NO es solo "agregar agencias"**, es un problema de gestión de múltiples períodos de contrato:

1. **ETAPA-RE1** (antiguo): Termina 2025-09-06
   - 23 servicios en agencias (CAPULISPAMBA, MAYANCELA, etc.)
   
2. **ETAPA-RE2** (nuevo): Comienza 2026-09-07
   - 22 nuevas ubicaciones (paradas + oficinas) con servicios
   - Upgrades de bandwidth en servicios migrando de ETAPA-RE1
   
3. **Presupuesto 2026**: Requiere cálculo por vigencia real
   - Cada servicio tiene `fecha_inicio` y `fecha_fin`
   - Presupuesto = Σ(valor_mensual × meses_vigentes_en_2026)
   - Ejemplo: IO247963 tiene presupuesto en ETAPA-RE1 (ene-sep) + ETAPA-RE2 con upgrade (sep-dic)

### Modelo de Datos Decidido

**Cambios al esquema actual:**

1. ✅ Agregar `fecha_inicio` / `fecha_fin` a SERVICIO
   - Crítico para cálculo de presupuesto

2. ✅ Agregar `periodo_id` a SERVICIO (FK → PERÍODO_CONTRATO)
   - Trackear qué contrato pertenece cada servicio

3. ✅ Nueva tabla `PERÍODO_CONTRATO`
   - id: "ETAPA-RE1", "ETAPA-RE2", etc.
   - fecha_inicio, fecha_fin, estado

4. ✅ Nueva tabla `HISTORIAL_BANDWIDTH`
   - Auditoría de cambios (10→25 MBPS)
   - cod_serv, bandwidth_anterior, bandwidth_nuevo, fecha_cambio

5. ✅ Renombrar `agencias.json` → `ubicaciones.json`
   - Ahora contiene: agencias, paradas, oficinas, radares

### Estructura de Archivos JSON (Plan)

```
facret/data/
├── periodos.json              (nuevo)
├── ubicaciones.json           (renombrado)
├── servicios/
│   ├── ETAPA-RE1.json        (actualizar con fecha_inicio/fin, periodo_id)
│   └── ETAPA-RE2.json        (crear con paradas, oficinas, upgrades)
└── historial_bandwidth.json  (nuevo)
```

### Próximos Pasos (Orden)

1. [ ] Diseñar JSON schemas exactos para cada tabla
2. [ ] Migrar ETAPA-RE1.json al nuevo formato
3. [ ] Crear ETAPA-RE2.json con paradas, oficinas, upgrades
4. [ ] Diseñar menú "Configuración de Infraestructura" (Agencias, Paradas, Oficinas, Radares)
5. [ ] Diseñar UI mockups (modal vs panel lateral)
6. [ ] Implementar código (SOLO después de aprobación)

### Referencias
- Análisis completo: `https://claude.ai/code/artifact/ca1eccbe-9250-48c8-9683-3de33bc5b0bd`
- Datos reales: PDF (instalaciones), Excel (upgrades)
- Fecha análisis: 2026-09-14

---

## Análisis y Mejoras: facs_manager.py (Octubre 2026)

### El Problema: Discrepancia de Nombres en Facturas

ETAPA EP envía archivos XML/PDF con **nombres incorrectos** en los correos vs. contenido real de las facturas.

**Ejemplo concreto:**
- Archivo recibido en correo: `FAC065173799_001.xml` / `FAC065173799_001.pdf` ❌ (INCORRECTO)
- Contenido real dentro del XML: `<numero>FAC001003055432769</numero>` ✅ (CORRECTO)
- Código de instalación: `I0247958`
- Fecha emisión: `02/10/2026` ← **NO está siendo extraído actualmente**

**Impacto:**
- CSV de `facturas.csv` tiene duplicados sin auditoría clara
- Ejemplo: Servicio `I0247958` aparece varias veces con diferentes números de factura
- No hay forma de relacionar el nombre del archivo recibido (para auditoría) con el número correcto

### Código Afectado

**Archivo:** `facret/src/logic/facs_manager.py`

**Función crítica:** `extract_fac_register()` (línea 171-179)
```python
# Actual - extrae 3 campos:
return Factura(code_inst=codigo, number_fac=numero, value_serv=valor)

# Falta: fechaEmision y nombre_archivo_original
```

**Función que genera CSV:** `process_all_xml_facs()` (línea 209-231)
- Llama a `extract_fac_register()`
- Genera `facturas.csv` y `facturas.json`
- Actualmente guarda solo: code_inst, number_fac, value_serv

### Solución Propuesta: OPCIÓN A (RECOMENDADA)

**Agregar 2 columnas al CSV sin renombrar archivos:**

1. ✅ Extraer `fechaEmision` del XML
2. ✅ Guarcar `archivo_original` (nombre del XML recibido)
3. ✅ Agregar ambos campos al CSV para auditoría

**Cambios técnicos necesarios:**

**Paso 1:** Actualizar dataclass `Factura` en `models.py`
```python
@dataclass
class Factura:
    code_inst: str
    number_fac: str
    value_serv: str
    fecha_emision: str = ""      # ← NUEVO
```

**Paso 2:** Modificar `extract_fac_register()` (línea 171)
```python
# Agregar extracción de fecha:
fecha = root.find(".//fechaEmision").text  # ← NUEVO
return Factura(code_inst=codigo, number_fac=numero, value_serv=valor, fecha_emision=fecha)
```

**Paso 3:** Modificar `process_all_xml_facs()` (línea 214-221)
```python
# En el loop donde se agregan registros:
registros.append({
    "code_inst":       r.code_inst,
    "number_fac":      r.number_fac,
    "value_serv":      r.value_serv,
    "fecha_emision":   r.fecha_emision,           # ← NUEVO
    "archivo_original": filename,                  # ← NUEVO
})
```

**Resultado esperado en CSV:**
```csv
code_inst,number_fac,value_serv,fecha_emision,archivo_original
I0247958,FAC001003055432769,328.32,02/10/2026,FAC065173799_001.xml
I0247958,FAC001003055432770,140.8,02/10/2026,FAC001003055432764.xml
I0247954,FAC001003055362149,51.8,01/10/2026,FAC001003055362149.xml
```

### Alternativa: OPCIÓN B (Más Completa)

Si también quieres **renombrar los PDFs para incluir el verdadero número:**
- Nombre actual: `FAC065173799_001.pdf`
- Nombre nuevo: `FAC065173799_001-FAC001003055432769-I0247958.pdf`

Esto requeriría función adicional `get_corrected_filename()` y procesar PDFs después de generar CSV. **Más complejo pero filesystem más claro.**

### Decisión Pendiente
**¿Implementar OPCIÓN A, B, o ambas?** Espera aprobación explícita antes de escribir código.

### Referencias
- Análisis visual: `https://claude.ai/artifact/HnotUF9XBFZYfxhVPBbXFK`
- Archivo: `facret/src/logic/facs_manager.py` (281 líneas)
- Modelo: `facret/src/models/models.py` (donde está dataclass Factura)
- Fecha análisis: 2026-10-03
