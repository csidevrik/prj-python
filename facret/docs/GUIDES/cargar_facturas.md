# Cargar facturas en Pago Empresas de ETAPA

Guía para registrar cada mes las facturas de `facturas.csv` en una orden de pago del sitio
"Pago Empresas" de ETAPA (`https://mietapa.etapa.net.ec/mi_etapa/`), usando el script de Playwright.

Estado a noviembre de 2026: funciona solo como **script de consola**. Todavía no tiene panel en la app de escritorio.
La primera carga real (103 facturas) dejó 50 guardadas y verificadas en un solo lote. El segundo lote falló por un
error de lectura que se describe en la sección 6.

---

## 1. Qué hace y qué no hace

**Hace:**
- Lee `facturas.csv`, el archivo que genera FACRET a partir de los XML.
- Entra a una orden que ya creaste a mano.
- Busca cada instalación, agrega cada factura al carrito y comprueba el carrito antes de guardar: las facturas una por una y el subtotal.
- Guarda el lote y luego relee el detalle de la orden para confirmar que están todas, sin sobrantes ni repetidas.
- Si se corta, se puede volver a correr: relee la orden y carga solo lo que falta.

**No hace nunca:**
- Anular órdenes.
- Usar "Agregar deuda por RUC".
- Vaciar el carrito con "Todos".
- Pulsar "Generar Pago".
- Tocar órdenes de otras personas.

Una prueba automática comprueba que esas acciones no aparezcan en el código.

**No guarda la contraseña.** El inicio de sesión y el reCAPTCHA siempre los haces tú.

---

## 2. Procedimiento mensual (paso a paso)

### Antes de empezar
1. Genera `facturas.csv` con FACRET, en "Gestión FACS". Queda en `<carpeta_trabajo>\facs\facturas.csv`.
2. Comprueba que existe `%LOCALAPPDATA%\FACRET\etapa_orden.json` con tus datos de registro.
   - Si no existe, copia `src/config/etapa_orden.example.json` y llénalo.
   - Ese archivo está **fuera del repositorio** a propósito.
3. Cierra todas las ventanas de Chrome que usen el perfil `facret_cdp`.

### Paso 1. Revisar sin escribir nada (recomendado)
```powershell
cd "C:\Users\adminos\dev\github\prj-python\facret"
poetry run python src/scripts/cargar_facturas_etapa.py --csv "<carpeta_trabajo>\facs\facturas.csv" --solo-revisar
```
Revisa qué facturas ya están en órdenes abiertas. No crea ni agrega nada.

