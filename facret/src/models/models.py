from dataclasses import dataclass, field


class Factura:
    def __init__(self, code_inst, number_fac, value_serv):
        self.code_inst = code_inst
        self.number_fac = number_fac
        self.value_serv = value_serv


class Retencion:
    def __init__(self, ret_number, ret_value, fac_number):
        self.ret_number = ret_number
        self.ret_value = ret_value
        self.fac_number = fac_number


# ---------------------------------------------------------------------------
# Contratos ETAPA
# ---------------------------------------------------------------------------

@dataclass
class Agencia:
    id: str
    nombre: str
    direccion: str
    tipo: str  # "agencia", "sede_central", "sede", "datacenter", "nodo_proveedor", "externo"


@dataclass
class Evento:
    fecha: str
    tipo: str
    descripcion: str


@dataclass
class EnlaceInternet:
    cod_serv: str
    agencia_id: str
    grupo: str
    isp: str
    sdwan: bool
    bandwidth: str
    valor_mensual: float
    ip_publica: str
    estado: str           # "ACTIVE", "CANCELED"
    estado_operativo: str # "UP", "DOWN"
    dias_servicio: int
    vigencia_meses: int
    fecha_inicio: str
    fecha_fin: str
    notas: str
    eventos: list[Evento] = field(default_factory=list)
    # resuelto en memoria al cargar — no está en el JSON
    agencia: Agencia | None = field(default=None, repr=False)


@dataclass
class EnlaceDatos:
    cod_serv: str
    extremo_a: str
    extremo_b: str
    grupo: str
    isp: str
    sdwan: bool
    bandwidth: str
    valor_mensual: float
    ip_publica: str
    estado: str
    estado_operativo: str
    dias_servicio: int
    vigencia_meses: int
    fecha_inicio: str
    fecha_fin: str
    notas: str
    eventos: list[Evento] = field(default_factory=list)
    # resueltos en memoria al cargar
    agencia_extremo_a: Agencia | None = field(default=None, repr=False)
    agencia_extremo_b: Agencia | None = field(default=None, repr=False)


@dataclass
class GrupoServicios:
    id: str
    nombre: str
    servicios: list[EnlaceInternet | EnlaceDatos] = field(default_factory=list)


@dataclass
class Contrato:
    id: str
    nombre: str
    proveedor: str
    administrador: str
    fecha_inicio: str
    fecha_fin: str
    duracion_meses: int
    estado: str
    grupos: list[GrupoServicios] = field(default_factory=list)

    def servicios_flat(self) -> list[EnlaceInternet | EnlaceDatos]:
        """Retorna todos los servicios de todos los grupos en una lista plana."""
        return [s for g in self.grupos for s in g.servicios]
