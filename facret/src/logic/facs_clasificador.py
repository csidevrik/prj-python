# =============================
# logic/facs_clasificador.py
# =============================
"""
Clasifica facturas ETAPA EP como TELECOM, AGUA o REVISAR a partir del XML.
Sin dependencias de Outlook ni de UI.
"""
import re
from dataclasses import dataclass, field

from logic.facs_manager import extract_xml_fragment

TELECOM = "TELECOM"
AGUA = "AGUA"
REVISAR = "REVISAR"

_PATRON_TELECOM = re.compile(r"^(I[O0]\d{6}|RDD\d{5})$")
_PATRON_AGUA = re.compile(r"^A\d+$")


@dataclass
class Clasificacion:
    tipo: str
    evidencia: list[str] = field(default_factory=list)


def _campo_adicional(root, nombre: str) -> str | None:
    elem = root.find(f'.//campoAdicional[@nombre="{nombre}"]')
    return elem.text if elem is not None else None


def clasificar_xml(xml_file_path: str) -> Clasificacion:
    root = extract_xml_fragment(xml_file_path, "<infoTributaria>", "</infoAdicional>")
    instalacion = _campo_adicional(root, "Instalacion")
    medidor = _campo_adicional(root, "Medidor")
    descripciones = sorted({d.text for d in root.findall(".//detalle/descripcion") if d.text})

    evidencia = []
    if instalacion:
        evidencia.append(f"Instalacion={instalacion}")
    if medidor is not None:
        evidencia.append(f"Medidor={medidor}")
    if descripciones:
        evidencia.append("descripciones: " + ", ".join(descripciones))

    senales_agua = medidor is not None or bool(instalacion and _PATRON_AGUA.match(instalacion))
    senales_telecom = bool(instalacion and _PATRON_TELECOM.match(instalacion)) and medidor is None

    if senales_agua and not senales_telecom:
        return Clasificacion(AGUA, evidencia)
    if senales_telecom and not senales_agua:
        return Clasificacion(TELECOM, evidencia)
    return Clasificacion(REVISAR, evidencia)
