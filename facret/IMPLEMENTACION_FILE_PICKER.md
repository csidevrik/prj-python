# 📂 Implementación: File Picker en Download FACS

**Fecha:** 26 de Julio 2026  
**Status:** ✅ Completado — Listo para testing

---

## 🎯 Cambios Realizados

### **Qué se agregó:**

1. **File Picker en Download FACS**
   - Botón "Explorar" (🗂️) junto al campo "Carpeta de descarga local"
   - Abre diálogo nativo de selección de carpetas
   - Al seleccionar, rellena el campo automáticamente

2. **Dos formas de configurar carpeta:**
   - ✅ **Copiar/pegar texto** (ya existía)
   - ✅ **Explorar con botón** (NUEVO)

---

## 📝 Código Modificado

### 1. Agregar File Picker en `__init__`
```python
# ── File Picker para seleccionar carpeta de descarga ──────────────
self._picker = ft.FilePicker(on_result=self._on_picker_result)
page.overlay.append(self._picker)
```

### 2. Campo con botón Explorar
```python
def _build_field_with_picker(self, label, hint, icon, field):
    """Campo con botón Explorar para seleccionar carpeta."""
    return ft.Container(
        content=ft.Row([
            ft.Container(icon),
            ft.Column([
                ft.Text(label),
                ft.Row([
                    field,  # TextField
                    ft.IconButton(  # ← Botón Explorar
                        icon=ft.Icons.FOLDER_OPEN_OUTLINED,
                        on_click=self._on_browse_click,
                    ),
                ]),
            ]),
        ]),
    )
```

### 3. Callbacks para manejar File Picker
```python
def _on_browse_click(self, e):
    """Abre el dialogo de selección de carpeta."""
    self._picker.get_directory_path()

def _on_picker_result(self, e: ft.FilePickerResultEvent):
    """Maneja la selección de carpeta."""
    if e.path:
        self._tf_guardar.value = e.path  # Rellena el TextField
        self._tf_guardar.update()
```

---

## 🧪 Testing

### Paso 1: Ejecutar app
```bash
cd facret
poetry run python src/main.py
```

### Paso 2: Ir a "Download FACS"
Ver el formulario con la nueva estructura:

```
┌─────────────────────────────────────────┐
│ Carpeta de descarga local               │
│                                         │
│ [texto actual] [🗂️ Explorar]           │
└─────────────────────────────────────────┘
```

### Paso 3: Probar dos opciones

#### Opción A: Copiar/Pegar
1. Copiar ruta desde tu File Explorer
2. Pegar en el campo
3. ✅ Debe aceptar el texto

#### Opción B: Explorar (NUEVO)
1. Haz clic en botón **🗂️ Explorar**
2. Se abre diálogo de selección de carpetas
3. Selecciona una carpeta
4. ✅ Campo debe rellenarse automáticamente

### Paso 4: Guardar y verificar
1. Haz clic en **"Guardar configuración"**
2. Mira el sidebar
3. ✅ Debe mostrar estadísticas de la nueva carpeta

### Paso 5: Ir a "Gestión FACS"
1. Campo "Carpeta de trabajo" debe mostrar la misma ruta
2. ✅ Sidebar muestra datos actualizados

---

## ✅ Checklist de Testing

- [ ] 1. Botón "Explorar" aparece junto al campo
- [ ] 2. Clic en botón abre diálogo de carpetas
- [ ] 3. Seleccionar carpeta rellena el campo
- [ ] 4. Copiar/pegar texto aún funciona
- [ ] 5. Guardar config actualiza sidebar
- [ ] 6. Gestión FACS ve la misma carpeta
- [ ] 7. Estadísticas son correctas en sidebar

---

## 🎨 UI Changes

**Antes:**
```
Carpeta de descarga local
[D:\Facturas_ETAPA]
```

**Después:**
```
Carpeta de descarga local
[D:\Facturas_ETAPA] [🗂️]
```

El botón 🗂️ abre el File Picker nativo de Windows.

---

## ⚡ Ventajas

- ✅ **Dos formas de entrada** — texto + explorador gráfico
- ✅ **Experiencia mejorada** — no necesita recordar rutas
- ✅ **Coherencia** — mismo patrón que "Gestión FACS"
- ✅ **Texto aún funciona** — no se quita la opción de pegar

---

## 🎯 Flujo Completo

```
User abre "Download FACS"
    │
    ├─ Opción 1: Pega ruta de texto
    │  └─ Campo se rellena
    │
    └─ Opción 2: Haz clic en botón 🗂️
       └─ Se abre diálogo
       └─ Selecciona carpeta
       └─ Campo se rellena automáticamente
           │
           ▼
       Hace clic en "Guardar"
           │
           ▼
       Se guarda en config.json
           │
           ▼
       Se notifica a gui.py
           │
           ▼
       Sidebar se reconstruye
           │
           ▼
       Muestra estadísticas de la nueva carpeta
```

---

**Status:** ✅ Listo para testing  
**Complejidad:** Baja — solo UI  
**Riesgo:** Muy bajo — no afecta lógica existente
