# =============================
# logic/cargar_facturas.py
# =============================
"""
Orquesta la carga de facturas por lotes en una orden de Pago Empresas.
No importa Playwright ni Flet: el sitio llega por parámetro, así se prueba con uno falso.

Reglas:
- El detalle de la orden es la fuente de verdad. Después de cada guardado se relee y se
  agrega solo lo que falta. Nunca se confía en el mensaje del sitio ni en la lista.
- Lotes: tamaño fijo si se pide (--lote); si no, 10 para empezar y luego 20. Nunca todo el archivo de una vez
  por decisión propia. La cantidad de lotes sale siempre del número de registros del CSV.
- Se detiene ante cualquier anomalía: facturas duplicadas, sobrantes en el carrito, facturas
  que no aparecen tras guardar, órdenes ajenas con facturas del lote, o un error del sitio.
- Las órdenes anuladas liberan sus facturas: no cuentan como ocupadas.
"""
import json
from dataclasses import asdict, dataclass, field, replace
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable, Protocol

from models.factura_pago import EstadoFactura, FacturaPago, ResultadoCarga

TAMANOS_LOTE = (10, 20)
ESTADOS_ABIERTOS = ("Creada", "Procesada")


class Sitio(Protocol):
    def listar_ordenes(self) -> list[dict]: ...
    def facturas_de_orden(self, id_orden: str) -> list[str]: ...
    def crear_orden(self) -> str: ...
    def cargar_lote(self, id_orden: str, lote: list[FacturaPago]) -> list[ResultadoCarga]: ...


class OperacionCancelada(Exception):
    pass


class OrdenAjenaDetectada(Exception):
    def __init__(self, id_orden: str):
        super().__init__(f"apareció la orden {id_orden} con facturas de este lote; se detiene la carga")
        self.id_orden = id_orden


class CargaInconsistente(Exception):
    pass


class DetalleNoLeido(Exception):
    pass


@dataclass
class EstadoCarga:
    orden_id: str | None = None
    guardadas: list[str] = field(default_factory=list)
    completada: bool = False


def cargar_estado(ruta: Path) -> EstadoCarga:
    if not ruta.exists():
        return EstadoCarga()
    return EstadoCarga(**json.loads(ruta.read_text(encoding="utf-8")))


def guardar_estado(ruta: Path, estado: EstadoCarga) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(asdict(estado), indent=2), encoding="utf-8")


FORMATOS_FECHA_CSV = ("%d/%m/%Y", "%d/%m/%y")
FORMATO_FECHA_LISTA = "%d/%m/%y"


def fecha_minima_emision(facturas: list[FacturaPago]) -> date | None:
    """Fecha de emisión más antigua del lote, un día antes por seguridad. None si alguna no se puede leer."""
    fechas = []
    for f in facturas:
        fecha = _parsear_fecha(f.fecha_emision, FORMATOS_FECHA_CSV)
        if fecha is None:
            return None
        fechas.append(fecha)
    return min(fechas) - timedelta(days=1) if fechas else None


def _parsear_fecha(texto: str | None, formatos: tuple[str, ...]) -> date | None:
    for formato in formatos:
        try:
            return datetime.strptime((texto or "").strip().split(" ")[0], formato).date()
        except ValueError:
            continue
    return None


def mapear_ocupadas(sitio: Sitio, ordenes: list[dict], desde: date | None = None) -> dict[str, str]:
    """Factura -> id de la orden abierta donde ya está. Las anuladas se ignoran.
    Con `desde`, solo se leen órdenes creadas desde esa fecha: una factura no puede estar en una orden anterior a su emisión."""
    mapa: dict[str, str] = {}
    for orden in ordenes:
        if orden["estado"] not in ESTADOS_ABIERTOS:
            continue
        if desde is not None:
            creada = _parsear_fecha(orden.get("fecha"), (FORMATO_FECHA_LISTA,))
            if creada is not None and creada < desde:
                continue
        numeros = sitio.facturas_de_orden(orden["id"])
        if not numeros and orden["valor"] not in ("0,00", ""):
            raise DetalleNoLeido(f"la orden {orden['id']} vale {orden['valor']} pero no se leyeron facturas; "
                                 "no se continúa para no duplicarlas")
        for numero in numeros:
            mapa.setdefault(numero, orden["id"])
    return mapa


