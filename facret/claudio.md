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

## Protocolo de Cambios: Documentación Previa

Antes de iniciar trabajo significativo:

1. **Actualizar `CHANGELOG.md`** con:
   - Qué se va a implementar (sección "### En Progreso")
   - Pasos principales del trabajo
   
2. **Ejecutar los cambios** en código:
   - Una vez documentado, proceder con implementación
   - Seguir reglas de autorización según corresponda
   
3. **Finalizar en `CHANGELOG.md`:**
   - Mover a "### Completado" 
   - Agregar detalles de qué se logró
   - Enumerar bugs corregidos (si aplica)
   
4. **Commit con referencia:**
   - Mensaje de commit incluye detalles de lo que se hizo
   - Referencia a CHANGELOG.md si es necesario

**Motivo:** Mantiene documentación y código sincronizados. Facilita rastrear qué se hizo, cuándo y por qué.

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

### Implementación: OPCIÓN A ✅ (Octubre 2026)

**Estado: COMPLETADO**

Cambios realizados:

1. ✅ **models.py** — Actualizar clase `Factura`:
   ```python
   class Factura:
       def __init__(self, code_inst, number_fac, value_serv, fecha_emision):
           self.fecha_emision = fecha_emision
   ```

2. ✅ **facs_manager.py línea 179-180** — Extraer `fechaEmision`:
   ```python
   fech_emi = root.find(".//fechaEmision").text
   return Factura(code_inst=codigo, number_fac=numero, value_serv=valor, fecha_emision=fech_emi)
   ```

3. ✅ **facs_manager.py línea 218-223** — Agregar a registros:
   ```python
   registros.append({
       "code_inst": r.code_inst,
       "number_fac": r.number_fac,
       "value_serv": r.value_serv,
       "fecha_emision": r.fecha_emision,
       "archivo_original": filename,
   })
   ```

### Problema Resuelto: Orden de Operaciones

**Dilema:** Si se renombraba antes de procesar, se perdía el `archivo_original`.

**Solución:** Llamar `process_all_xml_facs()` ANTES de `rename_files_with_attributes()`:
```
1. process_all_xml_facs()           ← Captura archivo_original CON nombre actual
2. rename_files_with_attributes()   ← Renombra después (ya está en CSV)
```

**Resultado CSV:**
- Columnas: code_inst, number_fac, value_serv, fecha_emision, archivo_original
- Ejemplo: I0247958 | FAC001003055432769 | 328.32 | 02/10/2026 | FAC065173799_001.xml
- ✅ Auditoría clara de discrepancias ETAPA EP

### Próximas Mejoras (Backlog)

- [ ] OPCIÓN B: Renombrar PDFs con nomenclatura extendida (si se necesita)
- [ ] Validación: Manejar campos faltantes `.//numDocSustento` en XMLs de retención
- [ ] Nota IDE: XPath `.//numDocSustento` en línea 191 marca falso positivo cuando XML abierto es de facturas (no retenciones)

### Referencias
- Análisis visual: `https://claude.ai/artifact/HnotUF9XBFZYfxhVPBbXFK`
- Archivo: `facret/src/logic/facs_manager.py` (283 líneas)
- Modelo: `facret/src/models/models.py` (clase Factura)
- Fecha implementación: 2026-10-05

---

## Estrategia: Compartir Archivos Excel (Octubre 2026)

### Problema
Usuario tiene un archivo Excel ("tabla de verdad") con:
- Datos de presupuestos y fórmulas
- Estructura de ubicaciones, servicios, períodos de contrato
- Cálculos de presupuesto prorrateado para 2026

Claude Code (este agente) **no puede procesar archivos `.xlsx` directamente**. Necesitamos una estrategia para extraer y compartir la estructura.

### Solución Propuesta

**Opción A (RECOMENDADA): Usar claude.ai/chat**

