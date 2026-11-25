from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class EstadoFactura(str, Enum):
    AGREGADA = "AGREGADA"
    YA_EN_ORDEN = "YA_EN_ORDEN"
    SIN_RESULTADOS = "SIN_RESULTADOS"
    FACTURA_NO_ENCONTRADA = "FACTURA_NO_ENCONTRADA"
    DIFERENCIA_VALOR = "DIFERENCIA_VALOR"
    NO_DISPONIBLE = "NO_DISPONIBLE"
    ERROR = "ERROR"


@dataclass(frozen=True)
class FacturaPago:
    code_inst: str
    number_fac: str
    valor_sin_iva: Decimal | None = None
    fecha_emision: str | None = None
    fecha_max_pago: str | None = None


@dataclass(frozen=True)
class ResultadoCarga:
    factura: FacturaPago
    estado: EstadoFactura
    lote: int | None = None
    valor_etapa: Decimal | None = None
    valor_esperado: Decimal | None = None
    diferencia: Decimal | None = None
    detalle: str = ""
