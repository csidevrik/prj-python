# Prompt — Proyecto base Flet (Desktop App)

Quiero construir una aplicación de escritorio en Python usando Flet, siguiendo
exactamente la arquitectura de un proyecto de referencia que ya existe y funciona.
El objetivo es tener una base reutilizable para cualquier nuevo proyecto.

---

## STACK

- Python >= 3.11
- Flet 0.28.x (flet + flet-desktop)
- Poetry para gestión de dependencias
- Compilación con: `flet build windows src --project APPNAME --product "APPNAME" --org com.empresa`

---

## ESTRUCTURA DE CARPETAS

```
src/
├── main.py                  # Punto de entrada — llama run_app() sin guard __main__
├── gui.py                   # Orquestador + router dinámico
├── assets/
│   ├── favicon.ico
│   ├── favicon.png
│   └── icon.png             # Ícono usado por flet build
├── components/
│   ├── header/
│   │   ├── responsive_header.py
│   │   ├── app_brand.py
│   │   ├── search_component.py
│   │   ├── tools_component.py
│   │   └── user_session.py
│   ├── sidebar.py
│   ├── toolbar.py
│   └── settings_panel.py
├── pages/
│   ├── home_page.py
│   └── <nombre>_page.py     # Una por cada sección del menú
├── config/
│   ├── menu_config.py       # Fuente única de verdad de la navegación
│   └── theme.py             # AppTheme — paleta semántica + helpers
├── logic/                   # Lógica de negocio sin dependencias de UI
└── models/
    └── models.py            # Dataclasses de dominio
```

---

## ARQUITECTURA DE NAVEGACIÓN (gui.py)

`gui.py` orquesta toda la UI. Implementa:

**1. Router dinámico con importlib:**
```python
def _load_page(page_class_path: str, flet_page) -> ft.Control:
    module_path, class_name = page_class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls(flet_page).build()
```

**2. Función `rebuild()`** que reconstruye todos los componentes desde cero
(header, sidebar, toolbar, content_area). Se llama al iniciar y cada vez
que el usuario cambia el tema.

**3. Callback `on_navigate(key)`** compartido entre sidebar y header,
expuesto a las páginas vía:
```python
page.data = {"on_navigate": on_navigate, "on_theme_change": rebuild}
```

**4. Layout fijo:**
```
Column [
  Header           (fijo arriba)
  Toolbar/breadcrumb (fijo debajo del header)
  Row [
    Sidebar (colapsable, 280px)
    Container(expand=True)  ← aquí se inyecta la página activa
  ]
]
```

---

## MENU CONFIG (config/menu_config.py)

Fuente única de verdad. Para agregar una página al menú, solo hay que
registrarla aquí. El router la carga automáticamente.

```python
@dataclass
class MenuItem:
    key: str
    label: str
    icon: str               # ft.Icons.XXXX
    page_class: str | None  # "pages.module.ClassName"
    children: list[MenuItem] = field(default_factory=list)

MENU_ITEMS = [
    MenuItem(key="home",     label="Inicio",    icon=ft.Icons.HOME_OUTLINED,
             page_class="pages.home_page.HomePage"),
    MenuItem(key="seccion1", label="Sección 1", icon=ft.Icons.XXXX,
             page_class="pages.seccion1_page.Seccion1Page"),
    # agregar secciones reales del proyecto
]

SYSTEM_ITEMS = [   # No aparecen en el sidebar, pero el router los conoce
    MenuItem(key="settings", label="Configuración",
             page_class="components.settings_panel.SettingsPanel"),
    MenuItem(key="profile",  label="Perfil", page_class=None),
    MenuItem(key="help",     label="Ayuda",  page_class=None),
]

ALL_ITEMS = MENU_ITEMS + SYSTEM_ITEMS
```

---

## SIDEBAR (components/sidebar.py)

Clase `DriveSidebarComponent`. Implementa tres zonas:

**ZONA SUPERIOR — Buscador de menús**
- `TextField` con `on_change` que filtra `MENU_ITEMS` por label
- Mientras hay texto: oculta `_nav_column`, muestra `_results_card` (lista filtrada)
- Al seleccionar resultado: limpia búsqueda, navega, restaura menú normal
- La búsqueda usa `flat_menu()` para soportar ítems con `children` en el futuro

