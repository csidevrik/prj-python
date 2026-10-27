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

from models.models import Factura, NotaCredito, Retencion
from utils.logger import get_logger

logger = get_logger(__name__)
LogFn = Optional[Callable[[str], None]]


def _log(msg: str, log_fn: LogFn):
    """Compatibilidad: si se pasa log_fn, úsalo; sino, usa el logger centralizado."""
    if log_fn:
        log_fn(msg)
    else:
        logger.info(msg)


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

def build_numero_noc(estab: str, pto_em: str, secue: str) -> str:
    return f"NOC{estab}{pto_em}{secue}"

def build_numero_ret(estab: str, pto_em: str, secue: str) -> str:
    return f"RET{estab}{pto_em}{secue}"

def build_filename_from_xml(file_path: str) -> str:
    """Construye nombre de archivo para FACTURA."""
    root   = extract_xml_fragment(file_path, "<infoTributaria>", "</infoAdicional>")
    estab  = root.find(".//estab").text
    pto_em = root.find(".//ptoEmi").text
    secue  = root.find(".//secuencial").text
    codigo = root.find('.//campoAdicional[@nombre="Instalacion"]').text
    return f"{build_numero_factura(estab, pto_em, secue)}-{codigo}"

def build_noc_filename_from_xml(file_path: str) -> str:
    """Construye nombre de archivo para NOTA DE CRÉDITO."""
    root   = extract_xml_fragment(file_path, "<infoTributaria>", "</infoAdicional>")
    estab  = root.find(".//estab").text
    pto_em = root.find(".//ptoEmi").text
    secue  = root.find(".//secuencial").text
    codigo = root.find('.//campoAdicional[@nombre="Instalacion"]').text
    return f"{build_numero_noc(estab, pto_em, secue)}-{codigo}"