1. Ir a [claude.ai/chat](https://claude.ai/chat)
2. Copiar y pegar este prompt:
   ```
   Tengo un archivo Excel con datos de presupuestos que necesito compartir 
   con un agente de desarrollo.
   
   El archivo contiene:
   - Ubicaciones con códigos de instalación
   - Servicios con rangos de fechas y valores mensuales
   - Períodos de contrato (ETAPA-RE1, ETAPA-RE2)
   - Cálculos de presupuestos prorrateados para 2026
   
   Extrae la estructura en CSV o JSON preservando:
   - Todas las columnas
   - Las fórmulas o lógica de cálculo (en comentarios si es necesario)
   - Valores numéricos correctos
   ```
3. Subir el Excel al chat
4. Copiar la salida (CSV o JSON) y compartirla aquí

**Opción B: Exportar manualmente a CSV**

1. Abrir Excel
2. Guardar cada hoja como `.csv` (archivo → guardar como)
3. Compartir los CSVs en el chat o pegar contenido aquí

**Opción C: Copiar/pegar directo**

1. Seleccionar tabla en Excel
2. Copiar (Ctrl+C)
3. Pegar aquí en el chat
4. Describir columnas y significado

### Beneficios

- ✅ Preserva fórmulas y lógica
- ✅ Estructura clara en JSON/CSV
- ✅ Se puede versionear en Git
- ✅ Facilita revisión en otra PC

### Próximo Paso
**Cuando tengas la estructura extraída, avísame y procedeamos a:**
1. Diseñar JSON schemas para `ubicaciones.json`, `servicios.json`, `periodos.json`
2. Implementar lógica de cálculo de presupuestos
3. Integrar en FACRET

**Fecha propuesta:** 2026-10-19

---

## Solución Final: Presupuesto Versionado (Octubre 2026)

### El Verdadero Problema Identificado

**NO es:** Calcular presupuestos una sola vez.

**ES:** Mantener presupuestos que **cambian constantemente** sin que el trabajo manual te mate.

**Raíz del problema:**
- Cambias 1 tarifa en Excel → tienes que recalcular 100+ servicios manualmente
- Agregas un servicio nuevo → más cálculos manuales
- Cambio de período → todo se recomputa
- Esto sucede **constantemente**, no una sola vez

### La Solución: Presupuesto Versionado

Un presupuesto que funciona como un **documento versionado** (como Git):
- **v1.0** (Presupuesto inicial Sep 2026)
- **v1.1** (Se agregaron 5 servicios en Oct)
- **v1.2** (Se cambió tarifa en Nov)
- **v2.0** (Se inició ETAPA-RE2 con cambios masivos)

Cada versión:
- ✅ Recalcula automáticamente (sin tocar Excel)
- ✅ Preserva histórico (nunca pierdes información)
- ✅ Es auditable (qué cambió, cuándo, por qué)
- ✅ Es versionable (puedes comparar v1.0 vs v1.2)

### Ventaja Estratégica

**Antes (Excel):**
```
1. Cambias tarifa
2. Esperas a que recalcule
3. Copias números
4. Haces ajustes manuales
5. Documentas (o no)
6. Repites cuando hay otro cambio
= TEDIOSO, PROPENSO A ERRORES, SIN AUDITORÍA
```

**Después (Presupuesto Versionado):**
```python
presupuesto.cambiar_tarifa_servicio("S015", 150.00, "Upgrade")
# Sistema genera v1.2 automáticamente
# Recalcula TODO
# Audita el cambio
# Listo
= 1 LÍNEA DE CÓDIGO, AUTOMÁTICO, AUDITADO
```

### Estructura de Datos (Concept)

```
PRESUPUESTO v1.0
├─ servicios[50]
│  ├─ S001: Ricaurte, $100/mes, 37 meses → $3,610
│  ├─ S002: I0247963, $100/mes, 37 meses → $3,610
│  └─ ... (50 servicios)
├─ total: $385,000

PRESUPUESTO v1.1 (Agregados 5 servicios)
├─ servicios[55]
│  ├─ ... (50 anteriores)
│  ├─ S051: Nueva parada, $100/mes, 36 meses → $3,600
│  └─ ... (5 nuevos)
├─ total: $387,500
├─ auditoria: {
│    tipo: "agregar_servicios",
│    cantidad: 5,
│    impacto: +$2,500
│  }

PRESUPUESTO v1.2 (Cambio de tarifa en S015)
├─ servicios[55]
│  ├─ ... (54 anteriores)
│  ├─ S015: Radar, $150/mes (fue $100), 37 meses → $5,550
│  └─ ... (restante)
├─ total: $390,000
├─ auditoria: {
│    tipo: "cambio_tarifa",
│    servicio: "S015",
│    tarifa_anterior: $100,
│    tarifa_nueva: $150,
│    impacto: +$1,850
│  }
```

### Comparativa de Cambios

Pregunta: "¿Cuál fue el impacto de los cambios?"
Respuesta automática:
```
v1.0 → v1.1: +$2,500 (5 servicios nuevos)
v1.1 → v1.2: +$1,850 (upgrade de bandwidth)
Total acumulado: +$4,350
```

### Fases de Implementación

**FASE 1:** Presupuesto Versionado para 1 servicio (caso base)
- Leer Excel actual
- Crear v1.0 con estructura JSON
- Implementar cambios (tarifa, agregar, eliminar)
- Generar nuevas versiones automáticamente
- Auditar cambios
- Duración: 4-6 días

**FASE 2:** Escalar a 100+ servicios
- Procesar todos los servicios en batch
- Generar reportes consolidados
- Integrar en UI de FACRET
- Duración: 2-3 días

**FASE 3:** Funcionalidades avanzadas
- Revertir a versión anterior
- Exportar reportes por período
- Análisis de impacto (qué cambió más, dónde se gasta más)
- Duración: 3-5 días

### Preguntas Clave para Fase 1

Antes de comenzar, necesito saber:

1. **Excel actual — Estructura:**
   - Columnas exactas (ubicación, código_inst, fecha_inicio, tarifa, etc.)
   - Cuántas filas (servicios)
   - Una hoja o varias (RE1 / RE2 separadas)

2. **Cambios que ocurren:**
   - ¿Qué tipos de cambios hay? (tarifa, agregar, eliminar, cambio de período)
   - ¿Con qué frecuencia? (diario, semanal, mensual)

3. **Almacenamiento:**
   - ¿JSON, DB, ambas?
   - ¿Dónde en FACRET? (carpeta `data/presupuestos/`)

4. **Workflow deseado:**
   - Hoy: "cambio en Excel"
   - Mañana: ¿cómo debería ser?

### Próximo Paso

Lee `PLAN_CALCULO_PRESUPUESTO.md` (documento completamente actualizado) y responde las 7 preguntas en la sección "Siguiente Paso: Preguntas para Fase 1".

Con eso, implementamos Fase 1 y liberamos tu tiempo de Excel para siempre.

**Fecha de esta decisión:** 2026-10-25

---

## Mejora: Extracción de FechaMaxPago desde Campos Adicionales (Octubre 2026)

### Problema Identificado

Necesitaba extraer **FechaMaxPago** de los XMLs de factura de ETAPA EP, pero el campo **no estaba donde se buscaba**.

**Estructura correcta encontrada:**
```xml
<infoAdicional>
    <campoAdicional nombre="FechaMaxPago">09/11/2026</campoAdicional>
    <campoAdicional nombre="Instalacion">RDD01974</campoAdicional>
    <campoAdicional nombre="Consumo">09/2026</campoAdicional>
    <!-- ... más campos adicionales -->
</infoAdicional>
```

**Lo que estaba mal:**
- Buscaba `<FechaMaxPago>` como tag directo
- Realidad: es un atributo `nombre` dentro de `<campoAdicional>`

### Solución Implementada

**1. Actualizar clase `Factura` en models.py:**
```python
class Factura:
    def __init__(self, code_inst, number_fac, value_serv, fecha_emision, fecha_max_pago=None):
        self.code_inst = code_inst
        self.number_fac = number_fac
        self.value_serv = value_serv
        self.fecha_emision = fecha_emision
        self.fecha_max_pago = fecha_max_pago  # ← NUEVO
```

**2. Actualizar `extract_fac_register()` en facs_manager.py:**
```python
# Extraer correctamente del campoAdicional
fech_max_pago_elem = root.find('.//campoAdicional[@nombre="FechaMaxPago"]')
fech_max_pago = fech_max_pago_elem.text if fech_max_pago_elem is not None else None
return Factura(code_inst=codigo, number_fac=numero, value_serv=valor, 
               fecha_emision=fech_emi, fecha_max_pago=fech_max_pago)
```

**3. Incluir en registros CSV:**
```python
registros.append({
    "code_inst":  r.code_inst,
    "number_fac": r.number_fac,
    "value_serv": r.value_serv,
    "fecha_emision": r.fecha_emision,
    "fecha_max_pago": r.fecha_max_pago,  # ← NUEVO
    "name_original": filename,
})
```

### Resultado

**Commit:** `cfda339` en rama `facreto`
- ✅ Extrae correctamente FechaMaxPago desde campoAdicional
- ✅ Manejo seguro: si el campo no existe, se asigna None
- ✅ CSV ahora incluye columna `fecha_max_pago` con fechas de vencimiento

**Archivo actualizado:** `facturas.csv`
```
code_inst | number_fac | value_serv | fecha_emision | fecha_max_pago | name_original
I0205929  | FAC...     | 416.64     | 2/10/2026     | 09/11/2026     | FAC065173793_001.xml
```

### Lecciones Aprendidas

**Importancia de ver la estructura XML real:**
- Asumir estructura sin verificar → código que no funciona
- Verificar tag exacto en XML → solución correcta

**XPath correcto para campos adicionales ETAPA EP:**
```python
.//campoAdicional[@nombre="NombreDelCampo"]
```

Este patrón puede reutilizarse para extraer otros campos adicionales (Consumo, Instalacion, Dir Instal, etc.).

**Fecha de implementación:** 2026-10-27

---

## Clasificador automático de facturas ETAPA (Octubre 2026)

### Estado
- Archivos: `src/logic/facs_clasificador.py`, `src/logic/outlook_reader.py`, `src/scripts/clasificar_facturas.py`, y los scripts de instalación de la tarea y la regla.
- Outlook: regla `ETAPA a FACS` activa. Carpetas `FACS\AGUA`, `FACS\TELECOM` y `FACS\REVISAR` creadas.
- Probado en esta PC: modo prueba, modo real y tarea programada. La creación de la regla por COM y el nuevo `ejecutar_clasificador.bat` aún no se han probado.

### Reglas de clasificación
- AGUA: existe `campoAdicional Medidor`, o `Instalacion` tiene formato `A` + dígitos (ej. `A0101712`).
- TELECOM: `Instalacion` tiene formato `I0`/`IO` + 6 dígitos o `RDD` + 5 dígitos, y no hay `Medidor`.
- REVISAR: señales contradictorias, sin `Instalacion`, sin XML o error al leer.

### Decisiones
- El clasificador reutiliza `extract_xml_fragment` y `extract_fac_register` de `facs_manager.py`. No se modificó ese archivo.
- Los informes van a `data/informes/informe_AAAA-MM-DD.csv`. El registro de procesados va en `data/informes/procesados.json`.
- Modo prueba por defecto (no mueve correos). `--real` mueve y registra.
- Bloqueo en `data/informes/.ejecucion.lock` para evitar ejecuciones simultáneas.
- Protección principal contra reprocesar: el correo sale de `FACS`. El registro es respaldo.

### Hallazgo
- `process_all_xml_facs` incluiría facturas de agua en `facturas.csv` (ej. `A0101712`). Por eso el CSV de telecom debe generarse solo con los XML clasificados como TELECOM.

### Pendiente
1. ~~Validar la regla con un XML de telecom real.~~ Hecho: `FAC063848613` (I0273682) clasificada como TELECOM.
2. ~~Ejecutar en modo prueba y revisar el informe.~~ Hecho el 28/10/2026: 7 correos, Telecom=1, Agua=6, Revisar=0.
3. Modo real ejecutado el 28/10/2026: 7 correos movidos (6 a AGUA, 1 a TELECOM).
4. Tarea programada `FACRET_ClasificadorETAPA` cada 5 minutos, ejecuta `src/scripts/ejecutar_clasificador.bat`. Log en `data/informes/tarea.log`. Cambiar a cada hora cuando se valide el funcionamiento (requiere autorización).
4. Crear la tarea de Windows cada 5 minutos, luego cada hora (requiere autorización explícita).

---

## Reglas operativas: clasificador de facturas

- Procedimiento de instalación y solución de problemas: `docs/GUIDES/clasificador_facturas.md`.
- Mantener la tarea programada activa solo en la PC principal. Las carpetas viajan por IMAP, pero el registro (`procesados.json`) y los informes son locales.
- No versionar `facret/data/informes/`: contiene datos reales de facturas. Ya está en `.gitignore`.
- La regla `ETAPA a FACS` se crea con `src/scripts/crear_regla_outlook.bat`; la tarea con `src/scripts/instalar_tarea.bat`. No crear ni modificar ambas a mano.
- Remitente de ETAPA: `info@comunicados-etapa.com`. Debe coincidir exactamente en la regla y en `outlook_reader.py`.
