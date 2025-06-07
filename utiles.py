import os
import hashlib

# def remove_prefix_files_pdf(folder, prefix):
#     # Obtener la lista de archivos en la carpeta
#     files = os.listdir(folder)
#     files_pdf = [file for file in files if file.lower().endswith(".pdf")]

#     # Iterar a través de los archivos PDF y renombrarlos
#     for file_pdf in files_pdf:
#         # Obtener el nombre del archivo sin extensión
#         nombre_sin_extension = os.path.splitext(file_pdf)[0]

#         # Verificar si el nombre del archivo PDF comienza con el prefijo dado
#         if nombre_sin_extension.startswith(prefix):
#             # Eliminar el prefijo del nombre del archivo PDF
#             nuevo_nombre = nombre_sin_extension[len(prefix):]

#             # Construir el nuevo nombre del archivo PDF
#             nuevo_nombre_pdf = nuevo_nombre + ".pdf"

#             # Ruta completa del archivo original y nuevo
#             ruta_archivo_original = os.path.join(folder, file_pdf)
#             ruta_archivo_nuevo = os.path.join(folder, nuevo_nombre_pdf)

#             # Renombrar el archivo PDF
#             os.rename(ruta_archivo_original, ruta_archivo_nuevo)

def remove_prefix_files_csv(folder, prefix):
    extension = '.csv'
    remove_prefix_files(folder, prefix, extension)

def remove_prefix_files_txt(folder, prefix):
    extension = '.txt'
    remove_prefix_files(folder, prefix, extension)
    
def remove_prefix_files_xml(folder, prefix):
    extension = '.xml'
    remove_prefix_files(folder, prefix, extension)

def remove_prefix_files(folder, prefix, extension):
    files = get_files_extension(folder, extension)
    """
    Elimina un prefijo específico de los nombres de archivos con una extensión dada en una carpeta.
    :param folder: Ruta de la carpeta donde buscar los archivos.
    :param prefix: Prefijo a eliminar de los nombres de archivo.
    :param extension: Extensión de los archivos a procesar (ejemplo: '.txt').
    :return: Lista de archivos renombrados.
    """
    for file in files:
        if get_name(file).startswith(prefix):
            new_name = remove_prefix(file, prefix)
            old_path = os.path.join(folder, file)
            new_path = os.path.join(folder, new_name)
            os.rename(old_path, new_path)

def get_files_extension(folder, extension):    
    """
    Obtiene una lista de archivos con una extensión específica en una carpeta.
    :param folder: Ruta de la carpeta donde buscar los archivos.
    :param extension: Extensión de los archivos a buscar (ejemplo: '.txt').
    :return: Lista de archivos con la extensión especificada.
    """
    files = os.listdir(folder)
    files_with_extension = [file for file in files if file.lower().endswith(extension.lower())] 
    return files_with_extension

def remove_prefix(filename, prefix):
    """
    Elimina un prefijo específico de un nombre de archivo.
    :param filename: Nombre del archivo original.
    :param prefix: Prefijo a eliminar.
    :return: Nombre del archivo sin el prefijo.
    """
    name, ext = os.path.splitext(os.path.basename(filename))
    if name.startswith(prefix):
        new_name = name[len(prefix):] + ext
    else:
        new_name = name + ext
    return new_name


def get_name(filename):
    return os.path.splitext(filename)[0].lower()

def get_path(filename):
    return os.path.dirname(filename) if os.path.dirname(filename) else '.'

def get_extension(filename):
    return os.path.splitext(filename)[1].lower()   
 
   

def remove_duplicate_files(folder):
    files = os.listdir(folder)
    # Agrupa los archivos por su valor de hash SHA-256
    grouped_files = {}
    for file_name in files:
        file_path = os.path.join(folder, file_name)
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        if file_hash not in grouped_files:
            grouped_files[file_hash] = []

        grouped_files[file_hash].append(file_path)

    # Elimina los archivos duplicados
    for file_group in grouped_files.values():
        oldest_file = min(file_group, key=lambda x: os.path.getctime(x))
        for file_path in file_group:
            if file_path != oldest_file:
                os.remove(file_path)

def replace_string_onxml(filexml: str, ssearch: str, sreplace: str):
    """
    Reemplaza todas las ocurrencias de ssearch por sreplace en el archivo XML dado.
    """
    try:
        with open(filexml, 'r+', encoding='utf-8') as f:
            contenido = f.read()
            nuevo_contenido = contenido.replace(ssearch, sreplace)
            if nuevo_contenido != contenido:
                f.seek(0)
                f.write(nuevo_contenido)
                f.truncate()
    except Exception as e:
        print(f"Error processing file {filexml}: {e}")

def delete_CDATA(folder):
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
    delete_CDATA(folder)