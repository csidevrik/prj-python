# 📝 Guía de Logging en FACRET

**Archivo:** `logic/logger.py`  
**Status:** ✅ Creado y listo para usar

---

## 🎯 Propósito

Proporcionar **trazabilidad completa** de errores, advertencias e información de la app para facilitar debugging y diagnostico.

---

## 📊 Características

- ✅ **Logs a archivo** — persistencia de eventos
- ✅ **Logs a consola** — feedback inmediato con colores
- ✅ **Rotación automática** — archivos de hasta 10 MB
- ✅ **5 niveles** — DEBUG, INFO, WARNING, ERROR, CRITICAL
- ✅ **Timestamps** — fecha/hora en cada evento
- ✅ **Nombres de módulo** — saber dónde se originó el log

---

## 🚀 Uso Básico

### Paso 1: Importar logger en tu archivo

```python
# En cualquier archivo de logic/, pages/, components/
from logic.logger import get_logger

logger = get_logger(__name__)
```

### Paso 2: Usar en tu código

```python
# INFO — eventos normales
logger.info("Carpeta cargada: D:\\Facturas")
logger.info(f"Se encontraron {count} archivos")

# WARNING — situaciones anómalas pero recuperables
logger.warning("Carpeta vacía, no hay archivos a procesar")
logger.warning(f"Archivo no legible: {filename}")

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
| **DEBUG** | Cyan | Información detallada para debugging | `"Procesando fila 42 de 100"` |
| **INFO** | Green | Eventos normales | `"Carpeta cargada exitosamente"` |
| **WARNING** | Yellow | Situaciones anómalas | `"Archivo no legible, saltando"` |
| **ERROR** | Red | Errores recuperables | `"Fallo al conectar Outlook: {ex}"` |
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
        logger.info(f"Encontrados {num_files} items en {folder_path}")
        
        return FolderStats(...)
    
    except Exception as e:
        logger.error(f"Error al analizar carpeta {folder_path}: {e}")
        return None
```

### En pages/contracts_page.py

```python
from logic.logger import get_logger

logger = get_logger(__name__)

class ContractsPage:
    def _on_edit(self, e):
        try:
            logger.debug(f"Editando servicio: {self._selected.cod_serv}")
            # ... código de edición ...
            logger.info(f"Servicio {self._selected.cod_serv} actualizado")
        except Exception as ex:
            logger.error(f"Fallo al editar servicio: {ex}")
            self._log("Error al guardar cambios")
```

### En logic/contracts_loader.py

```python
from logic.logger import get_logger

logger = get_logger(__name__)

def load_contratos():
    logger.info("Cargando contratos...")
    
    try:
        contratos = []
        agencias = load_agencias()
        logger.debug(f"Agencias cargadas: {len(agencias)}")
        
        for path in sorted(_CONTRACTS_DIR.glob("*.json")):
            logger.debug(f"Leyendo contrato: {path.name}")
            # ... procesar contrato ...
            contratos.append(...)
        
        logger.info(f"Contratos cargados: {len(contratos)}")
        return contratos
    
    except Exception as e:
        logger.critical(f"Fallo crítico al cargar contratos: {e}")
        raise
```

---

## 🔍 Leer Logs

### Opción 1: Desde archivo

```bash
# Ver últimas 50 líneas
tail -50 facret/logs/facret.log

# Ver todos los errores
grep ERROR facret/logs/facret.log

# Ver timeline completa
cat facret/logs/facret.log
```

### Opción 2: En consola (mientras corre la app)

La app imprime logs en consola con colores:

```
INFO | facret | Carpeta cargada: D:\Facturas
DEBUG | facret.folder_stats | Analizando carpeta...
INFO | facret.folder_stats | Encontrados 42 items
WARNING | facret.contracts_loader | Carpeta vacía
ERROR | facret | Fallo al conectar Outlook: [Exception]
```

---

## 📈 Casos de Uso

### 1. Debugging rápido

**Problema:** "¿Por qué no se cargan las estadísticas?"

**Solución:**
1. Abre `facret/logs/facret.log`
2. Busca ERROR o WARNING en las últimas líneas
3. Verás exactamente qué falló

### 2. Auditoría de operaciones

**Problema:** "¿Cuándo se descargó la última factura?"

**Solución:**
1. Busca en logs: `grep "factura" facret/logs/facret.log`
2. Verás timestamp exacto y detalles

### 3. Monitoring en producción

**Problema:** "¿Está la app working correctamente?"

**Solución:**
1. Monitorear `facret.log` buscando CRITICAL o ERROR
2. Alertar si hay eventos graves

### 4. Análisis de performance

**Problema:** "¿Dónde se pierde tiempo?"

**Solución:**
1. Comparar timestamps en logs
2. Identificar operaciones lentas

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

# Logs con strings vacíos
logger.info(f"Resultado: {result}")  # ← Si result es None, es confuso
```

### 🎯 Lo correcto

```python
if result:
    logger.info(f"Operación exitosa: {result}")
else:
    logger.warning("Operación sin resultado")
```

---

## 🔧 Configuración Avanzada

### Cambiar nivel de logging

```python
# En main.py o gui.py, antes de iniciar
from logic.logger import setup_logging
import logging

setup_logging(level=logging.DEBUG)  # ← Máxima verbosidad
```

### Niveles disponibles

```python
logging.DEBUG       # ← Máxima información
logging.INFO        # ← Normal
logging.WARNING     # ← Solo advertencias+
logging.ERROR       # ← Solo errores+
logging.CRITICAL    # ← Errores graves
```

---

## 📊 Estadísticas de Logs

```
Archivo actual:     facret/logs/facret.log
Tamaño máximo:      10 MB
Backups mantenidos: 5 archivos
Total máximo:       50 MB histórico
```

---

## ✅ Checklist: Agregar Logging a una Página

- [ ] Importar logger: `from logic.logger import get_logger`
- [ ] Crear instancia: `logger = get_logger(__name__)`
- [ ] Agregar INFO para eventos normales
- [ ] Agregar WARNING para situaciones anómalas
- [ ] Agregar ERROR en bloques try/except
- [ ] Agregar DEBUG para operaciones detalladas
- [ ] Probar: ejecutar y verificar logs en consola

---

## 🎓 Ejemplo Completo

```python
# pages/mi_pagina.py
import flet as ft
from logic.logger import get_logger

logger = get_logger(__name__)

class MiPagina:
    def __init__(self, page):
        self.page = page
        logger.info("MiPagina inicializada")
    
    def build(self):
        logger.debug("Construyendo UI de MiPagina")
        return ft.Container(...)
    
    def _on_button_click(self, e):
        try:
            logger.debug("Usuario hizo clic en botón")
            # ... lógica ...
            logger.info("Botón procesado exitosamente")
        except Exception as ex:
            logger.error(f"Error en _on_button_click: {ex}")
            # Mostrar error al user
```

---

## 📚 Referencia Rápida

```python
from logic.logger import get_logger

logger = get_logger(__name__)

logger.debug("Información de debugging")      # Cyan
logger.info("Información normal")              # Green
logger.warning("Advertencia anómala")          # Yellow
logger.error("Error recuperable")              # Red
logger.critical("Error grave en app")          # Magenta
```

---

## 🎯 Próximos Pasos

1. **Agregar logging a `logic/`** — máxima prioridad
2. **Agregar logging a `pages/`** — importante
3. **Agregar logging a `components/`** — cuando sea necesario
4. **Monitorear `facret.log`** — revisar periódicamente

---

**Generado:** 26 de Julio 2026  
**Ubicación:** `logic/logger.py` + esta guía
**Estado:** ✅ Listo para usar
