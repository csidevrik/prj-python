# ✅ Solución: Refresco Solo del Sidebar

**Fecha:** 26 de Julio 2026  
**Problema Resuelto:** Sidebar se actualiza sin interrumpir navegación

---

## 🎯 El Problema

**Antes:**
```
User en "Download FACS"
    ↓
Cambia carpeta y guarda
    ↓
rebuild() reconstruye TODA la UI
    ↓
Se pierde la página actual
    ↓
Usuario llevado a "Página principal" ❌
```

**Ahora:**
```
User en "Download FACS"
    ↓
Cambia carpeta y guarda
    ↓
update_sidebar_only() actualiza SOLO sidebar
    ↓
Sidebar se actualiza con nuevas estadísticas ✅
    ↓
Usuario permanece en "Download FACS" ✅
```

---

## ⚙️ Cómo Funciona

### Cambio en gui.py

**Antes:**
```python
page.data = {
    "on_config_change": rebuild,  # Reconstruía TODO
}
```

**Ahora:**
```python
def update_sidebar_only():
    """Actualiza solo el sidebar cuando cambia la carpeta de trabajo."""
    config = load_config()
    new_carpeta = config.get("carpeta_trabajo", "")
    sidebar.carpeta_trabajo = new_carpeta
    # Reconstruir solo el almacenamiento del sidebar
    sidebar._build_storage_section()
    sidebar._container.update()

page.data = {
    "on_config_change": update_sidebar_only,  # Solo actualiza sidebar
}
```

### Qué pasa cuando el user guarda

1. `facs_downloader_page._save_config()` ejecuta
2. Guarda config en `facs_config.json`
3. Llama: `page.data["on_config_change"]()`
4. `update_sidebar_only()` ejecuta:
   - Lee `carpeta_trabajo` del config actualizado
   - Actualiza `sidebar.carpeta_trabajo`
   - Reconstruye **solo** `_build_storage_section()`
   - Llama `sidebar._container.update()`
5. ✅ Sidebar se actualiza
6. ✅ Resto de la UI permanece intacto

---

## 📊 Flujo Simplificado

```
User en "Download FACS"
    │
    ├─ Cambia carpeta: "D:\Nueva\Ruta"
    │
    ├─ Haz clic en "Guardar"
    │    │
    │    └─ save_config({...})  [JSON actualizado]
    │    │
    │    └─ on_config_change()  [SOLO sidebar]
    │         │
    │         ├─ load_config()  [Lee valor fresco]
    │         │
    │         ├─ sidebar._build_storage_section()  [Recalcula stats]
    │         │
    │         └─ sidebar._container.update()  [Refresca sidebar]
    │
    ▼
User permanece en "Download FACS" ✅
Sidebar muestra nuevas estadísticas ✅
```

---

## ✅ Ventajas

| Aspecto | Antes | Ahora |
|--------|-------|-------|
| **Refresco** | Toda la UI | Solo sidebar |
| **Navegación** | Se pierde | Se mantiene |
| **Performance** | Más lento | Más rápido |
| **Experiencia** | Interrupta | Fluida |

---

## 🧪 Testing

### Paso 1: Ejecutar app
```bash
cd facret
poetry run python src/main.py
```

### Paso 2: En "Download FACS"
1. Observa el titulo: **"Download FACS"** en el toolbar
2. Mira el sidebar: muestra estadísticas actuales

### Paso 3: Cambiar carpeta
1. Haz clic en botón **🗂️ Explorar**
2. Selecciona otra carpeta
3. Campo se rellena automáticamente

### Paso 4: Guardar (EL TEST CLAVE)
1. Haz clic en **"Guardar configuración"**
2. **Observa que:**
   - ✅ Titulo sigue siendo **"Download FACS"** (NO cambió)
   - ✅ Permaneces en la misma página
   - ✅ Sidebar se actualiza con nuevas estadísticas
   - ✅ NO te lleva a "Página principal"

### Paso 5: Verificar sidebar
```
Almacenamiento
💾 XXX.XX MB
📄 XXXX archivos
📁 XX carpetas
```
Debe mostrar nuevas estadísticas de la carpeta seleccionada.

---

## ✅ Checklist

- [ ] 1. App inicia sin errores
- [ ] 2. Sidebar muestra estadísticas correctas al iniciar
- [ ] 3. En "Download FACS": cambias carpeta y guardas
- [ ] 4. ✅ Permaneces en "Download FACS" (NO te lleva a otra página)
- [ ] 5. ✅ Sidebar se actualiza con nuevas estadísticas
- [ ] 6. ✅ Nuevos números son correctos
- [ ] 7. Ve a "Gestión FACS" y verifica que carpeta es la misma
- [ ] 8. Sidebar mantiene mismo valor

---

## 🔧 Implementación Técnica

### Método `update_sidebar_only()` en gui.py

```python
def update_sidebar_only():
    # 1. Leer config actualizada
    config = load_config()
    new_carpeta = config.get("carpeta_trabajo", "")
    
    # 2. Actualizar referencia en sidebar
    sidebar.carpeta_trabajo = new_carpeta
    
    # 3. Reconstruir solo la sección de almacenamiento
    #    (no reconstruye todo el sidebar)
    sidebar._build_storage_section()
    
    # 4. Actualizar el Container del sidebar
    sidebar._container.update()
```

### Ventaja Técnica

- `sidebar._container` es una referencia a todo el sidebar
- Cuando llamamos `_build_storage_section()`, recalcula el widget
- `.update()` solo refresca ese Container específico
- No afecta header, toolbar, ni content_area

---

## 🎯 Casos de Uso Manejados

| Acción | Resultado |
|--------|-----------|
| Cambiar carpeta en Download FACS | Sidebar se actualiza, user permanece |
| Cambiar carpeta en Gestión FACS | Sidebar se actualiza, user permanece |
| Escribir ruta manualmente | Sidebar se actualiza al cambiar de campo |
| Cambiar tema (on_theme_change) | Reconstruye TODA la UI (intencional) |

---

## 💡 Diferencia con Cambio de Tema

Cuando el user **cambia el tema**:
```python
"on_theme_change": rebuild  # Reconstruye TODO
```

Esto es INTENCIONAL porque el tema afecta toda la app (colores en todos los componentes).

Cuando el user **cambia la carpeta**:
```python
"on_config_change": update_sidebar_only  # Solo sidebar
```

Esto es EFICIENTE porque solo el sidebar necesita actualizarse.

---

**Status:** ✅ Listo para testing  
**Complejidad:** Baja — cambio quirúrgico en gui.py  
**Riesgo:** Muy bajo — comportamiento más localizado
