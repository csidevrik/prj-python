# =============================
# scripts/clasificar_facturas.py
# =============================
"""
Clasifica las facturas de ETAPA que llegan a Outlook (carpeta FACS) como
TELECOM, AGUA o REVISAR, mueve el correo a su carpeta y genera un informe.

Uso:
    python scripts/clasificar_facturas.py          # modo prueba: no mueve correos
    python scripts/clasificar_facturas.py --real   # mueve correos y registra procesados
"""
import argparse
import csv
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC))

from logic.facs_clasificador import AGUA, REVISAR, TELECOM, clasificar_xml  # noqa: E402
from logic.facs_manager import extract_fac_register  # noqa: E402
from logic.outlook_reader import (  # noqa: E402
    RUTA_FACS,
    OutlookETAPA,
    guardar_xml_adjuntos,
    info_correo,
    mover,
)

DIR_INFORMES = SRC.parent / "data" / "informes"
ARCHIVO_REGISTRO = DIR_INFORMES / "procesados.json"
ARCHIVO_BLOQUEO = DIR_INFORMES / ".ejecucion.lock"
MINUTOS_BLOQUEO_OBSOLETO = 30

CARPETA_POR_TIPO = {TELECOM: "TELECOM", AGUA: "AGUA", REVISAR: "REVISAR"}
COLUMNAS = [
    "fecha_hora", "modo", "entry_id", "remitente", "asunto", "recibido", "archivo",
    "numero_factura", "code_inst", "valor", "fecha_emision", "tipo", "evidencia", "accion", "error",
]


def adquirir_bloqueo() -> bool:
    DIR_INFORMES.mkdir(parents=True, exist_ok=True)
    if ARCHIVO_BLOQUEO.exists():
        antiguedad = datetime.now().timestamp() - ARCHIVO_BLOQUEO.stat().st_mtime
        if antiguedad < MINUTOS_BLOQUEO_OBSOLETO * 60:
            return False
        ARCHIVO_BLOQUEO.unlink()
    ARCHIVO_BLOQUEO.write_text(str(os.getpid()))
    return True


def liberar_bloqueo() -> None:
    if ARCHIVO_BLOQUEO.exists():
        ARCHIVO_BLOQUEO.unlink()


def cargar_registro() -> dict:
    if ARCHIVO_REGISTRO.exists():
        return json.loads(ARCHIVO_REGISTRO.read_text(encoding="utf-8"))
    return {}


def guardar_registro(registro: dict) -> None:
    ARCHIVO_REGISTRO.write_text(json.dumps(registro, indent=2, ensure_ascii=False), encoding="utf-8")


def escribir_informe(filas: list[dict]) -> Path:
    ruta = DIR_INFORMES / f"informe_{datetime.now():%Y-%m-%d}.csv"
    nuevo = not ruta.exists()
    with open(ruta, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNAS)
        if nuevo:
            writer.writeheader()
        writer.writerows(filas)
    return ruta


def clasificar_correo(mensaje, directorio_tmp: str) -> dict:
    fila = {"error": "", "numero_factura": "", "code_inst": "", "valor": "", "fecha_emision": "", "evidencia": ""}
    rutas = guardar_xml_adjuntos(mensaje, directorio_tmp)
    fila["archivo"] = os.path.basename(rutas[0]) if rutas else ""

    if not rutas:
        fila["tipo"] = REVISAR
        fila["error"] = "sin XML adjunto"
        return fila

    clasificaciones = []
    for ruta in rutas:
        try:
            clasificaciones.append(clasificar_xml(ruta))
        except Exception as e:
            fila["error"] = f"{type(e).__name__}: {e}"

    tipos = {c.tipo for c in clasificaciones}
    fila["tipo"] = tipos.pop() if len(tipos) == 1 and len(clasificaciones) == len(rutas) else REVISAR
    if clasificaciones:
        fila["evidencia"] = " | ".join(clasificaciones[0].evidencia)

    try:
        factura = extract_fac_register(rutas[0])
        fila["numero_factura"] = factura.number_fac
        fila["code_inst"] = factura.code_inst
        fila["valor"] = factura.value_serv
        fila["fecha_emision"] = factura.fecha_emision
    except Exception as e:
        fila["error"] = fila["error"] or f"{type(e).__name__}: {e}"

    return fila


def ejecutar(modo_real: bool) -> None:
    if not adquirir_bloqueo():
        print("Otra ejecución está en curso. Se omite esta corrida.")
        return

    modo = "real" if modo_real else "prueba"
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    registro = cargar_registro()
    filas = []

    try:
        outlook = OutlookETAPA()
        origen = outlook.carpeta(RUTA_FACS)
        destinos = {tipo: outlook.carpeta(f"{RUTA_FACS}\\{nombre}") for tipo, nombre in CARPETA_POR_TIPO.items()}
        correos = outlook.correos_etapa(origen)

        with tempfile.TemporaryDirectory() as tmp:
            for mensaje in correos:
                info = info_correo(mensaje)
                if info["entry_id"] in registro:
                    continue

                fila = {"fecha_hora": ahora, "modo": modo, "entry_id": info["entry_id"],
                        "remitente": info["remitente"], "asunto": info["asunto"], "recibido": info["recibido"]}
                fila.update(clasificar_correo(mensaje, tmp))

                if modo_real:
                    mover(mensaje, destinos[fila["tipo"]])
                    fila["accion"] = f"movido a {CARPETA_POR_TIPO[fila['tipo']]}"
                    registro[info["entry_id"]] = {"tipo": fila["tipo"], "fecha": ahora}
                else:
                    fila["accion"] = f"simulado: iría a {CARPETA_POR_TIPO[fila['tipo']]}"

                filas.append(fila)
    finally:
        if modo_real:
            guardar_registro(registro)
        liberar_bloqueo()

    if filas:
        ruta = escribir_informe(filas)
        print(f"Informe: {ruta}")
    resumen = {t: sum(1 for f in filas if f["tipo"] == t) for t in (TELECOM, AGUA, REVISAR)}
    print(f"Modo {modo}: {len(filas)} correo(s) revisados. Telecom={resumen[TELECOM]} "
          f"Agua={resumen[AGUA]} Revisar={resumen[REVISAR]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Clasifica facturas ETAPA en Outlook.")
    parser.add_argument("--real", action="store_true", help="mueve correos y registra procesados")
    args = parser.parse_args()
    ejecutar(modo_real=args.real)


if __name__ == "__main__":
    main()
