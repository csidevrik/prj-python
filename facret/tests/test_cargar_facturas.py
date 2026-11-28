from decimal import Decimal

import pytest

from logic.cargar_facturas import (
    CargaInconsistente,
    EstadoCarga,
    OperacionCancelada,
    OrdenAjenaDetectada,
    cargar_estado,
    ejecutar_carga,
    siguiente_tamano,
)
from models.factura_pago import EstadoFactura, FacturaPago, ResultadoCarga


def _facturas(n, inicio=1, fecha="04/11/2026"):
    return [
        FacturaPago(code_inst=f"I{i:07d}", number_fac=f"FAC001003{i:09d}", valor_sin_iva=Decimal("10.00"),
                    fecha_emision=fecha)
        for i in range(inicio, inicio + n)
    ]


class SitioFalso:
    """Simula el sitio: las órdenes guardan las facturas que se les cargan."""

    def __init__(self, ordenes=None):
        self.ordenes = ordenes or {}
        self.siguiente = 9000
        self.creadas = 0
        self.lotes = []
        self.omitir_en_guardado = set()
        self.duplicar_en_guardado = set()
        self.extra_en_guardado = []
        self.al_listar = None

    def listar_ordenes(self):
        if self.al_listar:
            self.al_listar(self)
        return [{"id": k, "estado": v["estado"], "fecha": v.get("fecha", "26/11/26"), "valor": "0,00"}
                for k, v in self.ordenes.items()]

    def facturas_de_orden(self, id_orden):
        self.lecturas = getattr(self, "lecturas", []) + [id_orden]
        return list(self.ordenes[id_orden]["facturas"])

    def crear_orden(self):
        self.siguiente += 1
        self.creadas += 1
        self.ordenes[str(self.siguiente)] = {"estado": "Creada", "facturas": []}
        return str(self.siguiente)

    def cargar_lote(self, id_orden, lote):
        self.lotes.append(len(lote))
        for f in lote:
            if f.number_fac in self.omitir_en_guardado:
                continue
            self.ordenes[id_orden]["facturas"].append(f.number_fac)
            if f.number_fac in self.duplicar_en_guardado:
                self.ordenes[id_orden]["facturas"].append(f.number_fac)
        self.ordenes[id_orden]["facturas"].extend(self.extra_en_guardado)
        self.extra_en_guardado = []
        return [ResultadoCarga(f, EstadoFactura.AGREGADA, valor_etapa=Decimal("11.50")) for f in lote]


def _si():
    return True


def test_siguiente_tamano_empieza_en_10_y_sube_a_20_sin_pasar_de_ahi():
    assert siguiente_tamano(10, lote_bien=True) == 20
    assert siguiente_tamano(20, lote_bien=True) == 20


def test_siguiente_tamano_no_cambia_si_el_lote_fallo():
    assert siguiente_tamano(10, lote_bien=False) == 10


def test_lotes_de_10_y_luego_20_nunca_103_de_una(tmp_path):
    sitio = SitioFalso()
    ejecutar_carga(sitio, _facturas(103), _si, tmp_path / "e.json")
    assert sitio.lotes[0] == 10
    assert all(n <= 20 for n in sitio.lotes)
    assert sum(sitio.lotes) == 103


def test_lote_fijo_de_50_parte_103_en_50_50_y_3(tmp_path):
    sitio = SitioFalso()
    ejecutar_carga(sitio, _facturas(103), _si, tmp_path / "e.json", tamano_fijo=50)
    assert sitio.lotes == [50, 50, 3]


def test_lote_fijo_se_calcula_con_el_total_del_archivo(tmp_path):
    sitio = SitioFalso()
    ejecutar_carga(sitio, _facturas(167), _si, tmp_path / "e.json", tamano_fijo=50)
    assert sitio.lotes == [50, 50, 50, 17]


def test_factura_en_orden_abierta_ajena_no_se_vuelve_a_cargar(tmp_path):
    facturas = _facturas(3)
    sitio = SitioFalso({"7410": {"estado": "Creada", "facturas": [facturas[0].number_fac]}})
    resultados, _ = ejecutar_carga(sitio, facturas, _si, tmp_path / "e.json")
    ya = [r for r in resultados if r.estado == EstadoFactura.YA_EN_ORDEN]
    assert [r.factura.number_fac for r in ya] == [facturas[0].number_fac]
    assert sum(sitio.lotes) == 2


def test_no_lee_ordenes_creadas_antes_de_la_primera_emision(tmp_path):
    facturas = _facturas(2, fecha="04/11/2026")
    sitio = SitioFalso({"7100": {"estado": "Procesada", "fecha": "01/10/26", "facturas": []}})
    ejecutar_carga(sitio, facturas, _si, tmp_path / "e.json")
    assert "7100" not in sitio.lecturas


def test_si_una_fecha_no_se_puede_leer_se_leen_todas_las_ordenes(tmp_path):
    facturas = _facturas(1, fecha="fecha rara") + _facturas(1, inicio=2, fecha="04/11/2026")
    sitio = SitioFalso({"7100": {"estado": "Procesada", "fecha": "01/10/26", "facturas": []}})
    ejecutar_carga(sitio, facturas, _si, tmp_path / "e.json")
    assert "7100" in sitio.lecturas


