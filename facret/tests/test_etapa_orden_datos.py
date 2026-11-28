import json

import pytest

from logic.etapa_orden_datos import (
    DatosOrden,
    DatosOrdenInvalidos,
    cargar_datos_orden,
    validar_datos_orden,
)

VALIDOS = {
    "nombre": "ANITA",
    "apellido": "ORELLANA",
    "institucion": "EMOV EP",
    "cargo": "ANALISTA",
    "telefono": "0983933527",
}


def test_datos_validos_se_aceptan_sin_modificarlos():
    datos = validar_datos_orden(VALIDOS)
    assert datos == DatosOrden(nombre="ANITA", apellido="ORELLANA", institucion="EMOV EP",
                               cargo="ANALISTA", telefono="0983933527")


def test_cargo_y_telefono_son_opcionales():
    datos = validar_datos_orden({"nombre": "A", "apellido": "B", "institucion": "C"})
    assert datos.cargo == "" and datos.telefono == ""


@pytest.mark.parametrize("campo", ["nombre", "apellido", "institucion"])
def test_obligatorios_no_pueden_quedar_vacios(campo):
    datos = dict(VALIDOS, **{campo: "   "})
    with pytest.raises(DatosOrdenInvalidos) as e:
        validar_datos_orden(datos)
    assert f"{campo} es obligatorio" in e.value.errores


def test_cargo_largo_se_rechaza_y_no_se_trunca():
    # El sitio trunca "ANALISTA CONTABILIDAD" a 20 caracteres sin avisar; aquí debe fallar.
    datos = dict(VALIDOS, cargo="ANALISTA CONTABILIDAD")
    with pytest.raises(DatosOrdenInvalidos) as e:
        validar_datos_orden(datos)
    assert any("cargo excede 20" in err for err in e.value.errores)


@pytest.mark.parametrize("campo, limite", [("nombre", 35), ("apellido", 35), ("institucion", 30), ("cargo", 20)])
def test_limites_maximos_por_campo(campo, limite):
    validar_datos_orden(dict(VALIDOS, **{campo: "x" * limite}))
    with pytest.raises(DatosOrdenInvalidos):
        validar_datos_orden(dict(VALIDOS, **{campo: "x" * (limite + 1)}))


def test_telefono_solo_admite_digitos():
    with pytest.raises(DatosOrdenInvalidos) as e:
        validar_datos_orden(dict(VALIDOS, telefono="098-393"))
    assert "telefono solo admite dígitos" in e.value.errores


def test_telefono_mas_largo_de_10_digitos_se_rechaza():
    with pytest.raises(DatosOrdenInvalidos):
        validar_datos_orden(dict(VALIDOS, telefono="09839335271"))


def test_mensajes_de_error_no_contienen_los_datos_personales():
    with pytest.raises(DatosOrdenInvalidos) as e:
        validar_datos_orden(dict(VALIDOS, nombre="x" * 40, telefono="0983933527X"))
    texto = " ".join(e.value.errores)
    assert "ANITA" not in texto and "0983933527" not in texto


def test_datos_personales_no_aparecen_en_repr():
    datos = validar_datos_orden(VALIDOS)
    texto = repr(datos)
    assert "ANITA" not in texto and "ORELLANA" not in texto and "0983933527" not in texto
    assert "EMOV EP" in texto


def test_cargar_desde_archivo_valido(tmp_path):
    ruta = tmp_path / "etapa_orden.json"
    ruta.write_text(json.dumps(VALIDOS), encoding="utf-8")
    assert cargar_datos_orden(ruta).institucion == "EMOV EP"


def test_archivo_inexistente_pide_registrar_datos(tmp_path):
    with pytest.raises(FileNotFoundError, match="registre los datos"):
        cargar_datos_orden(tmp_path / "no_existe.json")


def test_archivo_con_json_roto_no_muestra_su_contenido(tmp_path):
    ruta = tmp_path / "etapa_orden.json"
    ruta.write_text('{"nombre": "ANITA", roto', encoding="utf-8")
    with pytest.raises(ValueError) as e:
        cargar_datos_orden(ruta)
    assert "ANITA" not in str(e.value)
