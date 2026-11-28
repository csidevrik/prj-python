# =============================
# scripts/cargar_facturas_etapa.py
# =============================
"""
Carga facturas de un CSV en una orden nueva de Pago Empresas, en lotes de 10.

Dos modos:
    --solo-revisar  Inicia sesión y revisa qué facturas ya están en órdenes abiertas.
                    NO crea órdenes, NO agrega nada al carrito.
    (sin opciones)  Carga real: pide SI, crea la orden y carga en lotes con SI por lote.

Todo lo que se imprime también queda en data\\informes\\cargas\\ en un archivo de registro.

Uso (PowerShell, desde la carpeta facret):
    poetry run python src/scripts/cargar_facturas_etapa.py --csv "RUTA\\facturas.csv" --solo-revisar
"""
import argparse
import csv
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC))

from logic.cargar_facturas import (  # noqa: E402
    TAMANOS_LOTE,
    fecha_minima_emision,
    OperacionCancelada,
    OrdenAjenaDetectada,
    ejecutar_carga,
    mapear_ocupadas,
    separar_pendientes,
)
from logic.etapa_csv import leer_facturas_csv  # noqa: E402
from logic.etapa_orden_datos import cargar_datos_orden  # noqa: E402
from logic.etapa_playwright import (  # noqa: E402
    CarritoConRestos,
    CarritoNoCoincide,
    ErrorAlAgregar,
    SesionDeCargaVencida,
    SitioEtapa,
    abrir_navegador,
    conectar_chrome_depuracion,
    esperar_login,
)
from logic.etapa_reglas import valor_esperado_con_iva  # noqa: E402
from models.factura_pago import EstadoFactura  # noqa: E402

RUTA_ESTADO = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "FACRET" / "etapa_estado.json"
CARPETA_CARGAS = SRC.parent / "data" / "informes" / "cargas"
COLUMNAS = ["code_inst", "number_fac", "valor_sin_iva", "valor_esperado_con_iva", "valor_etapa",
            "diferencia", "estado", "lote", "detalle"]


class Registro:
    """Imprime y guarda en archivo cada línea de la ejecución."""

    def __init__(self, carpeta: Path):
        carpeta.mkdir(parents=True, exist_ok=True)
        self.ruta = carpeta / f"ejecucion_{datetime.now():%Y%m%d_%H%M%S}.log"

    def __call__(self, mensaje: str = "") -> None:
        print(mensaje)
        with open(self.ruta, "a", encoding="utf-8") as f:
            f.write(mensaje + "\n")


def _escribir_csv(ruta: Path, filas: list[dict], columnas: list[str]) -> None:
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)


def _filas_resultados(resultados) -> list[dict]:
    return [{
        "code_inst": r.factura.code_inst,
        "number_fac": r.factura.number_fac,
        "valor_sin_iva": r.factura.valor_sin_iva,
        "valor_esperado_con_iva": r.valor_esperado,
        "valor_etapa": r.valor_etapa,
        "diferencia": r.diferencia,
        "estado": r.estado.value,
        "lote": r.lote,
        "detalle": r.detalle,
    } for r in resultados]