**ZONA MEDIA — Menú de navegación**
- Lista de `ListTile` por cada `MenuItem`
- Ítem seleccionado: fondo con opacidad 10% del PRIMARY, texto e ícono en PRIMARY
- Al hacer clic: actualiza `selected_item`, reconstruye la lista, llama `on_nav_change`

**ZONA INFERIOR — Footer fijo al fondo (estilo ChatGPT)**
- Sección de almacenamiento con `ProgressBar` (decorativa, configurable)
- `Divider`
- Avatar circular con iniciales + nombre + email + `PopupMenuButton` (icono `···`) con opciones:
  - Perfil → navega a `"profile"`
  - Configuración → navega a `"settings"`
  - Ayuda → navega a `"help"`
  - `[Divider]`
  - Cerrar sesión (en color ERROR)

Método `_toggle_sidebar(e)`: alterna `width` entre 280 y 0.
El botón hamburguesa del toolbar llama a este método.

---

## TOOLBAR / BREADCRUMB (components/toolbar.py)

Barra delgada debajo del header. Contiene:
- `IconButton` hamburguesa → llama `sidebar._toggle_sidebar`
- `Icon` CHEVRON_RIGHT
- `Text` con el label de la sección activa

Método `update_breadcrumb(key)`: actualiza el texto buscando el label en:
```python
LABEL_MAP = {item.key: item.label for item in ALL_ITEMS}
```

---

## HEADER (components/header/)

`ResponsiveDriveHeader` orquesta 4 subcomponentes en un `Row`:
1. `AppBrandComponent` — ícono de la app + nombre en texto
2. `SearchComponent` — `TextField` de búsqueda global (`expand=True`)
3. `ToolsComponent` — botones de acción rápida (`IconButton`)
4. `UserSessionComponent` — avatar del usuario

El header acepta un callback `on_navigate` para que los botones de herramientas
puedan navegar a secciones.

---

## SISTEMA DE TEMAS (config/theme.py)

Una sola clase `AppTheme` con atributos de clase (no de instancia).
Nombres semánticos siguiendo Material Design 3:

```python
class AppTheme:
    SEED = "#007a8c"
    PRIMARY = "#0b5f78"
    ON_PRIMARY = "#ffffff"
    PRIMARY_CONTAINER = "#b8dde6"
    SECONDARY = "#0097a7"
    SURFACE = "#ffffff"
    SURFACE_VARIANT = "#f0f7f8"
    ON_SURFACE = "#1a2b2e"
    ON_SURFACE_VARIANT = "#3d5a5e"
    OUTLINE = "#c2d8db"
    ERROR = "#ba1a1a"
    SUCCESS = "#1a7a4a"

    @staticmethod
    def get_theme() -> ft.Theme:
        return ft.Theme(color_scheme_seed=AppTheme.SEED,
                        visual_density=ft.VisualDensity.COMPACT)

    @staticmethod
    def get_card_style() -> dict:
        # bgcolor=SURFACE, border_radius=12, BoxShadow sutil
        ...

    @staticmethod
    def avatar_style(initials: str, size: int = 32) -> ft.Container:
        # Círculo con iniciales, bgcolor=PRIMARY
        ...
```

Para cambiar el tema en runtime: se modifican los atributos de clase
(`T.PRIMARY = nuevo_color`, etc.) y se llama `page.data["on_theme_change"]()`
que ejecuta `rebuild()` y reconstruye toda la UI con los nuevos colores.

---

## PANEL DE CONFIGURACIÓN (components/settings_panel.py)

Accesible desde Configuración (menú footer del sidebar). Secciones:

**1. Paleta de colores:** `GridView` de tarjetas, cada una muestra una franja
de 4 swatches (PRIMARY / PRIMARY_CONTAINER / SURFACE / ON_SURFACE).
Al hacer clic aplica el tema y llama `on_theme_change` → `rebuild()`.
Temas predefinidos: Google Blue, Teal Verde, Índigo, Navy Slate, Emerald, Rose.

**2. Acerca de:** versión, motor UI, información del sistema.

---

