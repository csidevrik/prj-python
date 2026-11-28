import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
MODULO = RAIZ / "src" / "logic" / "etapa_playwright.py"
DIAGNOSTICO = RAIZ / "src" / "scripts" / "diagnostico_etapa.py"
ACCIONES = [".click(", ".fill(", ".press(", ".check(", ".select_option(", "keyboard."]
# Únicas funciones que pueden accionar el sitio. Cada una tiene un paso de escritura explícito.
FUNCIONES_CON_ACCIONES = {
    "crear_orden",
    "_abrir_busqueda",
    "buscar_instalacion",
    "agregar_fila",
    "cargar_lote",
    "_inspeccionar_carrito",  # solo pulsa CONTINUAR para ver el carrito; nunca Guardar
    "_facturas_en_carrito",  # solo pulsa CONTINUAR para ver el carrito; nunca Guardar
}
PROHIBIDOS_EN_CODIGO = [
    "AGREGARDEUDAPORRUC",
    "Anular",
    "Generar Pago",
    "Todos\"",
]


def _funciones(ruta: Path) -> dict[str, str]:
    codigo = ruta.read_text(encoding="utf-8")
    arbol = ast.parse(codigo)
    return {n.name: ast.get_source_segment(codigo, n) or "" for n in arbol.body if isinstance(n, ast.FunctionDef)}


def test_solo_funciones_autorizadas_accionan_el_sitio():
    for nombre, fuente in _funciones(MODULO).items():
        if any(a in fuente for a in ACCIONES):
            assert nombre in FUNCIONES_CON_ACCIONES, f"{nombre} no está autorizada para accionar el sitio"


def test_el_diagnostico_no_accion_el_sitio():
    codigo = DIAGNOSTICO.read_text(encoding="utf-8")
    for accion in ACCIONES:
        assert accion not in codigo, f"diagnostico_etapa.py no debe usar {accion}"


@pytest.mark.parametrize("ruta", [MODULO, DIAGNOSTICO], ids=lambda p: p.name)
def test_no_contiene_acciones_prohibidas(ruta):
    codigo = ruta.read_text(encoding="utf-8")
    for prohibido in PROHIBIDOS_EN_CODIGO:
        assert prohibido not in codigo, f"{ruta.name} contiene {prohibido!r}"
