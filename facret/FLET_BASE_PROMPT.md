# 🏗️ Flet Modular — Blueprint Arquitectónico Reutilizable

Plantilla base para construir aplicaciones de escritorio Flet con **arquitectura modular, escalable y profesional**.

Esta es una **arquitectura de referencia** — copiar, adaptar y reutilizar en nuevos proyectos sin modificar los patrones base.

---

## 🎯 Principios Clave

```
┌─────────────────────────────────────────┐
│         FRONTEND (UI pura)              │
│   components/ + pages/ + gui.py         │
├─────────────────────────────────────────┤
│         BACKEND (Lógica sin UI)         │
│   logic/ (sin dependencias de Flet)     │
├─────────────────────────────────────────┤
│    DATA (Estructuras de datos)          │
│   models/ + config/                     │
└─────────────────────────────────────────┘
```

**Objetivo:** Separación clara permite testabilidad, reutilización y crecimiento escalable.

---

## 📦 Stack Recomendado

- **Python:** 3.11+
- **UI Framework:** Flet 0.28.x (desktop)
- **Package Manager:** Poetry
- **Build:** `flet build windows src`

---

## 📁 Estructura de Carpetas (Copy/Paste)

```
src/
├── main.py                      # Entry point — NO usar if __name__ == "__main__"
├── gui.py                       # Orquestador + router dinámico
│
├── config/                      # ⚙️ CONFIGURACIÓN GLOBAL
│   ├── menu_config.py           # Menú navegación (fuente única de verdad)
│   ├── theme.py                 # Tema Material Design 3
│   └── app_config.json          # Configuración persistente (opcional)
│
├── components/                  # 🎨 UI REUTILIZABLE (agnóstica a la lógica)
│   ├── header/
│   │   ├── responsive_header.py
│   │   ├── app_brand.py
│   │   ├── search_component.py
│   │   ├── tools_component.py
│   │   └── user_session.py
│   ├── sidebar.py               # Navegación
│   ├── toolbar.py               # Breadcrumb
│   ├── settings_panel.py        # Configuración
│   └── helpers.py               # Componentes genéricos reutilizables
│
├── pages/                       # 📄 VISTAS (específicas de cada sección)
│   ├── home_page.py             # Dashboard inicial
│   └── <seccion>_page.py        # Una por cada menú
│
├── logic/                       # 🧠 LÓGICA DE NEGOCIO (SIN FLET)
│   ├── logger.py                # Logging centralizado
│   ├── config_manager.py        # R/W config persistente
│   └── <dominio>_logic.py       # Tu lógica de negocio aquí
│
├── models/                      # 📊 ESTRUCTURAS DE DATOS (Dataclasses)
│   └── models.py
│
└── assets/                      # 🖼️ RECURSOS
    ├── icon.png
    └── favicon.ico
```

---

## 🔄 Flujo de Arquitectura

### Capa 1: Entry Point (`main.py`)
```python
import flet as ft
from gui import run_app

def main():
    ft.app(target=run_app)

if __name__ == "__main__":
    main()
```

### Capa 2: Orquestación (`gui.py`)
- ✅ Router dinámico (cargar páginas via `importlib`)
- ✅ Layout principal (header, sidebar, content area)
- ✅ Callbacks compartidos (`page.data`)
- ✅ Actualización de temas y navegación

**Responsabilidades:**
- NO contiene lógica de negocio
- NO contiene componentes específicos
- SÍ orquesta la experiencia de usuario

### Capa 3: UI (`components/` + `pages/`)

#### **components/** — Reutilizable, agnóstica
```python
# ✅ Puede usarse en múltiples páginas
def build_stat_card(label: str, value: str) -> ft.Container:
    return ft.Container(...)

def build_action_card(icon, label, description) -> ft.Container:
    return ft.Container(...)
```

#### **pages/** — Específica de cada sección
```python
class HomePage:
    def __init__(self, page):
        self.page = page
    
    def build(self) -> ft.Control:
        # Usa components/ + logic/
        return ft.Container(...)
```

### Capa 4: Lógica (`logic/`)
```python
# ❌ NUNCA importa Flet
# ✅ Puro, testeable, reutilizable

def procesar_datos(input_data):
    """Lógica de negocio pura"""
    resultado = ...
    return resultado
```

### Capa 5: Datos (`models/` + `config/`)
```python
@dataclass
class Entidad:
    campo1: str
    campo2: int
    # Sin métodos complejos
```

---

## 🎨 Sistema de Temas (config/theme.py)

**Semántica Material Design 3:**

```python
class AppTheme:
    # Colores semánticos (NUNCA hardcodear en componentes)
    PRIMARY = "#0b5f78"
    SECONDARY = "#0097a7"
    SUCCESS = "#1a7a4a"
    ERROR = "#ba1a1a"
    SURFACE = "#ffffff"
    ON_SURFACE = "#1a2b2e"
    
    @staticmethod
    def get_theme() -> ft.Theme:
        return ft.Theme(color_scheme_seed=AppTheme.PRIMARY)
```

