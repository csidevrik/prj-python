# 📝 Guía: Sistema de Logging

Trazabilidad completa de errores, advertencias e información para facilitar debugging.

---

## 🎯 Características

- ✅ Logs a archivo (`logs/facret.log`) + consola con colores
- ✅ Rotación automática (10 MB máximo)
- ✅ 5 niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL
- ✅ Timestamps y nombres de módulo
- ✅ DEBUG siempre a archivo; consola respeta nivel configurado

---

## 🚀 Uso Básico

### Importar logger en tu archivo

```python
from logic.logger import get_logger

logger = get_logger(__name__)
```

### Usar en tu código

```python
# INFO — eventos normales
logger.info("Carpeta cargada: D:\\Facturas")
logger.info(f"Se encontraron {count} archivos")

# WARNING — situaciones anómalas pero recuperables
logger.warning("Carpeta vacía, no hay archivos a procesar")

# ERROR — errores que detienen una operación
logger.error(f"No se pudo leer XML: {filepath}")
logger.error(f"Conexión a Outlook fallida: {ex}")

# DEBUG — información detallada para debugging
logger.debug(f"Iterando sobre {len(files)} archivos")
logger.debug(f"Estadísticas: {stats}")

# CRITICAL — errores graves en la aplicación
logger.critical("Fallo crítico: no se pudo inicializar UI")
```

---

## 📂 Archivos de Log

```
facret/
├── logs/
│   ├── facret.log           ← Log actual
│   ├── facret.log.1         ← Backup 1
│   ├── facret.log.2         ← Backup 2
│   └── ...
```

**Rotación:** Cuando `facret.log` alcanza 10 MB, se renombra a `.1` y se crea uno nuevo.

---

## 🎨 Niveles de Log

| Nivel | Color | Cuándo usar | Ejemplo |
|-------|-------|-------------|---------|
| **DEBUG** | Cyan | Información detallada | `"Procesando fila 42 de 100"` |
| **INFO** | Green | Eventos normales | `"Carpeta cargada exitosamente"` |
| **WARNING** | Yellow | Situaciones anómalas | `"Archivo no legible, saltando"` |
| **ERROR** | Red | Errores recuperables | `"Fallo al conectar: {ex}"` |
| **CRITICAL** | Magenta | Errores graves | `"App no puede inicializar"` |

---

## 💡 Ejemplos Prácticos

### En logic/folder_stats.py

```python
from logic.logger import get_logger

logger = get_logger(__name__)

def get_folder_stats(folder_path):
    logger.debug(f"Analizando carpeta: {folder_path}")
    
    try:
        path = Path(folder_path)
        if not path.exists():
            logger.warning(f"Carpeta no existe: {folder_path}")
            return None
        
        num_files = len(list(path.rglob("*")))
        logger.info(f"Encontrados {num_files} items")
        return FolderStats(...)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return None
```

### En pages/

```python
from logic.logger import get_logger

logger = get_logger(__name__)

class MiPagina:
    def _on_button_click(self, e):
        try:
            logger.debug("Usuario hizo clic en botón")
            # ... lógica ...
            logger.info("Operación exitosa")
        except Exception as ex:
            logger.error(f"Error: {ex}")
```

---

## 🔍 Leer Logs

### Opción 1: Desde archivo

```bash
# Ver últimas 50 líneas
tail -50 facret/logs/facret.log

# Ver todos los errores
grep ERROR facret/logs/facret.log

# Ver todos los eventos
cat facret/logs/facret.log
```

### Opción 2: En consola (mientras corre la app)

```
INFO | facret | Carpeta cargada: D:\Facturas
DEBUG | facret.folder_stats | Analizando carpeta...
INFO | facret.folder_stats | Encontrados 42 items
WARNING | facret.contracts_loader | Carpeta vacía
ERROR | facret | Fallo al conectar Outlook: [Exception]
```

---

## ⚠️ Buenas Prácticas

### ✅ Haz esto

```python
# Logs con información útil
logger.info(f"Descargados {count} archivos de {folder}")
logger.error(f"Fallo al guardar: {ex.__class__.__name__}: {ex}")
logger.debug(f"Estadísticas: {stats}")
```

### ❌ No hagas esto

```python
# Logs genéricos sin contexto
logger.info("Listo")
logger.error("Error")

# Logs con valores vacíos
logger.info(f"Resultado: {result}")  # ← Si result es None, confuso
```

---

## 🔧 Configuración Avanzada

### Cambiar nivel de logging

```python
# En main.py o gui.py
from logic.logger import setup_logging
import logging

setup_logging(level=logging.DEBUG)  # ← Máxima verbosidad
```

### Niveles disponibles

```python
logging.DEBUG       # ← Máxima información
logging.INFO        # ← Normal (default)
logging.WARNING     # ← Solo advertencias+
logging.ERROR       # ← Solo errores+
logging.CRITICAL    # ← Errores graves
```

---

## 📊 Estadísticas

- **Archivo actual:** `facret/logs/facret.log`
- **Tamaño máximo:** 10 MB
- **Backups mantenidos:** 5 archivos
- **Total máximo:** 50 MB histórico

---

## ✅ Checklist: Agregar Logging a una Página

- [ ] Importar: `from logic.logger import get_logger`
- [ ] Crear instancia: `logger = get_logger(__name__)`
- [ ] INFO para eventos normales
- [ ] WARNING para situaciones anómalas
- [ ] ERROR en bloques try/except
- [ ] DEBUG para operaciones detalladas
- [ ] Probar: ejecutar y verificar logs en consola

---

**Última actualización:** 26 de Julio 2026
