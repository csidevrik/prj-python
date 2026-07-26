# 🏛️ Arquitectura de FACRET

## Visión General

FACRET es una aplicación de escritorio modular para automatizar la revisión y procesamiento de facturas XML. Construida con **separación clara de capas** y **bajo acoplamiento** para facilitar testing y mantenimiento.

```
┌────────────────────────────────────────────────────┐
│                   gui.py                           │
│  (Orquestador principal + Router dinámico)         │
├────────────────────────────────────────────────────┤
│  components/    │    pages/           │  config/   │
│  (UI pura)      │    (Vistas UI)       │  (Global)  │
└─────────┬───────┴────────┬────────────┴──────┬─────┘
          │                │                   │
          └────────────────┼───────────────────┘
                           │
                      logic/ (Lógica pura, sin Flet)
                      models/ (Dataclasses)
```

---

## 📊 Capas Arquitectónicas

### Nivel 1: Orquestación (`gui.py`)
**Responsabilidad:** Router dinámico + Layout principal

```python
# Import dinámico de páginas
def _load_page(page_class_path, flet_page):
    module_path, class_name = page_class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)(flet_page).build()

# Callback centralizado
def on_navigate(key):
    content_area.content = _load_page(item.page_class, page)
    content_area.update()
```

**Ventaja:** Agregar página = 3 líneas en `menu_config.py`

---

### Nivel 2: UI (`components/`, `pages/`)

#### **components/** — Componentes Reutilizables
```
components/
├── header/                    # 516 líneas
│   ├── responsive_header.py   # Orquesta 4 sub-componentes
│   ├── app_brand.py
│   ├── search_component.py
│   ├── tools_component.py
│   └── user_session.py
├── sidebar.py                 # 345 líneas | Nav + almacenamiento
├── toolbar.py                 # 44 líneas | Hamburguesa + breadcrumb
├── settings_panel.py          # 351 líneas | Temas + sobre
└── helpers.py                 # Componentes genéricos reutilizables
```

**Principio:** Un componente = un concepto. Altamente reutilizable.

#### **pages/** — Vistas Dinámicas
```
pages/
├── home_page.py               # 259 líneas | Dashboard
├── facs_downloader_page.py    # 222 líneas | Download Outlook
├── facs_manager_page.py       # 353 líneas | Procesamiento XML
└── contracts_page.py          # 783 líneas | Tabla contratos
```

**Principio:** Cada página es independiente. Importa solo lo que necesita.

---

### Nivel 3: Lógica de Negocio (`logic/`)

**Principio:** Sin dependencias de Flet. Código puro y testeable.

```
logic/
├── config_manager.py          # R/W config JSON
├── folder_stats.py            # Cálculo de estadísticas
├── contracts_loader.py        # Carga datos + resuelve referencias
├── contracts_writer.py        # Actualiza servicios en JSON
├── facs_downloader.py         # Outlook COM API
├── facs_manager.py            # XML parsing, renombrado
└── logger.py                  # Logging centralizado (5 niveles)
```

**Ventaja:** Testeable sin UI. Reutilizable en CLI o API futura.

---

### Nivel 4: Datos (`models/`)

**Principio:** Dataclasses simples. Sin lógica de negocio.

```python
@dataclass
class Contrato:
    id: str
    nombre: str
    grupos: list[GrupoServicios]
    
    def servicios_flat(self) -> list:
        """Método único: retorna todos los servicios"""
        return [s for g in self.grupos for s in g.servicios]
```

---

### Nivel 5: Configuración (`config/`)

**Principio:** Centralizada. Accesible desde cualquier capa.

```
config/
├── theme.py                   # AppTheme global (Material Design 3)
├── menu_config.py             # Menú de navegación (fuente única)
└── facs_config.json          # Rutas, emails, carpetas
```

---

## 🔄 Flujos Clave

### Flujo 1: Agregar Página Nueva

