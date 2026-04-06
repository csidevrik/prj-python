# 🚀 ARQUITECTURA RÁPIDA DE FACRET

## El Flujo Principal (Lo que realmente corre)

```
main execution
    ↓
drive_gui.py (orquestador)
    ├── config/drive_theme.py (estilos globales)
    ├── components/header/responsive_header.py (top bar)
    │   ├── AppBrandComponent (logo)
    │   ├── SearchComponent (búsqueda)
    │   ├── ToolsComponent (botones)
    │   └── UserSessionComponent (usuario)
    ├── components/drive_sidebar.py (menú izq)
    ├── components/drive_content.py (contenido)
    │   └── core/services/ + logic/
    └── components/sync_status.py (barra estado)
```

## Carpetas Principales

| Carpeta | Propósito | Ejemplos |
|---------|-----------|----------|
| **`components/`** | UI widgets reutilizables | Header, Sidebar, Content, etc |
| **`components/header/`** | Subcomponentes del encabezado | SearchComponent, ToolsComponent |
| **`config/`** | Configuración y temas | `drive_theme.py` (el único que importas) |
| **`core/`** | Lógica de negocio | services, models, utils |
| **`logic/`** | Procesamiento XML | `logic.py`, `xml_processor.py` |
| **`models/`** | Estructuras de datos | Registro, RegistroRet, etc |
| **`pages/`** | Vistas completas (legacy) | No se usan en drive_gui |

## Componentes Activos

### Header
```python
from components.header.responsive_header import ResponsiveDriveHeader
# Contiene: Logo, Búsqueda, Botones, Sesión Usuario
```

### Sidebar
```python
from components.drive_sidebar import DriveSidebarComponent
# Menú de navegación izquierdo
```

### Contenido
```python
from components.drive_content import DriveContentComponent
# Área principal con listado y acciones
```

### Estado
```python
from components.sync_status import SyncStatusComponent
# Barra inferior de sincronización/notificaciones
```

### Tema
```python
from config.drive_theme import DriveTheme
# Colores, tipografía, estilos globales
# Úsalo: DriveTheme.get_theme()
```

## ¿Dónde Debo Agregar...?

### Una nueva página/vista
→ Crea en `components/` un archivo nuevo  
→ Importalo en `drive_gui.py`

### Nuevos datos/modelos
→ Crea en `core/models/` o usa `models/models.py`

### Nueva funcionalidad de negocio
→ Crea un servicio en `core/services/`

### Procesamiento XML nuevo
→ Expande `logic/xml_processor.py`

### Configuración/Estilos globales
→ Modifica `config/drive_theme.py`

## Archivos a IGNORAR (Legacy)

❌ `gui.py` - Versión vieja  
❌ `gui2.py` - Experimento  
❌ `main.py` - Punto entrada antiguo  
❌ `main2.py` - Sin uso  
❌ `main_drive.py` - Envoltorio innecesario  
❌ `components/app_bar.py` - Solo para gui.py  
❌ `components/nav_rail.py` - Solo para gui.py  
❌ `components/file_explorer.py` - Solo para gui.py  
❌ `components/preview_panel.py` - Solo para gui.py  
❌ `components/drive_header.py` - Reemplazado por responsive_header  
❌ `components/content_router.py` - Solo para gui2.py  
❌ `config/theme.py` - Usa drive_theme.py  

---

**Resumen**: Trabajas con `drive_gui.py` y sus componentes. TODO lo demás es legacy.
