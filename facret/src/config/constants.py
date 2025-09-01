# Constantes de la aplicación

# Menús de navegación
NAVIGATION_ITEMS = [
    {"id": "facturas", "title": "FACTURAS", "icon": "description", "view": "facturas_view"},
    {"id": "duplicates", "title": "DEL DUPLICATES", "icon": "delete", "view": "duplicates_view"},
    {"id": "rename", "title": "RENAME XML", "icon": "edit", "view": "rename_xml_view"},
    {"id": "del_prefix", "title": "DEL PREFIX", "icon": "remove_circle", "view": "del_prefix_view"},
    {"id": "retenciones", "title": "RETENCIONES", "icon": "receipt", "view": "retenciones_view"},
    {"id": "informes", "title": "INFORMES", "icon": "assessment", "view": "informes_view"},
    {"id": "xml", "title": "XML", "icon": "code", "view": "xml_view"},
    {"id": "pdf_viewer", "title": "PDF VIEWER", "icon": "visibility", "view": "pdf_viewer_view"}
]

# Extensiones de archivos soportadas
SUPPORTED_XML_EXTENSIONS = [".xml"]
SUPPORTED_PDF_EXTENSIONS = [".pdf"]
SUPPORTED_EXCEL_EXTENSIONS = [".xlsx", ".xls"]

# Mensajes de error
ERROR_MESSAGES = {
    "no_directory": "Por favor selecciona un directorio de trabajo",
    "invalid_file": "Archivo no válido o corrupto",
    "no_files_found": "No se encontraron archivos en el directorio",
    "permission_denied": "No tienes permisos para acceder a este archivo"
}