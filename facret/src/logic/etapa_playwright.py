# =============================
# logic/etapa_playwright.py
# =============================
"""
Acceso al sitio de Pago Empresas de ETAPA. Único módulo que importa Playwright.
Las funciones de lectura solo navegan, esperan el login manual, capturan y vuelcan páginas.
La única función que escribe es crear_orden, que solo guarda tras la confirmación del usuario.
"""
import json
import re
import time
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Callable

from logic.etapa_orden_datos import DatosOrden
from logic.etapa_reglas import (
    diferencia,
    hay_diferencia,
    normalizar_number_fac,
    normalizar_numero_mostrado,
    parse_valor,
    valor_esperado_con_iva,
)
from logic.logger import get_logger
from models.factura_pago import EstadoFactura, FacturaPago, ResultadoCarga
from playwright.sync_api import BrowserContext, Page, Playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

logger = get_logger(__name__)

BASE_URL = "https://mietapa.etapa.net.ec/mi_etapa/"
URL_LOGIN = BASE_URL + "hloginem.aspx"
URL_ORDENES = BASE_URL + "horpagempre.aspx"
URL_DETALLE_ORDEN = BASE_URL + "hwdeupag.aspx?{id_orden}"

TIMEOUT_LOGIN_MS = 10 * 60 * 1000
TIMEOUT_CARGA_MS = 30 * 1000


def abrir_navegador() -> tuple[Playwright, BrowserContext]:
    """Sesión temporal: cookies y login viven solo mientras la ventana está abierta; nada queda en disco."""
    playwright = sync_playwright().start()
    navegador = playwright.chromium.launch(headless=False)
    contexto = navegador.new_context(viewport={"width": 1280, "height": 900})
    return playwright, contexto


def esperar_login(pagina: Page, timeout_ms: int = TIMEOUT_LOGIN_MS) -> bool:
    """Espera a que el usuario inicie sesión manualmente. El login es exitoso cuando la URL llega a la lista de órdenes."""
    pagina.goto(URL_LOGIN, wait_until="domcontentloaded")
    try:
        pagina.wait_for_url("**/horpagempre.aspx*", timeout=timeout_ms)
    except PlaywrightTimeout:
        return False
    return True


def ir_a_ordenes(pagina: Page) -> None:
    pagina.goto(URL_ORDENES, wait_until="load", timeout=TIMEOUT_CARGA_MS)


def abrir_orden(pagina: Page, id_orden: int) -> None:
    pagina.goto(URL_DETALLE_ORDEN.format(id_orden=id_orden), wait_until="load", timeout=TIMEOUT_CARGA_MS)


def capturar_pantalla(pagina: Page) -> bytes:
    return pagina.screenshot(type="jpeg", quality=60)


def volcar_pagina(pagina: Page, carpeta: Path, nombre: str) -> tuple[Path, Path]:
    """Guarda el HTML y la lista de elementos con id (tipo, id, valor, texto) para documentar selectores."""
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta_html = carpeta / f"{nombre}.html"
    ruta_ids = carpeta / f"{nombre}_ids.json"
    ruta_html.write_text(pagina.content(), encoding="utf-8")
    elementos = pagina.eval_on_selector_all(
        "[id]",
        "els => els.map(e => ({tag: e.tagName, id: e.id, type: e.type || '', "
        "value: (e.value || '').slice(0, 80), texto: (e.innerText || '').trim().slice(0, 80)}))",
    )
    ruta_ids.write_text(json.dumps(elementos, ensure_ascii=False, indent=2), encoding="utf-8")
    return ruta_html, ruta_ids


class SesionVencida(Exception):
    pass


class OrdenAmbigua(Exception):
    pass


class OperacionCancelada(Exception):
    pass


class GuardadoNoConfirmado(Exception):
    pass


class ListaDeOrdenesVacia(Exception):
    pass


TIMEOUT_GUARDADO_CREAR_MS = 90 * 1000
CARPETA_EVIDENCIA = Path(__file__).resolve().parents[2] / "data" / "informes" / "cargas"


