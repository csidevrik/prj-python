# 📄 FACRET

Herramienta de escritorio para automatizar la descarga y procesamiento de facturas XML. Construida con Python + Flet para el área financiera de **EMOV EP**.

---

## 🎯 ¿Qué hace?

✅ **Descarga** facturas ETAPA desde Outlook local (sin cuenta Microsoft paga)  
✅ **Procesa** XML: extrae datos, detecta duplicados, renombra archivos  
✅ **Genera reportes** en CSV y JSON  
✅ **Interfaz moderna** estilo explorador de archivos con tema personalizable  
✅ **Logging profesional** para debugging y auditoría

---

## 🚀 Quick Start

### Requisitos
- Python 3.11+
- [Poetry](https://python-poetry.org/)
- Microsoft Outlook (para Download FACS)

### Instalar y ejecutar

```bash
cd facret
poetry install
poetry run python src/main.py
```

Ver [docs/SETUP.md](docs/SETUP.md) para más detalles.

---

## 📚 Documentación

| Documento | Para qué |
|-----------|----------|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Entender cómo está construida la app |
| **[CHANGELOG.md](CHANGELOG.md)** | Ver historial de cambios y features |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Contribuir al proyecto |
| **[docs/GUIDES/](docs/GUIDES/)** | Guías de desarrollo (logging, helpers, etc.) |
| **[docs/ANALYSIS/](docs/ANALYSIS/)** | Análisis técnicos (modularidad, arquitectura) |
| **[docs/ROADMAP/](docs/ROADMAP/)** | Futuro del proyecto (MQTT monitoring, etc.) |

---

## 🏛️ Arquitectura

La app está organizada en **5 capas independientes**:

```
gui.py (orquestador)
  ↓
components/ (UI reutilizable) | pages/ (vistas) | config/ (global)
  ↓
logic/ (lógica pura, sin Flet)
  ↓
models/ (dataclasses)
```

**Puntuación:** 8.5/10 en modularidad — sin código muerto, bajo acoplamiento, fácil de extender.

Ver [ARCHITECTURE.md](ARCHITECTURE.md) para detalles.

---

## 🌟 Features Principales

### 📥 Descarga de Facturas
- Descarga automática desde Outlook via `win32com`
- Configurable: carpeta, correo remitente, destinatario
- Logs detallados de cada operación

### 📋 Gestión de Facturas
- Exploración de carpetas con búsqueda
- Procesamiento de XML: parseo, validación, renombrado
- Generación de reportes CSV y JSON
- Eliminación de duplicados por SHA-256

### 📊 Monitoreo de Contratos ETAPA
- Tabla de 22 servicios (internet + datos)
- Edición en tiempo real
- Historial de cambios
- Estadísticas de uso

### ⚙️ Sistema Profesional
- **Logging en 5 niveles** — DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Helpers reutilizables** — componentes UI genéricos
- **Temas en tiempo real** — Material Design 3
- **Sincronización automática** — entre módulos

---

## 🛠️ Tecnología

| Layer | Stack |
|-------|-------|
| **Frontend** | Flet 0.28.3 (Python GUI) |
| **Backend** | Python 3.11+ |
| **Data** | JSON, CSV, SQLite (futuro) |
| **Integration** | Outlook COM (win32com) |
| **Package Mgmt** | Poetry |

---

## 📖 Cómo Usar

### Agregar una página nueva

```python
# 1. Crear: src/pages/nueva_page.py
class NuevaPage:
    def __init__(self, page): self.page = page
    def build(self): return ft.Container(...)

# 2. Registrar en src/config/menu_config.py
MenuItem(key="nueva", label="Nueva", page_class="pages.nueva_page.NuevaPage")
# ¡Listo!
```

### Agregar logging

```python
from logic.logger import get_logger
logger = get_logger(__name__)

logger.info("Operación normal")
logger.error(f"Error: {ex}")
```

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para guía completa.

---

## 🤝 Contribuir

Queremos tu ayuda. Ver [CONTRIBUTING.md](CONTRIBUTING.md) para:
- Cómo configurar desarrollo
- Patrones de código
- Checklist antes de PR
- Convenciones de commits

---

## 📊 Estado Actual

**v0.1.0** — MVP funcional con 4 páginas + logging profesional + arquitectura modular  
**Próximo:** v0.2.0 — MQTT monitoring en tiempo real

Ver [CHANGELOG.md](CHANGELOG.md) para historial completo.

---

## 📞 Contacto

- **Repo:** [github.com/tu-usuario/facret](https://github.com/)
- **Issues:** [Issues en GitHub]
- **Email:** tu-email@ejemplo.com

---

**Última actualización:** 26 de Julio 2026
