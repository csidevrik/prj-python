# Changelog

Todos los cambios notables en este proyecto se documentarán en este archivo.

---

## [Unreleased]

### Features ✨
- **Logging Profesional** — Sistema centralizado con 5 niveles (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Logs a archivo (`logs/facret.log`) + consola con colores
  - Rotación automática (10 MB máximo)
  - Timestamps y identificación de módulo
- **Helpers Reutilizables** — 6 componentes visuales genéricos en `components/helpers.py`
  - `build_stat_chip()` — chips etiqueta/valor
  - `build_status_text()` — texto con color por estado
  - `build_info_row()` — fila de información
  - `build_divider_section()` — secciones con divider
  - `build_action_card()` — tarjetas de acción
  - `build_labeled_field()` — campos con etiqueta
- **File Picker en Download FACS** — Botón "Explorar" para seleccionar carpetas
  - Opción 1: Copiar/pegar path (mantiene funcionalidad existente)
  - Opción 2: Diálogo nativo de selección (NUEVO)
- **Sincronización de Carpeta de Trabajo** — Compartida entre Download FACS y Gestión FACS
  - Actualiza automáticamente en sidebar sin interrumpir navegación
  - Usa `page.data["on_config_change"]` para comunicación desacoplada
- **Estadísticas en Tiempo Real en Sidebar** — Muestra tamaño, archivos, carpetas
  - Cálculo recursivo con `logic/folder_stats.py`
  - Se actualiza al guardar configuración
  - Formatea MB/GB automáticamente

### Improvements 🔧
- **Reducción de Duplicación** — ~50 líneas de código eliminadas
  - Helpers visuales centralizados
  - Fácil mantenimiento de componentes comunes
- **Arquitectura Modular** — Puntuación 8.5/10
  - Sin código muerto
  - Separación clara de capas
  - Bajo acoplamiento entre módulos
- **Documentación Consolidada** — Estructura profesional para GitHub
  - Archivos Markdown organizados en `docs/`
  - CONTRIBUTING.md para guía de desarrollo
  - ARCHITECTURE.md para visión técnica

### Documentation 📚
- `GUIA_LOGGING.md` — Cómo usar el sistema de logging
- `GUIA_HELPERS.md` — Cómo usar helpers reutilizables
- `ANALISIS_MODULARIDAD.md` — Análisis arquitectónico del proyecto
- `PROPUESTA_ESTRUCTURA_GITHUB.md` — Plan de reorganización formal

### Bug Fixes 🐛
- Corregido: `_estado_color()` removida sin actualizar usos
- Corregido: `_op_color()` removida sin actualizar usos

---

## [0.1.0] — 26 Julio 2026

### Initial Release 🚀

**Features:**
- Router dinámico con `importlib` — agregar páginas sin tocar `gui.py`
- Componentes reutilizables (header, sidebar, toolbar, settings)
- Sistema de temas Material Design 3 — cambio en tiempo real
- Módulo de Contratos ETAPA — tabla de 22 servicios
- Descarga de facturas desde Outlook — vía `win32com`
- Gestión y procesamiento de XML — renombrado, deduplicación, CSV/JSON
- Página principal con dashboard de resumen

**Architecture:**
- Separación clara: logic (sin Flet) | pages | components | models | config
- Tema centralizado en `AppTheme` — sin hardcoding de colores
- Menú de navegación en `menu_config.py` — fuente única de verdad
- Sistema de eventos vía `page.data` — desacoplamiento entre componentes
- Modelos como dataclasses simples — sin lógica de UI

**Data Model:**
- `Agencia` — 22 sedes y ubicaciones
- `Contrato` — ETAPA-RE1 con 22 servicios (internet + datos)
- `EnlaceInternet` y `EnlaceDatos` — tipos de servicio
- `Evento` — historial de cambios por servicio

**Documentation:**
- `README.md` — quick start e instalación
- `FLET_BASE_PROMPT.md` — template base para proyectos Flet
- `CONTRACTS_DESIGN.md` — diseño del módulo de contratos
- `MQTT_MONITOR_PROMPT.md` — especificación futura

---

## Notas sobre Versionado

- **Formato**: Semantic Versioning (MAJOR.MINOR.PATCH)
- **Canales**: development branch `facreto` → releases en tag
- **Próxima versión planeada**: 0.2.0 con MQTT monitoring

---

**Última actualización:** 26 de Julio 2026