def guardar_evidencia(pagina: Page, nombre: str) -> Path:
    """Captura y HTML de la página actual, para revisar qué respondió el sitio. No hace ninguna acción."""
    CARPETA_EVIDENCIA.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = CARPETA_EVIDENCIA / f"{nombre}_{marca}"
    pagina.screenshot(path=f"{ruta}.jpg", type="jpeg", quality=70, full_page=True)
    Path(f"{ruta}.html").write_text(pagina.content(), encoding="utf-8")
    return ruta


def _esperar_confirmacion_guardado(pagina: Page, timeout_ms: int) -> bool:
    """Espera a que el sitio confirme el guardado: vuelve a la lista o el botón Guardar deja de estar visible."""
    esperado = 0
    while esperado < timeout_ms:
        if "horpagempre" in pagina.url:
            return True
        boton = pagina.locator("#GUARDAR")
        if boton.count() == 0 or not boton.first.is_visible():
            return True
        pagina.wait_for_timeout(1000)
        esperado += 1000
    return False


def listar_ordenes(pagina: Page) -> list[dict]:
    """Filas de horpagempre.aspx: id, fecha, hora (UTC según el sitio), estado y valor."""
    return pagina.locator("tr").evaluate_all(
        """rows => rows
            .map(r => r.innerText.trim().split(/\\s+/))
            .filter(p => /^\\d{3,7}$/.test(p[0]))
            .map(p => ({id: p[0], fecha: p[1], hora_utc: p[2], estado: p[3], valor: p[4] || ''}))"""
    )


def crear_orden(pagina: Page, datos: DatosOrden, confirmar: Callable[[], bool]) -> str:
    """Crea una orden nueva y devuelve su Id. Escribe en ETAPA: solo se guarda si confirmar() devuelve True."""
    ir_a_ordenes(pagina)
    if "hloginem" in pagina.url:
        raise SesionVencida()

    pagina.wait_for_load_state("networkidle")
    antes_ordenes = listar_ordenes(pagina)
    if not antes_ordenes:
        raise ListaDeOrdenesVacia("la lista llegó vacía antes de crear; no se continúa")
    antes = {o["id"] for o in antes_ordenes}

    pagina.locator("#NUEVAORDEN").click()
    pagina.wait_for_url(re.compile(r"hnuorpag\.aspx"))
    pagina.locator("#vXUSINGNOM").wait_for()

    campos = {
        "#vXUSINGNOM": datos.nombre,
        "#vXUSINGAPE": datos.apellido,
        "#vXINSTNOMB": datos.institucion,
        "#vXINSUSCAR": datos.cargo,
        "#vXUSINGTEL": datos.telefono,
    }
    for selector, valor in campos.items():
        campo = pagina.locator(selector)
        if campo.input_value().strip() == valor:
            continue
        campo.fill(valor)
        campo.press("Tab")
        _esperar_red_tranquila(pagina)

    if not confirmar():
        raise OperacionCancelada("el usuario no confirmó la creación; no se guardó nada")

    _esperar_red_tranquila(pagina)
    pagina.locator("#GUARDAR").click()
    if not _esperar_confirmacion_guardado(pagina, TIMEOUT_GUARDADO_CREAR_MS):
        ruta = guardar_evidencia(pagina, "crear_orden_sin_confirmar")
        raise GuardadoNoConfirmado(f"el sitio no confirmó el guardado en {TIMEOUT_GUARDADO_CREAR_MS // 1000} s; "
                                   f"evidencia en {ruta}. No se volvió a intentar")

    if "horpagempre" not in pagina.url:
        pagina.locator("#REGRESAR").click()
        try:
            pagina.wait_for_url(re.compile(r"horpagempre\.aspx"), timeout=TIMEOUT_CARGA_MS)
        except PlaywrightTimeout:
            ruta = guardar_evidencia(pagina, "crear_orden_regresar_fallo")
            raise GuardadoNoConfirmado(f"no se volvió a la lista tras guardar; evidencia en {ruta}")
    pagina.wait_for_load_state("networkidle")

    nuevas = [o for o in listar_ordenes(pagina) if o["id"] not in antes]
    if len(nuevas) != 1:
        ruta = guardar_evidencia(pagina, "crear_orden_ambigua")
        logger.error("crear_orden: se esperaba 1 orden nueva y aparecieron %d; evidencia en %s", len(nuevas), ruta)
        raise OrdenAmbigua([o["id"] for o in nuevas])
    orden = nuevas[0]
    if orden["estado"] != "Creada" or orden["valor"] != "0,00":
        ruta = guardar_evidencia(pagina, "crear_orden_estado_raro")
        logger.error("crear_orden: la orden nueva %s no tiene estado Creada y valor 0,00; evidencia en %s",
                     orden["id"], ruta)
        raise OrdenAmbigua([orden["id"]])
    logger.info("Orden creada en ETAPA: id %s, fecha %s %s", orden["id"], orden["fecha"], orden["hora_utc"])
    return orden["id"]


