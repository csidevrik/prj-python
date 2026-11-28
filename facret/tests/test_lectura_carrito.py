from decimal import Decimal

from logic.etapa_playwright import PATRON_FACTURA_CARRITO, PATRON_SUBTOTAL_CARRITO
from logic.etapa_reglas import normalizar_numero_mostrado, parse_valor

TEXTO_CARRITO = """Carrito de pagos
10
Cédula	Cliente	Servicio	Referencia	Subtotal	Último pago
0160049360001	EMPRESA PUBLICA MUNICIPAL DE MOVILIDAD,TRANSITO Y	FAC001-003-055751634	HOU00013	1151,15	04/11/26
0160049360001	EMPRESA PUBLICA MUNICIPAL DE MOVILIDAD,TRANSITO Y	FAC001-003-055787579	I0205929	598,92	04/11/26
0160049360001	EMPRESA PUBLICA MUNICIPAL DE MOVILIDAD,TRANSITO Y	FAC001-003-055803013	I0247963	51,75	04/11/26
AGREGAR MÁS SERVICIOS	TODOS
Subtotal:2141,07	Interes Total:	0,00	Total:	2141,07
GUARDAR DETALLES"""


def test_lee_las_facturas_del_carrito():
    facturas = [normalizar_numero_mostrado(f) for f in PATRON_FACTURA_CARRITO.findall(TEXTO_CARRITO)]
    assert facturas == ["FAC001003055751634", "FAC001003055787579", "FAC001003055803013"]


def test_lee_el_subtotal_del_carrito_y_no_el_total_con_intereses():
    subtotal = PATRON_SUBTOTAL_CARRITO.search(TEXTO_CARRITO)
    assert parse_valor(subtotal.group(1)) == Decimal("2141.07")