```
1. Crear: pages/nueva_page.py
   class NuevaPage:
       def __init__(self, page): ...
       def build(self): ...

2. Registrar: menu_config.py
   MenuItem(key="nueva", label="Nueva", 
            page_class="pages.nueva_page.NuevaPage")

3. Router (gui.py) detecta automáticamente ✅
```

### Flujo 2: Cambio de Tema en Tiempo Real

```
User hace clic en tema
    ↓
settings_panel.py → AppTheme (actualiza colores)
    ↓
page.data["on_theme_change"]()
    ↓
gui.rebuild() (reconstruye TODA la UI)
    ↓
Todos los componentes usan AppTheme ✅
```

### Flujo 3: Sincronización de Carpeta

```
User en Download FACS cambia carpeta
    ↓
save_config({"carpeta_trabajo": path})
    ↓
page.data["on_config_change"]()
    ↓
sidebar.refresh_storage_section()
    ↓
logic.folder_stats.get_folder_stats() (cálculo)
    ↓
Sidebar actualizado SIN interrumpir navegación ✅
```

---

## 📈 Métricas de Salud

| Métrica | Valor | Evaluación |
|---------|-------|-----------|
| Separación de capas | ⭐⭐⭐⭐⭐ | Excelente |
| Bajo acoplamiento | ⭐⭐⭐⭐ | Muy bueno |
| Alta cohesión | ⭐⭐⭐⭐⭐ | Excelente |
| Extensibilidad | ⭐⭐⭐⭐⭐ | Excelente |
| Testabilidad | ⭐⭐⭐⭐ | Muy bueno |
| **Puntuación General** | **8.5/10** | ✅ Sólida |

---

## 🎯 Principios de Diseño

### 1. **Separación de Responsabilidades**
- `logic/` — pura, sin UI
- `pages/` — vistas específicas
- `components/` — UI genérica
- `config/` — configuración global

### 2. **Sin Acoplamiento Circular**
```
gui.py → pages/ → logic/ → models/
↑                              ↓
←─────← config/ ─────←────────↑
```

### 3. **Router Dinámico**
```python
# En lugar de if/else gigante:
if page_key == "home":
    return HomePage(page).build()
elif page_key == "contratos":
    return ContractsPage(page).build()
...

# Usamos importlib:
module = importlib.import_module(module_path)
return getattr(module, class_name)(page).build()
```

### 4. **Tema Centralizado**
```python
# En lugar de hardcoding en cada página:
ft.Text("Hola", color="#007a8c")

# Usamos AppTheme:
ft.Text("Hola", color=T.PRIMARY)
```

### 5. **Comunicación con Eventos**
```python
# En lugar de importar todo:
page.data["on_navigate"]("contratos")
page.data["on_theme_change"]()
page.data["on_config_change"]()
```

---

## 🔐 Decisiones Arquitectónicas

### ¿Por qué Flet?
- ✅ GUI multiplataforma desde Python
- ✅ Desarrollo rápido
- ✅ Material Design 3 built-in
- ✅ No requiere JavaScript

### ¿Por qué Poetry?
- ✅ Gestión de dependencias moderna
- ✅ Lock file determinista
- ✅ Fácil publicación a PyPI futura

### ¿Por qué dataclasses en models/?
- ✅ Sin ORM complejo (overkill)
- ✅ Fácil de serializar (JSON)
- ✅ Type hints claros

### ¿Por qué logic/ sin Flet?
- ✅ Testeable sin UI
- ✅ Reutilizable (CLI, API, etc.)
- ✅ Fácil de mantener

---

## 🚀 Próximas Mejoras Arquitectónicas

1. **Tests unitarios** — para logic/
2. **Extraer helpers comunes** — `components/helpers.py` (DONE)
3. **MQTT subscriber** — para monitoreo en tiempo real
4. **SQLite para eventos** — historial de cambios

---

**Última actualización:** 26 de Julio 2026