class SesionDeCargaVencida(SesionVencida):
    pass


class CarritoConRestos(Exception):
    pass


class CarritoNoCoincide(Exception):
    pass


class ErrorAlAgregar(Exception):
    pass


PATRON_FILA_BUSQUEDA = 'tr[id^="GriddeudasContainerRow_"]'
TIMEOUT_BUSQUEDA_MS = 20 * 1000
TIMEOUT_GUARDADO_MS = 90 * 1000
PASO_ESPERA_MS = 300
ESPERA_FACTURA_EN_GRILLA_MS = 10 * 1000


def _texto_visible(pagina: Page, selector: str) -> str:
    loc = pagina.locator(selector)
    if loc.count() == 0:
        return ""
    try:
        return loc.first.input_value().strip()
    except Exception:
        return loc.first.inner_text().strip()


def _contador_carrito(pagina: Page) -> int:
    texto = _texto_visible(pagina, "#W0008VERCARRITO")
    return int(texto) if texto.isdigit() else 0


def _verificar_sesion(pagina: Page) -> None:
    if "hloginem" in pagina.url:
        raise SesionDeCargaVencida()


def _abrir_detalle(pagina: Page, id_orden: str) -> None:
    abrir_orden(pagina, int(id_orden))
    _verificar_sesion(pagina)
    pagina.wait_for_load_state("load")


def _abrir_busqueda(pagina: Page, id_orden: str) -> None:
    """Entra a la orden desde la lista, pulsando su lupa (no por dirección web)."""
    ir_a_ordenes(pagina)
    _verificar_sesion(pagina)
    pagina.wait_for_load_state("networkidle")
    filas = pagina.locator('span[id^="span_vORDPAGID_"]')
    numero_fila = None
    for i in range(filas.count()):
        if filas.nth(i).inner_text().strip() == id_orden:
            numero_fila = (filas.nth(i).get_attribute("id") or "")[-4:]
            break
    if numero_fila is None:
        raise ErrorAlAgregar(f"la orden {id_orden} no aparece en la lista")
    try:
        pagina.locator(f"#vAGREGARDEUDAS_{numero_fila}").click()
        pagina.wait_for_url(re.compile(r"hwdeupag\.aspx"), timeout=TIMEOUT_CARGA_MS)
        _verificar_sesion(pagina)
        boton = pagina.locator("#AGREGARDEUDA")
        boton.wait_for(state="visible", timeout=TIMEOUT_CARGA_MS)
        _esperar_red_tranquila(pagina)
        boton.click()
        pagina.wait_for_url(re.compile(r"hagdeord\.aspx"), timeout=TIMEOUT_CARGA_MS)
        _verificar_sesion(pagina)
        pagina.locator("#vINSTALACION").wait_for(state="visible", timeout=TIMEOUT_CARGA_MS)
    except PlaywrightTimeout:
        ruta = guardar_evidencia(pagina, "abrir_busqueda_fallo")
        raise ErrorAlAgregar(f"no se llegó a la búsqueda de la orden {id_orden} (página actual: "
                             f"{pagina.url.split('?')[0].rsplit('/', 1)[-1]}); evidencia en {ruta}")


