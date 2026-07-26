# 📊 Implementación: Estadísticas de Carpeta en el Sidebar

**Fecha:** 26 de Julio 2026  
**Status:** ✅ Completado — Listo para testing

---

## 🎯 Cambios Realizados

### 1. **Librería de Estadísticas** (`src/logic/folder_stats.py`)
- ✅ Nueva función `get_folder_stats(folder_path)` 
- Calcula recursivamente:
  - Número de archivos
  - Número de carpetas
  - Tamaño total en bytes
  - Formato legible (MB/GB)
- Manejo robusto de errores (carpetas inexistentes, permisos)
- Devuelve `FolderStats` (NamedTuple) o `None`

### 2. **Modificaciones al Sidebar** (`src/components/sidebar.py`)
- ✅ Agregado parámetro `carpeta_trabajo` al constructor
- ✅ Modificado `_build_storage_section()` para:
  - Leer estadísticas reales de la carpeta
  - Mostrar:
    - 💾 **Tamaño total** (MB/GB)
    - 📄 **Cantidad de archivos**
    - 📁 **Cantidad de carpetas**
  - Manejo de caso sin carpeta configurada ("Sin datos")

### 3. **Conexión en gui.py** (`src/gui.py`)
- ✅ Importado `load_config` de `config_manager`
- ✅ Al reconstruir sidebar, se lee `carpeta_trabajo` del config
- ✅ Se pasa al constructor del sidebar automáticamente

---

## 📋 Plan de Testing

### **Paso 1: Test Unitario (5 minutos)**
```bash
cd facret
python test_folder_stats.py
```

**Esperado:**
```
✅ Estadísticas calculadas:
   • Archivos: XX
   • Carpetas: X
   • Tamaño: X.XX MB (o X.XX GB)
✅ Manejo correcto de error (retorna None)
✅ Todos los tests pasaron
```

---

### **Paso 2: Test en Aplicación (10 minutos)**

#### 2a. Ejecutar app
```bash
cd facret
poetry run python src/main.py
```

#### 2b. Ir a "Download FACS"
- Ver el campo "Carpeta de descarga local"
- Verificar que tiene una ruta configurada
- Si no, escribir una ruta de prueba: `C:\Temp\MisFacturas`

#### 2c. Hacer clic en "Guardar Configuración"
- Esperar mensaje "Configuracion guardada correctamente."

#### 2d. Revisar el Sidebar
- En la esquina inferior izquierda debe aparecer la sección **"Almacenamiento"**
- Debería mostrar:
  ```
  Almacenamiento
  💾 X.XX MB (o X.XX GB)
  📄 XXX archivos
  📁 XX carpetas
  ```

#### 2e. Navegar a "Gestión FACS"
- El campo "Carpeta de trabajo" debe mostrar la misma ruta
- El sidebar debe actualizar las estadísticas de esa carpeta

---

### **Paso 3: Test de Casos Especiales (5 minutos)**

#### 3a. Carpeta Vacía
- Crear carpeta de prueba: `C:\Temp\Prueba_Vacia`
- Configurar en Download FACS
- Guardar
- Debe mostrar:
  ```
  💾 0.00 MB
  📄 0 archivos
  📁 0 carpetas
  ```

#### 3b. Carpeta con Archivos Pequeños
- Crear carpeta: `C:\Temp\Prueba_Archivos`
- Agregar 5 archivos de texto pequeños
- Configurar en Download FACS
- Debe mostrar:
  ```
  💾 X.XX MB
  📄 5 archivos
  📁 X carpetas
  ```

#### 3c. Sin Carpeta Configurada
- En config `facs_config.json`, agregar `"carpeta_trabajo": ""`
- Ejecutar app
- Sidebar debe mostrar:
  ```
  Almacenamiento
  💾 Sin datos
  📄 0 archivos
  📁 0 carpetas
  ```

---

## ✅ Checklist Final

- [ ] 1. Script de test unitario ejecuta correctamente
- [ ] 2. App inicia sin errores
- [ ] 3. Sidebar carga sin crashes
- [ ] 4. Estadísticas se muestran en sidebar
- [ ] 5. Estadísticas actualizan al cambiar carpeta en Download FACS
- [ ] 6. Carpeta de trabajo en Gestión FACS coincide con Download FACS
- [ ] 7. Números de archivos/carpetas son correctos
- [ ] 8. Formato de tamaño es legible (MB/GB)

---

## 🚀 Próximas Mejoras (Opcional)

1. **Actualización en tiempo real**
   - Cada vez que se navega a Gestión FACS, recalcular estadísticas
   - Usar threading para no bloquear UI

2. **Indicador visual de progreso**
   - Mostrar barra de progreso mientras calcula (para carpetas grandes)

3. **Caché de estadísticas**
   - Guardar en session para evitar recalcular constantemente

4. **Detalles expandible**
   - Click en "Almacenamiento" para ver distribución por tipo de archivo

---

## 📞 Soporte

Si algo no funciona:
1. Verifica que `carpeta_trabajo` existe en `facs_config.json`
2. Verifica que la ruta es válida (no contiene caracteres especiales)
3. Revisa la consola de Python para errores
4. Ejecuta `test_folder_stats.py` para aislar el problema

---

**Status:** ✅ Listo para testing  
**Estimado:** 20 minutos de testing completo  
**Riesgo:** Muy bajo — cambios aislados, sin dependencias críticas
