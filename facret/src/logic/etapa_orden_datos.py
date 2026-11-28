# =============================
# logic/etapa_orden_datos.py
# =============================
"""
Datos de quien registra la orden en Pago Empresas. Viven fuera del repositorio
(%LOCALAPPDATA%\\FACRET\\etapa_orden.json) porque contienen nombre y teléfono.
Sin Flet ni Playwright.
"""
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

RUTA_DATOS = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "FACRET" / "etapa_orden.json"
CAMPOS = ("nombre", "apellido", "institucion", "cargo", "telefono")
OBLIGATORIOS = ("nombre", "apellido", "institucion")
LIMITES = {"nombre": 35, "apellido": 35, "institucion": 30, "cargo": 20, "telefono": 10}


class DatosOrdenInvalidos(ValueError):
    def __init__(self, errores: list[str]):
        super().__init__("; ".join(errores))
        self.errores = errores


@dataclass(frozen=True)
class DatosOrden:
    nombre: str = field(repr=False)
    apellido: str = field(repr=False)
    institucion: str
    cargo: str = field(default="", repr=False)
    telefono: str = field(default="", repr=False)


def validar_datos_orden(datos: dict) -> DatosOrden:
    """Valida sin truncar. Los mensajes de error no incluyen el valor, solo el campo y el largo."""
    errores = []
    limpios = {}
    for campo in CAMPOS:
        valor = str(datos.get(campo) or "").strip()
        limpios[campo] = valor
        if campo in OBLIGATORIOS and not valor:
            errores.append(f"{campo} es obligatorio")
        if len(valor) > LIMITES[campo]:
            errores.append(f"{campo} excede {LIMITES[campo]} caracteres (tiene {len(valor)})")
        if campo == "telefono" and valor and not valor.isdigit():
            errores.append("telefono solo admite dígitos")
    if errores:
        raise DatosOrdenInvalidos(errores)
    return DatosOrden(**limpios)


def cargar_datos_orden(ruta: Path = RUTA_DATOS) -> DatosOrden:
    if not ruta.exists():
        raise FileNotFoundError(f"no existe {ruta}; registre los datos desde el panel")
    try:
        crudo = json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"{ruta.name} no es JSON válido (línea {e.lineno})") from e
    if not isinstance(crudo, dict):
        raise ValueError(f"{ruta.name} debe contener un objeto JSON")
    return validar_datos_orden(crudo)
