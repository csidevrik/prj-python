# =============================
# logic/etapa_csv.py
# =============================
"""
Lectura de facturas.csv (generado por facs_manager) como FacturaPago.
Sin Flet ni Playwright.
"""
import csv
from pathlib import Path

from logic.etapa_reglas import normalizar_number_fac, parse_valor
from models.factura_pago import FacturaPago

COLUMNAS_OBLIGATORIAS = ("code_inst", "number_fac")
_CODIFICACIONES = ("utf-8-sig", "cp1252")


def leer_facturas_csv(ruta: str | Path) -> tuple[list[FacturaPago], list[str]]:
    """Devuelve (facturas válidas, errores por línea). No detiene la lectura por una fila mala."""
    texto = _leer_texto(Path(ruta))
    lector = csv.DictReader(texto.splitlines())
    columnas = set(lector.fieldnames or [])
    faltantes = [c for c in COLUMNAS_OBLIGATORIAS if c not in columnas]
    if faltantes:
        raise ValueError(f"faltan columnas en {ruta}: {', '.join(faltantes)}")

    facturas: list[FacturaPago] = []
    errores: list[str] = []
    for num_linea, fila in enumerate(lector, start=2):
        try:
            facturas.append(_fila_a_factura(fila))
        except ValueError as e:
            errores.append(f"línea {num_linea}: {e}")
    return facturas, errores


def _leer_texto(ruta: Path) -> str:
    bruto = ruta.read_bytes()
    for codificacion in _CODIFICACIONES:
        try:
            return bruto.decode(codificacion)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"no se pudo decodificar {ruta}")


def _fila_a_factura(fila: dict) -> FacturaPago:
    code_inst = (fila.get("code_inst") or "").strip()
    if not code_inst:
        raise ValueError("code_inst vacío")
    valor_raw = (fila.get("value_serv") or "").strip()
    return FacturaPago(
        code_inst=code_inst,
        number_fac=normalizar_number_fac(fila.get("number_fac") or ""),
        valor_sin_iva=parse_valor(valor_raw) if valor_raw else None,
        fecha_emision=(fila.get("fecha_emision") or "").strip() or None,
        fecha_max_pago=(fila.get("fecha_max_pago") or "").strip() or None,
    )
