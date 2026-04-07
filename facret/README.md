# FACRET — Automatización y Revisión de XML Financieros

Herramienta de escritorio desarrollada en Python con [Flet](https://flet.dev/), orientada a automatizar la revisión y procesamiento de archivos XML de facturas y retenciones para el área financiera de **EMOV EP**.

---

## Qué hace

- Explora carpetas y lista archivos XML, PDF y otros documentos financieros.
- Procesa y valida XML de facturas y retenciones: extracción de datos, detección de duplicados y renombrado.
- Descarga facturas ETAPA directamente desde Outlook local (sin cuenta Microsoft paga).
- Interfaz moderna estilo explorador de archivos con header responsivo, sidebar de navegación y breadcrumb.
- Cambio de tema visual en tiempo real desde el panel de configuración.

---

## Stack tecnológico

| Componente             | Tecnología                           |
| ---------------------- | ------------------------------------- |
| Lenguaje               | Python >= 3.11                        |
| UI Framework           | [Flet](https://flet.dev/) 0.28.3      |
| Renderizado PDF        | pdf2image + Poppler 24.08.0           |
| Automatización Outlook | pywin32 (win32com)                    |
| Gestión de proyecto    | [Poetry](https://python-poetry.org/)  |

---

## Requisitos previos

- Python 3.11 o superior
- [Poetry](https://python-poetry.org/docs/#installation) instalado
- Poppler incluido en `src/poppler-24.08.0/` para Windows
- Microsoft Outlook instalado y configurado (para la funcionalidad Download FACS)

---

## Instalación y ejecución en desarrollo

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd prj-python/facret

# Instalar dependencias con Poetry
poetry install

# Ejecutar la aplicación
poetry run python src/main.py
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
│   ├── main.py                 # Punto de entrada
│   ├── gui.py                  # Orquestador principal de la UI + router dinámico
│   │
│   ├── components/             # Componentes UI reutilizables
│   │   ├── header/
│   │   │   ├── responsive_header.py   # Orquestador del header
│   │   │   ├── app_brand.py           # Logo y nombre de la app
│   │   │   ├── search_component.py    # Búsqueda con filtros
│   │   │   ├── tools_component.py     # Botones de acción
│   │   │   └── user_session.py        # Sesión y perfil de usuario
│   │   ├── toolbar.py          # Barra secundaria: hamburguesa + breadcrumb
│   │   ├── sidebar.py          # Menú lateral de navegación (colapsable)
│   │   └── settings_panel.py   # Panel de configuración y cambio de tema
│   │
│   ├── pages/                  # Páginas cargadas dinámicamente por el router
│   │   ├── home_page.py        # Página principal
│   │   ├── facs_downloader_page.py  # Descarga de facturas ETAPA
│   │   └── facs_manager_page.py     # Gestión y procesamiento de facturas
│   │
│   ├── config/
│   │   ├── menu_config.py      # Fuente única de verdad para la navegación
│   │   ├── theme.py            # Tema global: colores, tipografía, estilos
│   │   ├── facs_config.json    # Configuración de rutas y parámetros FACS
│   │   └── gradients.json      # Paleta de gradientes para el tema
│   │
│   ├── logic/
│   │   ├── facs_downloader.py  # Descarga desde Outlook vía win32com
│   │   └── facs_manager.py     # Procesamiento de XML: parseo, renombrado, CSV/JSON
│   │
│   ├── models/
│   │   └── models.py           # Dataclasses: Factura, Retencion
│   │
│   ├── assets/                 # Recursos estáticos
│   │   ├── favicon.ico
│   │   ├── favicon.png
│   │   └── icon.png            # Ícono usado por flet build
│   │
│   └── poppler-24.08.0/        # Binarios Poppler para Windows (pdf2image)
│
├── data/
│   └── exports/                # Archivos generados (logs, reportes)
│
└── _legacy/                    # Versiones anteriores (no activas)
```

---

## Arquitectura

El router en `gui.py` carga las páginas dinámicamente usando `importlib`. Para agregar una nueva sección basta con registrarla en `config/menu_config.py`.

```
main.py
  └── gui.py  (orquestador + router)
        ├── config/theme.py                    ← tema global
        ├── config/menu_config.py              ← registro de rutas
        ├── components/header/
        │   └── responsive_header.py           ← header con 4 subcomponentes
        ├── components/toolbar.py              ← hamburguesa + breadcrumb
        ├── components/sidebar.py              ← navegación lateral (colapsable)
        └── pages/  (cargadas dinámicamente)
            ├── home_page.py
            ├── facs_downloader_page.py
            └── facs_manager_page.py
```

---

## Compilar el ejecutable para Windows

Requiere [Flutter](https://docs.flutter.dev/get-started/install) y Flet CLI instalados.

```bash
cd facret
flet build windows src --project FACRET --product "FACRET" --org com.facret
```

El `.exe` resultante queda en `src/build/windows/facret.exe`.

> **Importante:** `main.py` debe llamar a `run_drive_gui()` sin el guard `if __name__ == "__main__":`, ya que Flet importa el módulo en lugar de ejecutarlo directamente.

---

## Cambiar el ícono del ejecutable compilado

El build de Flet usa `src/assets/icon.png` para el ícono de la ventana. Para cambiar también el ícono del `.exe` a nivel del sistema operativo, usar **rcedit**:

1. Descargar `rcedit-x64.exe` desde: `github.com/electron/rcedit/releases`
2. Ejecutar en PowerShell:

```powershell
.\rcedit-x64.exe "src\build\windows\facret.exe" --set-icon "src\assets\favicon.ico"
```

> El archivo `.ico` debe contener múltiples resoluciones (16x16, 32x32, 48x48, 256x256). Se puede generar desde `favicon.png` con herramientas como GIMP o icoconvert.com.

---

## Licencia

MIT — Carlos Sigua