def _esperar_red_tranquila(pagina: Page) -> None:
    """GeneXus dispara peticiones al cambiar campos; pulsar un botón con peticiones pendientes lo deja trabado."""
    try:
        pagina.wait_for_load_state("networkidle", timeout=15 * 1000)
    except PlaywrightTimeout:
        pass


def _filas_busqueda(pagina: Page) -> list[dict]:
    filas = []
    loc = pagina.locator(PATRON_FILA_BUSQUEDA)
    for i in range(loc.count()):
        n = (loc.nth(i).get_attribute("id") or "")[-4:]
        filas.append({
            "n": n,
            "factura": _texto_visible(pagina, f"#span_vXSERVICIO_{n}"),
            "instalacion": _texto_visible(pagina, f"#span_vXIDREFERENCIA_{n}"),
            "valor": _texto_visible(pagina, f"#span_vXSUBTOTAL_{n}"),
        })
    return filas


def buscar_instalacion(pagina: Page, codigo: str, log: Callable[[str], None] = lambda m: None) -> list[dict]:
    """Consulta una instalación. Solo acepta filas de esa consulta, nunca restos de la anterior. Vacío = SIN_RESULTADOS."""
    campo = pagina.locator("#vINSTALACION")
    campo.fill(codigo)
    campo.press("Tab")
    _esperar_red_tranquila(pagina)
    pagina.locator("#CONSULTAR").click()
    esperado = 0
    filas = []
    anterior = None
    while esperado < TIMEOUT_BUSQUEDA_MS:
        filas = _filas_busqueda(pagina)
        # El sitio reutiliza la fila de la consulta anterior y actualiza sus celdas una por una:
        # solo se acepta cuando todas las filas son de este código y dos lecturas seguidas coinciden.
        if filas and all(f["instalacion"] == codigo for f in filas):
            if filas == anterior:
                return filas
            anterior = filas
        else:
            anterior = None
        pagina.wait_for_timeout(PASO_ESPERA_MS)
        esperado += PASO_ESPERA_MS
    vistas = sorted({f["instalacion"] for f in filas})[:3]
    log(f"    sin filas de {codigo} en {TIMEOUT_BUSQUEDA_MS // 1000} s (filas en pantalla: {len(filas)}, "
        f"instalaciones vistas: {vistas})")
    return []


def agregar_fila(pagina: Page, n: str) -> None:
    """Un solo clic en agregar. Si el contador salta más de 1, el carrito pudo quedar con repetidas: se detiene."""
    antes = _contador_carrito(pagina)
    pagina.locator(f"#vXAGREGAR_{n}").click()
    esperado = 0
    while esperado < TIMEOUT_BUSQUEDA_MS:
        if _contador_carrito(pagina) > antes:
            break
        pagina.wait_for_timeout(PASO_ESPERA_MS)
        esperado += PASO_ESPERA_MS
    else:
        raise ErrorAlAgregar(f"el carrito no subió desde {antes} tras agregar la fila {n}")
    _esperar_red_tranquila(pagina)
    despues = _contador_carrito(pagina)
    if despues != antes + 1:
        ruta = guardar_evidencia(pagina, "contador_salto")
        raise ErrorAlAgregar(f"el contador saltó de {antes} a {despues} (se esperaba {antes + 1}); "
                             f"el carrito puede tener repetidas; evidencia en {ruta}")


def valor_orden(pagina: Page, id_orden: str) -> Decimal:
    for orden in listar_ordenes(pagina):
        if orden["id"] == id_orden:
            return parse_valor(orden["valor"] or "0")
    raise ValueError("la orden no aparece en la lista")


