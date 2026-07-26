# 📦 Setup e Instalación

Guía para configurar FACRET en tu máquina local.

---

## 📋 Requisitos Previos

- **Python 3.11 o superior**
- **[Poetry](https://python-poetry.org/docs/#installation)** (gestor de dependencias)
- **Poppler 24.08.0** (incluido en `src/poppler-24.08.0/` para Windows)
- **Microsoft Outlook** (para funcionalidad Download FACS)
- **Git** (opcional, para clonar repo)

---

## 🚀 Instalación Rápida (5 minutos)

### Paso 1: Clonar y entrar a la carpeta

```bash
git clone <url-del-repo>
cd prj-python/facret
```

### Paso 2: Instalar dependencias con Poetry

```bash
poetry install
```

Esto descarga todas las dependencias especificadas en `pyproject.toml` y las instala en un entorno virtual.

### Paso 3: Ejecutar la aplicación

```bash
poetry run python src/main.py
```

La ventana de FACRET se abrirá en Windows.

---

## 📚 Stack Tecnológico

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| **Lenguaje** | Python | 3.11+ |
| **UI Framework** | Flet | 0.28.3 |
| **Renderizado PDF** | pdf2image + Poppler | 24.08.0 |
| **Automatización Outlook** | pywin32 (win32com) | Latest |
| **Gestión proyecto** | Poetry | Latest |

---

## 🔧 Desarrollo

### Instalar en modo desarrollo

Si vas a hacer cambios en el código:

```bash
poetry install --with dev
```

### Ejecutar con logging en DEBUG

```bash
FACRET_LOG_LEVEL=DEBUG poetry run python src/main.py
```

### Ejecutar tests (futuro)

```bash
poetry run pytest
```

---

## 📁 Estructura de Carpetas

```
facret/
├── src/
│   ├── main.py              ← Entry point
│   ├── gui.py               ← Orquestador (router + layout)
│   ├── config/
│   │   ├── theme.py         ← Tema global (Material Design 3)
│   │   ├── menu_config.py   ← Menú de navegación
│   │   └── facs_config.json ← Configuración persistente
│   ├── components/
│   │   ├── sidebar.py
│   │   ├── helpers.py       ← UI reutilizable
│   │   └── ...
│   ├── pages/
│   │   ├── home_page.py
│   │   ├── facs_downloader_page.py
│   │   ├── facs_manager_page.py
│   │   └── contracts_page.py
│   ├── logic/
│   │   ├── logger.py        ← Logging centralizado
│   │   ├── folder_stats.py
│   │   ├── contracts_loader.py
│   │   ├── contracts_writer.py
│   │   ├── config_manager.py
│   │   ├── facs_downloader.py
│   │   └── facs_manager.py
│   ├── models/
│   │   └── models.py        ← Dataclasses
│   ├── data/
│   │   ├── agencias.json
│   │   └── contracts/
│   │       └── ETAPA-RE1.json
│   └── poppler-24.08.0/     ← PDF rendering engine
├── tests/                   ← Tests unitarios (futuro)
├── logs/                    ← Logs generados al ejecutar
├── docs/                    ← Documentación
├── pyproject.toml           ← Dependencias Poetry
├── poetry.lock              ← Lock file
├── README.md                ← Punto de entrada
├── CHANGELOG.md             ← Historial de cambios
├── CONTRIBUTING.md          ← Guía de contribución
└── ARCHITECTURE.md          ← Visión técnica
```

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'flet'"

**Solución:**
```bash
poetry install
```

### Error: "Poppler not found"

**Solución:**
- Verifica que `src/poppler-24.08.0/` existe
- Usa ruta absoluta en imports si es necesario

### Error: "Microsoft Outlook no está instalado"

**Solución:**
- Descarga [Outlook de Microsoft Store](https://www.microsoft.com/outlook)
- Configura una cuenta de email
- FACRET requiere Outlook instalado localmente

### App no carga temas

**Solución:**
```bash
# Verifica que config/theme.py tiene AppTheme correctamente definida
python -c "from src.config.theme import AppTheme; print(AppTheme.PRIMARY)"
```

---

## 📝 Archivos de Configuración

### `src/config/facs_config.json`

Almacena preferencias del usuario:

```json
{
  "carpeta_guardar": "D:\\Descargas\\FACRET",
  "carpeta_trabajo": "D:\\CONTRATOS\\ZTEST",
  "email_remitente": "noreply@etapa.net.ec",
  "email_destinatario": "finanzas@empresa.com",
  "tema": "light"
}
```

### `src/data/contracts/ETAPA-RE1.json`

Contratos y servicios:

```json
{
  "id": "ETAPA-RE1",
  "proveedor": "ETAPA EP",
  "vigencia_inicio": "2022-09-01",
  "vigencia_fin": "2025-09-01",
  "servicios": [
    {
      "cod_serv": "IO247963",
      "tipo": "internet",
      "agencia_id": "CAPULISPAMBA",
      "estado": "ACTIVE",
      "estado_operativo": "UP"
    },
    ...
  ]
}
```

---

## 🌐 Conectividad Outlook

FACRET se conecta a Outlook via `win32com` (solo Windows):

1. **Requisito:** Outlook 2016+ instalado y configurado
2. **Acceso:** Se realiza localmente (no necesita credenciales extra)
3. **Riesgos:** Ninguno (acceso local, no cloud)

Para deshabilitar Download FACS:
- Comentar línea en `src/config/menu_config.py` que registra `facs_downloader_page`

---

## 📊 Primer Uso

Al abrir la app por primera vez:

1. ✅ Verás la página **Home** (dashboard)
2. ✅ Sidebar mostrará carpeta por defecto (o vacío si no hay config)
3. ⚙️ Abre **Configuración** para set:
   - Carpeta de descarga
   - Carpeta de trabajo
   - Tema (light/dark)
4. 📥 Ve a **Download FACS** para descargar facturas desde Outlook
5. 📋 Ve a **Contratos ETAPA** para ver/editar servicios

---

## 🚀 Próximos Pasos

- Lee [ARCHITECTURE.md](../ARCHITECTURE.md) para entender cómo está construida la app
- Lee [CONTRIBUTING.md](../CONTRIBUTING.md) para cómo contribuir
- Consulta [docs/GUIDES/](GUIDES/) para guías específicas

---

**Última actualización:** 26 de Julio 2026
