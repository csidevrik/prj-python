from decimal import Decimal

import pytest

from logic.etapa_csv import leer_facturas_csv

CABECERA = "code_inst,number_fac,value_serv,fecha_emision,fecha_max_pago,name_original\n"


def _escribir(tmp_path, contenido: str, codificacion: str = "utf-8"):
    ruta = tmp_path / "facturas.csv"
    ruta.write_bytes(contenido.encode(codificacion))
    return ruta


def test_lee_filas_validas_con_valor_y_fechas(tmp_path):
    ruta = _escribir(
        tmp_path,
        CABECERA + "I0247963,FAC001003055751634,76.88,02/10/2026,09/11/2026,FAC065173799_001.xml\n",
    )
    facturas, errores = leer_facturas_csv(ruta)
    assert errores == []
    assert len(facturas) == 1
    assert facturas[0].code_inst == "I0247963"
    assert facturas[0].number_fac == "FAC001003055751634"
    assert facturas[0].valor_sin_iva == Decimal("76.88")
    assert facturas[0].fecha_emision == "02/10/2026"
    assert facturas[0].fecha_max_pago == "09/11/2026"


def test_varias_facturas_de_la_misma_instalacion_se_leen_todas(tmp_path):
    ruta = _escribir(
        tmp_path,
        CABECERA
        + "I0242176,FAC001003055362148,140.8,02/10/2026,,a.xml\n"
        + "I0242176,FAC001003055432764,36,02/10/2026,,b.xml\n",
    )
    facturas, errores = leer_facturas_csv(ruta)
    assert errores == []
    assert [f.number_fac for f in facturas] == ["FAC001003055362148", "FAC001003055432764"]


def test_fila_con_numero_invalido_se_reporta_sin_detener_la_lectura(tmp_path):
    ruta = _escribir(
        tmp_path,
        CABECERA
        + "I0247963,FAC001003055751634,76.88,,,a.xml\n"
        + "I0247964,NO-ES-FACTURA,36,,,b.xml\n"
        + "I0247965,FAC001003055751999,36,,,c.xml\n",
    )
    facturas, errores = leer_facturas_csv(ruta)
    assert len(facturas) == 2
    assert len(errores) == 1
    assert errores[0].startswith("línea 3:")


def test_code_inst_vacio_se_reporta(tmp_path):
    ruta = _escribir(tmp_path, CABECERA + ",FAC001003055751634,36,,,a.xml\n")
    facturas, errores = leer_facturas_csv(ruta)
    assert facturas == []
    assert "code_inst vacío" in errores[0]


def test_valor_opcional_puede_venir_vacio(tmp_path):
    ruta = _escribir(tmp_path, CABECERA + "I0247963,FAC001003055751634,,,,a.xml\n")
    facturas, errores = leer_facturas_csv(ruta)
    assert errores == []
    assert facturas[0].valor_sin_iva is None
    assert facturas[0].fecha_max_pago is None


def test_lee_archivo_en_cp1252_que_escribe_windows(tmp_path):
    contenido = CABECERA + "I0247963,FAC001003055751634,76.88,,,Ñandú.xml\n"
    ruta = _escribir(tmp_path, contenido, codificacion="cp1252")
    facturas, errores = leer_facturas_csv(ruta)
    assert errores == []
    assert facturas[0].valor_sin_iva == Decimal("76.88")


def test_archivo_sin_columnas_obligatorias_falla_con_mensaje_claro(tmp_path):
    ruta = _escribir(tmp_path, "code_inst,valor\nI0247963,36\n")
    with pytest.raises(ValueError, match="number_fac"):
        leer_facturas_csv(ruta)
