# FACRET - Automatización y Revisión de XML Financieros

## Descripción

FACRET es una herramienta de escritorio desarrollada en Python con Flet, orientada a automatizar la revisión y procesamiento de archivos XML de facturas y retenciones, principalmente para el área financiera de EMVO EP. El objetivo es agilizar la validación y análisis de grandes volúmenes de documentos electrónicos, permitiendo obtener resultados más rápidos y confiables.

## Características principales

- **Explorador de archivos**: Selección de carpetas y visualización de archivos XML, PDF y otros.
- **Previsualización**: Vista previa de archivos de texto y PDF (primer página como imagen).
- **Búsqueda avanzada**: Campo de búsqueda con resaltado de coincidencias tanto en el texto como en el borde del archivo listado.
- **Interfaz moderna**: Barra superior personalizada, menú lateral (nav rail) y diseño adaptable.
- **Automatización**: (Próximamente) Procesamiento automático de XML para validación y extracción de datos clave.

## Estructura del proyecto

La organización del proyecto FACRET sigue una arquitectura modular para separar responsabilidades y facilitar el mantenimiento. A continuación se describe cada carpeta y su propósito:

- **`data/`**: Contiene archivos y plantillas utilizados por la aplicación. Incluye subdirectorios para exportaciones, reportes, muestras (`samples`) y plantillas tanto de informes como de XML.
  - `exports/` – espacio para archivos generados por el sistema.
  - `samples/` – ejemplos de documentos (`sample_pdf`, `sample_xml`) usados para pruebas.
  - `templates/` – diseños para generar reportes y estructuras XML.

- **`docs/`**: Documentación del proyecto. Se estructura en carpetas `api/` y `user/` con capturas de pantalla y guías de uso para desarrolladores y usuarios finales.

- **`src/`**: Código fuente principal de la aplicación. Aquí se encuentra la lógica Flet y los componentes de UI.
  - **Punto de entrada**: `drive_gui.py` (interfaz activa recomendada)
  - **Componentes modulares**:
    - `components/` – widgets reutilizables organizados jerárquicamente
      - `header/` – subcomponentes de encabezado (búsqueda, marca, herramientas, sesión)
      - `drive_sidebar.py`, `drive_content.py`, `sync_status.py` – componentes principales
    - `config/` – configuraciones de tema y estilos
    - `core/` – servicios, modelos y utilidades de negocio
    - `logic/` – procesamiento de XML y transformaciones
    - `models/` – estructuras de datos
  - **Legacy (no usar)**: `gui.py`, `gui2.py`, `main.py`, `main_drive.py`, `main2.py` – versiones antiguas mantenidas por compatibilidad
  - **Documentación detallada** → Ver [`ESTRUCTURA_COMPONENTES.md`](ESTRUCTURA_COMPONENTES.md)

- **`poppler-24.08.0/`**: Dependencia nativa de Poppler incluida para manejar la renderización de PDFs en Windows.

- **`pyproject.toml`**: Archivo de configuración del proyecto Python, con dependencias y metadatos.

Esta disposición permite a los desarrolladores localizar rápidamente las áreas de interés y añadir nuevas funcionalidades sin afectar otras partes del sistema.