def test_orden_anulada_libera_sus_facturas(tmp_path):
    facturas = _facturas(2)
    sitio = SitioFalso({"7971": {"estado": "Anulada", "facturas": [f.number_fac for f in facturas]}})
    resultados, _ = ejecutar_carga(sitio, facturas, _si, tmp_path / "e.json")
    assert not any(r.estado == EstadoFactura.YA_EN_ORDEN for r in resultados)
    assert sum(sitio.lotes) == 2


def test_sin_confirmar_inicio_no_se_crea_nada(tmp_path):
    sitio = SitioFalso()
    with pytest.raises(OperacionCancelada):
        ejecutar_carga(sitio, _facturas(2), lambda: False, tmp_path / "e.json")
    assert sitio.creadas == 0


def test_factura_que_no_aparece_tras_guardar_detiene_la_carga(tmp_path):
    facturas = _facturas(12)
    sitio = SitioFalso()
    sitio.omitir_en_guardado = {facturas[3].number_fac}
    ruta = tmp_path / "e.json"
    with pytest.raises(CargaInconsistente, match="faltan"):
        ejecutar_carga(sitio, facturas, _si, ruta)
    assert cargar_estado(ruta).orden_id is not None
    assert not cargar_estado(ruta).completada


def test_factura_duplicada_en_la_orden_detiene_la_carga(tmp_path):
    facturas = _facturas(12)
    sitio = SitioFalso()
    sitio.duplicar_en_guardado = {facturas[1].number_fac}
    with pytest.raises(CargaInconsistente, match="duplicadas"):
        ejecutar_carga(sitio, facturas, _si, tmp_path / "e.json")
    assert sum(sitio.lotes) == 10


def test_sobrante_en_la_orden_detiene_la_carga(tmp_path):
    sitio = SitioFalso()
    sitio.extra_en_guardado = ["FAC001003999999999"]
    with pytest.raises(CargaInconsistente, match="no estaban en el lote"):
        ejecutar_carga(sitio, _facturas(12), _si, tmp_path / "e.json")


def test_orden_ajena_con_factura_del_lote_detiene_la_carga(tmp_path):
    facturas = _facturas(12)

    def aparece_ajena(sitio):
        if len(sitio.lotes) == 1 and "ajena" not in sitio.ordenes:
            sitio.ordenes["ajena"] = {"estado": "Creada", "facturas": [facturas[10].number_fac]}

    sitio = SitioFalso()
    sitio.al_listar = aparece_ajena
    with pytest.raises(OrdenAjenaDetectada) as e:
        ejecutar_carga(sitio, facturas, _si, tmp_path / "e.json")
    assert e.value.id_orden == "ajena"
    assert len(sitio.lotes) == 1


def test_reanudar_usa_la_orden_guardada_y_agrega_solo_lo_que_falta(tmp_path):
    ruta = tmp_path / "e.json"
    facturas = _facturas(15)
    sitio = SitioFalso()
    orden = sitio.crear_orden()
    sitio.ordenes[orden]["facturas"] = [f.number_fac for f in facturas[:10]]
    ruta.write_text(f'{{"orden_id": "{orden}", "guardadas": [], "completada": false}}', encoding="utf-8")
    creadas_antes = sitio.creadas

    _, orden_usada = ejecutar_carga(sitio, facturas, _si, ruta)
    assert sitio.creadas == creadas_antes
    assert orden_usada == orden
    assert sitio.lotes == [5]
    assert cargar_estado(ruta).completada


def test_carga_completada_no_reusa_la_orden_en_la_siguiente_corrida(tmp_path):
    ruta = tmp_path / "e.json"
    ruta.write_text('{"orden_id": "8000", "guardadas": [], "completada": true}', encoding="utf-8")
    sitio = SitioFalso()
    _, orden = ejecutar_carga(sitio, _facturas(2), _si, ruta)
    assert sitio.creadas == 1
    assert orden != "8000"


def test_orden_existente_completa_no_crea_ni_carga_nada(tmp_path):
    facturas = _facturas(5)
    sitio = SitioFalso({"7995": {"estado": "Creada", "facturas": [f.number_fac for f in facturas]}})
    _, orden = ejecutar_carga(sitio, facturas, _si, tmp_path / "e.json", orden_existente="7995")
    assert orden == "7995"
    assert sitio.creadas == 0
    assert sitio.lotes == []


def test_acumulado_conserva_lo_guardado_si_la_carga_se_detiene(tmp_path):
    facturas = _facturas(12)
    sitio = SitioFalso()
    sitio.omitir_en_guardado = {facturas[11].number_fac}
    acumulado = []
    with pytest.raises(CargaInconsistente):
        ejecutar_carga(sitio, facturas, _si, tmp_path / "e.json", acumulado=acumulado)
    assert len(acumulado) == 10
    assert all(r.lote == 1 for r in acumulado)


def test_estado_inexistente_devuelve_estado_vacio(tmp_path):
    assert cargar_estado(tmp_path / "no.json") == EstadoCarga()
