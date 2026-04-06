# =============================
# logic/facs_manager.py
# =============================
"""
Funciones puras de procesamiento de facturas y retenciones XML del SRI Ecuador.
Sin dependencias de UI — importables desde cualquier página o script.

log_fn: función opcional para recibir mensajes de progreso.
        Si no se pasa, usa print() para compatibilidad con uso standalone.
"""
import csv
import hashlib
import json
import os
import platform
import subprocess
import xml.etree.ElementTree as ET
from typing import Callable, Optional

from models.models import Factura, Retencion

LogFn = Optional[Callable[[str], None]]


def _log(msg: str, log_fn: LogFn):
    if log_fn:
        log_fn(msg)
    else:
        print(msg)


# ── File utilities ────────────────────────────────────────────────────────────

def get_files_extension(folder: str, extension: str) -> list:
    """Retorna lista de archivos en folder que coincidan con la extension dada."""
    return [f for f in os.listdir(folder) if f.lower().endswith(extension.lower())]

def get_name(filename: str) -> str:
    return os.path.splitext(filename)[0].lower()

def get_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

def folder_exists(folder: str, log_fn: LogFn = None) -> bool:
    if not os.path.exists(folder):
        _log(f"El directorio {folder} no existe.", log_fn)
        return False
    return True

def remove_prefix(filename: str, prefix: str) -> str:
    name, ext = os.path.splitext(os.path.basename(filename))
    if name.startswith(prefix):
        return name[len(prefix):] + ext
    return name + ext

def remove_prefix_files(folder: str, prefix: str, extension: str, log_fn: LogFn = None):
    """Elimina el prefix de todos los archivos con la extension dada en folder."""
    count = 0
    for file in get_files_extension(folder, extension):
        if get_name(file).startswith(prefix.lower()):
            new_name = remove_prefix(file, prefix)
            os.rename(os.path.join(folder, file), os.path.join(folder, new_name))
            count += 1
    _log(f"Prefijo eliminado de {count} archivo(s).", log_fn)

def remove_prefix_files_pdf(folder: str, prefix: str, log_fn: LogFn = None):
    remove_prefix_files(folder, prefix, ".pdf", log_fn)


# ── XML utilities ─────────────────────────────────────────────────────────────

def replace_string_onxml(filexml: str, ssearch: str, sreplace: str = ""):
    try:
        with open(filexml, "r+", encoding="utf-8") as f:
            content = f.read()
            new_content = content.replace(ssearch, sreplace)
            if new_content != content:
                f.seek(0)
                f.write(new_content)
                f.truncate()
    except Exception as e:
        print(f"Error procesando {filexml}: {e}")

def replace_in_all_xml_files(folder: str, ssearch: str, sreplace: str = ""):
    for archivo in get_files_extension(folder, ".xml"):
        replace_string_onxml(os.path.join(folder, archivo), ssearch, sreplace)

def clean_xml_files(folder: str):
    """Normaliza entidades HTML y elimina envolturas CDATA en XMLs de retenciones."""
    replace_in_all_xml_files(folder, "&gt;", ">")
    replace_in_all_xml_files(folder, "&lt;", "<")
    replace_in_all_xml_files(
        folder,
        '<![CDATA[<?xml version="1.0" encoding="UTF-8"?>'
        '<comprobanteRetencion id="comprobante" version="1.0.0">',
    )
    replace_in_all_xml_files(folder, "</comprobanteRetencion>]]>")


# ── Hash / deduplicación ──────────────────────────────────────────────────────

