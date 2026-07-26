# 🔄 Actualización: Refresco Automático del Sidebar

**Fecha:** 26 de Julio 2026  
**Cambio:** Sidebar se actualiza automáticamente cuando cambia la carpeta de trabajo

---

## 🎯 El Problema

**Antes:**
1. User abre app → sidebar muestra estadísticas correctas
2. User cambia carpeta en "Download FACS" → `1.26 MB, 90 archivos`
3. User hace clic en "Guardar"
4. ❌ Sidebar **NO** se actualiza → sigue mostrando datos antiguos

**Ahora:**
1. User abre app → sidebar muestra estadísticas correctas
2. User cambia carpeta en "Download FACS" → `1.26 MB, 90 archivos`
3. User hace clic en "Guardar"
4. ✅ Sidebar **SE ACTUALIZA AUTOMÁTICAMENTE** → muestra nuevas estadísticas

---

## ⚙️ Cómo Funciona

### Flujo de Actualización

```
facs_downloader_page._save_config()
    ↓
save_config(data)  # Guardar en JSON
    ↓
page.data["on_config_change"]()  # ← NUEVA LÍNEA
    ↓
gui.rebuild()  # Reconstruye TODA la UI
    ↓
Sidebar se reconstruye con nueva carpeta_trabajo
    ↓
get_folder_stats() calcula nuevas estadísticas
    ↓
UI muestra nuevos números
```

### Eventos que Activan Refresco

| Evento | Página | Acción |
|--------|--------|--------|
| **Guardar config** | Download FACS | `_save_config()` |
| **Seleccionar carpeta** | Gestión FACS | `_on_picker_result()` |
| **Escribir ruta manualmente** | Gestión FACS | `_on_folder_change()` |

---

## 📝 Cambios de Código

### 1. gui.py — Agregar callback
```python
page.data = {
    "on_theme_change":  rebuild,
    "on_config_change": rebuild,  # ← NUEVO
    "on_navigate":      on_navigate,
}
```

### 2. facs_downloader_page.py — Notificar al guardar
```python
def _save_config(self, e):
    # ... guardar datos ...
    save_config(data)
    
    # ← NUEVO: Notificar cambio
    if "on_config_change" in self.page.data:
        self.page.data["on_config_change"]()
```

### 3. facs_manager_page.py — Notificar al cambiar carpeta
```python
def _on_picker_result(self, e):
    # ... cambiar carpeta ...
    set_value("carpeta_trabajo", e.path)
    
    # ← NUEVO: Notificar cambio
    if "on_config_change" in self.page.data:
        self.page.data["on_config_change"]()

def _on_folder_change(self, e):
    # ... cambiar carpeta ...
    set_value("carpeta_trabajo", e.control.value)
    
    # ← NUEVO: Notificar cambio
    if "on_config_change" in self.page.data:
        self.page.data["on_config_change"]()
```

---

## 🧪 Testing

### Escenario 1: Download FACS
1. Abre Download FACS
2. Mira sidebar → muestra estadísticas actuales
3. **Cambia el texto** en "Carpeta de descarga local"
4. **Haz clic en "Guardar Configuración"**
5. ✅ Sidebar se actualiza con nuevas estadísticas

### Escenario 2: Gestión FACS
1. Abre Gestión FACS
2. Mira sidebar → muestra estadísticas actuales
3. **Haz clic en "Explorar"** (FilePicker)
4. **Selecciona otra carpeta**
5. ✅ Sidebar se actualiza con nuevas estadísticas

### Escenario 3: Escribir ruta manualmente
1. Abre Gestión FACS
2. **Escribe una ruta diferente** en "Carpeta de trabajo"
3. **Presiona Enter o cambia de campo**
4. ✅ Sidebar se actualiza automáticamente

---

## ⚡ Ventajas

- ✅ **Refresco automático** — User no necesita navegar
- ✅ **Sincronización real** — Sidebar siempre muestra datos actuales
- ✅ **Dos puntos de entrada** — Download FACS y Gestión FACS
- ✅ **Experiencia fluida** — Cambio instantáneo

---

## 🎯 Próximas Mejoras (Opcional)

1. **Actualización en background**
   - Para carpetas muy grandes, usar threading
   - Mostrar indicador de carga mientras calcula

2. **Sin reconstruir todo**
   - Actualizar solo el sidebar sin reconstruir header/toolbar
   - Más eficiente pero más complejo

3. **Debounce**
   - Al escribir ruta manualmente, esperar 500ms antes de recalcular
   - Evita cálculos innecesarios mientras el user está escribiendo

---

## ✅ Testing Checklist

- [ ] 1. Abre app → sidebar muestra datos
- [ ] 2. Download FACS: cambia carpeta y guarda
  - [ ] Sidebar se actualiza con nuevas estadísticas
- [ ] 3. Gestión FACS: selecciona carpeta diferente
  - [ ] Sidebar se actualiza inmediatamente
- [ ] 4. Gestión FACS: escribe ruta manualmente
  - [ ] Sidebar se actualiza al cambiar de campo
- [ ] 5. Verifica que números son correctos
  - [ ] Archivos contados correctamente
  - [ ] Carpetas contadas correctamente
  - [ ] Tamaño en MB/GB correcto

---

**Status:** ✅ Listo para testing  
**Complejidad:** Baja — cambios simples y localizados  
**Riesgo:** Muy bajo — no afecta flujos existentes