### Paso 2. Abrir Chrome con depuración remota
En una ventana de PowerShell aparte:
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="$env:TEMP\facret_cdp" --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-renderer-backgrounding
```
- Las tres últimas opciones evitan que Chrome frene la página cuando la ventana queda tapada, por ejemplo al pasar a Excel.
- Sin ellas, las esperas se vencen.

### Paso 3. Crear la orden a mano
1. Inicia sesión en esa ventana de Chrome.
2. Pulsa "Nueva Orden", guarda y anota el **Id** de la orden nueva.
3. Si el carrito tiene restos de otra vez, vacíalo **tú** con "Todos".

### Paso 4. Correr la carga
```powershell
poetry run python src/scripts/cargar_facturas_etapa.py --csv "<carpeta_trabajo>\facs\facturas.csv" --cdp --orden <ID_NUEVA> --lote 10
```
1. Escribe `SI` cuando lo pida.
2. Al empezar, el log muestra cuántas facturas hay y cómo se reparten en lotes. El reparto se calcula con los registros del CSV, sin contar la cabecera.
3. **No toques la ventana de Chrome mientras corre.** Puedes usar otras ventanas si abriste Chrome con las opciones del paso 2.
4. Al terminar, el script pide que cierres sesión en ETAPA y presiones Enter. No cierra Chrome.

### Paso 5. Si se detiene
1. Lee el log `data\informes\cargas\ejecucion_*.log`. La última línea dice por qué se detuvo.
2. Si quedaron facturas en el carrito sin guardar, vacíalo con "Todos".
3. Cierra sesión y vuelve a entrar.
4. Corre otra vez el **mismo comando** con la misma `--orden`. El script relee la orden y carga solo las pendientes.

### Paso 6. Comprobar el resultado
1. El reporte `data\informes\cargas\carga_*.csv` tiene una fila por factura, con su estado y la diferencia de valor.
2. Compara el valor de la orden en el sitio con el total esperado con IVA que muestra el log al inicio.

---

## 3. Opciones del script

| Opción | Qué hace |
|---|---|
| `--csv RUTA` | Archivo `facturas.csv` (obligatorio). |
| `--solo-revisar` | Solo lee órdenes abiertas. No escribe nada. |
| `--cdp` | Se conecta al Chrome abierto en el paso 2 (puerto 9222). Sin esta opción abre un Chromium temporal. |
| `--orden ID` | Carga en una orden que ya existe. Es la forma recomendada. |
| `--lote N` | Tamaño de lote. Se recomienda **10** (ver sección 6). Sin esta opción: 10 y luego 20. |
| `--manual` | Tú creas la orden en la ventana y el script la detecta (la última "Creada" con 0,00). |

Lo que produce, en `data\informes\cargas\` (esa carpeta no se sube a Git):
- `ejecucion_*.log`: todo lo que pasó, factura por factura, con tiempos, contador del carrito y peticiones al servidor.
- `carga_*.csv`: el reporte por factura.
- `traza_*.zip`: la traza completa de Playwright. Se ve con `poetry run playwright show-trace "<ruta>"`.
- Carpetas `*_AAAAMMDD_HHMMSS`: captura y HTML de la página cuando algo falla.

El estado para reanudar queda en `%LOCALAPPDATA%\FACRET\etapa_estado.json`.

---

## 4. Archivos de esta funcionalidad

### Código
| Archivo | Para qué sirve | Lo usa |
|---|---|---|
| `src/models/factura_pago.py` | Modelos `FacturaPago`, `ResultadoCarga` y `EstadoFactura`. | Todo lo demás |
| `src/logic/etapa_reglas.py` | IVA 1,15 con redondeo; lee valores como "1.151,15", "1151,15" y "$ 1151.15"; normaliza números de factura (con o sin "FAC" o guiones). | csv, playwright, script |
| `src/logic/etapa_csv.py` | Lee y valida `facturas.csv` (utf-8 o cp1252). | script |
| `src/logic/etapa_orden_datos.py` | Lee y valida los datos de quien registra la orden, guardados en `%LOCALAPPDATA%`. | playwright, script |
| `src/logic/cargar_facturas.py` | Orquestador: lotes, reconciliación con el detalle, detección de duplicadas y órdenes ajenas, reanudación. No usa Playwright, así se prueba con un sitio falso. | script |
| `src/logic/etapa_playwright.py` | **Único** archivo que conoce el sitio: direcciones, selectores, clics, esperas, evidencia y monitor de red. | script, diagnóstico |
| `src/scripts/cargar_facturas_etapa.py` | Punto de entrada de la carga (opciones de la sección 3). | Tú |
| `src/scripts/diagnostico_etapa.py` | Herramienta de solo lectura: guarda la lista de órdenes y el detalle de una orden en `data\informes\diagnostico\`. Sirve si ETAPA cambia el sitio y hay que revisar sus pantallas. | Tú, cuando haga falta |
| `src/config/etapa_orden.example.json` | Plantilla vacía de `etapa_orden.json`. | Tú, la primera vez |
| `docs/etapa/PROMPT_carga_facturas.md` | Requerimiento original. | Referencia |

### Pruebas (`poetry run pytest`)
No forman parte del programa: se ejecutan para verificar que un cambio no rompió nada. Ninguna abre el navegador ni toca ETAPA.

| Archivo | Qué verifica |
|---|---|
| `tests/conftest.py` | Hace que las pruebas encuentren la carpeta `src`. |
| `tests/test_etapa_reglas.py` | IVA, lectura de valores, normalización de números de factura. |
| `tests/test_etapa_csv.py` | Lectura del CSV, columnas obligatorias, codificaciones. |
| `tests/test_etapa_orden_datos.py` | Validación de los datos de registro (obligatorios y longitudes). |
| `tests/test_cargar_facturas.py` | Orquestador con un sitio falso: reparto de lotes según el CSV, reanudación, duplicadas, sobrantes, órdenes ajenas y anuladas. |
| `tests/test_lectura_carrito.py` | Lectura del texto del carrito (facturas y subtotal). |
| `tests/test_etapa_playwright_solo_lectura.py` | Seguridad: solo ciertas funciones pueden hacer clic, y no aparecen "Anular", "Generar Pago", "Todos" ni "Agregar por RUC". |

---

## 5. Cómo se comporta el sitio (aprendido en las cargas reales)

**Flujo de pantallas:**
1. Lista de órdenes (`horpagempre.aspx`).
2. Lupa de la orden, que abre su detalle (`hwdeupag.aspx`).
3. "Agregar Deuda por Instalación", que abre la búsqueda (`hagdeord.aspx`).
4. CONTINUAR, que abre el carrito (`hverdeor.aspx`).
5. "Guardar Detalles".

**Comportamientos que hay que tener en cuenta:**
- Entrar al detalle de la orden escribiendo la dirección no funciona bien. Hay que entrar con la lupa.
- Algunas instalaciones tienen 2 facturas (instalación y consumo).
- La grilla de búsqueda reutiliza las filas de la consulta anterior y cambia las celdas poco a poco. Solo se acepta cuando todas las filas son de la instalación consultada y dos lecturas seguidas coinciden.
- Cada clic manda 2 peticiones al servidor.
- El carrito del servidor puede guardar **restos ocultos** de una corrida anterior aunque el contador diga 0. Por eso, antes de cada lote, el script abre el carrito real, y tú lo vacías con "Todos" entre corridas.
- Después de guardar, el sitio a veces no vuelve a la lista aunque sí guardó. La verdad está en el detalle de la orden, no en el mensaje.
- Una orden anulada libera sus facturas.
- Tiempos medidos: de 1 a 4 s por factura y de 25 a 90 s para guardar un lote. La sesión dura de 25 a 30 minutos.
- **Tamaño de lote** según las cargas reales:
  - 10 y 13 funcionaron siempre.
  - 20 cerró la sesión al pulsar CONTINUAR.
  - 30 mostró "Datos No Guardados" y dejó restos ocultos.
  - 50 funcionó una vez (26-nov-2026).
  - Por prudencia se recomienda 10.

---

## 6. Problemas conocidos y mejoras pendientes (no aplicadas)

Quedan para la próxima carga real. Cada una se aplica con autorización, con sus pruebas y en su propio commit.

| # | Mejora | Motivo |
|---|---|---|
| H | Leer la grilla de búsqueda en una sola lectura dentro del navegador (`pagina.evaluate`), no celda por celda. | **Fue el fallo del 26-nov**: al pasar de una instalación con 2 filas (I0277079) a una con 1 (RDD01974), la fila 2 desapareció a mitad de la lectura y la espera se colgó 30 s. Puede pasar con cualquier tamaño de lote. |
| A | Limitar el lote a un máximo de 13 (10 por defecto) y avisar si se pide más. | Resultados del sitio con 20 y 30 (sección 5). Hay que ajustar también `_resumen_inicial` del script y las pruebas que usan 12 facturas. |
| B | Contar también las órdenes en "Validación" como ocupadas, y usar la misma lista en `_revisar` del script. | Una orden en validación tiene sus facturas tomadas. Confirmar cómo escribe el sitio "Validación". |
| C | Esperar a la red contando las peticiones en curso (solo las de `mietapa.etapa.net.ec`), en vez de `networkidle`. | `networkidle` vuelve al instante si la página ya cargó y no ve las peticiones de GeneXus. |
| D | Espera de búsqueda de 45 s; si el contador no subió, releerlo una vez antes de dar error. | El sitio a veces está lento y el contador se actualiza tarde. |
| E | Si CONTINUAR no está visible después de que la red se calme, considerar el carrito vacío sin esperar 15 s. | Hoy se pierden 15 s por lote. Hay que mirar primero la red para no saltarse el control de restos ocultos. |
| F | Al conectarse a Chrome, usar la pestaña de `mietapa`, no la primera que encuentre. | Evita trabajar sobre otra pestaña. |

**Más adelante:**
- Crear la orden desde el script, en vez de a mano.
- Panel "Cargar facturas" en la app de escritorio.
- Fase 2: retenciones PDF y SPI.