def get_file_hash(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def remove_duplicate_files(folder: str, log_fn: LogFn = None):
    """Elimina duplicados por hash SHA-256, conservando el archivo más antiguo."""
    files = os.listdir(folder)
    grouped: dict = {}
    for name in files:
        path = os.path.join(folder, name)
        h = get_file_hash(path)
        grouped.setdefault(h, []).append(path)

    removed = 0
    for group in grouped.values():
        oldest = min(group, key=lambda x: os.path.getctime(x))
        for path in group:
            if path != oldest:
                os.remove(path)
                removed += 1

    _log(f"Duplicados eliminados: {removed} archivo(s).", log_fn)


# ── Renombrado ────────────────────────────────────────────────────────────────

def extract_xml_fragment(file_path: str, start_limit: str, end_limit: str):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    start = content.find(start_limit)
    end   = content.find(end_limit, start)
    return ET.fromstring(f"<factura>\n{content[start:end + len(end_limit)]}\n</factura>")

def build_numero_factura(estab: str, pto_em: str, secue: str) -> str:
    return f"FAC{estab}{pto_em}{secue}"

def build_filename_from_xml(file_path: str) -> str:
    root   = extract_xml_fragment(file_path, "<infoTributaria>", "</infoAdicional>")
    estab  = root.find(".//estab").text
    pto_em = root.find(".//ptoEmi").text
    secue  = root.find(".//secuencial").text
    codigo = root.find('.//campoAdicional[@nombre="Instalacion"]').text
    return f"{build_numero_factura(estab, pto_em, secue)}-{codigo}"

def rename_file_pair(folder: str, old_name: str, new_name: str):
    os.rename(
        os.path.join(folder, old_name),
        os.path.join(folder, f"{new_name}.xml"),
    )
    os.rename(
        os.path.join(folder, os.path.splitext(old_name)[0] + ".pdf"),
        os.path.join(folder, f"{new_name}.pdf"),
    )

def rename_files_with_attributes(folder: str, log_fn: LogFn = None):
    """Renombra pares XML+PDF usando los atributos del XML como nuevo nombre."""
    count = 0
    for xml_file in get_files_extension(folder, ".xml"):
        try:
            new_name = build_filename_from_xml(os.path.join(folder, xml_file))
            rename_file_pair(folder, xml_file, new_name)
            count += 1
        except Exception as e:
            _log(f"Error renombrando {xml_file}: {e}", log_fn)
    _log(f"Renombrados: {count} par(es) XML+PDF.", log_fn)


# ── Extracción XML → modelos ──────────────────────────────────────────────────

def extract_fac_register(xml_file_path: str) -> Factura:
    root   = extract_xml_fragment(xml_file_path, "<infoTributaria>", "</infoAdicional>")
    estab  = root.find(".//estab").text
    pto_em = root.find(".//ptoEmi").text
    secue  = root.find(".//secuencial").text
    codigo = root.find('.//campoAdicional[@nombre="Instalacion"]').text
    numero = build_numero_factura(estab, pto_em, secue)
    valor  = root.find(".//totalSinImpuestos").text
    return Factura(code_inst=codigo, number_fac=numero, value_serv=valor)

def get_register_xml_retencion(xml_file_path: str) -> Retencion:
    with open(xml_file_path, "r", encoding="utf-8") as f:
        content = f.read()
    root   = ET.fromstring(content)
    estab  = root.find(".//estab").text
    pto_em = root.find(".//ptoEmi").text
    secue  = root.find(".//secuencial").text
    ret_num = f"{estab}-{pto_em}-{secue}"
    ret_val = root.find(".//valorRetenido").text
    fac_num = "FAC" + root.find(".//numDocSustento").text
    return Retencion(ret_number=ret_num, ret_value=ret_val, fac_number=fac_num)


# ── Procesamiento masivo → JSON + CSV ─────────────────────────────────────────

def save_to_json(data, json_path: str):
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

def save_to_csv(data: list, csv_path: str):
    if not data:
        return
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(list(data[0].keys()))
        for row in data:
            writer.writerow(row.values())

def process_all_xml_facs(folder: str, log_fn: LogFn = None) -> int:
    """Procesa XMLs de facturas → facturas.json + facturas.csv. Retorna cantidad procesada."""
    if not folder_exists(folder, log_fn):
        return 0
    registros = []
    for filename in get_files_extension(folder, ".xml"):
        try:
            r = extract_fac_register(os.path.join(folder, filename))
            registros.append({
                "code_inst":  r.code_inst,
                "number_fac": r.number_fac,
                "value_serv": r.value_serv,
            })
        except Exception as e:
            _log(f"  Error en {filename}: {e}", log_fn)

    registros.sort(key=lambda x: x["code_inst"])
    json_path = os.path.join(folder, "facturas.json")
    csv_path  = os.path.join(folder, "facturas.csv")
    save_to_json(registros, json_path)
    save_to_csv(registros, csv_path)
    _log(f"Procesados {len(registros)} XML → facturas.json + facturas.csv", log_fn)
    return len(registros)

def process_all_xml_rets(folder: str, log_fn: LogFn = None) -> int:
    """Limpia y procesa XMLs de retenciones → retenciones.json + retenciones.csv."""
    if not folder_exists(folder, log_fn):
        return 0
    clean_xml_files(folder)
    registros = []
    for filename in get_files_extension(folder, ".xml"):
        try:
            r = get_register_xml_retencion(os.path.join(folder, filename))
            registros.append({
                "ret_number": r.ret_number,
                "ret_value":  r.ret_value,
                "fac_number": r.fac_number,
            })
        except Exception as e:
            _log(f"  Error en {filename}: {e}", log_fn)

    json_path = os.path.join(folder, "retenciones.json")
    csv_path  = os.path.join(folder, "retenciones.csv")
    save_to_json(registros, json_path)
    save_to_csv(registros, csv_path)
    _log(f"Procesadas {len(registros)} retenciones → retenciones.json + retenciones.csv", log_fn)
    return len(registros)


# ── Apertura de PDFs ──────────────────────────────────────────────────────────

def get_browser_command(browser: str) -> str:
    system = platform.system()
    if system == "Linux":
        return "google-chrome" if browser == "chrome" else "firefox"
    if system == "Windows":
        return f"start {browser}"
    raise OSError("Sistema operativo no compatible")

def open_pdf_with_browser(folder: str, browser_command: str, log_fn: LogFn = None):
    pdfs = get_files_extension(folder, ".pdf")
    pdfs.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
    for pdf in pdfs:
        path = os.path.abspath(os.path.join(folder, pdf))
        subprocess.run(f"{browser_command} --new-tab {path}", shell=True)
    _log(f"Abiertos {len(pdfs)} PDF(s) en el navegador.", log_fn)

def open_pdf_with_firefox(folder: str, log_fn: LogFn = None):
    open_pdf_with_browser(folder, get_browser_command("firefox"), log_fn)

def open_pdf_with_chrome(folder: str, log_fn: LogFn = None):
    open_pdf_with_browser(folder, get_browser_command("chrome"), log_fn)
