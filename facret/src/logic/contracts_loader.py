import json
from pathlib import Path
from models.models import (
    Agencia, Evento,
    EnlaceInternet, EnlaceDatos,
    GrupoServicios, Contrato,
)

_DATA_DIR = Path(__file__).parent.parent.parent / "data"
_AGENCIAS_FILE = _DATA_DIR / "agencias.json"
_CONTRACTS_DIR = _DATA_DIR / "contracts"


def load_agencias() -> dict[str, Agencia]:
    """Carga el catálogo maestro de agencias."""
    with open(_AGENCIAS_FILE, encoding="utf-8") as f:
        raw = json.load(f)
    return {k: Agencia(**v) for k, v in raw.items()}


def _parse_eventos(raw: list[dict]) -> list[Evento]:
    return [Evento(**e) for e in raw]


def _parse_servicio(
    raw: dict,
    agencias: dict[str, Agencia],
) -> EnlaceInternet | EnlaceDatos:
    tipo = raw["tipo"]
    eventos = _parse_eventos(raw.get("eventos", []))

    if tipo == "internet":
        agencia_id = raw["agencia_id"]
        return EnlaceInternet(
            cod_serv=raw["cod_serv"],
            agencia_id=agencia_id,
            grupo=raw["grupo"],
            isp=raw["isp"],
            sdwan=raw["sdwan"],
            bandwidth=raw["bandwidth"],
            valor_mensual=raw["valor_mensual"],
            ip_publica=raw.get("ip_publica", ""),
            estado=raw["estado"],
            estado_operativo=raw["estado_operativo"],
            dias_servicio=raw["dias_servicio"],
            vigencia_meses=raw["vigencia_meses"],
            fecha_inicio=raw["fecha_inicio"],
            fecha_fin=raw["fecha_fin"],
            notas=raw.get("notas", ""),
            eventos=eventos,
            agencia=agencias.get(agencia_id),
        )

    if tipo == "datos":
        extremo_a = raw["extremo_a"]
        extremo_b = raw["extremo_b"]
        return EnlaceDatos(
            cod_serv=raw["cod_serv"],
            extremo_a=extremo_a,
            extremo_b=extremo_b,
            grupo=raw["grupo"],
            isp=raw["isp"],
            sdwan=raw["sdwan"],
            bandwidth=raw["bandwidth"],
            valor_mensual=raw["valor_mensual"],
            ip_publica=raw.get("ip_publica", ""),
            estado=raw["estado"],
            estado_operativo=raw["estado_operativo"],
            dias_servicio=raw["dias_servicio"],
            vigencia_meses=raw["vigencia_meses"],
            fecha_inicio=raw["fecha_inicio"],
            fecha_fin=raw["fecha_fin"],
            notas=raw.get("notas", ""),
            eventos=eventos,
            agencia_extremo_a=agencias.get(extremo_a),
            agencia_extremo_b=agencias.get(extremo_b),
        )

    raise ValueError(f"Tipo de servicio desconocido: '{tipo}' en {raw.get('cod_serv')}")


def _parse_contrato(raw: dict, agencias: dict[str, Agencia]) -> Contrato:
    grupos = [
        GrupoServicios(
            id=g["id"],
            nombre=g["nombre"],
            servicios=[_parse_servicio(s, agencias) for s in g["servicios"]],
        )
        for g in raw.get("grupos", [])
    ]
    return Contrato(
        id=raw["id"],
        nombre=raw["nombre"],
        proveedor=raw["proveedor"],
        administrador=raw["administrador"],
        fecha_inicio=raw["fecha_inicio"],
        fecha_fin=raw["fecha_fin"],
        duracion_meses=raw["duracion_meses"],
        estado=raw["estado"],
        grupos=grupos,
    )


def load_contratos() -> list[Contrato]:
    """Carga todos los contratos de data/contracts/*.json con agencias resueltas."""
    agencias = load_agencias()
    contratos = []
    for path in sorted(_CONTRACTS_DIR.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        contratos.append(_parse_contrato(raw, agencias))
    return contratos


def load_servicios_flat() -> list[EnlaceInternet | EnlaceDatos]:
    """Retorna todos los servicios de todos los contratos en una lista plana."""
    return [s for c in load_contratos() for s in c.servicios_flat()]