def build_ret_filename_from_xml(file_path: str) -> str:
    """Construye nombre de archivo para RETENCIÓN (sin código de instalación)."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    root = ET.fromstring(content)
    estab  = root.find(".//estab").text
    pto_em = root.find(".//ptoEmi").text
    secue  = root.find(".//secuencial").text
    return build_numero_ret(estab, pto_em, secue)

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
    """Renombra pares XML+PDF detectando tipo (factura/NC/retención) y aplicando nomenclatura específica.

    Nomenclatura:
    - Factura:       FAC{estab}{ptoEmi}{secue}-{codigo}
    - Nota Crédito:  NOC{estab}{ptoEmi}{secue}-{codigo}
    - Retención:     RET{estab}{ptoEmi}{secue}
    """
    count = 0
    for xml_file in get_files_extension(folder, ".xml"):
        xml_path = os.path.join(folder, xml_file)
        try:
            doc_type = detect_document_type_etapa(xml_path)

            if doc_type == "factura":
                new_name = build_filename_from_xml(xml_path)
            elif doc_type == "notaCredito":
                new_name = build_noc_filename_from_xml(xml_path)
            elif doc_type == "retención":
                new_name = build_ret_filename_from_xml(xml_path)
            else:
                _log(f"Tipo desconocido para {xml_file}: {doc_type}", log_fn)
                continue

            rename_file_pair(folder, xml_file, new_name)
            count += 1
        except Exception as e:
            _log(f"Error renombrando {xml_file}: {e}", log_fn)
    _log(f"Renombrados: {count} par(es) XML+PDF.", log_fn)


# ── Detección de tipo de documento (ETAPA EP) ─────────────────────────────────

def detect_document_type_etapa(xml_file_path: str) -> str:
    """Detecta el tipo de documento XML de ETAPA EP.

    Analiza el campo <codDoc> para determinar si es factura o nota de crédito.

    Args:
        xml_file_path (str): Ruta del archivo XML a analizar.

    Returns:
        str: "factura" (codDoc=01) o "notaCredito" (codDoc=04).

    Raises:
        ValueError: Si el XML no tiene codDoc válido, la ruta no existe,
                   o no se puede parsear el archivo.

    Ejemplo:
        >>> tipo = detect_document_type_etapa("FAC001003000404284.xml")
        >>> print(tipo)
        'factura'
    """
    try:
        root = extract_xml_fragment(xml_file_path, "<infoTributaria>", "</infoAdicional>")
        cod_doc = root.find(".//codDoc").text

        if cod_doc == "01":
            return "factura"
        elif cod_doc == "04":
            return "notaCredito"
        else:
            raise ValueError(
                f"Tipo de documento no soportado en {xml_file_path}: codDoc={cod_doc} "
                f"(solo 01=Factura y 04=NotaCredito son válidos)"
            )
    except ValueError as e:
        raise ValueError(f"Error de validación en {xml_file_path}: {e}")
    except Exception as e:
        raise ValueError(
            f"Error al parsear XML {xml_file_path}: {type(e).__name__}: {e}"
        )


# ── Extracción XML → modelos ──────────────────────────────────────────────────

# Extract factura data from XML and return a Factura object.

def extract_fac_register(xml_file_path: str) -> Factura:
    root   = extract_xml_fragment(xml_file_path, "<infoTributaria>", "</infoAdicional>")
    estab  = root.find(".//estab").text
    pto_em = root.find(".//ptoEmi").text
    secue  = root.find(".//secuencial").text
    codigo = root.find('.//campoAdicional[@nombre="Instalacion"]').text
    numero = build_numero_factura(estab, pto_em, secue)
    valor  = root.find(".//totalSinImpuestos").text
    fech_emi  = root.find(".//fechaEmision").text
    fech_max_pago_elem = root.find('.//campoAdicional[@nombre="FechaMaxPago"]')
    fech_max_pago = fech_max_pago_elem.text if fech_max_pago_elem is not None else None
    return Factura(code_inst=codigo, number_fac=numero, value_serv=valor, fecha_emision=fech_emi, fecha_max_pago=fech_max_pago)

# Extract nota de crédito data from XML and return a NotaCredito object.

def extract_noc_register(xml_file_path: str) -> NotaCredito:
    root   = extract_xml_fragment(xml_file_path, "<infoTributaria>", "</infoAdicional>")
    estab  = root.find(".//estab").text
    pto_em = root.find(".//ptoEmi").text
    secue  = root.find(".//secuencial").text
    codigo = root.find('.//campoAdicional[@nombre="Instalacion"]').text
    numero = build_numero_factura(estab, pto_em, secue)
    valor  = root.find(".//valorModificacion").text
    fech_emi = root.find(".//fechaEmision").text
    fac_orig = root.find(".//numDocModificado").text
    fech_fac_orig = root.find(".//fechaEmisionDocSustento").text
    motivo = root.find(".//motivo").text
    return NotaCredito(code_inst=codigo, number_noc=numero, value_noc=valor, fecha_emision=fech_emi,
                       fac_original=fac_orig, fecha_fac_original=fech_fac_orig, motivo=motivo)

# Extract retencion data from XML and return a Retencion object.

def extract_ret_register(xml_file_path: str) -> Retencion:
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
                "fecha_emision":   r.fecha_emision,
                "fecha_max_pago": r.fecha_max_pago,
                "name_original": filename,
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

def process_all_xml_nocs(folder: str, log_fn: LogFn = None) -> int:
    """Procesa XMLs de notas de crédito → notas_credito.json + notas_credito.csv. Retorna cantidad procesada."""
    if not folder_exists(folder, log_fn):
        return 0
    registros = []
    for filename in get_files_extension(folder, ".xml"):
        try:
            r = extract_noc_register(os.path.join(folder, filename))
            registros.append({
                "code_inst": r.code_inst,
                "number_noc": r.number_noc,
                "value_noc": r.value_noc,
                "fecha_emision": r.fecha_emision,
                "fac_original": r.fac_original,
                "fecha_fac_original": r.fecha_fac_original,
                "motivo": r.motivo,
                "name_original": filename,
            })
        except Exception as e:
            _log(f"  Error en {filename}: {e}", log_fn)

    registros.sort(key=lambda x: x["code_inst"])
    json_path = os.path.join(folder, "notas_credito.json")
    csv_path  = os.path.join(folder, "notas_credito.csv")
    save_to_json(registros, json_path)
    save_to_csv(registros, csv_path)
    _log(f"Procesadas {len(registros)} notas de crédito → notas_credito.json + notas_credito.csv", log_fn)
    return len(registros)

def process_all_xml_rets(folder: str, log_fn: LogFn = None) -> int:
    """Limpia y procesa XMLs de retenciones → retenciones.json + retenciones.csv."""
    if not folder_exists(folder, log_fn):
        return 0
    clean_xml_files(folder)
    registros = []
    for filename in get_files_extension(folder, ".xml"):
        try:
            r = extract_ret_register(os.path.join(folder, filename))
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


# ── Orquestación automática: detectar, organizar, procesar ────────────────────

def has_valid_document_subdirs(folder: str) -> bool:
    """Verifica que existan AMBOS subdirectorios específicos: facs/ y nocs/"""
    facs_dir = os.path.join(folder, "facs")
    nocs_dir = os.path.join(folder, "nocs")
    return os.path.isdir(facs_dir) and os.path.isdir(nocs_dir)

def organize_documents_by_type(folder: str, log_fn: LogFn = None):
    """Detecta tipo de cada XML, crea subdirs (facs/, nocs/), mueve archivos XML + PDF correspondiente."""
    facs_dir = os.path.join(folder, "facs")
    nocs_dir = os.path.join(folder, "nocs")

    os.makedirs(facs_dir, exist_ok=True)
    os.makedirs(nocs_dir, exist_ok=True)

    moved_facs = 0
    moved_nocs = 0

    for filename in get_files_extension(folder, ".xml"):
        file_path = os.path.join(folder, filename)
        try:
            tipo = detect_document_type_etapa(file_path)
            base_name = os.path.splitext(filename)[0]
            pdf_name = base_name + ".pdf"
            pdf_path = os.path.join(folder, pdf_name)

            if tipo == "factura":
                new_xml_path = os.path.join(facs_dir, filename)
                os.rename(file_path, new_xml_path)
                if os.path.exists(pdf_path):
                    os.rename(pdf_path, os.path.join(facs_dir, pdf_name))
                moved_facs += 1
            elif tipo == "notaCredito":
                new_xml_path = os.path.join(nocs_dir, filename)
                os.rename(file_path, new_xml_path)
                if os.path.exists(pdf_path):
                    os.rename(pdf_path, os.path.join(nocs_dir, pdf_name))
                moved_nocs += 1
        except Exception as e:
            _log(f"  No se pudo organizar {filename}: {e}", log_fn)

    _log(f"Organizados: {moved_facs} facturas + PDFs → facs/, {moved_nocs} notas de crédito + PDFs → nocs/", log_fn)

def process_organized_folder(folder: str, log_fn: LogFn = None) -> dict:
    """Procesa los subdirectorios facs/ y nocs/ si existen."""
    result = {}

    facs_dir = os.path.join(folder, "facs")
    nocs_dir = os.path.join(folder, "nocs")

    if os.path.isdir(facs_dir):
        count = process_all_xml_facs(facs_dir, log_fn)
        result["facturas"] = count

    if os.path.isdir(nocs_dir):
        count = process_all_xml_nocs(nocs_dir, log_fn)
        result["notas_credito"] = count

    return result

def process_all_xml_documents(folder: str, log_fn: LogFn = None) -> dict:
    """Función maestra: auto-detecta estructura, organiza si es necesario, procesa.

    Retorna dict con resumen:
    {'facturas': N, 'notas_credito': M}
    """
    if not folder_exists(folder, log_fn):
        return {}

    _log(f"Procesando documentos ETAPA EP en {folder}...", log_fn)

    if has_valid_document_subdirs(folder):
        _log("Estructura válida detectada (facs/ + nocs/). Procesando...", log_fn)
    else:
        _log("Estructura incompleta/mezclada. Organizando automáticamente...", log_fn)
        organize_documents_by_type(folder, log_fn)

    return process_organized_folder(folder, log_fn)


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
