# =============================
# logic/etapa_reglas.py
# =============================
"""
Reglas de ETAPA para la carga de facturas: IVA, parseo de valores mostrados
por el sitio y normalización de números de factura. Sin Flet ni Playwright.
"""
import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

IVA = Decimal("1.15")
TOLERANCIA = Decimal("0.01")
_CENTAVOS = Decimal("0.01")
_PATRON_NUMERO_FAC = re.compile(r"^FAC\d{15}$")


def parse_valor(texto: str) -> Decimal:
    """Convierte valores del sitio y del CSV en Decimal.

    Acepta "1151,15", "1.151,15", "13759,85", "1151.15", "$ 1151.15" y "172.80".
    Con coma y punto a la vez, el último separador es el decimal.
    Un punto solo se trata como decimal; si tiene 3 dígitos tras él es ambiguo y se rechaza.
    """
    limpio = texto.replace("$", "").replace(" ", "").strip()
    if not limpio:
        raise ValueError("valor vacío")

    if "," in limpio and "." in limpio:
        if limpio.rfind(",") > limpio.rfind("."):
            limpio = limpio.replace(".", "").replace(",", ".")
        else:
            limpio = limpio.replace(",", "")
    elif "," in limpio:
        limpio = limpio.replace(",", ".")
    elif "." in limpio:
        if len(limpio.rsplit(".", 1)[1]) == 3:
            raise ValueError(f"valor ambiguo: {texto!r}")

    try:
        return Decimal(limpio)
    except InvalidOperation as e:
        raise ValueError(f"valor no numérico: {texto!r}") from e


def normalizar_number_fac(numero: str) -> str:
    """Quita guiones y espacios. Acepta 'FAC001-003-055751634' y 'FAC001003055751634'."""
    limpio = re.sub(r"[-\s]", "", numero).upper()
    if not _PATRON_NUMERO_FAC.match(limpio):
        raise ValueError(f"número de factura inválido: {numero!r}")
    return limpio


def valor_esperado_con_iva(base_sin_iva: Decimal) -> Decimal:
    return (base_sin_iva * IVA).quantize(_CENTAVOS, rounding=ROUND_HALF_UP)


def diferencia(valor_etapa: Decimal, esperado: Decimal) -> Decimal:
    return valor_etapa - esperado


def hay_diferencia(valor_etapa: Decimal, esperado: Decimal) -> bool:
    return abs(diferencia(valor_etapa, esperado)) > TOLERANCIA