## ESTRUCTURA DE CADA PÁGINA

Cada página es una clase con `__init__(self, page)` y `build() -> ft.Control`.
El `build()` retorna un `Container(expand=True)` con esta estructura:

```
Column [
  _build_header()      # Ícono grande + título + subtítulo, bgcolor=SURFACE
  Divider
  Container(expand, scroll=AUTO) [
    _build_<seccion>()     # Card con contenido específico (ej: formulario)
    _build_cards_grid()    # GridView de action cards
    _build_log_panel()     # Panel de registro de actividad (si aplica)
  ]
]
```

---

## SISTEMA DE CARDS DE ACCIÓN

Las acciones se declaran como lista de dicts al inicio del archivo de página:

```python
ACTIONS = [
    {
        "key":   "identificador",
        "label": "Nombre de la acción",
        "desc":  "Descripción corta (máx. 2 líneas)",
        "icon":  ft.Icons.XXXX,
        "fn":    lambda folder, log: logica.funcion(folder, log),
    },
]
```

Cada dict genera una tarjeta (`ft.Container` con `get_card_style()`):
- Esquina superior izquierda: ícono con fondo opacidad 10% PRIMARY
- Esquina superior derecha: `IconButton` PLAY_ARROW que ejecuta la acción
- Título de la acción (`W_600`)
- Descripción (`max_lines=2`, `overflow=ELLIPSIS`)
- `on_click` en el `Container` completo (`ink=True` para efecto ripple)

Las cards se disponen en:
```python
ft.GridView(runs_count=3, max_extent=340, child_aspect_ratio=1.6)
```

La ejecución corre en `threading.Thread(daemon=True)` para no bloquear la UI.
El log se escribe con `self._log(msg)` que hace append de un `ft.Text`
a un `Column` con `scroll=ScrollMode.AUTO`.

---

## HOME PAGE (pages/home_page.py)

Dashboard de resumen. Estructura:
1. Banner de bienvenida: título + subtítulo + botón CTA que navega a la primera
   sección funcional usando `page.data["on_navigate"]`
2. Row de stat cards (4 tarjetas): ícono coloreado + valor numérico grande + label
3. Sección "Actividad reciente": lista de ítems o estado vacío con
   ícono `INBOX_OUTLINED` + texto explicativo

---

## MODELOS (models/models.py)

Dataclasses simples de dominio, sin dependencias de UI:

```python
from dataclasses import dataclass

@dataclass
class EntidadA:
    campo1: str
    campo2: str
    campo3: str
```

---

## COMPILAR PARA WINDOWS

> **Importante:** `main.py` debe llamar `run_app()` **sin** el guard
> `if __name__ == "__main__":` porque Flet importa el módulo en lugar
> de ejecutarlo directamente.

```bash
cd proyecto
flet build windows src --project APPNAME --product "APPNAME" --org com.empresa
```

El `.exe` queda en `src/build/windows/APPNAME.exe`.

**Para cambiar el ícono del `.exe` a nivel sistema operativo (Windows):**
```powershell
.\rcedit-x64.exe "src\build\windows\APPNAME.exe" --set-icon "src\assets\favicon.ico"
```
`rcedit` disponible en: `github.com/electron/rcedit/releases`

---

## PATRONES CLAVE A RESPETAR

1. **Para agregar una página nueva:** solo editar `menu_config.py` + crear el archivo
   de página. El router la detecta automáticamente.

2. **Todos los colores vienen de `AppTheme`.** Nunca hardcodear colores en los widgets.

3. **La lógica de negocio vive en `logic/`**, nunca dentro de las páginas.
   Las páginas solo llaman funciones de `logic/` y muestran resultados en el log.

4. **`page.data` es el bus de comunicación** entre `gui.py` y las páginas:
   `{"on_navigate": callable, "on_theme_change": callable}`

5. **`page.session`** se usa para persistir estado liviano entre navegaciones
   (ej: carpeta de trabajo seleccionada por el usuario).

6. **Las páginas del sistema** (`settings`, `profile`, `help`) se registran en
   `SYSTEM_ITEMS` para que el router las conozca, pero no aparecen en el sidebar.
   Solo son accesibles desde el footer del sidebar (menú `···`).
