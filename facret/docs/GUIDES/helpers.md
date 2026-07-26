# 📦 Guía: Helpers Visuales Reutilizables

Componentes UI comunes centralizados en `components/helpers.py` para reducir duplicación.

---

## 🎯 Propósito

En lugar de repetir código para chips, campos, tarjetas, etc., usar helpers genéricos reutilizables en cualquier página.

---

## 📚 Helpers Disponibles

### 1. `build_stat_chip(label, value, icon=None)`

**Chip genérico para mostrar etiqueta + valor.**

```python
from components.helpers import build_stat_chip

# Básico
chip = build_stat_chip("Estado", "ACTIVO")

# Con ícono
chip = build_stat_chip(
    label="Tamaño",
    value="234.56 MB",
    icon=ft.Icons.STORAGE_OUTLINED
)
```

**Usado en:** `pages/contracts_page.py` (datos del servicio)

---

### 2. `build_status_text(text, status, size=13)`

**Texto con color mapeado según estado.**

```python
from components.helpers import build_status_text

# Resultado: texto en rojo si "CANCELED", verde si "ACTIVE"
text = build_status_text("Mi estado", "ACTIVE")

# Con tamaño personalizado
text = build_status_text("Operativo", "UP", size=14)
```

**Estados soportados:**
- `"ACTIVE"` → verde (SUCCESS)
- `"UP"` → verde (SUCCESS)
- `"CANCELED"` → rojo (ERROR)
- `"DOWN"` → rojo (ERROR)
- Otros → gris (ON_SURFACE_VARIANT)

---

### 3. `build_info_row(label, value, icon=None)`

**Fila de información: ícono + etiqueta + valor.**

```python
from components.helpers import build_info_row

row = build_info_row(
    label="Archivos:",
    value="42",
    icon=ft.Icons.INSERT_DRIVE_FILE_OUTLINED
)

# Resultado: 📄 Archivos:    42
```

---

### 4. `build_divider_section(title)`

**Sección con divider: título + línea divisoria.**

```python
from components.helpers import build_divider_section

section = build_divider_section("Información del Servicio")

# Resultado:
# Información del Servicio
# ────────────────────────
```

---

### 5. `build_action_card(icon, label, description, on_click=None, color=None)`

**Tarjeta de acción: ícono + label + descripción.**

```python
from components.helpers import build_action_card

card = build_action_card(
    icon=ft.Icons.DOWNLOAD_ROUNDED,
    label="Descargar Facturas",
    description="Descarga facturas desde Outlook",
    on_click=my_callback,
    color=T.PRIMARY
)
```

---

### 6. `build_labeled_field(label, field, icon=None, helper_text="")`

**Campo de entrada con etiqueta e ícono opcional.**

```python
from components.helpers import build_labeled_field

textfield = ft.TextField(value="D:\\Facturas")
field = build_labeled_field(
    label="Carpeta de descarga",
    field=textfield,
    icon=ft.Icons.FOLDER_OUTLINED,
    helper_text="Ruta local donde guardar archivos"
)
```

---

## 🔄 Antes vs Después

### Antes (duplicación)

```python
# contracts_page.py
def _ref_chip(label: str, value: str) -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Text(label, size=9, color=T.ON_SURFACE_VARIANT),
            ft.Text(value, size=11, weight=ft.FontWeight.W_600),
        ], spacing=1, tight=True),
        bgcolor=T.SURFACE,
        border=ft.border.all(1, T.OUTLINE),
        border_radius=6,
        padding=ft.padding.symmetric(horizontal=10, vertical=6),
    )

# Uso
chip1 = _ref_chip("Agencia", "Central")
chip2 = _ref_chip("Bandwidth", "10 MBPS")
```

### Después (reutilizable)

```python
# components/helpers.py
def build_stat_chip(label: str, value: str, icon: str | None = None) -> ft.Container:
    return ft.Container(...)  # Mismo código, centralizado

# Uso en cualquier página
from components.helpers import build_stat_chip

chip1 = build_stat_chip("Agencia", "Central")
chip2 = build_stat_chip("Bandwidth", "10 MBPS")
chip3 = build_stat_chip("Tamaño", "234 MB", icon=ft.Icons.STORAGE_OUTLINED)
```

**Ventajas:**
- ✅ Menos duplicación (~50 líneas ahorradas)
- ✅ Cambios centralizados
- ✅ Consistencia visual garantizada

---

## 📋 Checklist: Cómo Usar en Nuevas Páginas

Antes de hacer helpers propios, pregúntate:

- [ ] ¿Necesito un chip/badge? → Usa `build_stat_chip()`
- [ ] ¿Necesito mostrar estado con color? → Usa `build_status_text()`
- [ ] ¿Necesito una fila de info? → Usa `build_info_row()`
- [ ] ¿Necesito un divider con título? → Usa `build_divider_section()`
- [ ] ¿Necesito una tarjeta de acción? → Usa `build_action_card()`
- [ ] ¿Necesito un campo con etiqueta? → Usa `build_labeled_field()`
- [ ] ¿No existe el helper que necesito? → Agrégalo a `components/helpers.py`

---

## 🔧 Agregar Nuevo Helper

Si necesitas un helper que no existe:

1. **Crea la función en `components/helpers.py`:**
   ```python
   def build_mi_componente(...) -> ft.Control:
       """Descripción breve."""
       return ft.Container(...)
   ```

2. **Documen en docstring:**
   ```python
   """Mi componente hace esto.
   
   Args:
       param1: descripción
   
   Returns:
       Control: widget resultado
   """
   ```

3. **Usa en tu página:**
   ```python
   from components.helpers import build_mi_componente
   chip = build_mi_componente(...)
   ```

4. **Agregalo a esta guía**

---

## 📚 Referencia Rápida

```python
from components.helpers import (
    build_stat_chip,
    build_status_text,
    build_info_row,
    build_divider_section,
    build_action_card,
    build_labeled_field,
)

chip = build_stat_chip("Label", "Value")
text = build_status_text("Estado", "ACTIVE")
row = build_info_row("Archivos", "42", icon=ft.Icons.INSERT_DRIVE_FILE_OUTLINED)
section = build_divider_section("Mi Sección")
card = build_action_card(ft.Icons.DOWNLOAD_ROUNDED, "Descargar", "Desc")
field = build_labeled_field("Carpeta", textfield, icon=ft.Icons.FOLDER_OUTLINED)
```

---

**Última actualización:** 26 de Julio 2026