def _resumen_inicial(facturas, registro: Registro, tamano_lote: int | None = None) -> None:
    base = sum((f.valor_sin_iva or 0 for f in facturas), 0)
    esperado = sum((valor_esperado_con_iva(f.valor_sin_iva) for f in facturas if f.valor_sin_iva is not None), 0)
    registro(f"Facturas: {len(facturas)} · instalaciones: {len({f.code_inst for f in facturas})}")
    registro(f"Base sin IVA: {base} · esperado con IVA: {esperado}")
    if tamano_lote:
        reparto = [tamano_lote] * (len(facturas) // tamano_lote)
        if len(facturas) % tamano_lote:
            reparto.append(len(facturas) % tamano_lote)
        registro(f"Lotes de {tamano_lote} según los {len(facturas)} registros del CSV: {reparto}")
    else:
        registro(f"Lotes: empiezan de {TAMANOS_LOTE[0]} facturas, luego de {TAMANOS_LOTE[-1]}")


def _revisar(sitio, facturas, registro: Registro) -> Path:
    """Solo lectura: lista qué facturas ya están en órdenes abiertas y cuáles faltan."""
    ordenes = sitio.listar_ordenes()
    mapa = mapear_ocupadas(sitio, ordenes, desde=fecha_minima_emision(facturas))
    ya, pendientes = separar_pendientes(facturas, mapa)
    filas = []
    for r in ya:
        filas.append(_fila_revision(r.factura, "YA_EN_ORDEN", r.detalle))
    for f in pendientes:
        filas.append(_fila_revision(f, "PENDIENTE", ""))
    ruta = CARPETA_CARGAS / f"revision_{datetime.now():%Y%m%d_%H%M%S}.csv"
    _escribir_csv(ruta, filas, ["code_inst", "number_fac", "valor_sin_iva", "accion", "detalle"])
    registro(f"Órdenes abiertas revisadas: {sum(1 for o in ordenes if o['estado'] in ('Creada', 'Procesada'))}")
    registro(f"Facturas ya en órdenes abiertas: {len(ya)} · pendientes: {len(pendientes)}")
    return ruta


def _fila_revision(factura, accion: str, detalle: str) -> dict:
    return {"code_inst": factura.code_inst, "number_fac": factura.number_fac,
            "valor_sin_iva": factura.valor_sin_iva, "accion": accion, "detalle": detalle}


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga facturas en una orden nueva de Pago Empresas.")
    parser.add_argument("--csv", required=True, type=Path, help="facturas.csv generado por la app")
    parser.add_argument("--solo-revisar", action="store_true",
                        help="solo lee órdenes abiertas; no crea ni agrega nada")
    parser.add_argument("--cdp", action="store_true",
                        help="se conecta al Chrome abierto con depuración remota en el puerto 9222")
    parser.add_argument("--orden", help="usa una orden ya creada (por ejemplo 7995) en vez de crear una nueva")
    parser.add_argument("--lote", type=int,
                        help="tamaño fijo de lote (por ejemplo 50). Sin esta opción: 10 y luego 20")
    parser.add_argument("--manual", action="store_true",
                        help="tú creas la orden nueva en la ventana; el script la detecta y carga las facturas")
    args = parser.parse_args()

    registro = Registro(CARPETA_CARGAS)
    registro(f"Registro de esta ejecución: {registro.ruta}")
    registro(f"Modo: {'SOLO REVISAR (sin escritura)' if args.solo_revisar else 'CARGA REAL'}")

    datos = cargar_datos_orden()
    facturas, errores = leer_facturas_csv(args.csv)
    if errores:
        registro("El CSV tiene filas con error; corrígelas antes de cargar:")
        for e in errores:
            registro(f"   {e}")
        sys.exit(1)

    if args.lote is not None and args.lote < 1:
        registro("--lote debe ser 1 o más.")
        sys.exit(1)
    _resumen_inicial(facturas, registro, args.lote)
    if not args.solo_revisar:
        if input("Escribe SI para abrir el navegador, crear la orden y empezar la carga: ").strip() != "SI":
            registro("Cancelado. No se creó nada.")
            return

    acumulado = []
    if args.cdp:
        playwright, pagina = conectar_chrome_depuracion()
        contexto = None
        registro("Conectado a tu Chrome con depuración remota.")
    else:
        playwright, contexto = abrir_navegador()
        pagina = contexto.new_page()
    ruta_traza = CARPETA_CARGAS / f"traza_{datetime.now():%Y%m%d_%H%M%S}.zip"
    traza_activa = False
    try:
        pagina.context.tracing.start(screenshots=True, snapshots=True)
        traza_activa = True
        registro(f"Traza completa activada: {ruta_traza}")
    except Exception as e:
        registro(f"No se pudo activar la traza: {type(e).__name__}: {e}")
    try:
        registro("Inicia sesión en la ventana de ETAPA (usuario, clave y reCAPTCHA).")
        if not esperar_login(pagina):
            registro("No se detectó el inicio de sesión en 10 minutos. Se cancela.")
            return
        registro("Sesión detectada.")
        sitio = SitioEtapa(pagina, datos, log=registro)
        orden_existente = args.orden

        if args.manual:
            registro("Ahora tú: pulsa 'Nueva Orden', guarda y vuelve a la lista de órdenes.")
            input("Cuando la orden nueva aparezca en la lista, presiona Enter aquí...")
            candidatas = [o for o in sitio.listar_ordenes() if o["estado"] == "Creada" and o["valor"] == "0,00"]
            if not candidatas:
                registro("No veo ninguna orden Creada con 0,00. Revisa la lista y vuelve a intentar.")
                return
            nueva = max(candidatas, key=lambda o: int(o["id"]))
            registro(f"Orden detectada: {nueva['id']}")
            if input(f"Escribe SI para cargar las facturas en la orden {nueva['id']}: ").strip() != "SI":
                registro("Cancelado. No se cargó nada.")
                return
            orden_existente = nueva["id"]

        if args.solo_revisar:
            ruta = _revisar(sitio, facturas, registro)
            registro(f"Revisión guardada en: {ruta}")
            return

        resultados, orden = ejecutar_carga(
            sitio, facturas,
            confirmar_inicio=lambda: True,
            ruta_estado=RUTA_ESTADO,
            acumulado=acumulado,
            orden_existente=orden_existente,
            log=registro,
            tamano_fijo=args.lote,
        )
        conteo = {}
        for r in resultados:
            conteo[r.estado.value] = conteo.get(r.estado.value, 0) + 1
        registro(f"Orden: {orden}. Resumen: {conteo}")
    except OperacionCancelada as e:
        registro(f"Detenido: {e}. El estado quedó guardado para reanudar.")
    except OrdenAjenaDetectada as e:
        registro(f"Detenido: {e}. Revisa la orden en el sitio antes de continuar.")
    except SesionDeCargaVencida:
        registro("La sesión venció. Vuelve a ejecutar el script: reanuda desde la orden guardada.")
    except (CarritoConRestos, CarritoNoCoincide, ErrorAlAgregar) as e:
        registro(f"Detenido por seguridad: {e}. No se guardó el lote. Revisa el carrito en el sitio.")
    except Exception as e:
        registro(f"Error inesperado: {type(e).__name__}: {e}")
        registro(traceback.format_exc())
    finally:
        if acumulado:
            ruta = CARPETA_CARGAS / f"carga_{datetime.now():%Y%m%d_%H%M%S}.csv"
            _escribir_csv(ruta, _filas_resultados(acumulado), COLUMNAS)
            registro(f"Reporte de facturas: {ruta}")
        if traza_activa:
            try:
                pagina.context.tracing.stop(path=str(ruta_traza))
                registro(f"Traza guardada: {ruta_traza} (ver con: poetry run playwright show-trace \"{ruta_traza}\")")
            except Exception as e:
                registro(f"No se pudo guardar la traza: {type(e).__name__}: {e}")
        registro(f"Registro completo: {registro.ruta}")
        input("\nANTES DE CERRAR: haz clic en 'Cerrar Sesión' en la ventana de ETAPA. "
              "Luego presiona Enter aquí para terminar...")
        if contexto is not None:
            contexto.close()
        playwright.stop()


if __name__ == "__main__":
    main()
