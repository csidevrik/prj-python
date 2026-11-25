# Contexto
Tengo una app de escritorio en Python + Flet, hecha con componentes al estilo React, con un dashboard: menú desplegable a la izquierda y panel de contenido a la derecha. Procesa facturas y retenciones de ETAPA EP para EMOV EP. Quiero agregar un panel nuevo, "Cargar facturas", que registre automáticamente las facturas a pagar en la plataforma "Pago Empresas" de ETAPA (https://mietapa.etapa.net.ec/mi_etapa/hloginem.aspx) usando Playwright para Python.

# Paso 0 (obligatorio, sin escribir código)
Analiza mi app: estructura de carpetas, cómo se definen y componen los componentes, cómo se arma el dashboard, el menú lateral y los paneles, cómo se navega entre ellos y dónde se leen los XML/PDF. Luego propón:
- dónde va la opción "Cargar facturas" en el menú y cómo encaja el panel siguiendo MIS patrones de componentes;
- la estructura de archivos nueva.
Espera mi visto bueno antes de implementar.

# Panel "Cargar facturas" (lo que quiero ver)
- Botón "Seleccionar archivo" (FilePicker) para CSV o XLSX.
- Vista previa de las filas leídas.
- Por defecto la app CREA una orden de pago nueva (ver sección "Orden de pago"). Opción avanzada: campo "Usar orden existente" para reanudar una orden que la propia app creó.
- Botón "Iniciar sesión en ETAPA" y botón "Ejecutar carga".
- Vista en vivo de lo que hace el navegador: barra de progreso por lote, log en vivo y una captura de pantalla del navegador que se actualiza cada 1-2 s (page.screenshot -> ft.Image).
- Tabla de resultados por factura y botón "Descargar reporte".

# Sobre el navegador embebido
Playwright NO puede controlar un WebView dentro de Flet: el WebView es otro motor de navegador. Propuesta, evalúala y dime si hay algo mejor:
- Playwright abre su propio Chromium visible (headless=False), con perfil persistente en una carpeta de la app.
- El usuario hace ahí el login y el reCAPTCHA. Luego puede minimizar esa ventana.
- El panel de Flet muestra el espejo en vivo (capturas) y el progreso.
- Corre Playwright fuera del hilo de la UI (async o thread) para no congelar Flet.
Si existe un WebView para Flet en Windows que sirva solo para MOSTRAR, indícalo, pero la automatización debe seguir siendo Playwright.

# Entrada
El archivo que ya genera mi app. NO cambiar su formato. Columnas:
- code_inst (código de instalación o servicio): OBLIGATORIA.
- number_fac (formato FAC001003055751634; en el sitio aparece como FAC001-003-055751634; comparar ignorando guiones): OBLIGATORIA.
- valor de la factura SIN IVA: opcional, solo para control.
Una instalación puede tener 2 o más facturas (mismo code_inst, distinta factura): agregar todas.

# Control de valores (IVA)
- ETAPA muestra cada factura CON IVA 15 %. Mi archivo trae el valor SIN IVA a propósito, para revisar errores de cálculo.
- La carga usa solo code_inst + number_fac. El valor no bloquea la carga.
- Por cada factura: esperado = round(base * 1.15, 2); diferencia = valor_etapa - esperado. Si |diferencia| > 0.01, marcar DIFERENCIA_VALOR en el reporte y avisar en la UI (sin detener la carga).
- Mostrar total sin IVA del archivo, total esperado con IVA y total real de la orden.
- Caso real validado: 103 facturas, base 11965.11, orden final 13759.85 (diferencia total 0.03 por redondeo).

# Orden de pago (regla de negocio)
- Cada mes se registra en una orden NUEVA. Las órdenes "Procesada" ya no se pueden editar.
- En la lista pueden existir órdenes "Creada" con valor 0,00 que NO son mías (las creó otro usuario de la misma cuenta corporativa). NUNCA usarlas ni anularlas.
- Flujo por defecto: pulsar el botón "Nueva Orden" de horpagempre.aspx, completar lo que pida y guardar. Identificar el Id de la orden recién creada comparando la lista de órdenes ANTES y DESPUÉS de crearla (la nueva es la que aparece con estado "Creada" y valor 0,00), y guardar ese Id en el estado local de la app.
- Reanudar: si la ejecución se corta (sesión vencida, error), continuar en la orden guardada en el estado local, nunca crear otra.
- El formulario de "Nueva Orden" NO está documentado todavía. Antes de implementarlo, ayúdame a grabarlo con `playwright codegen https://mietapa.etapa.net.ec/mi_etapa/hloginem.aspx` y documenta sus campos e ids aquí. No inventes selectores.
- Anular órdenes: la app NO anula nada. Si hay que anular una orden de prueba, lo hago yo a mano. Una orden "Anulada" es irreversible: queda en la lista con su valor, sin lupa ni acciones.
- Pendiente de confirmar en la primera prueba: si al anular una orden ETAPA libera sus facturas. Si una factura que estaba en una orden anulada no aparece al consultar su instalación, marcarla como NO_DISPONIBLE y avisarme (no es un error del script).

# URLs del sitio (definirlas como constantes en infrastructure/etapa_playwright.py)
BASE_URL = "https://mietapa.etapa.net.ec/mi_etapa/"
- Login:                 https://mietapa.etapa.net.ec/mi_etapa/hloginem.aspx
- Lista de órdenes:      https://mietapa.etapa.net.ec/mi_etapa/horpagempre.aspx
- Detalle de una orden:  https://mietapa.etapa.net.ec/mi_etapa/hwdeupag.aspx?<idOrden>   (ej. ...hwdeupag.aspx?7971)
- Búsqueda de deudas:    https://mietapa.etapa.net.ec/mi_etapa/hagdeord.aspx   (se llega desde el botón, no abrir directo)
- Carrito de pagos:      https://mietapa.etapa.net.ec/mi_etapa/hverdeor.aspx   (se llega desde Continuar, no abrir directo)
Solo el login y el detalle de la orden se abren escribiendo la URL; las demás páginas dependen del estado de la sesión y se alcanzan con los botones.
La URL base debe poder cambiarse desde la configuración de la app (por si ETAPA la cambia), sin tocar el código.

# Cómo funciona el sitio (descubierto con DevTools, GeneXus .NET detrás de Cloudflare)
1. Login hloginem.aspx: usuario, clave y reCAPTCHA. SIEMPRE manual. Detectar el login exitoso cuando la URL llega a horpagempre.aspx. Nunca guardar ni escribir la contraseña en el código.
2. horpagempre.aspx: lista de órdenes (Id, fecha, estado, valor, lupa para agregar deudas, Anular, Generar Pago, Exportar) y botón "Nueva Orden" al final de la lista. La lupa solo aparece en órdenes "Creada".
3. hwdeupag.aspx?<idOrden>: detalle de la orden (lista de instalaciones y facturas ya cargadas). Esperar carga completa y luego pulsar #AGREGARDEUDA ("Agregar Deuda por Instalación").
   PROHIBIDO usar #AGREGARDEUDAPORRUC: se cuelga, Cloudflare devuelve 524 y deja la sesión inutilizable unos 10 min.
4. hagdeord.aspx (búsqueda): llenar #vINSTALACION, pulsar #CONSULTAR y esperar filas tr[id^="GriddeudasContainerRow_"]. En cada fila N (sufijo 0001, 0002...):
   - factura: #span_vXSERVICIO_000N
   - instalación: #span_vXIDREFERENCIA_000N
   - valor con IVA: #span_vXSUBTOTAL_000N (formato "1.151,15")
   - agregar al carrito: img #vXAGREGAR_000N
   - contador del carrito: #W0008VERCARRITO (value); total: #W0008TOTAL
   Tras cada clic, confirmar que el contador sube. Si la consulta no devuelve filas, el sitio NO muestra mensaje: registrar SIN_RESULTADOS.
5. #CONTINUAR lleva a hverdeor.aspx (Carrito de pagos). Continuar NO guarda. Verificar el número de filas ([id^="W0006vXELIMINAR_"]) y el Subtotal contra lo esperado; si no coincide, NO guardar y avisar.
6. #PAGARTC es el botón "Guardar Detalles" (el id está mal nombrado). Tarda unos 23-28 s y regresa a horpagempre.aspx. Verificar que el valor de la orden subió exactamente la suma del lote.
7. NO pulsar Anular, "Todos" (vacía el carrito) ni Generar Pago (fase 2).

# Reglas obligatorias
- Lotes de máximo 10 facturas: agregar, continuar, verificar, guardar, verificar el total de la orden.
- La sesión expira sola a los 25-30 min y el carrito sin guardar se pierde. Si aparece hloginem.aspx: pausar, pedir login en la UI y reanudar desde el último lote guardado.
- Idempotencia: antes de cada lote, leer el detalle de la orden y saltar las facturas que ya estén en ella.
- Esperas por condición (selector o URL), no sleeps fijos; timeouts generosos.
- El sitio envía 2 POST por clic: no reintentar clics a ciegas.
- Antes del primer guardado de cada ejecución, mostrar el resumen y pedir confirmación en la UI.

# Salida
Reporte CSV por factura: code_inst, number_fac, valor_sin_iva, valor_esperado_con_iva, valor_etapa, diferencia, estado (AGREGADA, YA_EN_ORDEN, SIN_RESULTADOS, FACTURA_NO_ENCONTRADA, DIFERENCIA_VALOR, ERROR) y lote.

# Arquitectura (clean architecture)
- domain/: modelos (FacturaPago, ResultadoCarga), reglas de IVA y comparación, parser de valores ("1.151,15" -> Decimal 1151.15). Usar Decimal, nunca float.
- infrastructure/etapa_playwright.py: único lugar con URLs, selectores e ids del sitio (constantes). Funciones: esperar_login, abrir_orden, leer_detalle_orden, consultar_instalacion, agregar_factura, continuar, guardar, capturar_pantalla.
- application/cargar_facturas.py: orquesta lotes, reanudación e idempotencia; no depende de Flet; emite eventos de progreso.
- ui/: componente(s) Flet del panel, siguiendo mis patrones.
- Tests del dominio y del parser, sin navegador.

# Fase 2 (NO implementar todavía, solo dejar el espacio en el diseño)
Después de cargar las facturas:
- Botón para elegir la carpeta con las retenciones (PDF) y el archivo SPI del pago.
- Unir las retenciones y el SPI en un solo PDF.
- Subirlo en la opción "Generar Pago" de la orden.
La tabla de horpagempre.aspx tiene columnas ocultas que se muestran según el estado: "Generar Pago", "Carga Comprobante", "Validar" y "Usuario Ingresa". El flujo probable es Generar Pago -> Carga Comprobante (retenciones + SPI) -> Validar. Todavía no está documentado; lo agregaré cuando lo tenga.