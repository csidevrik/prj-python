# 📚 GUÍAS DE ARQUITECTURA Y ESTRUCTURA - FACRET

## 🎯 ¿POR DÓNDE EMPIEZO?

Elige según tu necesidad:

### 0️⃣ [ESTRUCTURA_VISUAL.md](ESTRUCTURA_VISUAL.md) 🎨
**Lectura: 3 minutos**

Para ver de un vistazo:
- Diagrama árbol completo ANTES/DESPUÉS
- Qué está activo vs legacy
- Flujos de data visuales

**Perfecto para**: Ejecutivos, líderes de proyecto, entender en 3 minutos

---

### 1️⃣ [ARQUITECTURA_RAPIDA.md](ARQUITECTURA_RAPIDA.md) ⚡
**Lectura: 5 minutos**

Para desarrolladores que necesitan:
- Entender el flujo principal RÁPIDO
- Saber dónde agregar componentes nuevos
- Referencia rápida de carpetas

**Perfecto para**: Iniciar un feature nuevo, resolver dudas sobre estructura

---

### 2️⃣ [ESTRUCTURA_COMPONENTES.md](ESTRUCTURA_COMPONENTES.md) 📊
**Lectura: 10-15 minutos**

Para analistas/arquitectos que necesitan:
- Mapa completo de componentes
- Identificar archivos huérfanos
- Entender dependencias
- Gráficos de flujo

**Perfecto para**: Auditoría de código, entender arquitectura completa, tomar decisiones de refactoring

---

### 3️⃣ [PLAN_LIMPIEZA.md](PLAN_LIMPIEZA.md) 🧹
**Lectura: 10 minutos + 30-60 min ejecución**

Para líderes de proyecto / DevLead que necesitan:
- Plan paso a paso para limpiar código muerto
- Checklist de acciones
- Análisis de riesgos

**Perfecto para**: Planificar refactoring, mejorar calidad, decisiones de limpieza

---

## 📊 RESUMEN EJECUTIVO

### ✅ Lo Que Está ACTIVO
- **Interfaz**: `src/drive_gui.py` (punto de entrada recomendado)
- **Componentes**: `header/responsive_header.py` + `drive_sidebar.py` + `drive_content.py` + `sync_status.py`
- **Tema**: `config/drive_theme.py`
- **Lógica**: `logic/` + `core/`

### ❌ Lo Que Está DESUSO (15+ archivos)
- Múltiples puntos de entrada: `main.py`, `main2.py`, `gui.py`, `gui2.py`, `main_drive.py`
- Componentes legacy: `app_bar.py`, `nav_rail.py`, `file_explorer.py`, `preview_panel.py`, `drive_header.py`, `content_router.py`
- Configuración antigua: `theme.py`, `menu_structure.py`

### 🎯 RECOMENDACIÓN
1. Lee `ARQUITECTURA_RAPIDA.md` (5 min)
2. Lee `ESTRUCTURA_COMPONENTES.md` si necesitas contexto profundo
3. Ejecuta `PLAN_LIMPIEZA.md` Fase 1 + 2 (sin riesgo + consolidación)

---

## 🔗 Relación Entre Documentos

```
README.md (descripción principal)
    ↓
    Señala → ARQUITECTURA_RAPIDA.md ⚡ (inicio)
             ↓
             Detalla → ESTRUCTURA_COMPONENTES.md 📊 (completo)
                       ↓
                       Implementa → PLAN_LIMPIEZA.md 🧹 (acción)
```

---

## 📋 CAMBIOS IMPLEMENTADOS

✅ Actualizado `README.md` con referencias a documentación  
✅ Creado `ARQUITECTURA_RAPIDA.md` - guía rápida de 2 minutos  
✅ Creado `ESTRUCTURA_COMPONENTES.md` - análisis detallado con tablas y gráficos  
✅ Creado `PLAN_LIMPIEZA.md` - checklist ejecutable paso a paso  

---

## 💡 PRÓXIMOS PASOS RECOMENDADOS

### Corto Plazo (Esta Semana)
- [ ] Lee `ARQUITECTURA_RAPIDA.md`
- [ ] Entiende el flujo actual
- [ ] Identifica archivos que no necesitas

### Medio Plazo (Este Sprint)
- [ ] Ejecuta `PLAN_LIMPIEZA.md` Fase 1
- [ ] Verifica que todo funcione
- [ ] Haz commit de cambios

### Largo Plazo (Próximo Sprint)
- [ ] Ejecuta `PLAN_LIMPIEZA.md` Fase 2
- [ ] Consolida punto de entrada
- [ ] Considera Fase 3 (legacy cleanup)

---

## 🆘 ¿Tienes dudas?

| Pregunta | Respuesta |
|----------|-----------|
| ¿Dónde creo un componente nuevo? | Ver `ARQUITECTURA_RAPIDA.md` - "¿Dónde debo agregar...?" |
| ¿Cuál es el flujo completo? | Ver `ESTRUCTURA_COMPONENTES.md` - "Árbol de componentes" |
| ¿Qué archivos puedo eliminar? | Ver `PLAN_LIMPIEZA.md` - "PASO 1: Eliminación" |
| ¿Cuáles son las dependencias? | Ver `ESTRUCTURA_COMPONENTES.md` - "Mapa de dependencias" |

---

**Última actualización**: 2 de Marzo, 2026

