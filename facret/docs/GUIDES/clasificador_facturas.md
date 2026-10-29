# Clasificador automático de facturas ETAPA

Separa las facturas de ETAPA que llegan a Outlook en TELECOM, AGUA o REVISAR, mueve cada correo a su carpeta y genera un informe diario.

---

## Componentes

| Archivo | Función |
|---|---|
| `src/logic/facs_clasificador.py` | Decide el tipo a partir del XML. No usa Outlook. |
| `src/logic/outlook_reader.py` | Conecta con Outlook clásico, lee `FACS` y mueve correos. |
| `src/scripts/clasificar_facturas.py` | Punto de entrada. Modo prueba por defecto; `--real` mueve correos. |
| `src/scripts/ejecutar_clasificador.bat` | Lo ejecuta la tarea programada en modo real. |
| `src/scripts/instalar_tarea.bat` | Crea la tarea programada cada 5 minutos. |
| `src/scripts/crear_regla_outlook.bat` | Crea en Outlook la regla `ETAPA a FACS`. |
| `src/scripts/crear_regla_outlook.py` | Lógica de la regla. Lo llama el `.bat`. |

**Salidas** (en `facret/data/informes/`, no versionadas):
- `informe_AAAA-MM-DD.csv`: una fila por correo revisado.
- `procesados.json`: correos ya movidos. Evita repetir trabajo.
- `tarea.log`: registro de cada ejecución de la tarea.
- `.ejecucion.lock`: existe solo mientras corre el script.

---

## Reglas de clasificación

- **AGUA:** tiene el campo `Medidor`, o `Instalacion` con formato `A` + dígitos (ej. `A0101712`).
- **TELECOM:** `Instalacion` con formato `I0` o `IO` + 6 dígitos, o `RDD` + 5 dígitos, y sin `Medidor`.
- **REVISAR:** señales contradictorias, sin `Instalacion`, sin XML o error al leer.

---

## Instalación en una PC nueva

Requisitos: Windows, Outlook clásico con la cuenta de Simbra configurada, Python 3.11, Poetry.

1. Clonar o actualizar el repositorio y entrar a `facret`:
   ```
   git pull
   poetry install
   ```
2. En Outlook, crear dentro de `Bandeja de entrada > CONTRACT > ETAPA > FACS` las carpetas `AGUA`, `TELECOM` y `REVISAR`. Las carpetas viajan por IMAP, así que puede que ya existan.
3. Crear la regla de movimiento. Desde `facret`:
   ```
   src\scripts\crear_regla_outlook.bat
   ```
   Verifica en **Archivo → Administrar reglas y alertas** que aparezca `ETAPA a FACS`. Si el script ya la creó, no la duplica.
4. Crear la tarea programada:
   ```
   src\scripts\instalar_tarea.bat
   ```
5. Verificar (ver sección siguiente).

Los dos scripts pueden ejecutarse varias veces sin efectos adicionales.

---

## Verificación

1. Prueba manual en modo simulación, sin mover nada:
   ```
   poetry run python src\scripts\clasificar_facturas.py
   ```
   Debe terminar con una línea `Modo prueba: N correo(s) revisados...`.
2. Esperar hasta 5 minutos y revisar `data\informes\tarea.log`. Cada ejecución real agrega una línea con sus conteos.
3. Mover un correo de prueba de `ETAPA` a `FACS` y comprobar que sale de `FACS` y llega a `AGUA` o `TELECOM`.

---

## Regla: una sola PC con la tarea activa

Las carpetas y los correos se comparten por IMAP, pero `procesados.json`, los informes y la tarea son locales a cada PC. Si la tarea corre en dos PC a la vez, pueden intentar mover el mismo correo.

Mantén la tarea activa solo en la PC principal. La regla de Outlook también debe revisarse: en cuentas IMAP suele ejecutarse en el cliente, así que si Outlook está abierto con la regla en dos PC, ambas pueden mover el mismo correo.

---

## Solución de problemas

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `tarea.log` no crece | La PC estaba apagada o Outlook cerrado | Abrir Outlook. La tarea solo corre con la sesión iniciada. |
| `tarea.log` muestra "Otra ejecución está en curso" | Quedó un `.ejecucion.lock` de una corrida interrumpida | Borrar `data\informes\.ejecucion.lock` si ninguna ejecución está activa. Se considera obsoleto a los 30 minutos. |
| Un correo no se mueve | El remitente no coincide exactamente | Revisar que sea `info@comunicados-etapa.com`. |
| Un correo se clasifica como REVISAR | El XML no tiene el patrón de telecom o agua | Revisar la fila en el informe, columna `evidencia`. |
| Un correo ya procesado vuelve a `FACS` y se ignora | Está en `procesados.json` | Borrar su bloque en el archivo, o el archivo completo para reprocesar todo. |
| `poetry` no se reconoce en la tarea | `poetry` no está en el PATH del usuario | Agregar la carpeta de `poetry.exe` al PATH y volver a ejecutar `instalar_tarea.bat`. |

---

## Qué no está en el repositorio

- `data/informes/`, por contener datos reales de facturas.
- La regla y las carpetas de Outlook, que viven en el perfil de cada PC. Se recrean con los scripts indicados.
- La tarea programada, que se crea con `instalar_tarea.bat`.