def separar_pendientes(facturas: list[FacturaPago], mapa: dict[str, str]) -> tuple[list[ResultadoCarga], list[FacturaPago]]:
    ya = []
    pendientes = []
    for factura in facturas:
        if factura.number_fac in mapa:
            ya.append(ResultadoCarga(factura, EstadoFactura.YA_EN_ORDEN, detalle=f"orden {mapa[factura.number_fac]}"))
        else:
            pendientes.append(factura)
    return ya, pendientes


def siguiente_tamano(tamano_actual: int, lote_bien: bool) -> int:
    """Empieza en 10; tras un lote correcto sube a 20; nunca pasa de 20 automáticamente."""
    if not lote_bien:
        return tamano_actual
    return TAMANOS_LOTE[-1] if tamano_actual >= TAMANOS_LOTE[0] else TAMANOS_LOTE[0]


def ejecutar_carga(
    sitio: Sitio,
    facturas: list[FacturaPago],
    confirmar_inicio: Callable[[], bool],
    ruta_estado: Path,
    acumulado: list[ResultadoCarga] | None = None,
    orden_existente: str | None = None,
    log: Callable[[str], None] = lambda m: None,
    tamano_fijo: int | None = None,
) -> tuple[list[ResultadoCarga], str | None]:
    """`acumulado` recibe los resultados a medida que avanzan, para no perderlos si la carga se detiene.
    `orden_existente` usa una orden ya creada en lugar de crear una nueva."""
    estado = cargar_estado(ruta_estado)
    if orden_existente:
        estado = EstadoCarga(orden_id=orden_existente)
        guardar_estado(ruta_estado, estado)
    elif estado.completada:
        estado = EstadoCarga()

    ordenes_inicio = sitio.listar_ordenes()
    ids_previos = {o["id"] for o in ordenes_inicio}

    if estado.orden_id is None:
        if not confirmar_inicio():
            raise OperacionCancelada("no se confirmó el inicio; no se creó nada")
        estado.orden_id = sitio.crear_orden()
        guardar_estado(ruta_estado, estado)

    mapa = mapear_ocupadas(sitio, ordenes_inicio, desde=fecha_minima_emision(facturas))
    ya, _ = separar_pendientes(facturas, mapa)
    resultados = acumulado if acumulado is not None else []
    resultados.extend(ya)

    orden_id = estado.orden_id
    tamano = tamano_fijo or TAMANOS_LOTE[0]
    numero_lote = 0
    while True:
        en_orden = sitio.facturas_de_orden(orden_id)
        duplicadas = sorted({f for f in en_orden if en_orden.count(f) > 1})
        if duplicadas:
            raise CargaInconsistente(f"facturas duplicadas en la orden: {duplicadas}")

        en_ajenas = {f for f, oid in mapa.items() if oid != orden_id}
        pendientes = [f for f in facturas
                      if f.number_fac not in en_orden and f.number_fac not in en_ajenas]
        cargadas = sum(1 for f in facturas if f.number_fac in en_orden)
        log(f"Orden {orden_id}: {cargadas} facturas del archivo ya están en el detalle; pendientes {len(pendientes)}")
        if not pendientes:
            break

        lote = pendientes[:tamano]
        numero_lote += 1
        numeros_lote = {f.number_fac for f in lote}
        for orden in sitio.listar_ordenes():
            if orden["id"] in ids_previos or orden["id"] == orden_id:
                continue
            if orden["estado"] not in ESTADOS_ABIERTOS:
                continue
            if numeros_lote & set(sitio.facturas_de_orden(orden["id"])):
                raise OrdenAjenaDetectada(orden["id"])

        res = sitio.cargar_lote(orden_id, lote)

        en_orden_despues = sitio.facturas_de_orden(orden_id)
        faltan = [f.number_fac for f in lote if f.number_fac not in en_orden_despues]
        if faltan:
            raise CargaInconsistente(f"tras guardar el lote {numero_lote} faltan {len(faltan)} facturas en la orden")
        sobrantes = set(en_orden_despues) - set(en_orden) - numeros_lote
        if sobrantes:
            raise CargaInconsistente(f"la orden tiene {len(sobrantes)} facturas que no estaban en el lote")

        resultados.extend(replace(r, lote=numero_lote) for r in res)
        estado.guardadas.extend(f.number_fac for f in lote)
        guardar_estado(ruta_estado, estado)
        if not tamano_fijo:
            tamano = siguiente_tamano(tamano, lote_bien=True)

    estado.completada = True
    guardar_estado(ruta_estado, estado)
    return resultados, orden_id
