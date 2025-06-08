import os
import json
import csv
import xml.etree.ElementTree as ET
from src.models.models import Registro, RegistroRet
from src.utils.utiles import replace_string_onxml, remove_prefix_files, get_files_extension, remove_prefix, get_name, get_path




def delete_cdata(folder):
    ssearch1 = '<![CDATA[<?xml version="1.0" encoding="UTF-8"?><comprobanteRetencion id="comprobante" version="1.0.0">'
    ssearch2 = '</comprobanteRetencion>]]>'
    for archivo in os.listdir(folder):
        if archivo.lower().endswith('.xml'):
            ruta = os.path.join(folder, archivo)
            replace_string_onxml(ruta, ssearch1, '')
            replace_string_onxml(ruta, ssearch2, '')

def replace_menorque(folder):
    for archivo in os.listdir(folder):
        if archivo.lower().endswith('.xml'):
            ruta = os.path.join(folder, archivo)
            replace_string_onxml(ruta, '&lt;', '<')

def replace_mayorque(folder):
    for archivo in os.listdir(folder):
        if archivo.lower().endswith('.xml'):
            ruta = os.path.join(folder, archivo)
            replace_string_onxml(ruta, '&gt;', '>')

def clean_xml_files(folder):
    replace_mayorque(folder)
    replace_menorque(folder)
    delete_cdata(folder)

# ...aquí agrega el resto de tus funciones de lógica, como remove_duplicate_files, process_all_xml_files, etc...