# 🤝 Guía de Contribución

Gracias por interés en contribuir a FACRET. Esta guía te ayudará a entender la estructura del proyecto y las mejores prácticas.

---

## 📋 Requisitos Previos

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- Git
- Conocimiento básico de Flet (framework UI)

---

## 🚀 Configuración de Desarrollo

### 1. Clonar y configurar

```bash
git clone https://github.com/tu-usuario/facret.git
cd facret
poetry install
```

### 2. Ejecutar la app

```bash
poetry run python src/main.py
```

### 3. Crear rama de trabajo

```bash
git checkout -b feature/nombre-feature
# o
git checkout -b bugfix/nombre-bug
```

---

## 🏗️ Estructura del Proyecto

```
facret/
├── src/
│   ├── main.py           # Entry point
│   ├── gui.py            # Orquestador + router
│   ├── components/       # UI reutilizable
│   ├── pages/            # Vistas dinámicas
│   ├── logic/            # Lógica pura (sin Flet)
│   ├── models/           # Dataclasses
│   └── config/           # Configuración global
├── tests/                # Tests unitarios
├── docs/                 # Documentación
├── CHANGELOG.md          # Historial oficial
└── ARCHITECTURE.md       # Visión técnica
```

Ver [ARCHITECTURE.md](ARCHITECTURE.md) para detalles.

---

## 💡 Patrones de Desarrollo

### Agregar Una Página Nueva

1. **Crear archivo** en `src/pages/nueva_page.py`:
```python
import flet as ft
from config.theme import AppTheme as T
from logic.logger import get_logger

logger = get_logger(__name__)

class NuevaPage:
    def __init__(self, page: ft.Page):
        self.page = page
        logger.info("NuevaPage inicializada")
    
    def build(self) -> ft.Control:
        logger.debug("Construyendo UI")
        return ft.Container(...)
```

2. **Registrar en** `src/config/menu_config.py`:
```python
MenuItem(
    key="nueva",
    label="Nueva Página",
    icon=ft.Icons.XXXX,
    page_class="pages.nueva_page.NuevaPage",
)
```

3. ¡Listo! El router la detecta automáticamente.

### Usar Logging en tu Código

```python
from logic.logger import get_logger

logger = get_logger(__name__)

logger.debug("Información de debugging")
logger.info("Operación normal")
logger.warning("Situación anómala")
logger.error("Error recuperable")
logger.critical("Error grave")
```

Ver [docs/GUIDES/logging.md](docs/GUIDES/logging.md) para detalles.

### Usar Helpers Reutilizables

```python
from components.helpers import build_stat_chip, build_status_text

chip = build_stat_chip("Estado", "ACTIVO")
text = build_status_text("Mi estado", "ACTIVE")
```

Ver [docs/GUIDES/helpers.md](docs/GUIDES/helpers.md) para más.

### Agregar Lógica de Negocio

**Regla:** Toda lógica va en `logic/`, SIN dependencias de Flet.

```python
# src/logic/mi_logica.py
from logic.logger import get_logger

logger = get_logger(__name__)

def procesar_algo(data):
    """Lógica pura, testeable."""
    logger.debug(f"Procesando: {data}")
    try:
        resultado = ...
        logger.info(f"Resultado: {resultado}")
        return resultado
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
```

---

## 🧪 Testing

### Ejecutar tests

```bash
poetry run pytest
```

### Escribir tests

```python
# tests/test_folder_stats.py
from logic.folder_stats import get_folder_stats

def test_get_folder_stats():
    stats = get_folder_stats(".")
    assert stats.num_archivos >= 0
    assert stats.tamanio_mb >= 0
```

**Nota:** Los tests para `logic/` son prioritarios (código puro, testeable).

---

## 📝 Convenciones de Commits

### Formato
```
<tipo>: <descripción breve>

<descripción detallada (opcional)>
```

### Tipos
- `feat:` — Nueva feature
- `fix:` — Bug fix
- `docs:` — Documentación
- `refactor:` — Refactoring
- `test:` — Tests
- `chore:` — Tareas (dependencias, etc.)

### Ejemplos
```
feat: agregar File Picker en Download FACS

fix: corregir error en _estado_color()

docs: actualizar ARCHITECTURE.md

refactor: extraer helpers duplicados a components/helpers.py
```

---

## 🎯 Checklist Antes de PR

- [ ] Código escribe sin errores
- [ ] Tests pasan (`poetry run pytest`)
- [ ] Logging agregado a logic/
- [ ] Documentación actualizada
- [ ] Commits tienen mensajes claros
- [ ] Rama está actualizada con main

---

## 🔍 Code Review

Al revisar PRs, verificar:

1. **Separación de capas** — ¿logic/ está sin Flet?
2. **Bajo acoplamiento** — ¿Se importa solo lo necesario?
3. **Logging** — ¿Se agregó logging apropiadod?
4. **Tests** — ¿Hay tests para logic/?
5. **Documentación** — ¿Se actualizó docs/?

---

## 📚 Documentación

Al agregar feature, actualizar:

1. **CHANGELOG.md** — Agregar a sección `[Unreleased]`
2. **docs/GUIDES/features.md** — Resumen de feature
3. **Docstrings** en el código (si es complejo)
4. **ARCHITECTURE.md** — Si cambia arquitectura

---

## 🚨 Problemas Comunes

### Error: "NameError: name 'variable' is not defined"
→ Verificar que la función esté definida. Usar logging para debuggear:
```python
logger.debug(f"Variable: {variable}")
```

### Error: "Módulo no encontrado"
→ Verificar import path. Usar ruta absoluta:
```python
# ❌ NO
from pages.home_page import HomePage

# ✅ SÍ
from logic.contracts_loader import load_contratos
```

### La página no carga
→ Verificar `menu_config.py` y que la clase exista con método `build()`.

---

## 🤖 Continuous Integration (Futuro)

Planeamos agregar:
- ✅ Tests automáticos en push
- ✅ Type checking (mypy)
- ✅ Linting (ruff)
- ✅ Autoformato (black)

---

## 📞 ¿Preguntas?

- Revisa [ARCHITECTURE.md](ARCHITECTURE.md) para entender el diseño
- Revisa [docs/GUIDES/](docs/GUIDES/) para guías específicas
- Abre una issue con tu pregunta

---

**Última actualización:** 26 de Julio 2026

Gracias por contribuir a FACRET 🚀