def facturas_de_orden(pagina: Page, id_orden: str) -> list[str]:
    _abrir_detalle(pagina, id_orden)
    pagina.wait_for_load_state("networkidle")
    numeros = []
    loc = pagina.locator('span[id^="span_vFACNUM_"]')
    for i in range(loc.count()):
        texto = loc.nth(i).inner_text().strip()
        if texto:
            numeros.append(normalizar_numero_mostrado(texto))
    return numeros


def _mismo_numero(mostrado: str, numero: str) -> bool:
    try:
        return normalizar_numero_mostrado(mostrado) == numero
    except ValueError:
        return False


def _resultado_agregado(factura: FacturaPago, valor_etapa: Decimal) -> ResultadoCarga:
    if factura.valor_sin_iva is None:
        return ResultadoCarga(factura, EstadoFactura.AGREGADA, valor_etapa=valor_etapa)
    esperado = valor_esperado_con_iva(factura.valor_sin_iva)
    dif = diferencia(valor_etapa, esperado)
    estado = EstadoFactura.DIFERENCIA_VALOR if hay_diferencia(valor_etapa, esperado) else EstadoFactura.AGREGADA
    return ResultadoCarga(factura, estado, valor_etapa=valor_etapa, valor_esperado=esperado, diferencia=dif)


