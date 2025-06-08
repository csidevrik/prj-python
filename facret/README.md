# FACRET - Automatización y Revisión de XML Financieros

## Descripción

FACRET es una herramienta de escritorio desarrollada en Python con Flet, orientada a automatizar la revisión y procesamiento de archivos XML de facturas y retenciones, principalmente para el área financiera de EMVO EP. El objetivo es agilizar la validación y análisis de grandes volúmenes de documentos electrónicos, permitiendo obtener resultados más rápidos y confiables.

## Características principales

- **Explorador de archivos**: Selección de carpetas y visualización de archivos XML, PDF y otros.
- **Previsualización**: Vista previa de archivos de texto y PDF (primer página como imagen).
- **Búsqueda avanzada**: Campo de búsqueda con resaltado de coincidencias tanto en el texto como en el borde del archivo listado.
- **Interfaz moderna**: Barra superior personalizada, menú lateral (nav rail) y diseño adaptable.
- **Automatización**: (Próximamente) Procesamiento automático de XML para validación y extracción de datos clave.
- **Portabilidad**: No requiere instalación de dependencias externas por parte del usuario final, todo está incluido en el proyecto.

## Estructura del proyecto

````text
facret/
├── src/
│   ├── gui.py                # Interfaz gráfica principal (Flet)
│   ├── logic/                # (Opcional) Lógica de procesamiento XML
│   └── poppler-XX/           # Binarios de Poppler para previsualización de PDFs
├── README.md
├── pyproject.toml / requirements.txt
└── ...
````

- **`src/gui.py`**: Contiene toda la lógica de la interfaz gráfica, manejo de archivos, búsqueda y preview.
- **`src/poppler-XX/Library/bin`**: Binarios de Poppler necesarios para convertir PDFs a imágenes (usados por pdf2image).
- **`src/logic/`**: (Opcional) Lugar sugerido para módulos de procesamiento y validación de XML.

## Librerías externas utilizadas

- **[Flet](https://flet.dev/)**: Framework para crear GUIs multiplataforma en Python.
- **[pdf2image](https://github.com/Belval/pdf2image)**: Convierte páginas PDF a imágenes PNG/JPEG.
- **[Poppler](https://poppler.freedesktop.org/)**: Utilidad nativa para procesar PDFs (se incluye en el proyecto, no requiere instalación por parte del usuario).

### ¿Dónde se usan?

- En `src/gui.py`, la función `show_pdf_as_image` utiliza `pdf2image.convert_from_path` y requiere la ruta a los binarios de Poppler para convertir la primera página de un PDF en una imagen que se muestra en la GUI.
- El preview de archivos PDF es completamente automático y no requiere configuración adicional por parte del usuario.

## Estructura de la GUI

- **Barra superior (AppBar)**: Incluye el título de la aplicación, campo de búsqueda global y accesos rápidos (notificaciones, configuración, ayuda, etc.).
- **Menú lateral (Nav Rail)**: Acceso a herramientas y módulos adicionales (por ejemplo, navegación entre facturas, retenciones, pagos, etc.).
- **Área de contenido principal**:
  - **Campo de búsqueda de archivos**: Permite filtrar archivos por nombre, resaltando coincidencias en la lista.
  - **Selector de carpeta**: Botón para abrir el explorador de carpetas y seleccionar el directorio de trabajo.
  - **Listado de archivos**: Muestra los archivos del directorio seleccionado, con resaltado visual de coincidencias.
  - **Vista previa**: Muestra el contenido del archivo seleccionado (texto o PDF como imagen).

## Cómo ejecutar

1. **Instala las dependencias** (usa Poetry o pip):

   ```bash
   poetry install
   # o
   pip install -r requirements.txt
   ```

2. **Asegúrate de que la carpeta `poppler-XX/Library/bin` esté dentro de `src/`** (ya incluida en el repositorio).

3. **Ejecuta la aplicación:**

   ```bash
   poetry run python src/gui.py
   # o
   python src/gui.py
   ```

## Uso

- Haz clic en "Open directory" para seleccionar la carpeta con los archivos XML/PDF.
- Usa el campo de búsqueda para filtrar archivos por nombre; las coincidencias se resaltan tanto en el texto como en el borde del archivo.
- Haz clic en un archivo para previsualizarlo (texto o PDF).
- Navega por el menú lateral para futuras herramientas y módulos.

## Notas técnicas

- El preview de PDF funciona sin que el usuario instale Poppler, ya que los binarios están incluidos y se usan desde el código.
- El sistema está preparado para ser portable y fácil de usar para usuarios no técnicos.
- El procesamiento automático de XML se integrará en futuras versiones.
- El código está preparado para ser empaquetado como un solo ejecutable (.exe) usando herramientas como PyInstaller, incluyendo los binarios de Poppler.

## Roadmap / Futuro

- Integración de procesamiento automático de XML (validación, extracción de datos, reportes).
- Mejoras en la visualización y navegación de archivos.
- Exportación de resultados y reportes.
- Integración con otros sistemas internos de EMVO EP.

## Créditos

Desarrollado por el área de sistemas de EMVO EP.

---

**¿Dudas o sugerencias?**  
Contacta al equipo de desarrollo o abre un issue en este repositorio.

