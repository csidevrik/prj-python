"""
Escritura de cambios sobre los JSON de contratos.
Solo modifica los campos editables por el administrador:
  - estado_operativo
  - ip_publica
  - notas
  - eventos (agregar)

Los campos del contrato (bandwidth, valor_mensual, fechas, etc.)
son definidos por ETAPA EP y no se tocan desde aquí.
"""
import json
from pathlib import Path
from datetime import datetime

_CONTRACTS_DIR = Path(__file__).parent.parent.parent / "data" / "contracts"


def _find_contract_file(cod_serv: str) -> Path | None:
    """Busca el archivo .json que contiene el servicio dado."""
    for path in _CONTRACTS_DIR.glob("*.json"):
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        for grupo in raw.get("grupos", []):
            for svc in grupo.get("servicios", []):
                if svc.get("cod_serv") == cod_serv:
                    return path
    return None


def update_servicio(
    cod_serv: str,
    estado_operativo: str | None = None,
    ip_publica: str | None = None,
    notas: str | None = None,
) -> bool:
    """
    Actualiza los campos editables de un servicio en su JSON.
    Retorna True si encontró y guardó, False si no encontró el servicio.
    """
    path = _find_contract_file(cod_serv)
    if path is None:
        return False

    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    for grupo in raw.get("grupos", []):
        for svc in grupo.get("servicios", []):
            if svc.get("cod_serv") == cod_serv:
                if estado_operativo is not None:
                    svc["estado_operativo"] = estado_operativo
                if ip_publica is not None:
                    svc["ip_publica"] = ip_publica
                if notas is not None:
                    svc["notas"] = notas
                break

    with open(path, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)

    return True


def add_evento(
    cod_serv: str,
    tipo: str,
    descripcion: str,
    fecha: str | None = None,
) -> bool:
    """
    Agrega un evento al historial de un servicio.
    Si no se pasa fecha, usa la fecha actual.
    Retorna True si encontró y guardó, False si no encontró el servicio.
    """
    path = _find_contract_file(cod_serv)
    if path is None:
        return False

    fecha = fecha or datetime.now().strftime("%Y-%m-%d")

    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    for grupo in raw.get("grupos", []):
        for svc in grupo.get("servicios", []):
            if svc.get("cod_serv") == cod_serv:
                svc.setdefault("eventos", []).append({
                    "fecha": fecha,
                    "tipo": tipo,
                    "descripcion": descripcion,
                })
                break

    with open(path, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)

    return True