def cargar_lote(pagina: Page, id_orden: str, lote: list[FacturaPago],
                log: Callable[[str], None] = lambda m: None,
                monitor: "MonitorRed | None" = None) -> list[ResultadoCarga]:
    """Agrega un lote al carrito y lo guarda solo si el carrito coincide. Cada paso se verifica antes del siguiente."""
    log(f"  Entrando a la orden {id_orden} por la lupa...")
    _abrir_busqueda(pagina, id_orden)
    restos = _facturas_en_carrito(pagina, log)
    if restos:
        ruta = guardar_evidencia(pagina, "carrito_con_restos")
        raise CarritoConRestos(f"el carrito del sitio ya tiene {len(restos)} facturas de intentos anteriores "
                               f"(el contador no siempre lo muestra): {restos}; vacíalo a mano con 'Todos' en el "
                               f"carrito y vuelve a correr; evidencia en {ruta}")
    if restos is not None:
        log("  Carrito real vacío. Volviendo a la búsqueda...")
        _abrir_busqueda(pagina, id_orden)
    carrito = _contador_carrito(pagina)
    log(f"  Búsqueda abierta. Carrito: {carrito}")
    if carrito != 0:
        raise CarritoConRestos(f"el carrito tiene {carrito} filas de una ejecución anterior; "
                               "cierra sesión y vuelve a entrar para vaciarlo")

    resultados: list[ResultadoCarga] = []
    agregadas: list[tuple[FacturaPago, Decimal]] = []
    ultimo_codigo = None
    for i, factura in enumerate(lote, start=1):
        log(f"  [{i}/{len(lote)}] {factura.code_inst} {factura.number_fac}")
        if factura.code_inst == ultimo_codigo:
            # Otra factura de la misma instalación: se toma de la misma consulta, releyendo la grilla.
            _esperar_red_tranquila(pagina)
            filas = [f for f in _filas_busqueda(pagina) if f["instalacion"] == factura.code_inst]
        else:
            filas = buscar_instalacion(pagina, factura.code_inst, log)
        ultimo_codigo = factura.code_inst
        coincidencia = next((f for f in filas if _mismo_numero(f["factura"], factura.number_fac)), None)
        esperado = 0
        while coincidencia is None and filas and esperado < ESPERA_FACTURA_EN_GRILLA_MS:
            pagina.wait_for_timeout(PASO_ESPERA_MS)
            esperado += PASO_ESPERA_MS
            filas = [f for f in _filas_busqueda(pagina) if f["instalacion"] == factura.code_inst]
            coincidencia = next((f for f in filas if _mismo_numero(f["factura"], factura.number_fac)), None)
        if coincidencia is not None and esperado:
            log(f"    la factura apareció en la grilla tras {esperado / 1000:.1f} s más de espera")
        if coincidencia is None:
            log(f"    filas vistas: {[(f['factura'], f['instalacion']) for f in filas]}")
            motivo = "sin resultados" if not filas else f"la factura no está entre las {len(filas)} filas"
            ruta = guardar_evidencia(pagina, f"busqueda_{factura.code_inst}")
            raise ErrorAlAgregar(f"{factura.code_inst}: {motivo}; carrito con {len(agregadas)} filas sin guardar; "
                                 f"evidencia en {ruta}")
        valor_etapa = parse_valor(coincidencia["valor"])
        carrito_antes = _contador_carrito(pagina)
        total_antes = _texto_visible(pagina, "#W0008TOTAL")
        marca = monitor.marca() if monitor else None
        inicio = time.monotonic()
        try:
            agregar_fila(pagina, coincidencia["n"])
        except ErrorAlAgregar:
            red = monitor.resumen_desde(marca) if monitor else ""
            log(f"    FALLÓ al agregar · carrito {carrito_antes}→{_contador_carrito(pagina)} · total {total_antes}→"
                f"{_texto_visible(pagina, '#W0008TOTAL')} · {time.monotonic() - inicio:.1f} s · {red}")
            _inspeccionar_carrito(pagina, [f.number_fac for f, _ in agregadas] + [factura.number_fac], log)
            raise
        agregadas.append((factura, valor_etapa))
        resultados.append(_resultado_agregado(factura, valor_etapa))
        red = monitor.resumen_desde(marca) if monitor else ""
        log(f"    agregada · valor {valor_etapa} · carrito {carrito_antes}→{_contador_carrito(pagina)} · total "
            f"{total_antes}→{_texto_visible(pagina, '#W0008TOTAL')} · {time.monotonic() - inicio:.1f} s · {red}")

    pagina.locator("#CONTINUAR").click()
    pagina.wait_for_url(re.compile(r"hverdeor\.aspx"), timeout=TIMEOUT_CARGA_MS)
    _verificar_sesion(pagina)
    pagina.locator("#PAGARTC").wait_for(state="visible", timeout=TIMEOUT_CARGA_MS)
    esperadas = sorted(f.number_fac for f, _ in agregadas)
    facturas_carrito, total_carrito = _leer_carrito(pagina, len(esperadas))
    total_esperado = sum((v for _, v in agregadas), Decimal("0"))
    log(f"  Carrito: {len(facturas_carrito)} filas, subtotal {total_carrito} "
        f"(esperado {len(esperadas)} filas, {total_esperado})")
    if sorted(facturas_carrito) != esperadas:
        ruta = guardar_evidencia(pagina, "carrito_no_coincide")
        raise CarritoNoCoincide(f"las facturas del carrito no son las del lote; no se guarda; evidencia en {ruta}")
    if total_carrito != total_esperado:
        ruta = guardar_evidencia(pagina, "carrito_total_distinto")
        raise CarritoNoCoincide(f"subtotal del carrito {total_carrito} distinto de {total_esperado}; no se guarda; "
                                f"evidencia en {ruta}")

    log("  Guardando el lote (el sitio tarda unos 25 s)...")
    _esperar_red_tranquila(pagina)
    pagina.locator("#PAGARTC").click()
    if _esperar_fin_guardado(pagina):
        log("  El sitio volvió a la lista. Verificando en el detalle de la orden...")
    else:
        ruta = guardar_evidencia(pagina, "guardar_lote_sin_volver")
        log(f"  El sitio no volvió a la lista en {TIMEOUT_GUARDADO_MS // 1000} s; evidencia en {ruta}. "
            "Verificando en el detalle de la orden...")
    return resultados


PATRON_FACTURA_CARRITO = re.compile(r"FAC\d{3}-\d{3}-\d{9}")
PATRON_SUBTOTAL_CARRITO = re.compile(r"Subtotal\s*:?\s*([\d.,]+)")