**Uso en componentes:**
```python
from config.theme import AppTheme as T

ft.Text("Hola", color=T.PRIMARY)  # ✅ Centralizado
# ❌ NO: ft.Text("Hola", color="#0b5f78")  # Hardcoding
```

---

## 🧭 Router Dinámico (gui.py)

```python
import importlib

def _load_page(page_class_path: str, flet_page):
    """Carga cualquier página sin hardcode"""
    module_path, class_name = page_class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls(flet_page).build()

def on_navigate(key: str):
    """Callback de navegación"""
    item = next((i for i in MENU_ITEMS if i.key == key), None)
    if item and item.page_class:
        page.content_area.content = _load_page(item.page_class, page)
        page.content_area.update()
```

**Ventaja:** Agregar página nueva = solo 2 líneas en `menu_config.py`

---

## 📋 Menú Dinámico (config/menu_config.py)

**Fuente única de verdad:**

```python
from dataclasses import dataclass, field

@dataclass
class MenuItem:
    key: str
    label: str
    icon: str
    page_class: str | None = None
    children: list = field(default_factory=list)

MENU_ITEMS = [
    MenuItem(
        key="home",
        label="Inicio",
        icon=ft.Icons.HOME_OUTLINED,
        page_class="pages.home_page.HomePage"
    ),
    MenuItem(
        key="seccion1",
        label="Sección 1",
        icon=ft.Icons.SETTINGS_OUTLINED,
        page_class="pages.seccion1_page.Seccion1Page"
    ),
    # Agregar más ítems aquí
]
```

**Para agregar página nueva:**
1. Crear `pages/nueva_page.py`
2. Agregar `MenuItem(...)` a `MENU_ITEMS`
3. ¡Listo! Router lo detecta automáticamente

---

## 🎯 Estructura de una Página

```python
import flet as ft
from config.theme import AppTheme as T
from logic.logger import get_logger

logger = get_logger(__name__)

class MiPagina:
    def __init__(self, page: ft.Page):
        self.page = page
        logger.info("MiPagina inicializada")
    
    def build(self) -> ft.Control:
        """Retorna el widget raíz de la página"""
        return ft.Container(
            content=ft.Column([
                self._build_header(),
                self._build_content(),
            ]),
            expand=True,
        )
    
    def _build_header(self) -> ft.Control:
        """Encabezado de la página"""
        return ft.Text("Título", size=24, weight=ft.FontWeight.W_600)
    
    def _build_content(self) -> ft.Control:
        """Contenido principal"""
        return ft.Container(
            content=ft.Column([
                # Tu contenido aquí
            ]),
            expand=True,
        )
```

---

## 📡 Comunicación entre Componentes

**Via `page.data` (bus de eventos):**

```python
# En gui.py
page.data = {
    "on_navigate": on_navigate,
    "on_theme_change": rebuild,
    "on_config_change": update_config,
}

# En una página
def _on_button_click(self, e):
    self.page.data["on_navigate"]("nueva_seccion")
    self.page.data["on_theme_change"]()
```

**Ventaja:** Desacoplamiento — las páginas no se importan entre sí.

---

## 🧪 Logging Centralizado (logic/logger.py)

```python
import logging
from logic.logger import get_logger

logger = get_logger(__name__)

# En cualquier archivo
logger.info("Operación completada")
logger.error(f"Error: {excepcion}")
logger.debug("Información de debug")
```

**Características recomendadas:**
- Logs a archivo + consola
- Rotación automática
- 5 niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Timestamps y nombre de módulo

---

## 💾 Configuración Persistente (logic/config_manager.py)

```python
import json
from pathlib import Path

CONFIG_FILE = Path("config/app_config.json")

def load_config() -> dict:
    """Cargar configuración desde JSON"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def save_config(config: dict):
    """Guardar configuración a JSON"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
```

---

## 🧩 Helpers Reutilizables (components/helpers.py)

```python
import flet as ft
from config.theme import AppTheme as T

def build_stat_chip(label: str, value: str) -> ft.Container:
    """Chip genérico: etiqueta + valor"""
    return ft.Container(
        content=ft.Column([
            ft.Text(label, size=9, color=T.ON_SURFACE_VARIANT),
            ft.Text(value, size=11, weight=ft.FontWeight.W_600),
        ]),
        bgcolor=T.SURFACE,
        border=ft.border.all(1, T.OUTLINE),
        border_radius=6,
        padding=10,
    )

def build_action_card(icon: str, label: str, description: str) -> ft.Container:
    """Tarjeta de acción: ícono + label + descripción"""
    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(icon, color=T.PRIMARY), ft.Text(label)]),
            ft.Text(description, size=11, color=T.ON_SURFACE_VARIANT),
        ]),
        bgcolor=T.SURFACE,
        border_radius=8,
        padding=16,
    )

# Agregar más helpers aquí...
```

