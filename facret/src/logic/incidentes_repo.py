import os
from dataclasses import asdict
from datetime import datetime, timezone

from pymongo import MongoClient
from pymongo.collection import Collection

from models.models import Incidente, UMBRAL_SLA_SEGUNDOS, ATRIBUCION_PENDIENTE

_MONGO_URI = os.environ.get(
    "FACRET_MONGO_URI",
    "mongodb://facret:facret_dev@localhost:27017/facret?authSource=admin",
)
_DB_NAME = os.environ.get("FACRET_MONGO_DB", "facret")

_client: MongoClient | None = None


def _get_collection() -> Collection:
    global _client
    if _client is None:
        _client = MongoClient(_MONGO_URI)
        _client[_DB_NAME]["incidentes"].create_index([("cod_serv", 1), ("ts_inicio", -1)])
    return _client[_DB_NAME]["incidentes"]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def registrar_inicio_caida(
    cod_serv: str,
    tipo: str = "CAIDA_TOTAL",
    descripcion: str = "",
    registrado_por: str = "",
    ts_inicio: str | None = None,
) -> str:
    """Abre un incidente. Retorna el id del documento insertado."""
    incidente = Incidente(
        cod_serv=cod_serv,
        ts_inicio=ts_inicio or _now_iso(),
        tipo=tipo,
        atribuible_a=ATRIBUCION_PENDIENTE,
        descripcion=descripcion,
        registrado_por=registrado_por,
    )
    doc = asdict(incidente)
    doc.pop("id")
    result = _get_collection().insert_one(doc)
    return str(result.inserted_id)


def cerrar_incidente(
    incidente_id: str,
    atribuible_a: str,
    ts_fin: str | None = None,
    reportado_a_isp: bool = False,
) -> None:
    """Cierra un incidente abierto y calcula duración + si cae dentro del umbral de SLA."""
    from bson import ObjectId

    coll = _get_collection()
    doc = coll.find_one({"_id": ObjectId(incidente_id)})
    if doc is None:
        raise ValueError(f"Incidente no encontrado: {incidente_id}")

    ts_fin_val = ts_fin or _now_iso()
    ts_inicio_dt = datetime.fromisoformat(doc["ts_inicio"])
    ts_fin_dt = datetime.fromisoformat(ts_fin_val)
    duracion_seg = int((ts_fin_dt - ts_inicio_dt).total_seconds())

    coll.update_one(
        {"_id": ObjectId(incidente_id)},
        {"$set": {
            "ts_fin": ts_fin_val,
            "duracion_seg": duracion_seg,
            "dentro_umbral_sla": duracion_seg < UMBRAL_SLA_SEGUNDOS,
            "atribuible_a": atribuible_a,
            "reportado_a_isp": reportado_a_isp,
        }},
    )


def listar_incidentes(
    cod_serv: str | None = None,
    desde: str | None = None,
    hasta: str | None = None,
    atribuible_a: str | None = None,
) -> list[Incidente]:
    """Consulta incidentes con filtros opcionales. Sin filtros, trae todo el histórico."""
    query: dict = {}
    if cod_serv:
        query["cod_serv"] = cod_serv
    if atribuible_a:
        query["atribuible_a"] = atribuible_a
    if desde or hasta:
        rango: dict = {}
        if desde:
            rango["$gte"] = desde
        if hasta:
            rango["$lte"] = hasta
        query["ts_inicio"] = rango

    resultados = []
    for doc in _get_collection().find(query).sort("ts_inicio", -1):
        doc_id = str(doc.pop("_id"))
        resultados.append(Incidente(id=doc_id, **doc))
    return resultados