def _leer_carrito(pagina: Page, cantidad_esperada: int) -> tuple[list[str], Decimal]:
    """Lee las facturas y el subtotal del carrito. Espera a que la tabla termine de dibujarse."""
    facturas: list[str] = []
    total = Decimal("0")
    esperado = 0
    while esperado < TIMEOUT_BUSQUEDA_MS:
        texto = pagina.inner_text("body")
        facturas = [normalizar_numero_mostrado(f) for f in PATRON_FACTURA_CARRITO.findall(texto)]
        subtotal = PATRON_SUBTOTAL_CARRITO.search(texto)
        total = parse_valor(subtotal.group(1)) if subtotal else Decimal("0")
        if len(facturas) >= cantidad_esperada and total > 0:
            break
        pagina.wait_for_timeout(PASO_ESPERA_MS)
        esperado += PASO_ESPERA_MS
    return facturas, total


def _esperar_fin_guardado(pagina: Page) -> bool:
    """Espera a que el sitio termine de guardar. No decide el éxito: eso lo confirma el detalle de la orden."""
    esperado = 0
    while esperado < TIMEOUT_GUARDADO_MS:
        if "horpagempre" in pagina.url:
            return True
        pagina.wait_for_timeout(PASO_ESPERA_MS)
        esperado += PASO_ESPERA_MS
    return False


def _ruta(url: str) -> str:
    """Solo el nombre de la página, sin parámetros (las direcciones de hnuorpag llevan datos personales)."""
    return url.split("?")[0].rsplit("/", 1)[-1] or url


class MonitorRed:
    """Registra peticiones POST, fallas de red y cambios de página para la evidencia."""

    def __init__(self, pagina: Page, log: Callable[[str], None]):
        self.posts: list[str] = []
        self.fallas: list[str] = []
        self._pagina = pagina
        self._log = log
        pagina.on("request", self._al_pedir)
        pagina.on("requestfailed", self._al_fallar)
        pagina.on("response", self._al_responder)
        pagina.on("framenavigated", self._al_navegar)

    def _al_pedir(self, peticion) -> None:
        if peticion.method == "POST":
            self.posts.append(_ruta(peticion.url))

    def _al_fallar(self, peticion) -> None:
        self.fallas.append(f"{peticion.method} {_ruta(peticion.url)}: {peticion.failure}")

    def _al_responder(self, respuesta) -> None:
        if respuesta.status >= 400:
            self.fallas.append(f"HTTP {respuesta.status} en {_ruta(respuesta.url)}")

    def _al_navegar(self, marco) -> None:
        if marco == self._pagina.main_frame:
            self._log(f"    → página: {_ruta(marco.url)}")

    def marca(self) -> tuple[int, int]:
        return len(self.posts), len(self.fallas)

    def resumen_desde(self, marca: tuple[int, int] | None) -> str:
        marca = marca or (0, 0)
        posts = self.posts[marca[0]:]
        fallas = self.fallas[marca[1]:]
        texto = f"POST {len(posts)} ({', '.join(sorted(set(posts))) or 'ninguno'})"
        if fallas:
            texto += f" · FALLAS: {'; '.join(fallas)}"
        return texto


def _facturas_en_carrito(pagina: Page, log: Callable[[str], None]) -> list[str] | None:
    """Abre el carrito real con CONTINUAR (no guarda) y devuelve sus facturas. None si no se pudo abrir."""
    try:
        pagina.locator("#CONTINUAR").click()
        pagina.wait_for_url(re.compile(r"hverdeor\.aspx"), timeout=15 * 1000)
    except PlaywrightTimeout:
        log("  El carrito no se abrió con CONTINUAR (lo normal si está vacío).")
        return None
    _esperar_red_tranquila(pagina)
    facturas = [normalizar_numero_mostrado(f) for f in PATRON_FACTURA_CARRITO.findall(pagina.inner_text("body"))]
    log(f"  Carrito real al empezar el lote: {len(facturas)} facturas")
    return facturas


