# Contratos ETAPA — Modelo de datos e incidentes en MongoDB

Este documento resume las decisiones tomadas para modelar el nuevo contrato de servicios (internet, datos, housing) y por qué el historial de caídas se guarda en MongoDB en vez de JSON.

## Por qué dos almacenes de datos

- **Catálogo (JSON, en `data/contracts/*.json` y `data/agencias.json`)**: contratos, grupos y servicios. Bajo volumen, cambia poco, se puede editar/leer completo sin problema.
- **Incidentes (MongoDB)**: historial de caídas por servicio, con retención de 3 años. Alto volumen, necesita consultas por fecha/servicio/atribución y agregaciones para reportes — un JSON no aguanta eso bien (reescritura completa en cada evento, sin queries).

## Cambios en `src/models/models.py`

- `Upgrade`: plan de migración de un servicio (tipo y ancho de banda destino, fecha prevista, si ya se aplicó). Separado del servicio actual para no mezclar estado presente y futuro.
- `EnlaceHousing`: tercer tipo de servicio (espacio en datacenter), antes solo existían `EnlaceInternet` y `EnlaceDatos`.
- `tecnologia` (ej. "FIBRA GPON"), `cod_serv` opcional (no todos los servicios tienen código de instalación asignado aún), y `fecha_fin_real` (cuándo se dio de baja en la práctica, si fue antes de la `fecha_fin` contractual) agregados a los tres tipos de enlace.
- `Incidente`: vive en Mongo, no en el JSON. Campos: `cod_serv`, `ts_inicio`, `ts_fin`, `duracion_seg`, `tipo`, `atribuible_a` (`ISP`, `EMOV_EP`, `NO_ATRIBUIBLE`, `PENDIENTE`), `dentro_umbral_sla`.
- `UMBRAL_SLA_SEGUNDOS = 300`: caídas menores a 5 minutos se marcan como no imputables al proveedor automáticamente al cerrar el incidente.

## Levantar MongoDB (Docker)

Requiere Docker Desktop instalado y corriendo.

```bash
cd facret
docker compose up -d
```

Esto levanta un contenedor `facret-mongo` (imagen `mongo:7`) en el puerto `27017`, con:
- usuario: `facret`
- password: `facret_dev`
- base de datos: `facret`

Para verificar que está corriendo: abrir Docker Desktop → pestaña Containers → debe verse el stack `facret` con el contenedor `mongo` en estado activo (punto verde).

## Conexión desde Python

`src/logic/incidentes_repo.py` se conecta usando la variable de entorno `FACRET_MONGO_URI` (con un default apuntando al contenedor local de arriba). No hace falta configurar nada si usas el `docker-compose.yml` del repo tal cual.

Funciones disponibles:
- `registrar_inicio_caida(cod_serv, tipo, descripcion, registrado_por)` → abre un incidente, retorna su id.
- `cerrar_incidente(incidente_id, atribuible_a, ...)` → calcula duración y aplica el umbral de SLA.
- `listar_incidentes(cod_serv=None, desde=None, hasta=None, atribuible_a=None)` → consulta el histórico con filtros opcionales.

## Pendiente

- Importar el Excel real de servicios (grupos G1–G5, upgrades, housing) al catálogo JSON — falta el script de carga y decidir si se genera un catálogo de `Agencia` automático desde las ubicaciones del Excel.
- Vista en el dashboard de Flet para mostrar el historial de incidentes por servicio (disponibilidad, incidentes por atribución).
- Formulario o webhook para registrar caídas sin tener que llamar las funciones de `incidentes_repo.py` a mano.
