# prj-python

Repositorio de proyectos Python de Carlos Sigua.

---

## Proyectos

### [facret/](facret/)

Herramienta de escritorio para automatizar la revisión y procesamiento de archivos XML de facturas y retenciones financieras. Desarrollada con Python y [Flet](https://flet.dev/).

**Stack:** Python 3.11+, Flet 0.28.x, pdf2image, Poppler, Poetry

**Ejecutar:**
```bash
cd facret
poetry install
poetry run python src/drive_gui.py
```

Ver [facret/README.md](facret/README.md) para documentación completa.

#### Estructura de FACRET

Es una app de escritorio construida con **Flet** (Python + Flutter).

**Punto de entrada activo:** [drive_gui.py](facret/src/drive_gui.py) — el orquestador principal. Ensambla todos los componentes.

**Layout visual:**
```
┌─────────────────────────────────────────┐
│  Header (responsive_header.py)          │
│  [Logo] [Búsqueda] [Tools] [Usuario]    │
├─────────────────────────────────────────┤
│  Toolbar (drive_toolbar.py)             │
│  [≡]  >  Página principal              │
├──────────┬──────────────────────────────┤
│ Sidebar  │  sync_status.py (barra top)  │
│ (toggle) ├──────────────────────────────┤
│          │  drive_content.py            │
│          │  (contenido principal)       │
└──────────┴──────────────────────────────┘
```

**Carpetas importantes:**

| Carpeta | Qué hay |
|---------|---------|
| [components/](facret/src/components/) | Widgets UI: header, sidebar, content, sync |
| [components/header/](facret/src/components/header/) | Sub-partes del header (brand, search, tools, user) |
| [config/](facret/src/config/) | Tema visual (`drive_theme.py`) |
| [logic/](facret/src/logic/) | Procesamiento XML |
| [models/](facret/src/models/) | Estructuras de datos |

---

## Estructura del repositorio

```
prj-python/
├── facret/         # App de escritorio XML financiero (proyecto activo)
└── README.md
```