def _inspeccionar_carrito(pagina: Page, esperadas: list[str], log: Callable[[str], None]) -> None:
    """Abre el carrito con CONTINUAR (no guarda) y registra qué facturas sobran o faltan. No pulsa Guardar."""
    try:
        pagina.locator("#CONTINUAR").click()
        pagina.wait_for_url(re.compile(r"hverdeor\.aspx"), timeout=TIMEOUT_CARGA_MS)
        pagina.locator("#PAGARTC").wait_for(state="visible", timeout=TIMEOUT_CARGA_MS)
        facturas, subtotal = _leer_carrito(pagina, len(esperadas))
        sobran = [f for f in facturas if f not in esperadas]
        faltan = [f for f in esperadas if f not in facturas]
        repetidas = sorted({f for f in facturas if facturas.count(f) > 1})
        log(f"  Carrito real: {len(facturas)} filas, subtotal {subtotal}")
        log(f"    sobran ({len(sobran)}): {sobran}")
        log(f"    faltan ({len(faltan)}): {faltan}")
        log(f"    repetidas ({len(repetidas)}): {repetidas}")
        log(f"    evidencia del carrito: {guardar_evidencia(pagina, 'carrito_tras_salto')}")
    except Exception as e:
        log(f"  No se pudo inspeccionar el carrito: {type(e).__name__}: {e}")


PALABRAS_DIALOGO_PELIGROSO = ("elimin", "anul", "borr")


def manejar_dialogos(pagina: Page, log: Callable[[str], None] = lambda m: None) -> None:
    """Playwright rechaza en silencio los alert/confirm del sitio si nadie los atiende.
    Aquí se registran todos; se aceptan los de guardar y se rechaza cualquiera de eliminar o anular."""
    def _al_dialogo(dialogo) -> None:
        texto = dialogo.message
        if any(p in texto.lower() for p in PALABRAS_DIALOGO_PELIGROSO):
            log(f"  Diálogo del sitio RECHAZADO: «{texto}»")
            dialogo.dismiss()
        else:
            log(f"  Diálogo del sitio aceptado: «{texto}»")
            dialogo.accept()

    pagina.on("dialog", _al_dialogo)


def conectar_chrome_depuracion(puerto: int = 9222):
    """Se conecta a un Chrome abierto con depuración remota. Al terminar NO cierra ese Chrome."""
    playwright = sync_playwright().start()
    navegador = playwright.chromium.connect_over_cdp(f"http://localhost:{puerto}")
    contexto = navegador.contexts[0] if navegador.contexts else navegador.new_context()
    pagina = contexto.pages[0] if contexto.pages else contexto.new_page()
    return playwright, pagina


class SitioEtapa:
    """Implementa el contrato Sitio de logic/cargar_facturas sobre Playwright."""

    def __init__(self, pagina: Page, datos: DatosOrden, log: Callable[[str], None] = lambda m: None):
        self._pagina = pagina
        self._datos = datos
        self._log = log
        manejar_dialogos(pagina, log)
        self._monitor = MonitorRed(pagina, log)

    def listar_ordenes(self) -> list[dict]:
        ir_a_ordenes(self._pagina)
        _verificar_sesion(self._pagina)
        self._pagina.wait_for_load_state("networkidle")
        ordenes = listar_ordenes(self._pagina)
        if not ordenes:
            raise ListaDeOrdenesVacia("la lista de órdenes llegó vacía; no se continúa para no duplicar órdenes")
        return ordenes

    def facturas_de_orden(self, id_orden: str) -> list[str]:
        return facturas_de_orden(self._pagina, id_orden)

    def crear_orden(self) -> str:
        return crear_orden(self._pagina, self._datos, confirmar=lambda: True)

    def cargar_lote(self, id_orden: str, lote: list[FacturaPago]) -> list[ResultadoCarga]:
        self._log(f"Lote de {len(lote)} facturas en la orden {id_orden}")
        return cargar_lote(self._pagina, id_orden, lote, self._log, self._monitor)
