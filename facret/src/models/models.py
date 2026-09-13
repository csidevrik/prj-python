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
class Upgrade:
    """Migración planificada de un servicio: de su estado actual a un destino."""
    tipo_destino: str          # "INTERNET", "DATOS", "NO HOUSING"
    bandwidth_destino: str
    valor_destino: float | None = None
    fecha_prevista: str | None = None
    aplicado: bool = False
    notas: str = ""


@dataclass
class EnlaceInternet:
    agencia_id: str
    grupo: str
    isp: str
    sdwan: bool
    bandwidth: str
    valor_mensual: float
    estado: str            # "ACTIVE", "CANCELED"
    estado_operativo: str  # "UP", "DOWN"
    dias_servicio: int
    tecnologia: str = ""   # "FIBRA GPON", etc.
    cod_serv: str | None = None       # no todos tienen código de instalación asignado aún
    ip_publica: str | None = None
    vigencia_meses: int | None = None
    fecha_inicio: str | None = None
    fecha_fin: str | None = None       # fin contractual planeado
    fecha_fin_real: str | None = None  # cuándo dejó de usarse realmente, si fue antes de fecha_fin
    notas: str = ""
    upgrade: Upgrade | None = None
    eventos: list[Evento] = field(default_factory=list)
    # resuelto en memoria al cargar — no está en el JSON
    agencia: Agencia | None = field(default=None, repr=False)


@dataclass
class EnlaceDatos:
    extremo_a: str
    extremo_b: str
    grupo: str
    isp: str
    sdwan: bool
    bandwidth: str
    valor_mensual: float
    estado: str
    estado_operativo: str
    dias_servicio: int
    tecnologia: str = ""
    cod_serv: str | None = None
    ip_publica: str | None = None
    vigencia_meses: int | None = None
    fecha_inicio: str | None = None
    fecha_fin: str | None = None
    fecha_fin_real: str | None = None
    notas: str = ""
    upgrade: Upgrade | None = None
    eventos: list[Evento] = field(default_factory=list)
    # resueltos en memoria al cargar
    agencia_extremo_a: Agencia | None = field(default=None, repr=False)
    agencia_extremo_b: Agencia | None = field(default=None, repr=False)


@dataclass
class EnlaceHousing:
    """Espacio/servicio de housing en datacenter (no es un enlace de datos ni internet)."""
    agencia_id: str
    grupo: str
    estado: str
    cod_serv: str | None = None
    valor_mensual: float = 0.0
    fecha_inicio: str | None = None
    fecha_fin: str | None = None
    fecha_fin_real: str | None = None
    notas: str = ""
    upgrade: Upgrade | None = None
    eventos: list[Evento] = field(default_factory=list)
    agencia: Agencia | None = field(default=None, repr=False)


# ---------------------------------------------------------------------------
# Incidentes (persistidos en MongoDB, no en el JSON del catálogo)
# ---------------------------------------------------------------------------

ATRIBUCION_ISP = "ISP"
ATRIBUCION_EMOV = "EMOV_EP"
ATRIBUCION_NO_ATRIBUIBLE = "NO_ATRIBUIBLE"
ATRIBUCION_PENDIENTE = "PENDIENTE"

UMBRAL_SLA_SEGUNDOS = 5 * 60  # caídas menores a esto no son imputables al proveedor


@dataclass
class Incidente:
    """Un evento de caída/degradación de un servicio. Vive en MongoDB por volumen e histórico de 3 años."""
    cod_serv: str
    ts_inicio: str              # ISO 8601, con timezone
    tipo: str                   # "CAIDA_TOTAL", "DEGRADACION", "MANTENIMIENTO"
    atribuible_a: str = ATRIBUCION_PENDIENTE
    ts_fin: str | None = None   # None mientras el incidente sigue abierto
    duracion_seg: int | None = None
    dentro_umbral_sla: bool | None = None
    descripcion: str = ""
    registrado_por: str = ""
    reportado_a_isp: bool = False
    id: str | None = field(default=None)  # str(ObjectId) al leer de Mongo


@dataclass
class GrupoServicios:
    id: str
    nombre: str
    servicios: list[EnlaceInternet | EnlaceDatos | EnlaceHousing] = field(default_factory=list)


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

    def servicios_flat(self) -> list[EnlaceInternet | EnlaceDatos | EnlaceHousing]:
        """Retorna todos los servicios de todos los grupos en una lista plana."""
        return [s for g in self.grupos for s in g.servicios]
