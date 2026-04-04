# FACRET — Automatización y Revisión de XML Financieros

Herramienta de escritorio desarrollada en Python con [Flet](https://flet.dev/), orientada a automatizar la revisión y procesamiento de archivos XML de facturas y retenciones para el área financiera de **EMVO EP**.

---

## Qué hace

- Explora carpetas y lista archivos XML, PDF y otros documentos financieros.
- Previsualiza archivos de texto y PDF (primera página como imagen).
- Búsqueda avanzada con resaltado de coincidencias en contenido y nombre de archivo.
- Procesa y valida XML de facturas y retenciones: extracción de datos, detección de duplicados y renombrado.
- Interfaz moderna estilo explorador de archivos con header responsivo, sidebar de navegación y barra de estado.

---

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Lenguaje | Python >= 3.11 |
| UI Framework | [Flet](https://flet.dev/) 0.28.x |
| Renderizado PDF | pdf2image + Poppler 24.08.0 |
| Gestión de proyecto | [Poetry](https://python-poetry.org/) |

---

## Requisitos previos

- Python 3.11 o superior
- [Poetry](https://python-poetry.org/docs/#installation) instalado
- Poppler instalado en el sistema (incluido en `src/poppler-24.08.0/` para Windows)

---

## Instalación

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd prj-python/facret

# Instalar dependencias con Poetry
poetry install

# Ejecutar la aplicación
poetry run python src/drive_gui.py
```

---

## Estructura del proyecto

```
facret/
├── pyproject.toml              # Configuración Poetry
├── poetry.lock                 # Dependencias resueltas
├── README.md
│
├── src/                        # Código fuente
│   ├── drive_gui.py            # Punto de entrada principal
│   │
│   ├── components/             # Componentes UI reutilizables
│   │   ├── header/             # Encabezado superior (responsivo)
│   │   │   ├── responsive_header.py   # Orquestador del header
│   │   │   ├── app_brand.py           # Logo y nombre de la app
│   │   │   ├── search_component.py    # Búsqueda con filtros
│   │   │   ├── tools_component.py     # Botones de acción
│   │   │   └── user_session.py        # Sesión y perfil de usuario
│   │   ├── drive_sidebar.py    # Menú lateral de navegación
│   │   ├── drive_content.py    # Área principal de contenido
│   │   └── sync_status.py      # Barra de estado inferior
│   │
│   ├── config/
│   │   └── drive_theme.py      # Tema global: colores, tipografía, estilos
│   │
│   ├── core/                   # Lógica de negocio
│   │   ├── models/             # Estructuras de datos (file_model, xml_model)
│   │   ├── services/           # Servicios (file, xml, duplicados, renombrado)
│   │   └── utils/              # Utilidades internas
│   │
│   ├── logic/                  # Procesamiento XML
│   │   ├── logic.py
│   │   └── xml_processor.py
│   │
│   ├── models/                 # Modelos de datos (Registro, RegistroRet)
│   │   └── models.py
│   │
│   ├── utils/                  # Utilidades generales
│   │   ├── helpers.py
│   │   └── utiles.py
│   │
│   ├── assets/                 # Recursos estáticos
│   │   ├── favicon.ico
│   │   └── favicon.png
│   │
│   └── poppler-24.08.0/        # Binarios Poppler para Windows (PDF rendering)
│
├── data/                       # Datos y plantillas
│   ├── exports/                # Archivos generados (logs, reportes)
│   ├── samples/                # Documentos de ejemplo para pruebas
│   └── templates/              # Plantillas de reportes y XML
│
└── docs/                       # Documentación externa
    ├── api/
    └── user/
```

---

## Arquitectura

El flujo de ejecución sigue un patrón orquestador → componentes:

```
drive_gui.py  (orquestador)
    ├── config/drive_theme.py          ← tema global
    ├── components/header/
    │   └── responsive_header.py       ← header con 4 subcomponentes
    ├── components/drive_sidebar.py    ← navegación lateral
    ├── components/drive_content.py    ← contenido + servicios core
    └── components/sync_status.py      ← estado del sistema
```

Para más detalle ver:

- [ARQUITECTURA_RAPIDA.md](ARQUITECTURA_RAPIDA.md) — flujo completo en 5 minutos
- [ESTRUCTURA_COMPONENTES.md](ESTRUCTURA_COMPONENTES.md) — mapa detallado de dependencias
- [ESTRUCTURA_VISUAL.md](ESTRUCTURA_VISUAL.md) — diagramas visuales antes/después

---

## Estado actual del proyecto

### Logros implementados

- Interfaz de explorador de archivos completamente funcional con diseño responsivo.
- Header modular dividido en 4 subcomponentes independientes (brand, search, tools, session).
- Sidebar de navegación con estructura jerárquica.
- Área de contenido con listado, previsualización y operaciones sobre archivos.
- Barra de estado con soporte para notificaciones y progreso.
- Tema centralizado (`drive_theme.py`) que controla toda la paleta visual.
- Servicios de negocio para procesamiento XML, detección de duplicados y renombrado.
- Dependencia de Poppler empaquetada para funcionamiento offline en Windows.

### Deuda técnica identificada

Existen archivos legacy de versiones anteriores de la interfaz. Están documentados en [PLAN_LIMPIEZA.md](PLAN_LIMPIEZA.md) con un checklist de eliminación por fases.

---

## Documentación interna

| Archivo | Para qué sirve | Tiempo de lectura |
|---|---|---|
| [ARQUITECTURA_RAPIDA.md](ARQUITECTURA_RAPIDA.md) | Entender el flujo rápidamente | 5 min |
| [ESTRUCTURA_COMPONENTES.md](ESTRUCTURA_COMPONENTES.md) | Mapa completo de componentes y dependencias | 10-15 min |
| [ESTRUCTURA_VISUAL.md](ESTRUCTURA_VISUAL.md) | Diagramas visuales del árbol de archivos | 3 min |
| [PLAN_LIMPIEZA.md](PLAN_LIMPIEZA.md) | Checklist para eliminar código legacy | 10 min |
| [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) | Análisis de archivos huérfanos y recomendaciones | 5 min |
| [INDICE_DOCUMENTACION.md](INDICE_DOCUMENTACION.md) | Índice maestro de toda la documentación | referencia |

---

## Licencia

MIT — Carlos Sigua