---

## 🚀 Flujo de Desarrollo

### 1. Setup Inicial
```bash
mkdir mi_app && cd mi_app
poetry init
poetry add flet==0.28.3
mkdir -p src/{config,components,pages,logic,models,assets}
touch src/main.py src/gui.py
```

### 2. Crear Estructura Base
- Copiar archivos base: `main.py`, `gui.py`, `config/theme.py`, `config/menu_config.py`
- Crear `pages/home_page.py`
- Crear `logic/logger.py` y `logic/config_manager.py`

### 3. Agregar Páginas Nuevas
```python
# Paso 1: Crear archivo
# src/pages/nueva_page.py
class NuevaPage:
    def __init__(self, page): ...
    def build(self): ...

# Paso 2: Registrar en menu_config.py
MenuItem(key="nueva", label="Nueva", page_class="pages.nueva_page.NuevaPage")

# Paso 3: ¡Listo! Router lo detecta automáticamente
```

### 4. Agregar Lógica de Negocio
```python
# src/logic/mi_logica.py
# ❌ NUNCA importar Flet
# ✅ Solo librerías estándar + dependencias específicas del dominio

def procesar_datos(input_data):
    resultado = ...
    return resultado
```

---

## ✅ Checklist: Repo Listo para Usar

- [ ] `src/main.py` — Entry point (sin `if __name__`)
- [ ] `src/gui.py` — Router + layout principal
- [ ] `config/theme.py` — AppTheme centralizado
- [ ] `config/menu_config.py` — Menú en fuente única
- [ ] `pages/home_page.py` — Primera página
- [ ] `logic/logger.py` — Logging centralizado
- [ ] `logic/config_manager.py` — Config persistente
- [ ] `components/helpers.py` — Componentes reutilizables
- [ ] `models/models.py` — Dataclasses de dominio
- [ ] `pyproject.toml` — Dependencias Poetry
- [ ] `.gitignore` — Excluir venv, logs, __pycache__
- [ ] `README.md` — Documentación base

---

## 🎓 Patrones Clave a Respetar

### 1. Separación de Capas
```
GUI (components + pages + gui.py)
  ↓ (llama a)
LOGIC (sin Flet, puro)
  ↓ (usa)
MODELS (dataclasses simples)
```

### 2. Colores Centralizados
```python
# ✅ SIEMPRE
ft.Text("Hola", color=T.PRIMARY)

# ❌ NUNCA
ft.Text("Hola", color="#0b5f78")
```

### 3. Rutas de Menú en Fuente Única
```python
# ✅ menu_config.py es la autoridad
MENU_ITEMS = [...]

# ❌ NUNCA hardcodear rutas en pages
```

### 4. Lógica en logic/, No en Pages
```python
# ✅ logic/procesador.py
def procesar(data):
    return resultado

# En página
resultado = procesar(datos)

# ❌ NUNCA
class MiPagina:
    def _procesar(self, data):  # ← NO
        return resultado
```

### 5. Eventos vía page.data
```python
# ✅ Desacoplado
self.page.data["on_navigate"]("seccion2")

# ❌ Acoplado
from pages.seccion2_page import Seccion2Page
page.content = Seccion2Page(page).build()
```

### 6. Tema Modular
```python
# ✅ SIEMPRE importar tema
from config.theme import AppTheme as T

# ✅ Usar helpers genéricos
from components.helpers import build_stat_chip

# ❌ NUNCA crear componentes ad-hoc en páginas
```

---

## 🔧 Compilación para Windows

```bash
flet build windows src \
  --project APPNAME \
  --product "APPNAME" \
  --org com.empresa
```

El `.exe` queda en `src/build/windows/APPNAME.exe`.

---

## 📚 Referencia Rápida de Archivos Clave

| Archivo | Responsabilidad |
|---------|-----------------|
| `main.py` | Entry point |
| `gui.py` | Orquestación + router |
| `config/theme.py` | Tema centralizado |
| `config/menu_config.py` | Menú (fuente única) |
| `components/helpers.py` | Componentes genéricos |
| `pages/*.py` | Vistas específicas |
| `logic/*.py` | Lógica sin Flet |
| `models/models.py` | Dataclasses |

---

## 🚀 Próximas Mejoras (Roadmap)

- [ ] Tests unitarios para `logic/`
- [ ] Type hints completos
- [ ] CI/CD (GitHub Actions)
- [ ] Documentación generada (Sphinx)

---

**Esta es una arquitectura de referencia reutilizable. Cópiala, adáptala y escala tus proyectos Flet profesionalmente.**

Última actualización: 26 de Julio 2026
