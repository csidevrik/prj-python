from decimal import Decimal

import pytest

from logic.etapa_reglas import (
    diferencia,
    hay_diferencia,
    normalizar_number_fac,
    parse_valor,
    valor_esperado_con_iva,
)


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("1151,15", Decimal("1151.15")),
        ("2152,80", Decimal("2152.80")),
        ("13759,85", Decimal("13759.85")),
        ("1.151,15", Decimal("1151.15")),
        ("1.234.567,89", Decimal("1234567.89")),
        ("$ 1151.15", Decimal("1151.15")),
        ("$1151.15", Decimal("1151.15")),
        ("1151.15", Decimal("1151.15")),
        ("172.80", Decimal("172.80")),
        ("45", Decimal("45")),
    ],
)
def test_parse_valor_acepta_formatos_del_sitio_y_del_csv(texto, esperado):
    assert parse_valor(texto) == esperado


@pytest.mark.parametrize("texto", ["", "   ", "abc", "1.151", "$"])
def test_parse_valor_rechaza_textos_no_validos_o_ambiguos(texto):
    with pytest.raises(ValueError):
        parse_valor(texto)


def test_parse_valor_devuelve_decimal_no_float():
    assert isinstance(parse_valor("1151,15"), Decimal)


def test_normalizar_number_fac_quita_guiones():
    assert normalizar_number_fac("FAC001-003-055751634") == "FAC001003055751634"


def test_normalizar_number_fac_acepta_formato_del_csv():
    assert normalizar_number_fac("FAC001003055751634") == "FAC001003055751634"


def test_normalizar_number_fac_pasa_a_mayusculas():
    assert normalizar_number_fac("fac001-003-055751634") == "FAC001003055751634"


@pytest.mark.parametrize("numero", ["", "FAC001003", "XYZ001003055751634", "FAC00100305575163A"])
def test_normalizar_number_fac_rechaza_formatos_invalidos(numero):
    with pytest.raises(ValueError):
        normalizar_number_fac(numero)


def test_valor_esperado_aplica_iva_15_por_ciento():
    assert valor_esperado_con_iva(Decimal("1000")) == Decimal("1150.00")


def test_valor_esperado_redondea_medio_hacia_arriba():
    assert valor_esperado_con_iva(Decimal("0.05")) == Decimal("0.06")


def test_valor_esperado_conserva_centavos():
    assert valor_esperado_con_iva(Decimal("1000.01")) == Decimal("1150.01")


def test_diferencia_y_hay_diferencia_dentro_de_tolerancia():
    esperado = Decimal("1150.00")
    assert diferencia(Decimal("1150.01"), esperado) == Decimal("0.01")
    assert not hay_diferencia(Decimal("1150.01"), esperado)


def test_hay_diferencia_fuera_de_tolerancia():
    esperado = Decimal("1150.00")
    assert hay_diferencia(Decimal("1150.02"), esperado)
    assert hay_diferencia(Decimal("1149.98"), esperado)
